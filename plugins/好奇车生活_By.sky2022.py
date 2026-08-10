# [pin:false]
# [disable:true]
# [title: 好奇车生活]
# [rule: ^车生活(.*)$]
# [author: sky2022]
# [icon: https://i.miji.bid/2025/06/27/c8004b046fc16179e17701da31a05ab6.png]
# [admin: false]
# [service: 2661320550]
# [price: 8.88]
# [version: V7.9]
# [public:true]
# [description: 指令：车生活上车 车生活管理 车生活查询 车生活配置 车生活授权 车生活教程 车生活入口]
# [param: {"required":true,"key":"dd_hqcsh.zsm","bool":false,"placeholder":"http://127.0.0.1/赞赏码.png","name":"赞赏码链接","desc":"你的机器人赞赏码链接"}]
# [param: {"required":true,"key":"dd_hqcsh.sqje","bool":false,"placeholder":"0","name":"授权金额(元)","desc":"设置授权需要支付金额为多少元，默认不设置为0元"}]
# [param: {"required":true,"key":"dd_hqcsh.sqsj","bool":false,"placeholder":"30","name":"授权时间(天)","desc":"设置授权金额的授权天数，默认不设置为30天"}]
# [param: {"required":true,"key":"dd_hqcsh.Qinglong","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割"}]
# [param: {"required":true,"key":"dd_hqcsh.osname","bool":false,"placeholder":"必填项,例:cshAccountId","name":"提交到青龙的变量名","desc":"青龙容器内车生活的变量名"}]

import random
import threading
import middleware, requests, time, json
from datetime import datetime, timedelta
import asyncio, aiohttp

try:
    import concurrent.futures
except:
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    sender.reply("请先安装concurrent依赖")
    exit(0)
ts_all = []


