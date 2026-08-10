# [disable:false]
# [icon: https://bbs.autman.cn/assets/files/2024-06-17/1718632766-289372-bfad933f-4de4-4cb6-9128-09bb3ef70981.svg]
# [title:奥特曼助手]
# [author: 241793]
# [class: 工具类]
# [price: 0.5]
# [rule: ^查询云币$]
# [rule: ^添加云币$]
# [rule: ^删除云币$]
# [rule: ^助手教程$]
# [rule: ^插件授权$]
# [rule: ^添加白名单$]
# [rule: ^删除白名单$]
# [rule: ^查询白名单$]
# [rule: ^查询动态$]
# [rule: ^查询插件$]
# [rule: ^已购买$]
# [rule: ^定时推送$]
# [cron: 0 */10 * * * *]
# [admin: false]
# [version: 1.0.4]
# [description: 1.0.5新增查询作者插件动态，查询作者全部吃插件。小助手(给插件权限)方便操作，可以让用户在你的机器人查询云币，你可以给用户添加云币(减少云币)、授权某一插件、添加市场白名单。</br>管理员指令：添加云币，删除云币，添加白名单，删除白名单，查询白名单，插件授权，查询动态，查询插件$</br>用户指令：查询云币，助手教程。</br>详细教程:<a href="https://bbs.autman.cn/d/136-ao-te-man-zhu-shou-cha-jian-xiao-guo">点我查看</a>]
# [service: 大帅逼]
# [param: {"required":true,"key":"otto.atmtool_url","bool":false,"placeholder":"奥特曼地址#云账号","name":"奥特曼地址+作者云账号","desc":"本地奥特曼地址#作者云账号,例如：http://123:8080#你要监控的云账号，结尾不要/,如果不用云动态可不填"}]
# [param: {"required":true,"key":"otto.atmtool_ts","bool":false,"placeholder":"qq:123,wx:456","name":"群推送","desc":"有更新自动推送群，不填不推送，多个推送渠道用,机器人登陆哪个渠道就填哪个,分开,例如：qq:123,wx:456,tb:-123"}]
import json
import re
import time
from datetime import datetime
import middleware,requests

try:
    from croniter import croniter
except:
    middleware.pip_install("croniter")
