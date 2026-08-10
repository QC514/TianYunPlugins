#[pin:true]
#[author: mrconli]
#[title: 沪上阿姨]
#[language: python]
#[class: 餐饮类]
#[service: mrconli，Q群：1040780519] 售后联系方式
#[disable: false] 禁用开关，true表示禁用，false表示可用
#[admin: false] 是否为管理员指令
#[rule: ^沪上(.*)|(.*)沪上$] 匹配规则，多个规则时向下依次写多个
#[cron: 46 7 * * *] cron定时，支持5位域和6位域
#[priority: 66] 优先级，数字越大表示优先级越高
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[open_source: false]是否开源
#[icon: http://www.fulemi.com/static/upload/image/20241123/1732344330950667.jpg]
#[version: 1.0.2]版本号
#[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
#[price: 1] 上架价格
#[description: 微信小程序-沪上阿姨，每日签到。指令：沪上(登录|登陆|上车|提交)、沪上查询、沪上管理。触发指令【沪上】你可以改成自己喜欢的文字。内置脚本，无授权系统。需要在计划任务添加 定时指令【沪上运行】 启用自处理 伪装管理员] 使用方法尽量写具体


# [param: {"required":true,"key":"mrconli_hsay.notify","bool":false,"placeholder":"","name":"管理员通知","desc":"如 qq,wx,tg 用英文“,”符号分割,不设默认qq"}]
# [param: {"required":true,"key":"mrconli_hsay.yxbf","bool":false,"placeholder":"5","name":"运行并发数","desc":"并发阅读多少号，任务并发非抢购,默认5"}]
# [param: {"required":true,"key":"mrconli_hsay.proxy","bool":false,"placeholder":"","name":"代理api","desc":"号多或者报错才加代理，不加留空即可"}]


import middleware, requests, time, json, re
from datetime import datetime, timedelta

try:
    import concurrent.futures
except:
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    sender.reply("请安装concurrent依赖，可用订阅里面的插件安装")
    exit(0)

def get_ip(url,ts):
    try:
        res = requests.get(url)
        if res.status_code == 200 and "白名单" not in res.text:
            print(f"获取到ip---{res.text}")
            proxy = {
                "https":f"http://{res.text}",
                "http":f"http://{res.text}"
            }
            return proxy
        elif "白名单" in res.text:
            print(res.text)
            middleware.notifyMasters(f"[沪上阿姨代理异常通知]{res.text}",ts)
        else:
            return ""
    except:
        return ""