class JD:
    def __init__(self, user, sender):
        self.user = user
        self.sender = sender
        self.bz = None
        self.sqsj = None
        self.ck = None
        self.point = None
        self.gq_point = None
        if middleware.bucketGet("dd_hqcsh", "delbtn") == "":
            middleware.bucketSet('dd_hqcsh', "delbtn", "true")
        if middleware.bucketGet("dd_hqcsh", "jfpay") == "":
            middleware.bucketSet('dd_hqcsh', "jfpay", "true")
        self.hd = {
            'Host': 'channel.cheryfs.cn',
            'wxappid': '619669369294712832',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
            'tenantId': '619669306447261696',
            'activityId': '621883730893492225',
            'Accept': 'application/json,text/plain, */*',
        }
        self.hd2 = {
            'Host': 'channel.cheryfs.cn',
            'Connection': 'keep-alive',
            'wxappid': '619669369294712832',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
            'tenantId': '619669306447261696',
            'activityId': '620821692188483585',
            'requestUrl': 'https://channel.cheryfs.cn/archer/act/619669306447261696/619669369294712832/activity/luckydraw-detail/620821692188483585',
            'Accept': 'application/json, text/plain, */*',
            'timestamp': str(round(time.time() * 1000)),
            'assemblyName': '%E5%88%AE%E5%88%AE%E4%B9%90',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://channel.cheryfs.cn/archer/act/619669306447261696/619669369294712832/activity/luckydraw-detail/620821692188483585',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-us,en',
        }

    def login(self, ck):
        self.hd["accountId"] = ck
        url = "https://channel.cheryfs.cn/archer/activity-api/common/accountPointLeft?pointId=620415610219683840&showExpire=true&timeType=day&indexDay="
        res = requests.get(url, headers=self.hd).json()
        if res["code"] == 200:
            self.gq_point = res["message"]
            self.point = res["result"]

            return True
        else:
            self.sender.reply("url请求失败！")
            return False

    def reward(self, ck):
        url = "https://channel.cheryfs.cn/archer/activity-api/pointsmall/queryPointsMallCardList?isGroup=false"
        headers = {
            'Host': 'channel.cheryfs.cn',
            'Connection': 'keep-alive',
            'wxappid': '619669369294712832',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
            'tenantId': '619669306447261696',
            'activityId': '621950054462152705',
            'requestUrl': 'https://channel.cheryfs.cn/archer/act/619669306447261696/619669369294712832/activity/luckydraw-detail/620821692188483585',
            'Accept': 'application/json, text/plain, */*',
            'timestamp': str(round(time.time() * 1000)),
            'assemblyName': '%E5%88%AE%E5%88%AE%E4%B9%90',
            'sign': 'eff41a284067d208807fbd94740245c7',
            'accountId': ck,
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://channel.cheryfs.cn/archer/act/619669306447261696/619669369294712832/activity/pointsmall-detail/621911913692942337?miniopeonid=ad332eed2e5dcccab7b9fc5068569c234fd17d426a4c447150b81a64f2faca43d09133dc910a196f3cd3c7dd29a720bd881ce390a785e9319cfb5f8f9b9443ea690b18b7f55ff124887643066a6ffee24a3e8fa2756c9360fa3c4c7bef095bc52e1621178de3ec6cdc2a20d5e32105db676c324392d0d67c982795bb&xcxAppId=wx8c6e8a965158ad6c',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-us,en',
        }
        res = requests.get(url, headers=headers)
        if res.json()["success"] == True:
            list0 = []
            msg = "最新奖励id\n"
            for i in range(len(res.json()["result"]["全部"])):
                cardid = res.json()["result"]["全部"][i]["id"]
                cardname = res.json()["result"]["全部"][i]["cardName"]
                cardjf = res.json()["result"]["全部"][i]["exchangePointsValue"]
                listdata = {
                    "name": cardname,
                    "jf": cardjf,
                    "id": cardid
                }
                msg += f"奖励{cardname}:id[{cardid}]:需要积分{cardjf}\n"
                list0.append(listdata)
            print(f"======\n{msg}======")
            return list0

    def today(self, ck):
        url = "https://channel.cheryfs.cn/archer/activity-api/common/accountPointInfo"
        headers = {
            'Host': 'channel.cheryfs.cn',
            'Connection': 'keep-alive',
            'wxappid': '619669369294712832',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
            'tenantId': '619669306447261696',
            'activityId': '621950054462152705',
            'requestUrl': 'https://channel.cheryfs.cn/archer/act/619669306447261696/619669369294712832/activity/luckydraw-detail/620821692188483585',
            'Accept': 'application/json, text/plain, */*',
            'timestamp': str(round(time.time() * 1000)),
            'assemblyName': '%E5%88%AE%E5%88%AE%E4%B9%90',
            'sign': 'eff41a284067d208807fbd94740245c7',
            'accountId': ck,
            "Content-Length": "113",
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://channel.cheryfs.cn/archer/act/619669306447261696/619669369294712832/activity/pointsmall-detail/621911913692942337?miniopeonid=ad332eed2e5dcccab7b9fc5068569c234fd17d426a4c447150b81a64f2faca43d09133dc910a196f3cd3c7dd29a720bd881ce390a785e9319cfb5f8f9b9443ea690b18b7f55ff124887643066a6ffee24a3e8fa2756c9360fa3c4c7bef095bc52e1621178de3ec6cdc2a20d5e32105db676c324392d0d67c982795bb&xcxAppId=wx8c6e8a965158ad6c',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-us,en',
        }
        data = {"pointId": "620415610219683840", "accountId": "", "type": 2, "pageNumber": 1, "pageSize": 10,
                "startDate": "", "endDate": ""}
        res = requests.post(url, headers=headers, json=data).json()
        if res["code"] == 200:
            jf = 0
            for d in res["result"]["accountPointLogs"]:
                t = d["updateTime"].split(" ")[0]
                if t == datetime.now().strftime("%Y-%m-%d"):
                    jf += d["amount"]
            return jf

    def tj(self):
        tong = middleware.bucketGet("dd_hqcsh", self.user)
        if tong == "":
            self.sender.reply("欢迎使用车生活系统, 请先设置您的备注名(1-6个字符)。退出输入'q'!")
            bz = self.sender.listen(180000)
            if bz == "q":
                self.sender.reply("退出！")
                exit(0)
            else:
                self.sender.reply(
                    f"{bz}， 你好!\n抓包: 好奇车生活小程序\n域名:channel.cheryfs.cn \n请求头里面的accountId数据\n说明: 一天50积分左右，月积分2000+可以抢e卡,现金....\n请在120s内发送你的accountId数据, 退出回复'q'!")
                ck = self.sender.listen(180000)
                if ck == "q":
                    self.sender.reply("退出！")
                    exit(0)
                else:
                    if self.login(ck):
                        cks = []
                        data = {
                            bz: {
                                "ck": ck,
                                "qd": self.sender.getImtype(),
                                "sqsj": datetime.now().strftime("%Y-%m-%d")

                            }
                        }
                        cks.append(data)
                        middleware.bucketSet("dd_hqcsh", self.user, f"{cks}")
                        self.sender.reply("🔔登录成功!发送'车生活管理'对账号进行管理!")
                    else:
                        self.sender.reply("输入有误，退出！")
                        exit(0)
        else:
            self.sender.reply(f"欢迎使用车生活系统, 请先设置您的备注名(1-6个字符)，当前已有[{len(eval(tong))}]个账号。退出输入'q'!")
            bz = self.sender.listen(180000)
            if bz == "q":
                self.sender.reply("退出！")
                exit(0)
            else:
                self.sender.reply(
                    f"{bz}， 你好!\n抓包: 好奇车生活小程序\n域名:channel.cheryfs.cn \n请求头里面的accountId数据\n说明: 一天50积分左右，月积分2000+可以抢e卡,现金....\n请在120s内发送你的accountId数据, 退出回复'q'!")
                ck = self.sender.listen(180000)
                if ck == "q":
                    self.sender.reply("退出！")
                    exit(0)
                else:
                    if self.login(ck):
                        userdata = eval(tong)
                        for aaa in userdata:
                            for k, y in aaa.items():
                                if k == bz:
                                    aaa[k] = {'ck': ck, "qd": self.sender.getImtype(), 'sqsj': y["sqsj"]}
                                    middleware.bucketSet("dd_hqcsh", self.user, f"{userdata}")
                                    self.sender.reply(f"[{k}]更新ck成功")
                                    exit(0)

                        data = {
                            bz: {
                                "ck": ck,
                                "qd": self.sender.getImtype(),
                                "sqsj": datetime.now().strftime("%Y-%m-%d")
                            }
                        }
                        userdata.append(data)
                        middleware.bucketSet("dd_hqcsh", self.user, f"{userdata}")
                        self.sender.reply("🔔登录成功!发送'车生活管理'对账号进行管理!")  
                    else:
                        self.sender.reply("输入有误，退出！")
                        exit(0)

    def cx(self):
        tong = middleware.bucketGet("dd_hqcsh", self.user)
        if tong == "" or tong == "[]":
            self.sender.reply("您当前没有提交账号！")
            exit(0)
        else:
            tong = eval(tong)
            msg = ""
            a = 0
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            for user in tong:
                key = list(user.keys())
                bz = key[a]
                if user[key[a - 1]].get("qd", None) is None:
                    user[bz] = {'ck': user[key[a - 1]]['ck'], "qd": self.sender.getImtype(),
                                'sqsj': user[key[a - 1]]["sqsj"]}
                    middleware.bucketSet("dd_hqcsh", self.user, f"{tong}")

                ck = user[key[a - 1]]['ck']
                auth_date = user[key[a - 1]]['sqsj']

                if len(ck.split('#')) != 1:
                    ck = user[key[a - 1]]['ck'].split('#')[0]

                # 检查授权是否过期
                if auth_date <= current_date:
                    msg += f"备注：{bz}\n授权状态：已过期 ⚠️\n授权到期：{auth_date}\n======================\n"
                    continue

                if self.login(ck):
                    msg += f"备注：{bz}\n今日积分：{self.today(ck)}\n总积分：{self.point}\n授权状态：有效 ✅\n授权到期：{auth_date}\n======================\n"
                else:
                    msg += f"车生活账号{bz}失效，请及时更新CK\n--------\n"
            self.sender.reply(f"========车生活查询========\n{msg}")
            exit(0)

    def gl(self):
        tong = middleware.bucketGet("dd_hqcsh", self.user)
        if tong == "" or tong == "[]":
            self.sender.reply("您当前没有提交账号！")
            exit(0)
        else:
            msg = f"======车生活管理======\n"
            d = eval(tong)
            account_map = {}  # 用于存储序号到账号信息的映射
            
            for i, user_data in enumerate(d, 1):  # 从1开始编号
                for bz, info in user_data.items():
                    msg += f"账号[{i}]：{bz}\n"
                    account_map[str(i)] = {
                        "bz": bz,
                        "ck": info["ck"],
                        "sqsj": info["sqsj"],
                        "index": i-1  # 保存原始索引
                    }
                    
            self.sender.reply(f"{msg}\n\n请输入序号进行操作！---q退出")
            index = self.sender.listen(180000)
            
            if index == "q":
                self.sender.reply("退出！")
                exit(0)
            
            if index not in account_map:
                self.sender.reply("输入的序号不存在")
                exit(0)
            
            # 获取选中的账号信息
            selected_account = account_map[index]
            self.bz = selected_account["bz"]
            self.ck = selected_account["ck"]
            self.sqsj = selected_account["sqsj"]
            
            if self.login(self.ck):
                msg = f"======车生活管理======\n账号：{self.bz}\n1、账号授权\n2、提交青龙\n3、删除账号\n====================\n回复序号,退出【q】！"
                self.sender.reply(msg)
                cz = self.sender.listen(120000)
                
                if cz == "q":
                    self.sender.reply("退出")
                    exit(0)
                elif cz == "1":
                    try:
                        # 检查授权金额配置
                        if middleware.bucketGet('dd_hqcsh', 'sqje') == "" or middleware.bucketGet('dd_hqcsh', 'sqje') == "":
                            self.sender.reply(f"插件配参不完整，请管理员发送【车生活配置】设置授权金额")
                            exit(0)
                            
                        # 检查是否支持积分支付
                        if middleware.bucketGet("dd_hqcsh", "jfpay") == "true":
                            userjf = middleware.bucketGet('bd_jf', self.user)
                            if userjf == "":
                                userjf = 0
                                
                        # 调用授权处理
                        self.dssq(2, selected_account["index"])
                        ds = self.sender.listen(120000)
                        if ds == "q":
                            self.sender.reply("退出")
                            exit(0)
                            
                    except Exception as e:
                        self.sender.reply(f"授权处理异常: {str(e)}")
                        exit(0)
                elif cz == "2":
                    # 获取青龙配置
                    ql_config = middleware.bucketGet("dd_hqcsh", "Qinglong")
                    if ql_config:
                        ql_params = ql_config.split('丨')
                        if len(ql_params) == 3:
                            QLurl = ql_params[0]
                            ClientID = ql_params[1]
                            ClientSecret = ql_params[2]
                            
                            # 获取变量名
                            osname = middleware.bucketGet("dd_hqcsh", "osname")
                            if osname:
                                try:
                                    # 获取青龙token
                                    url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
                                    token_res = requests.get(url).json()
                                    if token_res['code'] == 200:
                                        qltoken = token_res['data']['token']
                                        
                                        # 提交变量到青龙
                                        url = f"{QLurl}/open/envs"
                                        headers = {
                                            "Authorization": "Bearer" + ' ' + qltoken,
                                            "Content-Type": "application/json"
                                        }
                                        data = [{
                                            "value": self.ck,
                                            "name": osname,
                                            "remarks": f'车生活账号:{self.bz}丨用户:{self.user}'
                                        }]
                                        res = requests.post(url, headers=headers, json=data)
                                        if res.status_code == 200:
                                            self.sender.reply("✅变量已提交到青龙")
                                        else:
                                            self.sender.reply("❌提交青龙失败")
                                except Exception as e:
                                    self.sender.reply(f"提交青龙异常:{str(e)}")
                    
                    msg = f'【好奇车生活】当前用户: {self.user}\n授权天数: {int(self.sqsj)}天\n到期时间: {self.sqsj}'
                    self.sender.reply(msg)
                    notify = middleware.bucketGet('dd_hqcsh', 'notify')
                    if notify:
                        tsqd = notify.split(',')
                        middleware.notifyMasters(msg, tsqd)
                    
                elif cz == "3":
                    self.sc(selected_account["index"])
                else:
                    self.sender.reply("输入错误")
                    exit(0)
            else:
                self.sender.reply(f"[{self.bz}]账号失效")
                exit(0)

    def sc(self, index):
        """删除账号"""
        tong = middleware.bucketGet("dd_hqcsh", self.user)
        if tong == "":
            self.sender.reply("当前没有账号")
            exit(0)
        else:
            self.sender.reply(f"确定删除【{self.bz}】，确定发送【y】\n退出【q】！")
            qd = self.sender.listen(120000)
            if qd == "q":
                self.sender.reply("取消")
                exit(0)
            elif qd == "y":
                # 先删除青龙中的变量
                try:
                    # 获取青龙配置
                    ql_config = middleware.bucketGet("dd_hqcsh", "Qinglong")
                    if ql_config:
                        ql_params = ql_config.split('丨')
                        if len(ql_params) == 3:
                            QLurl = ql_params[0]
                            ClientID = ql_params[1]
                            ClientSecret = ql_params[2]
                            
                            # 获取变量名
                            osname = middleware.bucketGet("dd_hqcsh", "osname")
                            if osname:
                                # 获取青龙token
                                url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
                                token_res = requests.get(url).json()
                                if token_res['code'] == 200:
                                    qltoken = token_res['data']['token']
                                    
                                    # 获取所有环境变量
                                    url = f"{QLurl}/open/envs"
                                    headers = {
                                        "Authorization": "Bearer" + ' ' + qltoken
                                    }
                                    res = requests.get(url, headers=headers).json()
                                    
                                    if res['code'] == 200:
                                        # 查找匹配的变量
                                        for env in res['data']:
                                            if env['name'] == osname and f'车生活账号:{self.bz}丨用户:{self.user}' in env['remarks']:
                                                # 删除变量
                                                del_url = f"{QLurl}/open/envs"
                                                headers = {
                                                    "Authorization": "Bearer" + ' ' + qltoken,
                                                    "Content-Type": "application/json"
                                                }
                                                del_data = [env['id']]
                                                requests.delete(del_url, headers=headers, json=del_data)
                                                msg = f"已删除青龙变量\n"
                                                break
                except Exception as e:
                    msg = f"删除青龙变量异常:{str(e)}\n"
                
                # 删除本地账号数据
                tong = eval(tong)
                del tong[index]
                middleware.bucketSet("dd_hqcsh", self.user, f"{tong}")
                self.sender.reply(f"删除【{self.bz}】成功")
            else:
                self.sender.reply("输入错误")
                exit(0)

    def pz(self):
        if self.sender.isAdmin():
            zsm = middleware.bucketGet('dd_hqcsh', 'zsm')
            if zsm == '':
                pz1 = '未配置'
            else:
                pz1 = '已配置'

            sqje = middleware.bucketGet('dd_hqcsh', 'sqje')
            if sqje == '':
                sqje = 3

            sqsj = middleware.bucketGet('dd_hqcsh', 'sqsj')
            if sqsj == '':
                sqsj = 30

            msg = f'========车生活配置========\n1、赞赏码({pz1})\n2、授权金额({sqje}元)\n3、授权时间({sqsj}天)\n====================\n回复序号,退出【q】！'
            self.sender.reply(msg)
            zh = self.sender.listen(60000)
            if zh == 'q' or zh == 'Q':
                self.sender.reply("退出！")
            elif zh is None:
                self.sender.reply(f'超时退出！')
            elif zh == '1':
                self.sender.reply('请发送您的wx机器人赞赏码:')
                pz = self.sender.listen(60000)
                if pz == 'q' or pz == 'Q':
                    self.sender.reply("退出！")
                elif pz is None:
                    self.sender.reply(f'超时退出！')
                else:
                    self.sender.replyImage(pz)
                    middleware.bucketSet('dd_hqcsh', 'zsm', f'{pz}')
                    self.sender.reply('赞赏码配置成功!')
            elif zh == '2':
                self.sender.reply('设置授权金额:')
                pz = self.sender.listen(60000)
                if pz == 'q' or pz == 'Q':
                    self.sender.reply("退出！")
                elif pz is None:
                    self.sender.reply(f'超时退出！')
                else:
                    middleware.bucketSet('dd_hqcsh', 'sqje', f'{pz}')
                    self.sender.reply(f'授权金额配置成功: {pz}元')
            elif zh == '3':
                self.sender.reply('设置授权时间:')
                pz = self.sender.listen(60000)
                if pz == 'q' or pz == 'Q':
                    self.sender.reply("退出！")
                elif pz is None:
                    self.sender.reply(f'超时退出！')
                else:
                    middleware.bucketSet('dd_hqcsh', 'sqsj', f'{pz}')
                    self.sender.reply(f'授权时间配置成功: {pz}天')
            else:
                self.sender.reply(f'输入有误!!')
        else:
            self.sender.reply("不是管理员")
            exit(0)

    def sq(self):
        """车生活授权"""
        if self.sender.isAdmin():
            msg = f'========车生活授权========\n1、一键授权所有用户\n2、单独授权用户\n======================\n回复序号,退出【q】！'
            self.sender.reply(msg)
            xz = self.sender.listen(60000)
            
            if xz == 'q' or xz == 'Q':
                self.sender.reply("退出！")
                return
            elif xz is None:
                self.sender.reply(f'超时退出！')
                return
            elif xz == '1':
                self.qbqbsq()
            elif xz == '2':
                msg = f'请输入需要授权的账号id\n通过给机器人发送myuid获得\n退出【q】！'
                self.sender.reply(msg)
                myuid = self.sender.listen(60000)
                if myuid == 'q' or myuid == 'Q':
                    self.sender.reply("退出！")
                elif myuid == 1:
                    self.qbqbsq()
                elif myuid is None:
                    self.sender.reply(f'超时退出！')
                else:
                    ts = middleware.bucketGet('dd_hqcsh', myuid)
                    if ts == '' or ts == '{}':
                        self.sender.reply(f"车生活系统未查询到{myuid}的信息! 请先上车! ")
                    else:
                        ts = eval(ts)
                        n = 0
                        id_dict = {}
                        msg = '========车生活授权========\n'
                        msg += '0、授权所有账号\n======================\n'
                        for user in ts:
                            for k, y in user.items():
                                n += 1
                                id_dict[n] = {'bz': k, 'ck': y['ck'], 'sqsj': y['sqsj']}
                                msg += f'{n}、{k}\n授权时间: ⏰{y["sqsj"]}\n======================\n'
                        msg += f'回复序号选择账号,退出【q】！'
                        self.sender.reply(msg)
                        xz = self.sender.listen(60000)
                        xz_list = []
                        for k, y in id_dict.items():
                            xz_list.append(k)
                        if xz == 'q' or xz == 'Q':
                            self.sender.reply("退出！")
                        elif xz is None:
                            self.sender.reply(f'超时退出！')
                        elif xz == '0':
                            msg = f'请输入给所有账号授权的天数！！\n回复序号,退出【q】！'
                            self.sender.reply(msg)
                            sjts = self.sender.listen(60000)
                            if sjts == 'q' or sjts == 'Q':
                                self.sender.reply("退出！")
                            elif sjts is None:
                                self.sender.reply(f'超时退出！')
                            elif isinstance(int(sjts), int):
                                success_count = 0
                                for user in ts:
                                    for k, y in user.items():
                                        try:
                                            dqsj = datetime.now().strftime("%Y-%m-%d")
                                            if y['sqsj'] > dqsj:
                                                sqsj = datetime.strptime(y['sqsj'], "%Y-%m-%d")
                                                new_sqsj = sqsj + timedelta(days=int(sjts))
                                            else:
                                                new_sqsj = datetime.now() + timedelta(days=int(sjts))
                                            new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                                            user[k]['sqsj'] = new_sqsj
                                            success_count += 1
                                        except:
                                            continue
                                middleware.bucketSet('dd_hqcsh', myuid, f'{ts}')
                                msg = f"授权完成!\n成功授权: {success_count}个账号\n授权天数: {sjts}天"
                                self.sender.reply(msg)
                                notify = middleware.bucketGet('dd_hqcsh', 'notify')
                                if notify:
                                    tsqd = notify.split(',')
                                    middleware.notifyMasters(msg, tsqd)
                            else:
                                self.sender.reply(f'输入天数有误，退出！')
                        elif int(xz) in xz_list:
                            zh = id_dict[int(xz)]
                            self.bz = zh['bz']
                            self.ck = zh['ck']
                            self.sqsj = zh['sqsj']

                            msg = f'请输入给【{self.bz}】授权的天数！！\n回复序号,退出【q】！'
                            self.sender.reply(msg)
                            sjts = self.sender.listen(60000)
                            if sjts == 'q' or sjts == 'Q':
                                self.sender.reply("退出！")
                            elif sjts is None:
                                self.sender.reply(f'超时退出！')
                            elif isinstance(int(sjts), int):
                                dqsj = datetime.now().strftime("%Y-%m-%d")
                                if self.sqsj > dqsj:
                                    sqsj1 = datetime.strptime(self.sqsj, "%Y-%m-%d")
                                    new_sqsj = sqsj1 + timedelta(days=int(sjts))
                                else:
                                    sj = datetime.now()
                                    new_sqsj = sj + timedelta(days=int(sjts))
                                new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                                for user in ts:
                                    for k, y in user.items():
                                        if k == self.bz:
                                            user[k]['sqsj'] = new_sqsj
                                            break
                                middleware.bucketSet('dd_hqcsh', myuid, f'{ts}')
                                msg = f'当前用户: {myuid}\n授权用户: {self.bz}\n授权天数: {int(sjts)}天\n到期时间: {new_sqsj}'
                                self.sender.reply(msg)
                                notify = middleware.bucketGet('dd_hqcsh', 'notify')
                                if notify:
                                    tsqd = notify.split(',')
                                    middleware.notifyMasters(msg, tsqd)
                            else:
                                self.sender.reply(f'{sjts} 输入有误，退出！')
                        else:
                            self.sender.reply(f'{xz} 输入有误，退出！')
            else:
                self.sender.reply("不是管理员")
                exit(0)

    def qbqbsq(self):
        """一键授权所有用户"""
        try:
            # 获取所有用户的数据
            ts = middleware.bucketAllKeys('dd_hqcsh')
            if not ts:
                self.sender.reply("车生活系统未查询到任何用户信息!")
                return
            
            # 过滤掉非用户数据的键
            user_keys = [key for key in ts if key not in ['zsm', 'sqje', 'sqsj', 'Qinglong', 'osname', 'notify', 'delbtn', 'jfpay']]
            
            if not user_keys:
                self.sender.reply("车生活系统未查询到任何用户信息!")
                return
            
            self.sender.reply('请输入要给所有用户授权的天数！\n退出【q】！')
            sjts = self.sender.listen(60000)
            if sjts == 'q' or sjts == 'Q':
                self.sender.reply("退出！")
                return
            elif sjts is None:
                self.sender.reply(f'超时退出！')
                return
            
            try:
                sjts = int(sjts)
            except:
                self.sender.reply(f'输入的天数无效，必须是数字！')
                return
            
            success_count = 0
            fail_count = 0
            
            for myuid in user_keys:
                try:
                    user_data = middleware.bucketGet('dd_hqcsh', myuid)
                    if not user_data or user_data == '[]':
                        continue
                        
                    user_data = eval(user_data)
                    if not isinstance(user_data, list):
                        continue
                        
                    modified = False
                    for user in user_data:
                        if not isinstance(user, dict):
                            continue
                            
                        for k, y in user.items():
                            try:
                                if not isinstance(y, dict) or 'sqsj' not in y:
                                    continue
                                    
                                dqsj = datetime.now().strftime("%Y-%m-%d")
                                if y['sqsj'] > dqsj:
                                    sqsj = datetime.strptime(y['sqsj'], "%Y-%m-%d")
                                    new_sqsj = sqsj + timedelta(days=sjts)
                                else:
                                    new_sqsj = datetime.now() + timedelta(days=sjts)
                                new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                                
                                y['sqsj'] = new_sqsj
                                modified = True
                                success_count += 1

                                # 授权成功后提交到青龙
                                ql_config = middleware.bucketGet("dd_hqcsh", "Qinglong")
                                if ql_config:
                                    ql_params = ql_config.split('丨')
                                    if len(ql_params) == 3:
                                        QLurl = ql_params[0]
                                        ClientID = ql_params[1]
                                        ClientSecret = ql_params[2]
                                        
                                        osname = middleware.bucketGet("dd_hqcsh", "osname")
                                        if osname:
                                            url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
                                            token_res = requests.get(url).json()
                                            if token_res['code'] == 200:
                                                qltoken = token_res['data']['token']
                                                
                                                # 先检查变量是否存在
                                                url = f"{QLurl}/open/envs"
                                                headers = {
                                                    "Authorization": "Bearer" + ' ' + qltoken,
                                                    "Content-Type": "application/json"
                                                }
                                                check_res = requests.get(url, headers=headers).json()
                                                
                                                env_exists = False
                                                env_id = None
                                                
                                                if check_res['code'] == 200:
                                                    for env in check_res['data']:
                                                        if env['name'] == osname and f'车生活账号:{k}丨用户:{myuid}' in env['remarks']:
                                                            env_exists = True
                                                            env_id = env['id']
                                                            break
                                                
                                                if env_exists:
                                                    # 更新已存在的变量
                                                    update_data = {
                                                        "id": env_id,
                                                        "value": y['ck'],
                                                        "name": osname,
                                                        "remarks": f'车生活账号:{k}丨用户:{myuid}'
                                                    }
                                                    res = requests.put(url, headers=headers, json=update_data)
                                                else:
                                                    # 创建新变量
                                                    create_data = [{
                                                        "value": y['ck'],
                                                        "name": osname,
                                                        "remarks": f'车生活账号:{k}丨用户:{myuid}'
                                                    }]
                                                    res = requests.post(url, headers=headers, json=create_data)
                                                
                                                if res.status_code != 200:
                                                    self.sender.reply(f"账号[{k}]提交青龙失败: {res.text}")
                                                else:
                                                    if env_exists:
                                                        self.sender.reply(f"账号[{k}]青龙变量更新成功")
                                                    else:
                                                        self.sender.reply(f"账号[{k}]青龙变量添加成功")
                            except Exception as e:
                                self.sender.reply(f"账号[{k}]提交青龙异常:{str(e)}")
                                fail_count += 1
                                continue
                    
                    if modified:
                        middleware.bucketSet('dd_hqcsh', myuid, str(user_data))
                    
                except:
                    fail_count += 1
                    continue
                
            msg = f"一键授权完成!\n成功授权: {success_count}个账号\n授权失败: {fail_count}个账号\n授权天数: {sjts}天\n已同步更新青龙变量"
            self.sender.reply(msg)
            
            # 发送管理员通知
            notify = middleware.bucketGet('dd_hqcsh', 'notify')
            if notify:
                tsqd = notify.split(',')
                middleware.notifyMasters(msg, tsqd)
            
        except Exception as e:
            self.sender.reply(f'一键授权发生错误: {str(e)}')

    def dssq(self, type, index):
        """打赏授权"""
        if type == 2:
            try:
                # 检查是否有其他用户正在付款
                try:
                    pay_status = middleware.bucketGet("dd_hqcsh", "paying_status")
                    if pay_status and pay_status == "true":
                        self.sender.reply("🔔目前有其他用户正在付款，请稍后再试！！")
                        return
                    # 设置支付状态为正在支付
                    middleware.bucketSet("dd_hqcsh", "paying_status", "true")
                except:
                    # 如果出错，继续执行
                    pass
                
                sqsj = middleware.bucketGet('dd_hqcsh', 'sqsj')
                sqje = middleware.bucketGet('dd_hqcsh', 'sqje')
                if sqsj == '':
                    sqsj = 30
                if sqje == '':
                    sqje = 3
                    
                # 如果授权金额为0，直接授权
                if float(sqje) == 0:
                    dqsj = datetime.now().strftime("%Y-%m-%d")
                    if str(self.sqsj) > str(dqsj):
                        sqsj1 = datetime.strptime(str(self.sqsj), "%Y-%m-%d")
                        new_sqsj = sqsj1 + timedelta(days=int(sqsj))
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                    else:
                        sj = datetime.now()
                        new_sqsj = sj + timedelta(days=int(sqsj))
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                        
                    ts = middleware.bucketGet('dd_hqcsh', self.user)
                    ts = eval(ts)
                    for k, y in ts[index].items():
                        if self.bz == k:
                            b = {}
                            b[f'{k}'] = {'ck': self.ck, 'qd': y["qd"], 'sqsj': new_sqsj}
                            ts[index] = b
                            middleware.bucketSet('dd_hqcsh', self.user, f'{ts}')
                            
                            # 授权后自动提交青龙
                            self.submit_to_qinglong(k)
                            
                            msg = f'【好奇车生活】当前用户: {self.user}\n授权天数: {int(sqsj)}天\n到期时间: {new_sqsj}'
                            self.sender.reply(msg)
                            notify = middleware.bucketGet('dd_hqcsh', 'notify')
                            if notify:
                                tsqd = notify.split(',')
                                middleware.notifyMasters(msg, tsqd)
                            # 重置支付状态
                            middleware.bucketSet("dd_hqcsh", "paying_status", "false")
                            return
                            
                # 如果授权金额不为0，走付款流程
                zsm = middleware.bucketGet('dd_hqcsh', 'zsm')
                if zsm == '':
                    self.sender.reply('管理员还未配置收款码!')
                    # 重置支付状态
                    middleware.bucketSet("dd_hqcsh", "paying_status", "false")
                    return
                
                self.sender.replyImage(zsm)
                self.sender.reply(
                    f"请在120s内使用wx扫码付款\n每付款{sqje}元授权时间增加{sqsj}天!\n发起支付期间不要发其他无关内容！退出回复'q'退出！")
                waitPay = self.sender.waitPay("q", 120000)
                # 支付完成后重置支付状态
                middleware.bucketSet("dd_hqcsh", "paying_status", "false")
                
                if waitPay == 'q':
                    self.sender.reply("退出付款！")
                elif isinstance(waitPay, dict) or isinstance(waitPay, str):
                    if isinstance(waitPay, str):
                        waitPay = json.loads(waitPay)
                    Time = waitPay['Time']
                    userName = waitPay['FromName']
                    Money = waitPay['Money']
                    Type = waitPay['Type']
                    dqsj = datetime.now().strftime("%Y-%m-%d")
                    if str(self.sqsj) > str(dqsj):
                        sqsj1 = datetime.strptime(str(self.sqsj), "%Y-%m-%d")
                        new_sqsj = sqsj1 + timedelta(days=int(float(Money) / float(sqje) * int(sqsj)))
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                    else:
                        sj = datetime.now()
                        new_sqsj = sj + timedelta(days=int(float(Money) / float(sqje) * int(sqsj)))
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                    ts = middleware.bucketGet('dd_hqcsh', self.user)
                    ts = eval(ts)
                    for k, y in ts[index].items():
                        if self.bz == k:
                            b = {}
                            b[f'{k}'] = {'ck': self.ck, 'qd': y["qd"], 'sqsj': new_sqsj}
                            ts[index] = b
                            middleware.bucketSet('dd_hqcsh', self.user, f'{ts}')
                            
                            # 获取青龙配置
                            ql_config = middleware.bucketGet("dd_hqcsh", "Qinglong")
                            if ql_config:
                                ql_params = ql_config.split('丨')
                                if len(ql_params) == 3:
                                    QLurl = ql_params[0]
                                    ClientID = ql_params[1]
                                    ClientSecret = ql_params[2]
                                    
                                    # 获取变量名
                                    osname = middleware.bucketGet("dd_hqcsh", "osname")
                                    if osname:
                                        try:
                                            # 获取青龙token
                                            url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
                                            token_res = requests.get(url).json()
                                            if token_res['code'] == 200:
                                                qltoken = token_res['data']['token']
                                                
                                                # 提交变量到青龙
                                                url = f"{QLurl}/open/envs"
                                                headers = {
                                                    "Authorization": "Bearer" + ' ' + qltoken,
                                                    "Content-Type": "application/json"
                                                }
                                                data = [{
                                                    "value": self.ck,
                                                    "name": osname,
                                                    "remarks": f'车生活账号:{k}丨用户:{self.user}'
                                                }]
                                                res = requests.post(url, headers=headers, json=data)
                                                if res.status_code == 200:
                                                    self.sender.reply("✅变量已提交到青龙")
                                                else:
                                                    self.sender.reply("❌提交青龙失败")
                                        except Exception as e:
                                            self.sender.reply(f"提交青龙异常:{str(e)}")
                            
                            msg = f'【好奇车生活】当前用户: {userName}\n付款: {float(Money)}\n付款渠道：{self.sender.getImtype().upper()}\n授权id: {self.user}\n付款时间: {Time}\n授权天数: {int(float(Money) / float(sqje) * int(sqsj))}天\n到期时间: {new_sqsj}'
                            self.sender.reply(msg)
                            notify = middleware.bucketGet('dd_hqcsh', 'notify')
                            if notify:
                                tsqd = notify.split(',')
                                middleware.notifyMasters(msg, tsqd)
                            return
                
                # 付款成功后自动提交青龙
                self.submit_to_qinglong(k)
                
            except Exception as e:
                # 确保异常情况下也重置支付状态
                middleware.bucketSet("dd_hqcsh", "paying_status", "false")
                self.sender.reply(f"{e}或者超时了！")
                
        else:
            jf = middleware.bucketGet("bd_jf", self.user)
            zsm = middleware.bucketGet('dd_hqcsh', 'zsm')
            sqsj = middleware.bucketGet('dd_hqcsh', 'sqsj')
            sqje = middleware.bucketGet('dd_hqcsh', 'sqje')
            if sqsj == '':
                sqsj = 30
            if sqje == '':
                sqje = 3
            dqsj = str(datetime.now().strftime("%Y-%m-%d"))
            if int(jf) >= int(float(sqje) * 100):
                if str(self.sqsj) > dqsj:
                    self.sqsj = datetime.strptime(str(self.sqsj), "%Y-%m-%d")
                    new_sqsj = self.sqsj + timedelta(days=int(sqsj))
                    new_sqsj = new_sqsj.strftime("%Y-%m-%d")

                else:
                    sj = datetime.now()
                    new_sqsj = sj + timedelta(days=int(sqsj))
                    new_sqsj = new_sqsj.strftime("%Y-%m-%d")

                ts = middleware.bucketGet('dd_hqcsh', self.user)
                ts = eval(ts)

                for k, y in ts[index].items():
                    if self.bz == k:
                        a = {}
                        a[f'{k}'] = {'ck': self.ck, 'sqsj': new_sqsj}
                        ts[index] = a
                        middleware.bucketSet('dd_hqcsh', self.user, f'{ts}')
                        middleware.bucketSet("bd_jf", self.user, f"{int(jf) - int(float(sqje) * 100)}")
                        
                        # 获取青龙配置
                        ql_config = middleware.bucketGet("dd_hqcsh", "Qinglong")
                        if ql_config:
                            ql_params = ql_config.split('丨')
                            if len(ql_params) == 3:
                                QLurl = ql_params[0]
                                ClientID = ql_params[1]
                                ClientSecret = ql_params[2]
                                
                                # 获取变量名
                                osname = middleware.bucketGet("dd_hqcsh", "osname")
                                if osname:
                                    try:
                                        # 获取青龙token
                                        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
                                        token_res = requests.get(url).json()
                                        if token_res['code'] == 200:
                                            qltoken = token_res['data']['token']
                                            
                                            # 提交变量到青龙
                                            url = f"{QLurl}/open/envs"
                                            headers = {
                                                "Authorization": "Bearer" + ' ' + qltoken,
                                                "Content-Type": "application/json"
                                            }
                                            data = [{
                                                "value": self.ck,
                                                "name": osname,
                                                "remarks": f'车生活账号:{k}丨用户:{self.user}'
                                            }]
                                            res = requests.post(url, headers=headers, json=data)
                                            if res.status_code == 200:
                                                self.sender.reply("✅变量已提交到青龙")
                                            else:
                                                self.sender.reply("❌提交青龙失败")
                                    except Exception as e:
                                        self.sender.reply(f"提交青龙异常:{str(e)}")
                    
                    msg = f'【好奇车生活】当前用户: {self.user}\n付款积分: {int(float(sqje) * 100)}\n付款渠道：{self.sender.getImtype().upper()}\n付款时间：{datetime.now()}\n授权id: {self.user}\n授权天数: {int(sqsj)}天\n到期时间: {new_sqsj}'
                    self.sender.reply(msg)
                    notify = middleware.bucketGet('dd_hqcsh', 'notify')
                    if notify == '':
                        pass
                    else:
                        tsqd = notify.split(',')
                        middleware.notifyMasters(msg, tsqd)
                    exit(0)
            else:
                self.sender.reply("积分不足，退出")
                exit(0)

    def jc(self):
        msg = f"抓包：车生活小程序\n域名：https://channel.cheryfs.cn/下请求头里面的accountId数据\n说明：一天50积分左右，月积分2000+，可以抢购兑换ek或者现金\n上车指令: 车生活上车\n管理指令: 车生活管理\n查询指令: 车生活查询\n入口指令: 车生活入口"
        self.sender.reply(msg)

    def rk(self):
        msg = "http://mcg888.yy2088.cn:18080/admin/images/gallery/1736328296136190264.jpg"
        self.sender.replyImage(msg)

    def QLtoken(self, QLurl, ClientID, ClientSecret):  # 获取青龙token
        try:
            url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
            A = requests.get(url)
            if "token" in A.text:
                ql = A.content
                qlrequests = json.loads(ql)
                qltoken = qlrequests['data']['token']
                return qltoken
            else:
                self.sender.reply('链接青龙失败,请检查青龙配参！')
                exit(0)
        except Exception:
            self.sender.reply("链接青龙失败,请检查青龙配参！")
            exit(0)

    def Addenvs(self, QLurl, qltoken, osname, value, account):  # 添加青龙变量
        try:
            qlurl = f"{QLurl}/open/envs"
            data = [{
                "value": value,
                "name": osname,
                "remarks": f'车生活账号:{account}丨用户:{self.user}'
            }]
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            r = requests.post(qlurl, headers=headers, data=json.dumps(data))
            if "value must be unique" in r.text:
                return
            else:
                qlid = r.json()['data'][0]['id']
                return qlid
        except Exception:
            self.sender.reply("添加青龙变量错误,请联系管理员处理")
            exit(0)

    def submit_to_qinglong(self, account_name):
        """提交变量到青龙"""
        # 检查授权是否有效
        tong = middleware.bucketGet("dd_hqcsh", self.user)
        if tong:
            tong = eval(tong)
            current_date = datetime.now().strftime("%Y-%m-%d")
            is_authorized = False
            
            for user in tong:
                for bz, info in user.items():
                    if bz == account_name:
                        # 修改判断逻辑,当天到期的也视为已过期
                        if info['sqsj'] > current_date:  
                            is_authorized = True
                        break
            
            if not is_authorized:
                self.sender.reply("❌账号未授权或授权已过期，无法提交到青龙")
                return

        # 获取青龙配置
        ql_config = middleware.bucketGet("dd_hqcsh", "Qinglong")
        if ql_config:
            ql_params = ql_config.split('丨')
            if len(ql_params) == 3:
                QLurl = ql_params[0]
                ClientID = ql_params[1]
                ClientSecret = ql_params[2]
                
                # 获取变量名
                osname = middleware.bucketGet("dd_hqcsh", "osname")
                if osname:
                    try:
                        # 获取青龙token
                        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
                        token_res = requests.get(url).json()
                        if token_res['code'] == 200:
                            qltoken = token_res['data']['token']
                            
                            # 提交变量到青龙
                            url = f"{QLurl}/open/envs"
                            headers = {
                                "Authorization": "Bearer" + ' ' + qltoken,
                                "Content-Type": "application/json"
                            }
                            data = [{
                                "value": self.ck,
                                "name": osname,
                                "remarks": f'车生活账号:{account_name}丨用户:{self.user}'
                            }]
                            res = requests.post(url, headers=headers, json=data)
                            if res.status_code == 200:
                                self.sender.reply("✅变量已提交到青龙")
                            else:
                                self.sender.reply("❌提交青龙失败")
                    except Exception as e:
                        self.sender.reply(f"提交青龙异常:{str(e)}")
                else:
                    self.sender.reply("❌未配置变量名")
            else:
                self.sender.reply("❌青龙配置格式错误")
        else:
            self.sender.reply("❌未配置青龙参数")

    def check_auth(self):
        """检测授权状态并处理过期账号"""
        if not self.sender.isAdmin():
            self.sender.reply("⚠️ 该指令仅管理员可用")
            return
        
        try:
            # 获取所有用户的数据
            all_users = middleware.bucketAllKeys('dd_hqcsh')
            if not all_users:  # 检查是否为None或空
                self.sender.reply("未找到任何用户数据")
                return
            
            # 过滤掉非用户数据的键
            user_keys = [key for key in all_users if key not in ['zsm', 'sqje', 'sqsj', 'Qinglong', 'osname', 'notify', 'delbtn', 'jfpay']]
            
            if not user_keys:  # 检查是否有用户数据
                self.sender.reply("未找到任何用户账号")
                return
            
            msg = "========授权检测========\n"
            expired_count = 0
            valid_count = 0
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            for myuid in user_keys:
                user_data = middleware.bucketGet('dd_hqcsh', myuid)
                if not user_data or user_data == '[]':
                    continue
                    
                try:
                    user_data = eval(user_data)
                except:
                    continue
                    
                if not isinstance(user_data, list):
                    continue
                    
                for user in user_data:
                    if not isinstance(user, dict):
                        continue
                        
                    for bz, info in user.items():
                        try:
                            auth_date = info.get('sqsj')
                            if not auth_date:
                                continue
                                
                            # 修改判断逻辑,当天到期的也视为已过期
                            if auth_date <= current_date:
                                expired_count += 1
                                msg += f"用户ID: {myuid}\n账号[{bz}]已过期\n过期时间:{auth_date}\n"
                                
                                # 删除青龙中的变量
                                try:
                                    ql_config = middleware.bucketGet("dd_hqcsh", "Qinglong")
                                    if not ql_config:  # 检查青龙配置是否存在
                                        continue
                                        
                                    ql_params = ql_config.split('丨')
                                    if len(ql_params) != 3:  # 确保配置格式正确
                                        continue
                                        
                                    QLurl, ClientID, ClientSecret = ql_params
                                    
                                    osname = middleware.bucketGet("dd_hqcsh", "osname")
                                    if not osname:  # 检查变量名是否存在
                                        continue
                                        
                                    # 获取token
                                    token_url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
                                    token_res = requests.get(token_url, timeout=10)  # 添加超时
                                    if token_res.status_code != 200:
                                        continue
                                        
                                    token_data = token_res.json()
                                    if token_data.get('code') != 200 or 'data' not in token_data or 'token' not in token_data['data']:
                                        continue
                                        
                                    qltoken = token_data['data']['token']
                                    
                                    # 获取环境变量列表
                                    env_url = f"{QLurl}/open/envs"
                                    headers = {
                                        "Authorization": f"Bearer {qltoken}",
                                        "Content-Type": "application/json"
                                    }
                                    
                                    env_res = requests.get(env_url, headers=headers, timeout=10)
                                    if env_res.status_code != 200:
                                        continue
                                        
                                    env_data = env_res.json()
                                    if env_data.get('code') != 200 or 'data' not in env_data:
                                        continue
                                    
                                    # 查找并删除匹配的变量
                                    for env in env_data['data']:
                                        if (env.get('name') == osname and 
                                            env.get('remarks', '').startswith(f'车生活账号:{bz}丨用户:{myuid}')):
                                            
                                            del_url = f"{QLurl}/open/envs"
                                            del_data = [env['id']]
                                            del_res = requests.delete(del_url, headers=headers, json=del_data, timeout=10)
                                            
                                            if del_res.status_code == 200:
                                                msg += f"已删除青龙变量\n"
                                            break
                                
                                except requests.exceptions.RequestException as e:
                                    msg += f"删除青龙变量网络异常:{str(e)}\n"
                        except Exception as e:
                            msg += f"删除青龙变量异常:{str(e)}\n"
                        else:
                            valid_count += 1
                            msg += f"用户ID: {myuid}\n账号[{bz}]授权有效\n到期时间:{auth_date}\n"
                            
                            msg += "--------------------\n"
                
            msg += f"\n授权统计:\n有效账号:{valid_count}个\n过期账号:{expired_count}个"
            self.sender.reply(msg)
            
        except Exception as e:
            self.sender.reply(f"检测授权状态异常:{str(e)}")


if __name__ == "__main__":
    name = "好奇车生活"
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    user = sender.getUserID()
    JD = JD(user, sender)
    message = sender.getMessage()

    if "上车" in message:
        JD.tj()
    elif "管理" in message:
        JD.gl()
    elif "查询" in message:
        JD.cx()
    elif "配置" in message:
        JD.pz()
    elif "授权" in message:
        JD.sq()
    elif "教程" in message:
        JD.jc()
    elif "入口" in message:
        JD.rk()
    elif "检测" in message:
        JD.check_auth()
    elif '车生活版本'in message:
        if sender.isAdmin():
            sender.reply(
                f"🔔当前版本V7.8\n======================\n用户指令:\n上车指令: 车生活上车\n管理指令: 车生活管理\n查询指令: 车生活查询\n入口指令：车生活入口\n教程指令：车生活教程\n检测指令：车生活检测\n======================\n管理员指令:\n插件配置: 车生活配置\n账号授权: 车生活授权\n======================")