class JD:
    def __init__(self, user, sender):
        self.user = user
        self.sender = sender
        self.ck = None
        self.host = None
        self.zh = None
        self.mm = None
    def add_coin(self):
        if self.sender.isAdmin():
            self.sender.reply("发送需要充值的云账号---q退出")
            zh = self.sender.listen(180000)
            if zh == "q" or zh == "":
                self.sender.reply("退出")
                exit(0)
            else:
                tong = middleware.bucketGet("autMarketCoins", zh)
                if tong == "":
                    tong = 0

                self.sender.reply(f"给ta(当前:{tong})充值多少云币(整数)100/元---q退出")
                coin = self.sender.listen(180000)
                if coin == "q" or coin == "":
                    self.sender.reply("退出")
                    exit(0)
                else:
                    tong = middleware.bucketGet("autMarketCoins",zh)
                    if tong == "":

                        middleware.bucketSet("autMarketCoins",zh,f"{int(coin)}")
                        self.sender.reply(f"【{zh}】充值{int(coin)}云币成功")
                        exit(0)
                    else:
                        middleware.bucketSet("autMarketCoins", zh, f"{int(tong)+int(coin)}")
                        self.sender.reply(f"【{zh}】充值{int(tong)+int(coin)}云币成功")
                        exit(0)

    def reduce_coin(self):
        if self.sender.isAdmin():
            self.sender.reply("发送需要减少云币的云账号---q退出")
            zh = self.sender.listen(180000)
            if zh == "q" or zh == "":
                self.sender.reply("退出")
                exit(0)
            else:
                bi = middleware.bucketGet("autMarketCoins", zh)
                if bi == "":
                    self.sender.reply("ta木有币，不用减少")
                    exit(0)
                tong = middleware.bucketGet("autMarketCoins", zh)
                if tong == "":
                    tong = 0
                self.sender.reply(f"给ta(当前:{tong})减少多少云币(整数)100/元---q退出")
                coin = self.sender.listen(180000)
                if coin == "q" or coin == "":
                    self.sender.reply("退出")
                    exit(0)
                else:

                    yunbi = int(bi) - int(coin)
                    if yunbi < 0:
                        self.sender.reply("ta都被你减成负数啦，退出")
                        exit(0)

                    middleware.bucketSet("autMarketCoins",zh,f"{yunbi}")
                    self.sender.reply(f"【{zh}】当前云币{yunbi}")
                    exit(0)

    def add_white(self):
        if self.sender.isAdmin():
            self.sender.reply("给ta添加你的市场白名单---q退出")
            white = self.sender.listen(180000)
            if white == "q" or white == "":
                self.sender.reply("退出")
                exit(0)
            else:

                tong = middleware.bucketGet("autMarketCfgs", "testers")
                if tong == "":
                    middleware.bucketSet("autMarketCfgs", "testers", f"{white}")
                    self.sender.reply(f"【{white}】添加市场白名单成功")
                    exit(0)
                else:
                    a = tong.split(",")
                    for i in a:
                        if i == white:
                            self.sender.reply("该账号已经在白名单了")
                            exit(0)
                    middleware.bucketSet("autMarketCfgs", "testers", f"{tong},{white}")
                    self.sender.reply(f"【{white}】添加市场白名单成功")
                    exit(0)
    def cx_white(self):
        if self.sender.isAdmin():
            tong = middleware.bucketGet("autMarketCfgs", "testers")
            if tong == "":
                self.sender.reply(f"市场白名单为空")
                exit(0)
            else:
                tong = tong.split(",")
                msg = ""
                for user in tong:
                    msg += f"{user}\n"
                self.sender.reply(f"您的市场白名单如下：\n{msg}")
                exit(0)

    def reduce_white(self):
        if self.sender.isAdmin():
            self.sender.reply("删除ta在你市场的白名单---q退出")
            white = self.sender.listen(180000)
            if white == "q" or white == "":
                self.sender.reply("退出")
                exit(0)
            else:
                tong = middleware.bucketGet("autMarketCfgs", "testers")
                if tong == "":
                    self.sender.reply(f"【{white}】不在白名单")
                    exit(0)
                else:
                    tong = tong.split(",")
                    for i in range(len(tong)):
                        if tong[i] == white:
                            del tong[i]
                            msg = ""
                            for b in tong:
                                msg += f"{b},"
                            middleware.bucketSet("autMarketCfgs", "testers", f"{msg[:-1]}")
                            self.sender.reply(f"【{white}】删除市场白名单成功")
                            exit(0)
                    self.sender.reply(f"【{white}】不在白名单")
                    exit(0)

    def login(self):
        url = f"{self.host}/login"
        headers = {
            "Host": re.search(r"//(.*)",self.host).group(1),
            "Connection": "keep-alive",
            "sec-ch-ua": "\";Not A Brand\";v=\"99\", \"Chromium\";v=\"94\"",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Core/1.94.233.400 QQBrowser/12.3.5574.400",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"{self.host}/admin/aut_market_aut.html",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        data = f"username={self.zh}&password={self.mm}"

        res = requests.post(url,headers=headers,data=data)
        print(res.json())
        if res.json()["code"] == 200:
            self.ck = res.cookies
            return True
        elif res.json()["code"] == 401:
            self.sender.reply(res.json()["message"])
            exit(0)
        else:
            return False
    def sq(self):
        if self.sender.isAdmin():
            self.sender.reply("请输入需要添加某插件授权的云账号(该云账号可以免费下载此插件)---q退出")
            zh = self.sender.listen(180000)
            if zh == "q" or zh == "":
                self.sender.reply("退出")
            else:
                self.sender.reply("授权你的哪一个插件(例如：Pro登陆)---q退出")
                name = self.sender.listen(180000)
                if name == "q" or name == "":
                    self.sender.reply("退出")
                else:
                    tong = middleware.bucketGet("autMarketBoughts",zh)

                    if tong == "":
                        middleware.bucketSet("autMarketBoughts", zh, name)
                        middleware.bucketSet("autMarketBoughtDetails",str(time.time()),f"{zh},{name},0")
                        self.sender.reply("授权成功")
                        exit(0)
                    else:
                        tong1 = tong.split(",")
                        for i in range(len(tong1)):
                            if tong1[i] == name:
                                self.sender.reply("已经授权过了")
                                exit(0)
                        t = middleware.bucketGet("autMarketBoughts", zh)
                        middleware.bucketSet("autMarketBoughts", zh, f"{t},{name}")
                        self.sender.reply("授权成功")
                        exit(0)
    def cx_coin(self):
        self.sender.reply("请输入需要查询在本市场云币的云账号---q退出")
        zh = self.sender.listen(180000)
        if zh == "q" or zh == "":
            self.sender.reply("退出")
        else:
            tong = middleware.bucketGet("autMarketCoins", zh)
            if tong == "":
                self.sender.reply(f"[{zh}]当前有0个云币")
                exit(0)
            self.sender.reply(f"[{zh}]当前有{tong}个云币")
            exit(0)




    def gz(self):
        if self.sender.isAdmin():
            zhmm = middleware.get("atmtool_zhmm")
            if zhmm == "":
                self.sender.reply("请先去插件配置设置插件数据")
                exit(0)
            self.host = zhmm.split("#")[0]
            self.zh = zhmm.split("#")[1]
            self.mm = zhmm.split("#")[2]
            self.sender.reply("请发送作者备注---q退出")
            bz = self.sender.listen(180000)
            if bz == "q" or bz == "":
                self.sender.reply("退出")
                exit(0)
            else:
                self.sender.reply("请发送作者云账号---q退出")
                zh = self.sender.listen(180000)
                if zh == "q" or zh == "":
                    self.sender.reply("退出")
                    exit(0)
                else:

                    if self.login():
                        url = f"{self.host}/market/subs"
                        headers = {
                            "Content-Length":"37",
                            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
                            "Cookie":self.ck
                        }
                        data = [{"name":bz,"author":zh}]
                        res = requests.post(url,headers=headers,json=data).json()
                        print(res)
                        if res["code"] == 200:
                            self.sender.reply(f"订阅作者【{zh}】成功")
                            exit(0)
                        else:
                            self.sender.reply(f"订阅作者【{zh}】失败：{res['message']}")
                            exit(0)
                    else:
                        self.sender.reply(f"订阅作者【{zh}】失败：奥特曼域名错误")
                        exit(0)
    def jc(self):
        msg = f"===奥特曼助手1.0.4===\n"
        msg += f"[如果发现手动授权的用户不能更新插件，请去桶	autMarketBoughts，把该用户桶里面出现的'[]'等符号删了]"
        msg += f"【管理员指令】\n给ta充值币：添加云币\n减少ta的币：删除云币\n市场白名单：添加/删除/查询白名单\n给ta授权某插件：插件授权\n"
        msg += f"【用户指令】\n查询云币\n助手教程\n查询动态(查询作者插件动态)\n查询插件(查询作者的插件)"
        self.sender.reply(msg)
    def ydt(self):
        host = middleware.get("atmtool_url")
        if host == "":
            self.sender.reply("请先配置插件参数")
            exit(0)
        host1 = host.split("#")[0]
        zh = host.split("#")[1]

        tong = middleware.bucketAllKeys("bc_userversion")
        headers = {
            "Connection": "keep-alive",
            "sec-ch-ua": "\";Not A Brand\";v=\"99\", \"Chromium\";v=\"94\"",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Core/1.94.233.400 QQBrowser/12.3.5574.400",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        url = f"{host1}/js/cloud"
        params = {
            "tab": f"{zh}",
            "keyword": "",
            "class": "",
            "page": "1",
            "pageSize": "60",
            "orderby": ""
        }
        res = requests.get(url, headers=headers, params=params, verify=False)

        data = res.json()["data"]["data"]
        up = ""
        sc = ""
        for i in data:
            title = i["title"]
            price = i["price"]
            author = i["author"]
            description = i["description"]
            version = i["version"]
            bdversion = middleware.bucketGet("bc_userversion", title)
            if title not in tong:
                middleware.bucketSet("bc_userversion", title, version)
                sc += f"名字：{title}\n作者：{author}\n价格：{price}\n介绍：{description}\n版本：{version}\n--------\n"
            elif version != bdversion:
                up += f"{title}（{bdversion}==>{version}）\n介绍：{description}\n--------\n"
                # middleware.bucketSet("bc_userversion", title, version)

        msg = f"【{zh}】{datetime.now().strftime('%Y-%m-%d')}\n===作者云动态===\n{sc}\n\n===有更新===\n{up}"

        self.sender.reply(msg)
        exit(0)
    def cloud(self):
        host = middleware.get("atmtool_url")
        ts = middleware.get("atmtool_ts")
        if host == "":
            print(f"===云动态===请先配置插件参数，奥特曼链接")
            exit(0)
        if ts == "":
            print(f"===云动态===请先配置插件参数,推送群")
            exit(0)
        host1 = host.split("#")[0]
        zh = host.split("#")[1]
        tong = middleware.bucketAllKeys("bc_userversion")
        headers = {
            "Connection": "keep-alive",
            "sec-ch-ua": "\";Not A Brand\";v=\"99\", \"Chromium\";v=\"94\"",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Core/1.94.233.400 QQBrowser/12.3.5574.400",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        url = f"{host1}/js/cloud"
        params = {
            "tab": f"{zh}",
            "keyword": "",
            "class": "",
            "page": "1",
            "pageSize": "120",
            "orderby": ""
        }
        res = requests.get(url, headers=headers, params=params, verify=False)

        data = res.json()["data"]["data"]
        up = ""
        sc = ""
        for i in data:
            title = i["title"]
            price = i["price"]
            author = i["author"]
            description = i["description"]
            version = i["version"]
            bdversion = middleware.bucketGet("bc_userversion", title)
            if title not in tong:
                middleware.bucketSet("bc_userversion", title, version)
                sc += f"名字：{title}\n作者：{author}\n价格：{price}\n介绍：{description}\n版本：{version}\n--------\n"
            elif version != bdversion:
                up += f"{title}（{bdversion}==>{version}）\n介绍：{description}\n--------\n"
                middleware.bucketSet("bc_userversion", title, version)
        if up != "" or sc != "":
            msg = f"【{zh}】{datetime.now().strftime('%Y-%m-%d')}\n===作者云动态===\n{sc}\n\n===有更新===\n{up}"
            allts = ts.split(",")
            for b in allts:
                middleware.push(b.split(":")[0],b.split(":")[1],"","",msg)


    def allcj(self):
        host = middleware.get("atmtool_url")
        if host == "":
            self.sender.reply("请先配置插件参数")
            exit(0)
        host1 = host.split("#")[0]
        zh = host.split("#")[1]
        headers = {
            "Connection": "keep-alive",
            "sec-ch-ua": "\";Not A Brand\";v=\"99\", \"Chromium\";v=\"94\"",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Core/1.94.233.400 QQBrowser/12.3.5574.400",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        url = f"{host1}/js/cloud"
        params = {
            "tab": f"{zh}",
            "keyword": "",
            "class": "",
            "page": "1",
            "pageSize": "120",
            "orderby": ""
        }
        res = requests.get(url, headers=headers, params=params, verify=False)

        data = res.json()["data"]["data"]
        sc = ""
        for i in data:
            title = i["title"]
            price = i["price"]
            author = i["author"]
            description = i["description"]
            version = i["version"]
            sc += f"名字：{title}\n作者：{author}\n价格：{price}\n介绍：{description}\n版本：{version}\n--------\n"


        self.sender.reply(f"===作者：{zh}插件如下===\n{sc}")
        exit(0)
    def buy(self):
        self.sender.reply(f"请发送你的云账号,q退出")
        user = self.sender.listen(180000)
        if user == "q" or user is None:
            self.sender.reply("退出")
            return

        ts = middleware.bucketGet("autMarketBoughts",user)
        title = ts.split(",")
        msg = ""
        a = 0
        for i in title:
            def timee(user,i):
                t = middleware.bucketAllKeys("autMarketBoughtDetails")

                for tt in t:
                    ttt = middleware.bucketGet("autMarketBoughtDetails", tt)
                    try:
                        if ttt.split(",")[0] == user and ttt.split(",")[1] == i:
                            return ttt.split(',')[2]

                    except:
                        pass
                return 0
            money = timee(user,i)
            msg += f"插件名：{i}\n花费：{money}\n------\n"
            a += int(money)
        if msg == "":
            self.sender.reply(f"没有发现你的购买记录")
        else:
            self.sender.reply(msg+f"\n------\n总消费{a}云币({a/100}元)")

    def cron_(self):
        if self.sender.isAdmin():
            ts = middleware.bucketAllKeys("autSysCroncmds")
            print(ts)
            msg = ""
            for id in ts:
                d = json.loads(middleware.bucketGet("autSysCroncmds",id))
                disable = d["disable"]
                if not disable:
                    disable = "✅"
                else:
                    disable = "❌"
                cron = d["cron"]
                name = d["cmd"]
                msg += f"【{id}】{name}-{cron}-{disable}\n"
            self.sender.reply(f"您的所有定时指令如下(❌为禁用状态)\n{msg}")
            return 
            self.sender.reply(f"您的所有定时指令如下(❌为禁用状态)\n【0】添加定时\n{msg}\n------\n发送【】里面的数字进行操作，q退出")
            id = self.sender.listen(120000)
            if id == "q" or id is None:
                self.sender.reply("退出")
                return
            elif id == "0":
                self.sender.reply("输入定时推送的名称,q退出")
                title = self.sender.listen(120000)
                if title == "q" or title is None:
                    self.sender.reply("退出")
                    return
                else:
                    self.sender.reply(f"输入cron定时，例如：10 10 8 * * *,q退出")
                    cron = self.sender.listen(120000)
                    if cron == "q" or cron is None:
                        self.sender.reply("退出")
                        return
                    elif self.is_valid_cron(cron):
                        t1 = {"id":len(ts)+1,"disable":True,"pinned":0,"cron":cron,"last_running_time":"2024-10-25 09:00:00","next_running_time":"2024-10-26 09:00:00","cmd":title,"to_self":True,"disguise_imtype":"","disguise_group":"","disguise_user":"","to_others":"","intervals":0,"memo":"","default":False}
                        t1 = json.dumps(t1,ensure_ascii=False)
                        middleware.bucketSet("autSysCroncmds", f"{len(ts)+1}", f"{t1}")
                        self.sender.reply(f"添加定时【{title}】为{cron}成功")
                    else:
                        self.sender.reply("cron定时输入错误，可以百度cron时间格式")


            else:
                t1 = json.loads(middleware.bucketGet("autSysCroncmds",id))
                if t1:
                    self.sender.reply(f"1、启用/禁用该定时指令\n2、修改定时\n3、删除定时\n----\nq退出")
                    index = self.sender.listen(120000)
                    if index == "q" or index is None:
                        self.sender.reply("退出")
                        return
                    elif index == "1":
                        if t1["disable"]:
                            t1["disable"] = False
                            t1 = json.dumps(t1,ensure_ascii=False)
                            middleware.bucketSet("autSysCroncmds",f"{id}",f"{t1}")
                            self.sender.reply("启用成功")
                        else:
                            t1["disable"] = True
                            t1 = json.dumps(t1,ensure_ascii=False)
                            middleware.bucketSet("autSysCroncmds", f"{id}", f"{t1}")
                            self.sender.reply("禁用成功")
                    elif index == "2":
                        self.sender.reply(f"输入cron定时，例如：10 10 8 * * *(当前：{t1['cron']}),q退出")
                        cron = self.sender.listen(120000)
                        if cron == "q" or cron is None:
                            self.sender.reply("退出")
                            return
                        elif self.is_valid_cron(cron):
                            t1["cron"] = cron
                            t1 = json.dumps(t1,ensure_ascii=False)
                            middleware.bucketSet("autSysCroncmds", f"{id}", f"{t1}")
                            self.sender.reply(f"定时修改成功，当前：{cron}")
                        else:
                            self.sender.reply("cron定时输入错误，可以百度cron时间格式")

                    elif index == "3":
                        self.sender.reply(f"输入y确定删除,q退出")
                        sc = self.sender.listen(120000)
                        if sc == "q" or sc is None:
                            self.sender.reply("退出")
                            return
                        else:
                            middleware.bucketDel("autSysCroncmds",f"{id}")
                            self.sender.reply("删除成功")

    def is_valid_cron(self,c):
        try:
            # 创建一个 croniter 对象，使用当前时间作为基准
            cron = croniter(c, datetime.now())
            # 如果 cron 表达式有效，则可以获取下一个执行时间
            next_run = cron.get_next(datetime)
            return True  # 如果没有异常，返回 True
        except ValueError:
            return False  # 如果抛
if __name__ == "__main__":
    name = "csh插件"
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    user = sender.getUserID()
    JD = JD(user, sender)
    message = sender.getMessage()
    if message == "查询云币":
        JD.cx_coin()
    if message == "查询插件":
        JD.allcj()
    elif message == "添加云币":
        JD.add_coin()
    elif message == "删除云币":
        JD.reduce_coin()
    elif message == "助手教程":
        JD.jc()
    elif message == "添加白名单":
        JD.add_white()
    elif message == "删除白名单":
        JD.reduce_white()
    elif message == "查询白名单":
        JD.cx_white()
    elif message == "插件授权":
        JD.sq()
    elif message == "查询动态":
        JD.ydt()
    elif message == "查询插件":
        JD.allcj()
    elif message == "已购买":
        JD.buy()
    elif message == "定时推送":
        JD.cron_()
    else:
        JD.cloud()