class LT:
    def __init__(self, user, sender):
        self.user = user
        self.sender = sender
        self.tongname = "mrconli_hsay_token"
        self.tongconfig = "mrconli_hsay"
        self.xwid = None
        self.dlapi = middleware.bucketGet(self.tongconfig,"proxy")
        ts = middleware.bucketGet(self.tongconfig,"notify")
        if ts == "":
            self.ts = f'{["qq"]}'
        else:
            self.ts = ts.split(",")
        self.msg = ""
        self.userts = ""
        self.erro_msg = ""
    def login(self,ck):
        url = "https://webapi.qmai.cn/web/catering/crm/personal-info?appid=wxd92a2d29f8022f40"
        headers = {
            "Host": "webapi.qmai.cn",
            "Connection": "keep-alive",
            "promotion-code": "",
            "work-wechat-userid": "",
            "store-id": "201424",
            "Accept-Language": "zh-CN",
            "work-staff-id": "",
            "scene": "1178",
            "Qm-From-Type": "catering",
            "multi-store-id": "60808",
            "Qm-User-Token": ck,
            "work-staff-name": "",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b11) XWEB/9129",
            "qz-gtd": "",
            "Qm-From": "wechat",
            "Content-Type": "application/json",
            "Accept": "v=1.0",
            "channelCode": "",
            "xweb_xhr": "1",
            "gdt-vid": "",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://servicewechat.com/wxd92a2d29f8022f40/314/page-frame.html",
            "Accept-Encoding": "gzip, deflate, br"
        }
        res = requests.get(url, headers=headers).json()
        if res["code"] == "0":
            phone = res["data"]["mobilePhone"]
            return phone
        else:
            return False


    def card(self, ck):
        url = "https://webapi.qmai.cn/web/catering/crm/coupon/list"
        headers = {
            "Host": "webapi.qmai.cn",
            "Connection": "keep-alive",
            "store-id": "201424", 
            "Accept-Language": "zh-CN",
            "scene": "1256",
            "Qm-From-Type": "catering",
            "multi-store-id": "60808",
            "Qm-User-Token": ck,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B)",
            "Content-Type": "application/json",
            "Accept": "v=1.0",
        }
        
        data = {
            "pageNo": 1,
            "pageSize": 50,
            "useStatus": 0,
            "appid": "wxd92a2d29f8022f40"
        }
        
        try:
            if self.dlapi != "":
                proxy = get_ip(self.dlapi, self.ts)
                res = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=10)
            else:
                res = requests.post(url, headers=headers, json=data, timeout=10)
                
            res_json = res.json()
            
            if res_json["code"] == "0" and "data" in res_json:
                coupons = res_json["data"].get("data", [])
                msg = ""
                for i in coupons:
                    expire_time = i.get("endAt", "未知")
                    title = i.get("title", "未知券名")
                    msg += f"[{title}] 过期时间: {expire_time}\n"
                
                total = res_json["data"].get("total", 0)
                return total, msg
            else:
                return 0, f"查询失败: {res_json.get('message', '未知错误')}"
                
        except Exception as e:
            print(f"优惠券查询异常: {str(e)}")
            return 0, f"查询异常: {str(e)}"

    def daycoin(self,ck):
        url = "https://webapi.qmai.cn/web/catering/crm/points-info"
        headers = {
            "Host": "webapi.qmai.cn",
            "Connection": "keep-alive",
            "Content-Length": "30",
            "promotion-code": "",
            "work-wechat-userid": "",
            "store-id": "201424",
            "Accept-Language": "zh-CN",
            "work-staff-id": "",
            "scene": "1178",
            "Qm-From-Type": "catering",
            "multi-store-id": "60808",
            "Qm-User-Token": ck,
            "work-staff-name": "",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b11) XWEB/9129",
            "qz-gtd": "",
            "Qm-From": "wechat",
            "Content-Type": "application/json",
            "Accept": "v=1.0",
            "channelCode": "",
            "xweb_xhr": "1",
            "gdt-vid": "",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://servicewechat.com/wxd92a2d29f8022f40/314/page-frame.html",
            "Accept-Encoding": "gzip, deflate, br"
        }
        data = {"appid":"wxd92a2d29f8022f40"}
        res = requests.post(url, headers=headers,json=data).json()
        if res["code"] == "0":
            coins = res["data"]["totalPoints"]
            return coins
        else:
            return 0

    def sign(self,phone,ck):
        url = "https://webapi.qmai.cn/web/cmk-center/sign/takePartInSign"
        headers = {
            "Host": "webapi.qmai.cn",
            "Connection": "keep-alive",
            "Content-Length": "65",
            "Qm-From": "wechat",
            "Accept": "v=1.0",
            "Qm-User-Token": ck,
            "xweb_xhr": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090b11) XWEB/9129",
            "Qm-From-Type": "catering",
            "Content-Type": "application/json",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://servicewechat.com/wxd92a2d29f8022f40/314/page-frame.html",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        data = {"activityId":"1004435002421583872","appid":"wxd92a2d29f8022f40"}
        try:
            time.sleep(1.5)
            res = requests.post(url,headers=headers,data=json.dumps(data)).json()
            if res["status"]:
                for i in res["data"]["rewardDetailList"]:
                    if i["rewardName"] == "积分奖励":
                        self.msg += f"{phone[:3]}***{phone[7:]}:获得积分{i['sendNum']}\n"
                        return f"获得积分{i['sendNum']}"
                    else:
                        self.msg += f'{phone[:3]}***{phone[7:]}:获得{res["data"]["rewardDetailList"][0]["rewardName"]}\n'
                        try:
                            middleware.push(self.userts,"",self.user,"沪上阿姨",f"[沪上阿姨]领取签到奖励：{phone}---"+res["data"]["rewardDetailList"][0]["rewardShowExtra"]["expiredDateStr"])
                        except:
                            print("领取错误")
                        return res["data"]["rewardDetailList"][0]["rewardName"]
            elif res["code"] == 0 and "已签到" in res["message"]:
                self.msg += f"{phone[:3]}***{phone[7:]}:已签到\n"
                return True
            else:
                self.msg += f"{phone[:3]}***{phone[7:]}:异常，可能过期\n"
                return False
        except Exception as e:
            try:
                if self.dlapi != "":
                    proxy = get_ip(self.dlapi,self.ts)
                else:
                    proxy = ""
                res = requests.post(url, headers=headers, data=json.dumps(data), proxies=proxy).json()
                if res["status"]:
                    for i in res["data"]["rewardDetailList"]:
                        if i["rewardName"] == "积分奖励":
                            self.msg += f"{phone[:3]}***{phone[7:]}:获得积分{i['sendNum']}\n"
                            return f"获得积分{i['sendNum']}"
                        else:
                            self.msg += f'{phone[:3]}***{phone[7:]}:获得{res["data"]["rewardDetailList"][0]["rewardName"]}\n'
                            try:
                                middleware.push(self.userts, "", self.user, "沪上阿姨", f"[沪上阿姨]领取签到奖励：{phone}---" +
                                                res["data"]["rewardDetailList"])
                            except:
                                print("领取错误")
                            return res["data"]["rewardDetailList"][0]["rewardName"]
                elif res["code"] == 0 and "已签到" in res["message"]:
                    self.msg += f"{phone[:3]}***{phone[7:]}:已签到\n"
                    return True
                else:
                    self.msg += f"{phone[:3]}***{phone[7:]}:异常，可能过期\n"
                    return False
            except:
                print(f"{phone}异常{e}")
                self.erro_msg += f"{phone[:3]}***{phone[7:]}签到异常（代理）\n"
                pass
                
 
    def signnum(self, ck):
        url = "https://webapi.qmai.cn/web/cmk-center/sign/userSignStatistics"
        headers = {
            "Host": "webapi.qmai.cn",
            "Connection": "keep-alive",
            "store-id": "201424",
            "Accept-Language": "zh-CN",
            "scene": "1256",
            "Qm-From-Type": "catering",
            "multi-store-id": "60808", 
            "Qm-User-Token": ck,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B)",
            "Content-Type": "application/json",
            "Accept": "v=1.0",
        }
    
        data = {
            "activityId": "1004435002421583872",
            "appid": "wxd92a2d29f8022f40"
        }
    
        try:
        # 修复了代理判断和请求逻辑
            if self.dlapi != "":
                proxy = get_ip(self.dlapi, self.ts)
                res = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=10)
            else:
                res = requests.post(url, headers=headers, json=data, timeout=10)
            
            res_json = res.json()
        
            if res_json.get("status") and "data" in res_json:
                signs = res_json["data"].get("signDays", 0)
                next_reward = "暂无"
            
                if res_json["data"].get("nextRewardList"):
                    next_rewards = res_json["data"]["nextRewardList"][0].get("rewardList", [])
                    if next_rewards:
                        next_days = res_json["data"].get("nextSignDays", 0)
                        next_reward = f'{next_rewards[0]["rewardName"]}差{next_days}天'
                return signs, next_reward
            else:
                print(f"签到统计响应异常: {res_json}")
                return 0, "获取失败"
            
        except Exception as e:
            print(f"签到统计异常: {str(e)}")
            return 0, f"查询异常: {str(e)}"

    def tj(self):
        tong = middleware.bucketGet(self.tongname, self.user)
        self.sender.reply(
            f"【沪上阿姨】请发送小程序抓的Qm-User-Token\n---按q退出")
        token = self.sender.listen(180000)
        if token == "q" or token == "":
            self.sender.reply("退出")
            exit(0)
        else:
            if self.login(token):
                phone = self.login(token)
                if tong == "":
                    t = []
                    d = {}
                    d[phone] = {
                        "token":token,
                        "qd": self.sender.getImtype(),
                        "sqsj": datetime.now().strftime("%Y-%m-%d")
                    }
                    t.append(d)
                    middleware.bucketSet(self.tongname, self.user, f"{t}")
                    self.sender.reply(f"账号{phone[:3]}***{phone[7:]}提交成功，发送【沪上查询】查看")
                    exit(0)
                else:
                    tong1 = eval(tong)
                    for t in tong1:
                        for k, y in t.items():
                            if k == phone:
                                t[k] = {
                                    "token": token,
                                    "qd": self.sender.getImtype(),
                                    "sqsj": datetime.now().strftime("%Y-%m-%d")
                                }
                                middleware.bucketSet(self.tongname,self.user,f"{tong1}")
                                self.sender.reply(f"{phone[:3]}***{phone[7:]}更新成功")
                                exit(0)
                    d = {}
                    d[phone] = {
                        "token": token,
                        "qd": self.sender.getImtype(),
                        "sqsj": datetime.now().strftime("%Y-%m-%d")
                    }
                    tong1.append(d)
                    middleware.bucketSet(self.tongname, self.user, f"{tong1}")
                    self.sender.reply(f"账号{phone[:3]}***{phone[7:]}提交成功，发送【沪上查询】查看")
                    exit(0)
            else:
                self.sender.reply("token错误或失效，退出")
                exit(0)


    def cx(self):
        tong = middleware.bucketGet(self.tongname, self.user)
        if tong == "":
            self.sender.reply("当前没有账号")
            exit(0)
        else:
            tong1 = eval(tong)
            msg = ""
            for sj in tong1:
                for k,y in sj.items():
                    ck = y["token"]
                    self.userts = y["qd"]
                    phone = k
                    if self.login(ck):
                        if self.sign(phone,ck):
                            qd = "✅"
                        else:
                            qd = "❎"
                        try:
                            num,card = self.card(ck)
                        except:
                            num,card = None,None
                        try:
                            if self.signnum(ck):
                                signs,next = self.signnum(ck)
                            else:
                                signs,next = "",""
                        except:
                            signs, next = "", ""
                        msg += f"📱手机号：{phone[:3]}***{phone[7:]}\n👛当前积分：{self.daycoin(ck)}\n📒累计签到：{signs}天\n🏷️签到状态：{qd}\n🚩目标：{next}\n🎫优惠券数量：{num}\n---------------------------\n"
                    else:
                        msg += f"【登陆失败】\n📱手机号：{phone[:3]}***{phone[7:]}token失效\n------------------------\n"
                    time.sleep(1)
            self.sender.reply(f"=======沪上查询=======\n{msg}\n🔔更多操作发送【沪上管理】")
            exit(0)

    def gl(self):
        tong = middleware.bucketGet(self.tongname, self.user)
        if tong == "":
            self.sender.reply("当前没有账号")
            exit(0)
        else:
            try:
                tong1 = eval(tong)
                msg = ""
                a = 1
                for sj in tong1:
                    for k, y in sj.items():
                        ck = y["token"]
                        phone = k
                        if self.login(ck):
                            msg += f"[{a}]:{phone[:3]}***{phone[7:]}\n"
                            a += 1
                        else:
                            msg += f"【登陆失败】\n📱手机号：{phone[:3]}***{phone[7:]}token失效\n------\n"
            
                self.sender.reply(f"=======沪上管理=======\n{msg}\n------------------------\n👉请发送数字序号，发送q退出")
                index = self.sender.listen(180000)
            
            # 添加输入检查
                if not index.isdigit():
                    self.sender.reply("请输入正确的数字序号")
                    exit(0)
                
                index = int(index)
                if index <= 0 or index > len(tong1):
                    self.sender.reply("序号超出范围")
                    exit(0)
                
            # 调整索引
                index = index - 1
                msg = ""
            
            # 使用 list() 确保是可迭代对象
                curr_account = list(tong1[index].items())[0]
                k, y = curr_account
            
                ck = y["token"]
                self.userts = y["qd"]
            
                if self.login(ck):
                    if self.sign(k,ck):
                        qd = "✅"
                    else:
                        qd = "❎"
                    try:
                        num,card = self.card(ck)
                    except:
                        num,card = 0,"获取失败"
                    
                    msg += f"\n📱手机号：{k[:3]}***{k[7:]}\n👛当前积分：{self.daycoin(ck)}\n🏷️签到状态：{qd}\n🎫优惠券数量：{num}\n------------------------\n"
                else:
                    msg += f"📱手机号：{k[:3]}***{k[7:]}token失效\n------------------------\n"
                
                self.sender.reply(f"=======沪上管理=======\n{msg}1. 查看优惠券\n2. 删除账号\n\n👉请发送数字序号，发送q退出")
    # 添加对选项的处理
                choice = self.sender.listen(180000)
                if choice == "q" or choice == "":
                    self.sender.reply("退出")
                    exit(0)
                elif choice == "1":
                    try:
                        num, card = self.card(ck)
                        self.sender.reply(f"=======优惠券列表=======\n{card}")
                    except Exception as e:
                        self.sender.reply(f"获取优惠券失败:{str(e)}")
                elif choice == "2":
                    # 调用删除账号方法
                    self.sc(index)
                else:
                    self.sender.reply("输入错误，退出")
                    exit(0)
            except Exception as e:
                self.sender.reply(f"操作异常:{str(e)}")
                exit(0)

    def sc(self, index):
        self.sender.reply(f"是否删除账号，y/n。\n---n退出")
        y = self.sender.listen(180000)
        if y == "n" or y == "":
            self.sender.reply("退出")
            exit(0)
        elif "y" == y:
            tong1 = eval(middleware.bucketGet(self.tongname, self.user))
            del tong1[index]
            middleware.bucketSet(self.tongname, self.user, f"{tong1}")
            if middleware.bucketGet(self.tongname, self.user) == "[]":
                middleware.bucketDel(self.tongname, self.user)
            self.sender.reply("删除成功，拜拜~")
            exit(0)
        else:
            self.sender.reply("输入错误，退出")
            exit(0)

    def run(self):
        if self.sender.isAdmin():
            users = middleware.bucketAllKeys(self.tongname)
            cks = 0
            for usid in users:
                for i in eval(middleware.bucketGet(self.tongname, usid)):
                    cks += 1
            results = []
            bfs = middleware.bucketGet(self.tongconfig, "yxbf")
            if bfs == "":
                bfs = 5
            else:
                bfs = int(bfs)
            middleware.notifyMasters(f"🔔[沪上阿姨]🔔\n当前账号数{cks}，并发{bfs}运行中---", self.ts)
            with concurrent.futures.ThreadPoolExecutor(max_workers=bfs) as executor:
                for usid in users:
                    for i in eval(middleware.bucketGet(self.tongname, usid)):
                        self.user = usid
                        for k, y in i.items():
                            ck = y["token"]
                            self.userts = y["qd"]
                            if self.login(ck):
                                future = executor.submit(self.sign(k,ck))
                                results.append(future)
                            else:
                            #    middleware.notifyMasters(f"{k[:3]}***{k[7:]}运行异常，可能token失效", self.ts)
                                continue
        #    middleware.notifyMasters(f"🔔[沪上阿姨]🔔\n运行完毕\n======\n{self.msg}\n{self.erro_msg}", self.ts)
            middleware.notifyMasters(f"🔔[沪上阿姨]运行完毕\n", self.ts)
            exit(0)

if __name__ == "__main__":
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    user = sender.getUserID()
    JD = LT(user, sender)
    message = sender.getMessage()
    if "提交" in message or "上车" in message or "登录" in message or "登陆" in message:
        JD.tj()
    elif "查询" in message:
        JD.cx()
    elif "运行" in message:
        JD.run()
    elif "管理" in message:
        JD.gl()
