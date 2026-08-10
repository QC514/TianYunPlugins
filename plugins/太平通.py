# [pin:false]
# [disable:false]
# [title: 太平通]
# [author: linzixuan]
# [icon: https://img1.baidu.com/it/u=35209519,2603388558&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500]
# [rule: ^太平(上车|管理|查询|授权|配置|运行|教程|检测).*$]
# [admin: false]
# [service: 2661320550]
# [price: 38.88]
# [version: V6.60]
# [public:true]
# [description: 介绍：《太平通插件指令说明》  插件自带任务! <br>地址：https://www.yuque.com/yuqueyonghulzdzov/fuzugi/xxdck3s248edagql?singleDoc#<br>更新：支持批量授权用户<br>更新：运行时账号火爆通知用户<br>更新：到期前三天自动检测通知用户<br>更新：支持自定义教程地址链接<br>更新：支持签到积分支付上分，需使用市场中的卡密系统<br>更新：新增火爆推送用户开关功能<br>更新：新增代理IP功能<br>更新：修复验证码登录，现已支持验证码登录！]
# [param: {"required":true,"key":"bd_tptconfig.wxzsm","bool":false,"placeholder":"http://127.0.0.1/赞赏码.png","name":"赞赏码链接","desc":"你的机器人赞赏码链接"}]
# [param: {"required":true,"key":"bd_tptconfig.sqje","bool":false,"placeholder":"6.6","name":"授权金额(元)","desc":"设置授权需要支付金额为多少元，默认不设置为6.6元"}]
# [param: {"required":true,"key":"bd_tptconfig.sqsj","bool":false,"placeholder":"30","name":"授权时间(天)","desc":"设置授权金额的授权天数，默认不设置为30天"}]
# [param: {"required":true,"key":"bd_tptconfig.yxbf","bool":false,"placeholder":"1","name":"运行并发数","desc":"设置管理员一键运行所有账号同时最多多少账号一起运行,默认1"}]
# [param: {"required":true,"key":"bd_tptconfig.notify","bool":false,"placeholder":"qq,wx","name":"管理员通知","desc":"设置接受管理员通知的渠道，如 qq,wx,tg  用英文逗号分割,不设置不推送"}]
# [param: {"required":true,"key":"bd_tptconfig.wxpusher","bool":false,"placeholder":"UIDxxxxx","name":"WxPusher任务日志汇总推送","desc":"首先关注https://wxpusher.zjiecode.com/wxuser/?type=1&id=74454#/follow 然后获取自己的UID配置"}]
# [param: {"required":false,"key":"bd_tptconfig.sdyx","bool":true,"placeholder":"","name":"手动运行","desc":"是否允许用户手动执行任务(默认否)"}]
# [param: {"required":false,"key":"bd_tptconfig.jcurl","bool":false,"placeholder":"https://www.yuque.com/yuqueyonghulzdzov/fuzugi/xvy3lp28apxnpvoq?singleDoc#","name":"教程链接","desc":"自定义抓包教程链接,不填则使用默认链接"}]
# [param: {"required":false,"key":"bd_tptconfig.jfkt","bool":true,"placeholder":"","name":"积分开通","desc":"是否允许用户使用积分开通授权(默认否)"}]
# [param: {"required":false,"key":"bd_tptconfig.jfsl","bool":false,"placeholder":"1000","name":"积分开通数量","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":false,"key":"bd_tptconfig.hbtz","bool":true,"placeholder":"","name":"火爆推送","desc":"是否开启账号火爆时推送给用户(默认否)"}]
# [param: {"required":false,"key":"bd_tptconfig.proxy_api","bool":false,"placeholder":"http://api.xiequ.cn/VAD/GetIp.aspx?act=get&...","name":"代理API","desc":"代理API地址,留空则不使用代理"}]

import concurrent.futures
import json
import random
import time
from datetime import datetime, timedelta
import middleware
import os

try:
    from curl_cffi import requests
except:
    import requests

def ts_qb(data, wxpusher_alluid, name, arg1, arg2):
    # WxPusher API地址
    api_url = 'https://wxpusher.zjiecode.com/api/send/message'

    # 按照序号字段对数据进行排序
    sorted_data = sorted(data, key=lambda x: x['序号'])

    # 构造要推送的表格内容
    table_content = ''
    for row in sorted_data:
        # 检查金币值是否为0或异常
        if row['arg1'] == '0' or row['arg2'] == '0':
            arg1_value = '🔔账号异常' 
            arg2_value = '🔔请打开APP'
        else:
            arg1_value = row['arg1']
            arg2_value = row['arg2']
            
        table_content += f"<tr><td style='border: 1px solid #ccc; padding: 6px;'>{row['序号']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['用户']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{arg1_value}</td><td style='border: 1px solid #ccc; padding: 6px;'>{arg2_value}</td></tr>"

    table_html = f"<table style='border-collapse: collapse;'><tr style='background-color: #f2f2f2;'><th style='border: 1px solid #ccc; padding: 8px;'>🆔</th><th style='border: 1px solid #ccc; padding: 8px;'>{name}</th><th style='border: 1px solid #ccc; padding: 8px;'>{arg1}</th><th style='border: 1px solid #ccc; padding: 8px;'>{arg2}</th></tr>{table_content}</table>"

    # 构造请求参数
    params = {
        "appToken": 'AT_rrzWgxSQm9PBZoysnSp9vMpCYyPPTSMv',
        'content': table_html,
        'contentType': 3,  # 表格类型
        'topicIds': [],  # 接收消息的用户ID列表，为空表示发送给所有用户
        "summary": f'太平通日志推送',
        "uids": [wxpusher_alluid],
    }

    # 发送POST请求
    response = requests.post(api_url, json=params)

    notify = middleware.bucketGet('bd_tptconfig', 'notify')

    # 检查API响应
    if response.status_code == 200:
        result = response.json()
        if result['code'] == 1000:
            # 只发送一次通知
            if notify:
                tsqd = notify.split(',')
                middleware.notifyMasters(f"🎉wxpusher推送成功", tsqd)
            # 删除对sender的重复通知
        else:
            if notify:
                tsqd = notify.split(',')
                middleware.notifyMasters(f'💔wxpusher推送失败，错误信息：{result["msg"]}', tsqd)
            else:
                sender.reply(f'💔wxpusher推送失败，错误信息：{result["msg"]}')
    else:
        if notify:
            tsqd = notify.split(',')
            middleware.notifyMasters('⛔wxpusher推送请求失败', tsqd)
        else:
            sender.reply('⛔️wxpusher推送请求失败')


class ATM_tpt:
    def __init__(self, u, s):
        self.black_box = None
        self.code = None
        self.phone = None
        self.user = u
        self.sender = s
        self.usid = None
        self.ck = None
        self.name = None
        self.sqsj = None

    def set_name(self):
        self.sender.reply("欢迎使用太平系统, 请先设置您的备注名(1-6个字符)。退出输入'q'!")
        name = self.sender.listen(60000)
        if name == 'q' or name == 'Q':
            self.sender.reply("退出！")
            return False
        elif name is None:
            self.sender.reply(f'超时退出！')
            return False
        else:
            if len(name) > 6 or len(name) < 1:
                self.sender.reply("备注名不符合要求，退出！")
                return False
            else:
                return name

    def tpsc(self):
        self.name = self.set_name()
        if self.name:
            # 获取自定义教程链接
            jcurl = middleware.bucketGet('bd_tptconfig', 'jcurl')
            if jcurl == '':
                jcurl = 'https://www.yuque.com/yuqueyonghulzdzov/fuzugi/xvy3lp28apxnpvoq?singleDoc#'
            
            self.sender.reply(f"""=====太平通登录方式=====
1️⃣ 短信验证码登录
2️⃣ CK直接登录
========================
请回复序号选择登录方式
退出请回复【q】
========================""")
            qmdl = self.sender.listen(60000)
            if qmdl == 'q' or qmdl == 'Q':
                self.sender.reply("退出！")
            elif qmdl is None:
                self.sender.reply(f'超时退出！')
            elif qmdl == '1':
                self.dx_login()
            elif qmdl == '2':
                self.ck_login()
            else:
                self.sender.reply(f'输入有误!!')

    def gl_login(self):
        try:
            xx_url = 'https://ecustomer.cntaiping.com/tpayms/app/tpay/account/getAcct'
            headers = {
                'Host': 'ecustomer.cntaiping.com',
                'x-ac-black-box': '',
                'x-ac-token-ticket': self.ck,
                'x-ac-channel-id': 'KHT',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'application/json;charset=UTF-8',
                'Origin': 'https://ecustomercdn.itaiping.com',
                'User-Agent': "Mozilla/5.0 (Linux; Android 13; Pixel 4 XL Build/TP1A.220905.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/119.0.6045.163 Mobile Safari/537.36;yuangongejia#android#kehutong;webank/h5face;webank/1.0;netType:NETWORK_WIFI;appVersion:334;packageName:com.cntaiping.tpapp",
                'Connection': 'keep-alive',
                'Referer': 'https://ecustomercdn.itaiping.com/',
                'x-ac-mc-type': 'gateway.user'
            }
            r = requests.get(xx_url, headers=headers)
            success = r.json().get('success', None)
            if success:
                return '✅有效'
            else:
                return '❌失效'
        except Exception as e:
            return f'⛔{e}'

    def tpgl(self):
        ts = middleware.bucketGet('bd_tptcks', self.user)
        if ts == '' or ts == '{}':
            self.sender.reply("太平系统未查询到您的信息! 请先上车! ")
        else:
            ts = eval(ts)
            n = 0
            id_dict = {}
            msg = """=====太平账号管理=====\n"""
            zhszt = {}
            for k, y in ts.items():
                n += 1
                self.ck = y['ck']
                id_dict[n] = {'usid': k, 'name': y['name'], 'ck': y['ck'], 'sqsj': y['sqsj']}
                zhzt = self.gl_login()
                if y['sqsj'] <= datetime.now().strftime("%Y-%m-%d"):
                    msg += f"""📱 账号{n}：{y["name"]}
🔐 状态: {zhzt}
⏰ 授权: {y["sqsj"]}(已到期)
------------------------\n"""
                else:
                    msg += f"""📱 账号{n}：{y["name"]}
🔐 状态: {zhzt}
⏰ 授权: {y["sqsj"]}
------------------------\n"""
                zhszt[n] = {'zhzt': zhzt}

            msg += """请回复序号选择账号
退出请回复【q】
========================"""
            self.sender.reply(msg)
            xz = self.sender.listen(60000)
            xz_list = []
            for k, y in id_dict.items():
                xz_list.append(k)
            if xz == 'q' or xz == 'Q':
                self.sender.reply("退出！")
            elif xz is None:
                self.sender.reply(f'超时退出！')
            elif int(xz) in xz_list:
                zh = id_dict[int(xz)]
                self.usid = zh['usid']
                self.ck = zh['ck']
                self.name = zh['name']
                self.sqsj = zh['sqsj']
                zhzt = zhszt[int(xz)]['zhzt']
                if '有效' in zhzt:
                    self.gl_zh()
                else:
                    self.sender.reply(f'你都失效了！先去上车更新一下吧！')

            else:
                self.sender.reply(f'输入有误，退出！')

    def gl_zh(self):
        """管理账号"""
        msg = f"""=====账号管理面板=====
📱 当前账号: {self.name}

1️⃣ 账号授权
2️⃣ 任务运行  
3️⃣ 删除账号
========================

请回复序号选择操作
退出请回复【q】"""
        self.sender.reply(msg)
        xz = self.sender.listen(60000)
        if xz == 'q' or xz == 'Q':
            self.sender.reply("退出！")
        elif xz is None:
            self.sender.reply(f'超时退出！')
        elif xz == '1':
            self.gl_sq()
        elif xz == '2':
            self.gl_yx()
        elif xz == '3':
            self.gl_sc()
        else:
            self.sender.reply(f'输入有误，退出！')

    def gl_sq(self):
        """账号授权"""
        try:
            sqje = middleware.bucketGet('bd_tptconfig', 'sqje')
            sqsj = middleware.bucketGet('bd_tptconfig', 'sqsj')
            if sqje == '':
                sqje = '6.6'
            if sqsj == '':
                sqsj = '30'
            
            # 检查授权金额是否为0
            if float(sqje) == 0:
                self.sender.reply(f"""=====免费授权=====
⏰ 授权时长: {sqsj}天

请输入需要开通的月数
退出请回复【q】
========================""")
                xz = self.sender.listen(60000)
                
                if xz == 'q' or xz == 'Q':
                    self.sender.reply("退出！")
                    return
                    
                try:
                    if not xz.isdigit():
                        self.sender.reply("❌ 请输入正确的数字！")
                        return
                        
                    months = int(xz)
                    if months <= 0:
                        self.sender.reply("❌ 月数必须大于0！")
                        return
                    
                    # 直接更新授权时间
                    try:
                        if self.sqsj <= datetime.now().strftime("%Y-%m-%d"):
                            new_sqsj = datetime.now() + timedelta(days=int(sqsj) * months)
                        else:
                            sqsj1 = datetime.strptime(self.sqsj, "%Y-%m-%d")
                            new_sqsj = sqsj1 + timedelta(days=int(sqsj) * months)
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                        
                        ts = middleware.bucketGet('bd_tptcks', self.user)
                        if ts:
                            ts = eval(ts)
                            ts[self.usid]['sqsj'] = new_sqsj
                            middleware.bucketSet('bd_tptcks', self.user, f'{ts}')
                            
                            msg = f"""=====授权开通成功=====
👤 用户: {self.name}
💰 费用: 免费
🆔 授权ID: {self.user}
⏰ 授权天数: {int(sqsj) * months}天
📅 到期时间: {new_sqsj}
========================"""
                            self.sender.reply(msg)
                            
                            notify = middleware.bucketGet('bd_tptconfig', 'notify')
                            if notify:
                                tsqd = notify.split(',')
                                middleware.notifyMasters(msg, tsqd)
                        else:
                            self.sender.reply("❌ 获取用户信息失败，请联系管理员")
                            
                    except Exception as e:
                        self.sender.reply(f"❌ 授权处理发生错误: {str(e)}")
                        
                except ValueError as e:
                    self.sender.reply(f"❌ 输入处理错误: {str(e)}")
                return
            
            # 检查是否允许使用积分开通
            jfkt = middleware.bucketGet('bd_tptconfig', 'jfkt')
            if jfkt.lower() == 'true':
                jfsl = middleware.bucketGet('bd_tptconfig', 'jfsl') or '1000'
                self.sender.reply(f"""=====授权开通方式=====
1️⃣ 付费开通
   💰 {sqje}元/{sqsj}天
   
2️⃣ 积分开通
   🎯 {jfsl}积分/30天

请回复序号选择方式
退出请回复【q】
========================""")
                
                xz = self.sender.listen(60000)
                if xz == 'q' or xz == 'Q':
                    self.sender.reply("退出！")
                    return
                    
                if xz == '2':
                    self.jf_kt()
                    return
                elif xz != '1':
                    self.sender.reply("输入有误，退出！")
                    return
            
            # 付费开通流程
            self.sender.reply(f"""=====付费开通授权=====
💰 单价: {sqje}元/月
⏰ 时长: 每月{sqsj}天

请输入需要开通的月数
退出请回复【q】
========================""")
            xz = self.sender.listen(60000)
            
            if xz == 'q' or xz == 'Q':
                self.sender.reply("退出！")
                return
                
            try:
                if not xz.isdigit():
                    self.sender.reply("❌ 请输入正确的数字！")
                    return
                    
                months = int(xz)
                if months <= 0:
                    self.sender.reply("❌ 月数必须大于0！")
                    return
                    
                # 计算总金额
                total = float(sqje) * months
                
                # 显示确认信息
                self.sender.reply(f"""=====确认订单信息=====
🎫 商品: 太平通授权
📅 时长: {months}个月
💰 单价: {sqje}元/月
💳 总价: {total:.2f}元

确认请回复【y】
取消请回复【n】
========================""")
                
                confirm = self.sender.listen(60000)
                if confirm is None:
                    self.sender.reply("❌ 超时退出！")
                    return
                elif confirm.lower() == 'n':
                    self.sender.reply("已取消支付！")
                    return
                elif confirm.lower() != 'y':
                    self.sender.reply("输入有误，已取消！")
                    return
                    
                # 调用支付函数并获取支付结果
                pay_result = self.zf(total, months)
                
                # 只有在支付成功时才继续处理
                if pay_result is True:
                    try:
                        # 计算新的授权时间
                        if self.sqsj <= datetime.now().strftime("%Y-%m-%d"):
                            new_sqsj = datetime.now() + timedelta(days=int(sqsj) * months)
                        else:
                            sqsj1 = datetime.strptime(self.sqsj, "%Y-%m-%d")
                            new_sqsj = sqsj1 + timedelta(days=int(sqsj) * months)
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                        
                        # 更新授权信息
                        ts = middleware.bucketGet('bd_tptcks', self.user)
                        if ts:
                            ts = eval(ts)
                            ts[self.usid]['sqsj'] = new_sqsj
                            middleware.bucketSet('bd_tptcks', self.user, f'{ts}')
                            
                            msg = f"""=====授权开通成功=====
👤 用户: {self.name}
💰 付款: {total:.2f}元
💳 渠道: {self.sender.getImtype().upper()}
🆔 授权ID: {self.user}
⏰ 授权天数: {int(sqsj) * months}天
📅 到期时间: {new_sqsj}
========================"""
                            self.sender.reply(msg)
                            
                            notify = middleware.bucketGet('bd_tptconfig', 'notify')
                            if notify:
                                tsqd = notify.split(',')
                                middleware.notifyMasters(msg, tsqd)
                        else:
                            self.sender.reply("❌ 获取用户信息失败，请联系管理员")
                            
                    except Exception as e:
                        self.sender.reply(f"❌ 授权处理发生错误: {str(e)}")
                        
            except ValueError as e:
                self.sender.reply(f"❌ 输入处理错误: {str(e)}")
                
        except Exception as e:
            self.sender.reply(f"❌ 授权处理发生错误: {str(e)}")

    def gl_yx(self):
        """运行账号"""
        sdyx = middleware.bucketGet('bd_tptconfig', 'sdyx')
        if sdyx == '':
            sdyx = 'false'
        if sdyx == 'false':
            self.sender.reply("""=====运行失败=====
❌ 管理员未开启手动运行
========================""")
        elif sdyx == 'true':
            if self.sqsj <= datetime.now().strftime("%Y-%m-%d"):
                self.sender.reply(f"""=====运行失败=====
📱 账号: {self.name}
❌ 授权已过期，请及时续费
========================""")
            else:
                tpt = TPT(self.user, 'qd', self.name, self.ck, self.usid, 1)
                tpt.main()

    def gl_sc(self):
        """删除账号"""
        self.sender.reply(f"""=====删除账号确认=====
📱 账号: {self.name}

⚠️ 删除后将清空所有授权信息
确认请回复【y】
取消请回复【n】
========================""")
        zh = self.sender.listen(60000)
        if zh == 'n' or zh == 'N':
            self.sender.reply("已取消删除")
        elif zh is None:
            self.sender.reply("❌ 超时退出")
        elif zh == 'y' or zh == 'Y':
            ts = middleware.bucketGet('bd_tptcks', self.user)
            ts = eval(ts)
            del ts[f'{self.usid}']
            middleware.bucketSet('bd_tptcks', self.user, f'{ts}')
            self.sender.reply(f"""=====删除账号成功=====
📱 账号: {self.name}
✅ 状态: 已删除
========================""")
        else:
            self.sender.reply("❌ 输入有误")

    def dssq(self):
        """打赏授权"""
        try:
            status = sender.atWaitPay()
            if status == "True" or status or status == "true":
                self.sender.reply("⚠️ 目前有其他用户正在付款，请稍后再试！")
            else:
                zsm = middleware.bucketGet('bd_tptconfig', 'wxzsm')
                sqje = middleware.bucketGet('bd_tptconfig', 'sqje')
                sqsj = middleware.bucketGet('bd_tptconfig', 'sqsj')
                if zsm == '':
                    self.sender.reply("❌ 管理员未配置收款码！")
                    return
                if sqje == '':
                    sqje = '6.6'
                if sqsj == '':
                    sqsj = '30'
                
                # 检查是否允许使用积分开通
                jfkt = middleware.bucketGet('bd_tptconfig', 'jfkt')
                if jfkt.lower() == 'true':
                    jfsl = middleware.bucketGet('bd_tptconfig', 'jfsl') or '1000'
                    user_jf = int(middleware.bucketGet('dd_sign_points', self.user) or '0')
                    
                    msg = f"""=====选择支付方式====="""
                    if zsm != '':
                        msg += f"""
1️⃣ 微信支付
   💰 {sqje}元/{sqsj}天"""
                    if jfkt == 'true':
                        msg += f"""
2️⃣ 积分支付
   🎯 {jfsl}积分/{sqsj}天
   💫 当前积分: {user_jf}"""
                    msg += """

请回复序号选择方式
退出请回复【q】
========================"""
                    
                    self.sender.reply(msg)
                    choice = self.sender.listen(60000)
                    
                    if choice == 'q' or choice == 'Q':
                        self.sender.reply("已取消支付")
                        return
                        
                    elif choice == '1' and zsm != '':
                        # 微信支付流程
                        self.sender.replyImage(zsm)
                        self.sender.reply(f"""=====微信扫码支付=====
💰 单价: {sqje}元/{sqsj}天
⏰ 有效期: 120秒

请使用微信扫码完成支付
支付期间请勿发送其他内容
取消支付请回复【q】
========================""")
                        
                        waitPay = self.sender.waitPay("q", 120000)
                        if waitPay == 'q':
                            self.sender.reply("已取消支付")
                        elif isinstance(waitPay, dict) or isinstance(waitPay, str):
                            try:
                                # 处理支付结果
                                Money = 0
                                Time = ''
                                if isinstance(waitPay, str):
                                    try:
                                        waitPay = json.loads(waitPay)
                                        if isinstance(waitPay, dict) and waitPay.get('type') == '微信收款':
                                            Money = float(waitPay.get('money', 0))
                                            Time = waitPay.get('time', '')
                                            waitPay = {
                                                "Money": Money,
                                                "Time": Time
                                            }
                                    except:
                                        if "二维码赞赏到账" in waitPay:
                                            try:
                                                amount = waitPay.split("收款金额￥")[1].split("\n")[0]
                                                time = waitPay.split("到账时间")[1].split("\n")[0]
                                                waitPay = {
                                                    "Money": float(amount),
                                                    "Time": time.strip()
                                                }
                                            except Exception as e:
                                                self.sender.reply(f"❌ 解析收款信息失败: {str(e)}")
                                                return

                                Money = float(waitPay.get('Money') or waitPay.get('money', 0))
                                days = int(float(Money) / float(sqje) * int(sqsj))
                                self._update_auth_time(days)
                            
                            except Exception as e:
                                self.sender.reply(f"❌ 支付处理失败: {str(e)}")
                                return
                        
                    elif choice == '2' and jfkt == 'true':
                        # 积分支付逻辑
                        if user_jf < int(jfsl):
                            self.sender.reply(f"""=====积分不足=====
👤 当前积分: {user_jf}
📍 需要积分: {jfsl}
========================""")
                            return
                            
                        self.sender.reply(f"""=====积分开通确认=====
💫 消耗积分: {jfsl}
⏰ 授权时长: {sqsj}天

确认请回复【y】
取消请回复【n】
========================""")
                        confirm = self.sender.listen(60000)
                        
                        if confirm.lower() == 'y':
                            # 扣除积分
                            new_jf = user_jf - int(jfsl)
                            middleware.bucketSet('dd_sign_points', self.user, str(new_jf))
                            
                            # 更新授权时间
                            self._update_auth_time(int(sqsj))
                            
                            self.sender.reply(f"""=====积分开通成功=====
💫 扣除积分: {jfsl}
💰 剩余积分: {new_jf}
========================""")
                        else:
                            self.sender.reply("已取消支付")
                    else:
                        self.sender.reply("❌ 输入有误")
                    
        except Exception as e:
            self.sender.reply(f"❌ 支付处理失败: {str(e)}")

    def _update_auth_time(self, days):
        """更新授权时间的辅助方法"""
        try:
            dqsj = datetime.now().strftime("%Y-%m-%d")
            if self.sqsj > dqsj:
                self.sqsj = datetime.strptime(self.sqsj, "%Y-%m-%d")
                new_sqsj = self.sqsj + timedelta(days=days)
            else:
                sj = datetime.now()
                new_sqsj = sj + timedelta(days=days)
            new_sqsj = new_sqsj.strftime("%Y-%m-%d")
            
            ts = middleware.bucketGet('bd_tptcks', self.user)
            ts = eval(ts)
            ts[self.usid] = {'name': self.name, 'ck': self.ck, 'sqsj': new_sqsj}
            middleware.bucketSet('bd_tptcks', self.user, f'{ts}')
            
            msg = f"""=====授权开通成功=====
👤 用户: {self.name}
🆔 授权ID: {self.usid}
⏰ 授权天数: {days}天
📅 到期时间: {new_sqsj}
========================"""
            self.sender.reply(msg)
            
            notify = middleware.bucketGet('bd_tptconfig', 'notify')
            if notify:
                tsqd = notify.split(',')
                middleware.notifyMasters(msg, tsqd)
                
        except Exception as e:
            self.sender.reply(f"❌ 授权更新失败: {str(e)}")

    def tpcx(self):
        ts = middleware.bucketGet('bd_tptcks', self.user)
        if ts == '' or ts == '{}':
            self.sender.reply("❌ 太平系统未查询到您的信息! 请先上车!")
        else:
            ts = eval(ts)
            msg = """=====太平通账号查询=====\n"""
            n = 0
            for k, y in ts.items():
                n += 1
                self.ck = y['ck']
                self.usid = k
                self.name = y['name']
                self.sqsj = y['sqsj']

                zhzt = self.gl_login()
                if '有效' in zhzt:
                    if self.sqsj <= datetime.now().strftime("%Y-%m-%d"):
                        msg += f"""📱 账号{n}：{self.name}
🔐 状态: {zhzt}
⏰ 授权: {self.sqsj} (已过期)
------------------------\n"""
                    else:
                        tpt = TPT(self.user, 'qd', self.name, self.ck, self.usid, 1)
                        coins = tpt.cx()
                        if isinstance(coins, tuple):
                            dqjb, jrjb, llzx, hyyd, rcrw = coins
                            msg += f"""📱 账号{n}：{self.name}
🔐 状态: {zhzt}
💰 今日金币: {jrjb}
💎 当前金币: {dqjb}
⏰ 授权: {self.sqsj}
------------------------\n"""
                        else:
                            msg += f"""📱 账号{n}：{self.name}
🔐 状态: {zhzt}
⚠️ 查询失败，账号可能火爆
⏰ 授权: {self.sqsj}
------------------------\n"""
                else:
                    msg += f"""📱 账号{n}：{self.name}
🔐 状态: {zhzt}
❌ 账号已失效
⏰ 授权: {self.sqsj}
------------------------\n"""
            msg += """⚠️ 温馨提示：
• 账号火爆请打开APP解决
• 一机一号抓包，多号共用会黑
========================"""
            self.sender.reply(msg)

    def get_tptcks(self):
        try:
            if self.sender.isAdmin():
                ts = middleware.bucketAllKeys('bd_tptcks')
                kong = 0
                wsqzhs = {}
                start_zhs = {}
                for i in ts:
                    ts_data = middleware.bucketGet('bd_tptcks', f'{i}')
                    ts_data = eval(ts_data)
                    if ts_data == {}:
                        kong += 1
                        middleware.bucketDel('bd_tptcks', f'{i}')
                        continue
                    else:
                        for k, y in ts_data.items():
                            ck = y['ck']
                            name = y['name']
                            sqsj = y['sqsj']
                            if sqsj > datetime.now().strftime("%Y-%m-%d"):
                                start_zhs[k] = {
                                    'name': name,
                                    'ck': ck,
                                    'user': i
                                }
                            else:
                                wsqzhs[i] = k
                                continue

                for k, y in wsqzhs.items():
                    ts_data = middleware.bucketGet('bd_tptcks', f'{k}')
                    ts_data = eval(ts_data)
                    del ts_data[f'{y}']
                    middleware.bucketSet('bd_tptcks', f'{k}', f'{ts_data}')

                return start_zhs, kong, wsqzhs
        except Exception as e:
            return e

    def tpyx(self):
        try:
            get_tptcks = self.get_tptcks()
            if isinstance(get_tptcks, tuple):
                tptcks, kong, wsqzhs = get_tptcks
                yxbf = middleware.bucketGet('bd_tptconfig', 'yxbf')
                if yxbf == '':
                    yxbf = 1

                with concurrent.futures.ThreadPoolExecutor(max_workers=int(yxbf)) as executor:
                    notify = middleware.bucketGet('bd_tptconfig', 'notify')
                    if notify == '':
                        self.sender.reply(
                            f"🔔共获取到{len(tptcks)}个账号！\n🔔删除未授权账号{len(wsqzhs)}个! \n🔔删除空账号{kong}个!\n🔔开始{yxbf}线程运行所有账号!")
                    else:
                        tsqd = notify.split(',')
                        self.sender.reply(
                            f"🔔共获取到{len(tptcks)}个账号！\n🔔删除未授权账号{len(wsqzhs)}个! \n🔔删除空账号{kong}个!\n🔔开始{yxbf}线程运行所有账号!")
                        middleware.notifyMasters(
                            f"🔔共获取到{len(tptcks)}个账号！\n🔔删除未授权账号{len(wsqzhs)}个! \n🔔删除空账号{kong}个!\n🔔开始{yxbf}线程运行所有账号!",
                            tsqd)

                    results = []
                    for k, y in tptcks.items():
                        tpt = TPT(y['user'], 'qd', y['name'], y['ck'], k, 1)
                        future = executor.submit(tpt.main)
                        results.append(future)
                        time.sleep(0.5)
                        continue

                    a = 0
                    ts_all = []
                    for future in concurrent.futures.as_completed(results):
                        a += 1
                        if a % 100 == 1 and a != 1:
                            wxpusher_alluid = middleware.bucketGet('bd_tptconfig', 'wxpusher')
                            if wxpusher_alluid == '':
                                pass
                            else:
                                ts_qb(ts_all, wxpusher_alluid, '用户', '今日金币', '当前金币')
                                ts_all = []

                        result = future.result()
                        if isinstance(result, tuple):
                            if len(result) == 3:
                                name, jrjb, dqjb = result
                                ts = {
                                    '序号': a,
                                    '用户': name,
                                    'arg1': jrjb,
                                    'arg2': f'{int(dqjb)}({int(dqjb) / 100}元)'
                                }
                                ts_all.append(ts)
                                continue
                            elif len(result) == 2:
                                name, yc = result
                                ts = {
                                    '序号': a,
                                    '用户': name,
                                    'arg1': yc,
                                    'arg2': yc
                                }
                                ts_all.append(ts)
                                continue
                            else:
                                continue
                        else:
                            continue

                    wxpusher_alluid = middleware.bucketGet('bd_tptconfig', 'wxpusher')
                    if wxpusher_alluid == '':
                        pass
                    else:
                        ts_qb(ts_all, wxpusher_alluid, '用户', '今日金币', '当前金币')

                notify = middleware.bucketGet('bd_tptconfig', 'notify')
                if notify == '':
                    self.sender.reply(
                        f'🔔所有账号运行完毕！')
                else:
                    tsqd = notify.split(',')
                    self.sender.reply(
                        f'🔔所有账号运行完毕！')
                    middleware.notifyMasters(
                        f'🔔所有账号运行完毕！', tsqd)
            else:
                self.sender.reply(f'🔔获取ck错误:\n🔔{get_tptcks}')
        except Exception as e:
            self.sender.reply(f'运行错误: {e}')

    def tppz(self):
        wxzsm = middleware.bucketGet('bd_tptconfig', 'wxzsm')
        pz1 = '已配置' if wxzsm else '未配置'

        sqje = middleware.bucketGet('bd_tptconfig', 'sqje') or '6.6'
        sqsj = middleware.bucketGet('bd_tptconfig', 'sqsj') or '30'
        sdyx = middleware.bucketGet('bd_tptconfig', 'sdyx') or 'false'
        yxbf = middleware.bucketGet('bd_tptconfig', 'yxbf') or '1'
        notify = middleware.bucketGet('bd_tptconfig', 'notify')
        pz2 = '已配置' if notify else '未配置'
        wxpusher = middleware.bucketGet('bd_tptconfig', 'wxpusher')
        pz3 = '已配置' if wxpusher else '未配置'

        msg = f"""=====太平通配置管理=====
1️⃣ 赞赏码 ({pz1})
2️⃣ 授权金额 ({sqje}元)
3️⃣ 授权时间 ({sqsj}天)
4️⃣ 手动运行 ({sdyx})
5️⃣ 运行并发 ({yxbf})
6️⃣ 管理通知 ({pz2})
7️⃣ WxPusher ({pz3})

请回复序号选择配置项
退出请回复【q】
========================"""
        self.sender.reply(msg)
        zh = self.sender.listen(60000)
        if zh == 'q' or zh == 'Q':
            self.sender.reply("已取消操作")
        elif zh is None:
            self.sender.reply("❌ 超时退出")
        elif zh == '1':
            self.sender.reply("""=====赞赏码配置=====
请发送微信赞赏码图片
退出请回复【q】
========================""")
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("已取消操作")
            elif pz is None:
                self.sender.reply("❌ 超时退出")
            else:
                self.sender.replyImage(pz)
                middleware.bucketSet('bd_tptconfig', 'wxzsm', f'{pz}')
                self.sender.reply("""=====配置成功=====
✅ 赞赏码已更新
========================""")
        elif zh == '2':
            self.sender.reply("""=====授权金额配置=====
请输入每月授权金额
退出请回复【q】
========================""")
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("已取消操作")
            elif pz is None:
                self.sender.reply("❌ 超时退出")
            else:
                middleware.bucketSet('bd_tptconfig', 'sqje', f'{pz}')
                self.sender.reply(f"""=====配置成功=====
✅ 授权金额: {pz}元/月
========================""")
        elif zh == '3':
            self.sender.reply("""=====授权时间配置=====
请输入每月授权天数
退出请回复【q】
========================""")
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("已取消操作")
            elif pz is None:
                self.sender.reply("❌ 超时退出")
            else:
                middleware.bucketSet('bd_tptconfig', 'sqsj', f'{pz}')
                self.sender.reply(f"""=====配置成功=====
✅ 授权时间: {pz}天/月
========================""")
        elif zh == '4':
            self.sender.reply("""=====手动运行配置=====
请输入是否允许用户手动运行
true: 允许
false: 禁止

退出请回复【q】
========================""")
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("已取消操作")
            elif pz is None:
                self.sender.reply("❌ 超时退出")
            else:
                middleware.bucketSet('bd_tptconfig', 'sdyx', f'{pz}')
                status = "允许" if pz.lower() == 'true' else "禁止"
                self.sender.reply(f"""=====配置成功=====
✅ 手动运行: {status}
========================""")
        elif zh == '5':
            self.sender.reply("""=====并发数配置=====
请输入最大并发运行数量
退出请回复【q】
========================""")
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("已取消操作")
            elif pz is None:
                self.sender.reply("❌ 超时退出")
            else:
                middleware.bucketSet('bd_tptconfig', 'yxbf', f'{pz}')
                self.sender.reply(f"""=====配置成功=====
✅ 最大并发: {pz}
========================""")
        elif zh == '6':
            self.sender.reply("""=====通知渠道配置=====
请输入通知渠道，用英文逗号分隔
支持渠道: qq,wx,tg
不设置则不推送

退出请回复【q】
========================""")
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("已取消操作")
            elif pz is None:
                self.sender.reply("❌ 超时退出")
            else:
                middleware.bucketSet('bd_tptconfig', 'notify', f'{pz}')
                self.sender.reply(f"""=====配置成功=====
✅ 通知渠道: {pz}
========================""")
        elif zh == '7':
            self.sender.reply("""=====WxPusher配置=====
请输入WxPusher的UID
退出请回复【q】
========================""")
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("已取消操作")
            elif pz is None:
                self.sender.reply("❌ 超时退出")
            else:
                middleware.bucketSet('bd_tptconfig', 'wxpusher', f'{pz}')
                self.sender.reply(f"""=====配置成功=====
✅ WxPusher UID: {pz}
========================""")
        else:
            self.sender.reply("❌ 输入有误")

    def tpsq(self):
        msg = f"""=====太平通授权管理=====
1️⃣ 一键授权所有用户
2️⃣ 单独授权用户

请回复序号选择操作
退出请回复【q】
========================"""
        self.sender.reply(msg)
        xz = self.sender.listen(60000)
        
        if xz == 'q' or xz == 'Q':
            self.sender.reply("已取消操作")
            return
        elif xz is None:
            self.sender.reply("❌ 超时退出")
            return
        elif xz == '1':
            self.qbqbsq()
        elif xz == '2':
            msg = f"""=====用户授权=====
请输入需要授权的账号ID
(可通过发送myuid获取)

退出请回复【q】
========================"""
            self.sender.reply(msg)
            myuid = self.sender.listen(60000)
            if myuid == 'q' or myuid == 'Q':
                self.sender.reply("已取消操作")
            elif myuid == 1:
                self.qbqbsq()
            elif myuid is None:
                self.sender.reply("❌ 超时退出")
            else:
                ts = middleware.bucketGet('bd_tptcks', myuid)
                if ts == '' or ts == '{}':
                    self.sender.reply(f"""=====查询失败=====
❌ 未找到用户 {myuid} 的信息
请确认ID是否正确
========================""")
                else:
                    ts = eval(ts)
                    n = 0
                    id_dict = {}
                    msg = """=====选择授权账号=====
0️⃣ 授权所有账号
------------------------\n"""
                    for k, y in ts.items():
                        n += 1
                        self.ck = y['ck']
                        self.usid = k
                        self.name = y['name']
                        self.sqsj = y['sqsj']
                        id_dict[n] = {'usid': self.usid, 'name': self.name, 'ck': self.ck, 'sqsj': self.sqsj}
                        msg += f"""📱 账号{n}：{y["name"]}
⏰ 授权: {self.sqsj}
------------------------\n"""
                    msg += """请回复序号选择账号
退出请回复【q】
========================"""
                    self.sender.reply(msg)
                    xz = self.sender.listen(60000)
                    xz_list = []
                    for k, y in id_dict.items():
                        xz_list.append(k)
                    if xz == 'q' or xz == 'Q':
                        self.sender.reply("已取消操作")
                    elif xz is None:
                        self.sender.reply("❌ 超时退出")
                    elif xz == '0':
                        msg = f"""=====批量授权=====
请输入授权天数
退出请回复【q】
========================"""
                        self.sender.reply(msg)
                        sjts = self.sender.listen(60000)
                        if sjts == 'q' or sjts == 'Q':
                            self.sender.reply("已取消操作")
                        elif sjts is None:
                            self.sender.reply("❌ 超时退出")
                        elif isinstance(int(sjts), int):
                            success_count = 0
                            for k, y in ts.items():
                                try:
                                    dqsj = datetime.now().strftime("%Y-%m-%d")
                                    if y['sqsj'] > dqsj:
                                        sqsj = datetime.strptime(y['sqsj'], "%Y-%m-%d")
                                        new_sqsj = sqsj + timedelta(days=int(sjts))
                                    else:
                                        new_sqsj = datetime.now() + timedelta(days=int(sjts))
                                    new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                                    ts[k]['sqsj'] = new_sqsj
                                    success_count += 1
                                except:
                                    continue
                            middleware.bucketSet('bd_tptcks', myuid, f'{ts}')
                            msg = f"""=====授权完成=====
✅ 成功授权: {success_count}个账号
⏰ 授权天数: {sjts}天
========================"""
                            self.sender.reply(msg)
                            notify = middleware.bucketGet('bd_tptconfig', 'notify')
                            if notify:
                                tsqd = notify.split(',')
                                middleware.notifyMasters(msg, tsqd)
                        else:
                            self.sender.reply("❌ 天数格式错误")
                    elif int(xz) in xz_list:
                        zh = id_dict[int(xz)]
                        self.usid = zh['usid']
                        self.ck = zh['ck']
                        self.name = zh['name']
                        self.sqsj = zh['sqsj']

                        msg = f"""=====账号授权=====
📱 账号: {self.name}

请输入授权天数
退出请回复【q】
========================"""
                        self.sender.reply(msg)
                        sjts = self.sender.listen(60000)
                        if sjts == 'q' or sjts == 'Q':
                            self.sender.reply("已取消操作")
                        elif sjts is None:
                            self.sender.reply("❌ 超时退出")
                        elif isinstance(int(sjts), int):
                            dqsj = datetime.now().strftime("%Y-%m-%d")
                            if self.sqsj > dqsj:
                                self.sqsj = datetime.strptime(self.sqsj, "%Y-%m-%d")
                                new_sqsj = self.sqsj + timedelta(days=int(sjts))
                                new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                            else:
                                sj = datetime.now()
                                new_sqsj = sj + timedelta(days=int(sjts))
                                new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                            ts = middleware.bucketGet('bd_tptcks', f'{myuid}')
                            ts = eval(ts)
                            for k, y in ts.items():
                                if self.usid == k:
                                    ts[f'{k}'] = {'name': self.name, 'ck': self.ck, 'sqsj': new_sqsj}
                                    middleware.bucketSet('bd_tptcks', f'{myuid}', f'{ts}')
                                    msg = f"""=====授权成功=====
👤 用户ID: {myuid}
📱 账号: {self.name}
🆔 授权ID: {self.usid}
⏰ 授权天数: {int(sjts)}天
📅 到期时间: {new_sqsj}
========================"""
                                    self.sender.reply(msg)
                                    break
                                else:
                                    continue
                        else:
                            self.sender.reply("❌ 天数格式错误")
                    else:
                        self.sender.reply("❌ 输入有误")

    def qbqbsq(self):
        """一键授权所有用户"""
        try:
            # 获取所有用户的数据
            ts = middleware.bucketAllKeys('bd_tptcks')
            if not ts:
                self.sender.reply("""=====查询失败=====
❌ 未找到任何用户信息
========================""")
                return
            
            self.sender.reply("""=====批量授权=====
请输入授权天数
退出请回复【q】
========================""")
            sjts = self.sender.listen(60000)
            if sjts == 'q' or sjts == 'Q':
                self.sender.reply("已取消操作")
                return
            elif sjts is None:
                self.sender.reply("❌ 超时退出")
                return
            
            try:
                sjts = int(sjts)
            except:
                self.sender.reply("❌ 天数格式错误")
                return
            
            success_count = 0
            fail_count = 0
            
            for myuid in ts:
                user_data = middleware.bucketGet('bd_tptcks', myuid)
                if user_data == '' or user_data == '{}':
                    continue
                
                user_data = eval(user_data)
                for usid, info in user_data.items():
                    dqsj = datetime.now().strftime("%Y-%m-%d")
                    if info['sqsj'] > dqsj:
                        sqsj = datetime.strptime(info['sqsj'], "%Y-%m-%d")
                        new_sqsj = sqsj + timedelta(days=sjts)
                    else:
                        new_sqsj = datetime.now() + timedelta(days=sjts)
                    new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                    
                    try:
                        user_data[usid]['sqsj'] = new_sqsj
                        middleware.bucketSet('bd_tptcks', myuid, f'{user_data}')
                        success_count += 1
                    except:
                        fail_count += 1
                    
            msg = f"""=====批量授权完成=====
✅ 成功授权: {success_count}个账号
❌ 授权失败: {fail_count}个账号
⏰ 授权天数: {sjts}天
========================"""
            self.sender.reply(msg)
            
            # 发送管理员通知
            notify = middleware.bucketGet('bd_tptconfig', 'notify')
            if notify:
                tsqd = notify.split(',')
                middleware.notifyMasters(msg, tsqd)
            
        except Exception as e:
            self.sender.reply(f"❌ 批量授权失败: {str(e)}")

    def jf_kt(self):
        """积分开通授权"""
        try:
            # 获取积分配置
            jfsl = middleware.bucketGet('bd_tptconfig', 'jfsl')
            sqsj = middleware.bucketGet('bd_tptconfig', 'sqsj')
            if not jfsl:
                jfsl = '1000'
            if not sqsj:
                sqsj = '30'
                
            # 获取用户当前积分
            user_jf = middleware.bucketGet('dd_sign_points', self.user) or '0'
            try:
                user_jf = int(user_jf)
                jfsl = int(jfsl)
            except:
                self.sender.reply("❌ 积分格式错误")
                return

            # 显示积分开通选项
            self.sender.reply(f"""=====积分开通授权=====
💫 当前积分: {user_jf}
💰 开通费用: {jfsl}积分/{sqsj}天

请输入需要开通的月数
退出请回复【q】
========================""")
        
            months = self.sender.listen(60000)
            if months == 'q' or months == 'Q':
                self.sender.reply("已取消操作")
                return
                
            try:
                months = int(months)
                if months <= 0:
                    self.sender.reply("❌ 月数必须大于0！")
                    return
                    
                total_points = jfsl * months
                if user_jf < total_points:
                    self.sender.reply(f"""=====积分不足=====
👤 当前积分: {user_jf}
📍 需要积分: {total_points}
========================""")
                    return
                    
                # 确认开通
                self.sender.reply(f"""=====积分开通确认=====
💫 消耗积分: {total_points}
⏰ 授权时长: {int(sqsj) * months}天

确认请回复【y】
取消请回复【n】
========================""")
                confirm = self.sender.listen(60000)
                
                if confirm and confirm.lower() == 'y':
                    # 扣除积分
                    new_jf = user_jf - total_points
                    middleware.bucketSet('dd_sign_points', self.user, str(new_jf))
                    
                    # 更新授权时间
                    if self.sqsj <= datetime.now().strftime("%Y-%m-%d"):
                        new_sqsj = datetime.now() + timedelta(days=int(sqsj) * months)
                    else:
                        sqsj1 = datetime.strptime(self.sqsj, "%Y-%m-%d")
                        new_sqsj = sqsj1 + timedelta(days=int(sqsj) * months)
                    new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                    
                    # 更新授权信息
                    ts = eval(middleware.bucketGet('bd_tptcks', self.user))
                    ts[self.usid]['sqsj'] = new_sqsj
                    middleware.bucketSet('bd_tptcks', self.user, f'{ts}')
                    
                    msg = f"""=====积分开通成功=====
💫 扣除积分: {total_points}
💰 剩余积分: {new_jf}
⏰ 授权天数: {int(sqsj) * months}天
📅 到期时间: {new_sqsj}
========================"""
                    self.sender.reply(msg)
                    
                    # 通知管理员
                    notify = middleware.bucketGet('bd_tptconfig', 'notify')
                    if notify:
                        tsqd = notify.split(',')
                        admin_msg = f"""=====积分开通通知=====
👤 用户: {self.user}
{msg}"""
                        middleware.notifyMasters(admin_msg, tsqd)
                        
                else:
                    self.sender.reply("已取消支付")
                    
            except ValueError:
                self.sender.reply("❌ 请输入正确的数字！")
                
        except Exception as e:
            self.sender.reply(f"❌ 积分开通出错: {str(e)}")

    def zf(self, total, months):
        """支付处理"""
        try:
            # 如果金额为0，显示支付成功并返回
            if total == 0:
                self.sender.reply(f"""=====支付成功=====
✅ 金额: 0.00元
💫 状态: 已完成
========================""")
                return True
                
            # 获取赞赏码
            wxzsm = middleware.bucketGet('bd_tptconfig', 'wxzsm')
            if not wxzsm:
                self.sender.reply("❌ 管理员未配置收款码!")
                return False
            
            # 显示订单信息和赞赏码
            self.sender.reply(f"""=====微信扫码支付=====
🎫 商品: 太平通授权
📅 时长: {months}个月
💳 应付: {total:.2f}元

请使用微信扫码完成支付
取消支付请回复【q】
========================""")
            self.sender.replyImage(wxzsm)  # 显示收款码
            
            # 等待支付结果
            status = self.sender.atWaitPay()
            if status == "True" or status or status == "true":
                self.sender.reply("⚠️ 目前有其他用户正在付款，请稍后再试！")
                return False
            
            result = self.sender.waitPay("q", 120000)  # 等待120秒
            
            # 检查是否是退出指令
            if isinstance(result, str) and result.lower() == 'q':
                self.sender.reply('❌ 已取消支付')
                return False
            elif result is None:  # 超时处理
                self.sender.reply('❌ 支付超时，已退出')
                return False
            
            try:
                # 处理支付结果
                if isinstance(result, dict):
                    # 新版微信赞赏消息格式
                    if result.get('type') == '微信赞赏':
                        Money = float(result.get('money', 0))
                        Time = result.get('time', '')
                        From = result.get('from_name', '')
                    # 旧版微信收款消息格式
                    elif result.get('type') == '微信收款':
                        Money = float(result.get('money', 0))
                        Time = result.get('time', '')
                        From = result.get('from_name', '')
                    else:
                        Money = float(result.get('Money', 0))
                        Time = result.get('Time', '')
                        From = ''
                else:
                    # 尝试解析JSON字符串
                    try:
                        result = json.loads(result)
                        if result.get('type') == '微信赞赏':
                            Money = float(result.get('money', 0))
                            Time = result.get('time', '')
                            From = result.get('from_name', '')
                        elif result.get('type') == '微信收款':
                            Money = float(result.get('money', 0))
                            Time = result.get('time', '')
                            From = result.get('from_name', '')
                        else:
                            Money = float(result.get('Money', 0))
                            Time = result.get('Time', '')
                            From = ''
                    except:
                        self.sender.reply("❌ 无法解析支付结果")
                        return False
                        
                # 验证支付金额
                if abs(Money - total) < 0.000001:  # 使用浮点数比较
                    self.sender.reply(f"""=====支付成功=====
💰 金额: {Money:.2f}元
⏰ 时间: {Time}
✨ 状态: 已完成
========================""")
                    return True
                else:
                    self.sender.reply(f"""=====支付金额错误=====
💰 应付: {total:.2f}元
💳 实付: {Money:.2f}元
👤 付款人: {From}

❗ 请联系管理员处理退款！
========================""")
                    return False
                
            except Exception as e:
                self.sender.reply(f"❌ 支付处理失败: {str(e)}")
                return False
            
        except Exception as e:
            self.sender.reply(f"❌ 支付处理出错: {str(e)}")
            return False

    def dx_login(self):
        """短信验证码登录"""
        try:
            # 导入必要的模块
            import uuid
            import ssl
            import urllib3
            import subprocess
            
            # 禁用SSL警告
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            def generate_device_id():
                """生成设备ID"""
                return f"{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:12]}-{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:7]}-{uuid.uuid4().hex[:12]}"
            
            # 获取手机号
            self.sender.reply(f"""=====短信验证码登录=====
🔔{self.name},你好！
请输入手机号码
退出请回复【q】
========================""")
            phone = self.sender.listen(60000)
            if phone == 'q' or phone == 'Q':
                self.sender.reply("退出！")
                return
            elif phone is None:
                self.sender.reply(f'超时退出！')
                return
            elif len(phone) != 11 or not phone.isdigit():
                self.sender.reply("❌ 请输入11位手机号码")
                return
                
            self.phone = phone
            
            # 生成设备ID
            device_id = generate_device_id()
            
            # 公共请求头
            common_headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Origin': 'https://ecustomercdn.itaiping.com',
                'Referer': 'https://ecustomercdn.itaiping.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'x-ac-device-id': device_id,
                'anonymousId': device_id,
                'x-ac-channel-id': 'KHT',
                'x-ac-mc-type': 'gateway.user',
                'x-ac-utm': '11810',
                'x-ac-live-room': '',
                'x-ac-sourceutm': '',
                'x-ac-token-ticket': ''
            }
            
            # 创建一个会话，用于所有请求
            session = requests.Session()
            # 设置SSL验证为False，绕过SSL验证
            session.verify = False
            
            try:
                # 步骤1：启动通知
                self.sender.reply("🔄 正在初始化登录服务...")
                start_url = 'https://ecustomer.cntaiping.com/userms/anonymous/startup/notify'
                
                response = session.get(start_url, headers=common_headers, timeout=30)
                if response.status_code != 200:
                    self.sender.reply("❌ 启动通知失败")
                    return
                
                switch_url = 'https://ecustomer.cntaiping.com/userms/unifiedLogin/captcha/switch/v2'
                switch_headers = common_headers.copy()
                switch_headers['Content-Type'] = 'application/json; charset=utf-8'
                
                switch_data = {
                    "mobile": phone,
                    "internatCode": "0086",
                    "businessCode": "LOGIN"
                }
                
                response = session.post(switch_url, json=switch_data, headers=switch_headers, timeout=30)
                if response.status_code != 200:
                    self.sender.reply("❌ 验证码配置检查失败")
                    return
                
                # 步骤3：发送短信验证码
                self.sender.reply("📱 正在发送短信验证码...")
                sms_url = 'https://ecustomer.cntaiping.com/commonms/unifiedLogin/msg/verifyCodeSms'
                
                sms_data = {
                    "mobile": phone,
                    "internatCode": "0086", 
                    "businessCode": "LOGIN",
                    "serviceType": "KHTBASIC",
                    "type": "QUICKLOGON"
                }
                
                response = session.post(sms_url, json=sms_data, headers=switch_headers, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success') or result.get('code') == '0000':
                        self.sender.reply("✅ 验证码发送成功！")
                    else:
                        self.sender.reply(f"❌ 验证码发送失败: {result.get('message', '未知错误')}")
                        return
                else:
                    self.sender.reply("❌ 验证码发送请求失败")
                    return
                
                # 步骤4：等待用户输入验证码并登录
                retry_count = 3
                while retry_count > 0:
                    self.sender.reply("""=====验证码验证=====
请输入收到的6位验证码
退出请回复【q】
========================""")
                    
                    code = self.sender.listen(60000)
                    if code == 'q' or code == 'Q':
                        self.sender.reply("退出！")
                        return
                    elif code is None:
                        self.sender.reply(f'超时退出！')
                        return
                    elif len(code) != 6 or not code.isdigit():
                        self.sender.reply("❌ 请输入6位数字验证码")
                        continue
                    
                    # 使用验证码登录
                    login_url = 'https://ecustomer.cntaiping.com/userms/anonymous/auth/unifiedLog/loginByMobileVerifyCode/v1'
                    
                    login_data = {
                        "phone": phone,
                        "internatCode": "0086",
                        "verificationcode": code,
                        "x_agentcode": "1762724346751963136",
                        "userSysType": "UNIFORM_USER",
                        "userSource": "TPT_WEB"
                    }
                    
                    response = session.post(login_url, json=login_data, headers=switch_headers, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get('success') and result.get('code') == "0000":
                            # 登录成功
                            auth_token = result.get('data', {}).get('authToken')
                            user_id = result.get('data', {}).get('userId')
                            
                            if auth_token and user_id:
                                self.usid = user_id
                                self.ck = auth_token
                                
                                # 保存登录信息
                                ts = middleware.bucketGet('bd_tptcks', self.user)
                                if not ts:
                                    data = {
                                        f'{self.usid}': {
                                            'name': self.name,
                                            'ck': self.ck,
                                            'sqsj': f'{datetime.now().strftime("%Y-%m-%d")}'
                                        }
                                    }
                                    middleware.bucketSet('bd_tptcks', self.user, f'{data}')
                                    self.sender.reply(f'{self.name}>>>🔔首次登录成功!发送【太平管理】对账号进行管理!')
                                else:
                                    ts = eval(ts)
                                    if self.usid in ts:
                                        for k, y in ts.items():
                                            if self.usid == k:
                                                ts[f'{k}'] = {'name': self.name, 'ck': self.ck, 'sqsj': y['sqsj']}
                                                middleware.bucketSet('bd_tptcks', self.user, f'{ts}')
                                                self.sender.reply(f'{self.name}>>>🔔更新账号成功！发送【太平管理】对账号进行管理!')
                                                break
                                    else:
                                        ts[f'{self.usid}'] = {
                                            'name': self.name,
                                            'ck': self.ck,
                                            'sqsj': f'{datetime.now().strftime("%Y-%m-%d")}'
                                        }
                                        middleware.bucketSet('bd_tptcks', self.user, f'{ts}')
                                        self.sender.reply(f'{self.name}>>>🔔新增登录成功!发送【太平管理】对账号进行管理!')
                                return
                            else:
                                self.sender.reply("❌ 登录响应数据不完整")
                                return
                        else:
                            error_msg = result.get('message', result.get('desc', '未知错误'))
                            if "验证码" in error_msg:
                                retry_count -= 1
                                if retry_count > 0:
                                    self.sender.reply(f"❌ 验证码错误，还有{retry_count}次机会")
                                    continue
                                else:
                                    self.sender.reply("❌ 验证码错误次数过多，请稍后重试")
                                    return
                            else:
                                self.sender.reply(f"❌ 登录失败: {error_msg}")
                                return
                    else:
                        self.sender.reply("❌ 登录请求失败")
                        return
                
            except requests.exceptions.RequestException as e:
                self.sender.reply(f"❌ 网络请求异常: {str(e)}")
                return
            except Exception as e:
                self.sender.reply(f"❌ 登录过程中发生错误: {str(e)}")
                return
                
        except Exception as e:
            self.sender.reply(f"❌ 登录过程异常: {str(e)}")

    def get_token(self):
        try:
            url = "https://ecustomer.cntaiping.com/userms/anonymous/auth/unifiedLog/loginByMobileVerifyCode/v1"

            payload = {
                "phone": f"{self.phone}",
                "internatCode": "0086",
                "verificationcode": f"{self.code}",
                "x_agentcode": "",
                "userSysType": "UNIFORM_USER",
                "userSource": "TPT_WEB"
            }

            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
                'Accept-Encoding': "gzip, deflate, br, zstd",
                'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\"",
                'x-ac-channel-id': "KHT",
                'x-ac-device-id': "2905f0b73df93c-05f7e12b4e0a4e-4c657b58-2359296-1905f0b73e0edb",
                'x-ac-utm': "11180",
                'x-ac-sourceutm': "",
                'sec-ch-ua-mobile': "?0",
                'anonymousId': "1905f0b73df93c-05f7e12b4e0a4e-4c657b58-2359296-1905f0b73e0edb",
                'Content-Type': "application/json; charset=utf-8",
                'x-ac-mc-type': "gateway.user",
                'x-ac-black-box': self.black_box,
                'x-ac-live-room': "",
                'x-ac-token-ticket': "",
                'sec-ch-ua-platform': "\"Windows\"",
                'Origin': "https://ecustomercdn.itaiping.com",
                'Sec-Fetch-Site': "cross-site",
                'Sec-Fetch-Mode': "cors",
                'Sec-Fetch-Dest': "empty",
                'Referer': "https://ecustomercdn.itaiping.com/",
                'Accept-Language': "zh-CN,zh;q=0.9"
            }

            r = requests.post(url, json=payload, headers=headers)

            success = r.json().get('success', None)
            if success:
                self.usid = r.json()['data']['userId']
                self.ck = r.json()['data']['authToken']
                return True
            else:
                self.sender.reply(f"❌登录失败!\n{r.json().get('desc', None)}")
                return False
        except Exception as e:
            self.sender.reply(f'⛔登录异常!\n{e}')
            return False

    def ck_login(self):
        # 获取自定义教程链接
        jcurl = middleware.bucketGet('bd_tptconfig', 'jcurl')
        if jcurl == '':
            jcurl = 'https://www.yuque.com/yuqueyonghulzdzov/fuzugi/xvy3lp28apxnpvoq?singleDoc#'
        
        self.sender.reply(f"""=====太平通CK登录=====
👤 {self.name}，您好!

📖 抓包教程: {jcurl}
🎯 抓包应用: 太平通APP
🔍 抓包域名: ecustomer.cntaiping.com
🎫 抓包参数: x-ac-token-ticket

💰 收益说明: 
- 每天约100金币 ≈ 1RMB
- 可兑换话费、e卡、会员等

⚠️ 注意事项:
- 一机一号抓包
- 多号共用设备会被封禁

请在120秒内发送您的x-ac-token-ticket
退出请回复'q'
========================""")

        ck = self.sender.input(120000, 1000, False)
        if ck == 'q' or ck == 'Q':
            self.sender.reply("退出！")

        elif ck is None:
            self.sender.reply(f'超时退出！')

        elif 'ey' in ck:
            xx_url = 'https://ecustomer.cntaiping.com/tpayms/app/tpay/account/getAcct'
            headers = {
                'Host': 'ecustomer.cntaiping.com',
                'x-ac-black-box': '',
                'x-ac-token-ticket': ck,
                'x-ac-channel-id': 'KHT',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'application/json;charset=UTF-8',
                'Origin': 'https://ecustomercdn.itaiping.com',
                'User-Agent': "Mozilla/5.0 (Linux; Android 13; Pixel 4 XL Build/TP1A.220905.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/119.0.6045.163 Mobile Safari/537.36;yuangongejia#android#kehutong;webank/h5face;webank/1.0;netType:NETWORK_WIFI;appVersion:334;packageName:com.cntaiping.tpapp",
                'Connection': 'keep-alive',
                'Referer': 'https://ecustomercdn.itaiping.com/',
                'x-ac-mc-type': 'gateway.user'
            }
            try:
                r = requests.get(xx_url, headers=headers)
                success = r.json().get('success', None)
                if success:
                    usid = r.json()["data"]["userId"]
                    ts = middleware.bucketGet('bd_tptcks', self.user)
                    if not ts:
                        data = {
                            f'{usid}': {
                                'name': self.name,
                                'ck': ck,
                                'sqsj': f'{datetime.now().strftime("%Y-%m-%d")}'
                            }
                        }
                        middleware.bucketSet('bd_tptcks', self.user, f'{data}')
                        self.sender.reply(f"{self.name}>>>🔔登录成功!发送'太平管理'对账号进行管理!")
                    else:
                        ts = eval(ts)
                        if usid in ts:
                            for k, y in ts.items():
                                if usid == k:
                                    ts[f'{k}'] = {'name': self.name, 'ck': ck, 'sqsj': y['sqsj']}
                                    middleware.bucketSet('bd_tptcks', self.user, f'{ts}')
                                    self.sender.reply(f"{self.name}>>>🔔更新成功！发送'太平管理'对账号进行管理!")
                                    break
                                else:
                                    continue
                        else:
                            ts[f'{usid}'] = {
                                'name': self.name,
                                'ck': ck,
                                'sqsj': f'{datetime.now().strftime("%Y-%m-%d")}'
                            }
                            middleware.bucketSet('bd_tptcks', self.user, f'{ts}')
                            self.sender.reply(f"{self.name}>>>🔔登录成功!发送'太平管理'对账号进行管理!")
                else:
                    msg = r.json()['msg']
                    self.sender.reply(f'{self.name}登录失败>>>{msg}')
            except Exception as e:
                self.sender.reply(f'{self.name}登录错误>>>{e}')
        else:
            self.sender.reply(f'输入有误，退出！')

    def tpjc(self):
        """定时太平检测 - 检查所有用户的授权过期情况"""
        try:
            if not self.sender.isAdmin():
                self.sender.reply("❌ 此功能仅限管理员使用")
                return
                
            # 获取所有用户数据
            all_users = middleware.bucketAllKeys('bd_tptcks')
            if not all_users:
                self.sender.reply("""=====检测完成=====
📊 检测结果: 无用户数据
========================""")
                return
            
            # 统计数据
            total_accounts = 0
            expired_accounts = []
            expiring_accounts = []
            normal_accounts = 0
            
            current_date = datetime.now()
            
            for user_id in all_users:
                user_data = middleware.bucketGet('bd_tptcks', user_id)
                if not user_data or user_data == '{}':
                    continue
                    
                try:
                    user_data = eval(user_data)
                    for account_id, account_info in user_data.items():
                        total_accounts += 1
                        account_name = account_info.get('name', '未知')
                        expire_date_str = account_info.get('sqsj', '')
                        
                        if expire_date_str:
                            expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d")
                            days_left = (expire_date - current_date).days
                            
                            if days_left < 0:
                                # 已过期
                                expired_accounts.append({
                                    'user_id': user_id,
                                    'account_name': account_name,
                                    'expire_date': expire_date_str,
                                    'days_overdue': abs(days_left)
                                })
                            elif 0 <= days_left <= 3:
                                # 即将过期(3天内)
                                expiring_accounts.append({
                                    'user_id': user_id,
                                    'account_name': account_name,
                                    'expire_date': expire_date_str,
                                    'days_left': days_left
                                })
                            else:
                                # 正常
                                normal_accounts += 1
                                
                except Exception as e:
                    print(f"处理用户 {user_id} 数据时出错: {e}")
                    continue
            
            # 发送过期提醒通知
            notification_count = 0
            for account in expiring_accounts:
                try:
                    msg = f"""⚠️ 授权即将到期提醒 ⚠️

📱 账号: {account['account_name']}
⏰ 剩余时间: {account['days_left']}天
📅 到期时间: {account['expire_date']}

请及时续费以免影响使用！
发送【太平管理】进行续费操作"""
                    
                    # 通过多个渠道推送给用户
                    middleware.push('wb', '', account['user_id'], '', msg)
                    middleware.push('tg', '', account['user_id'], '', msg) 
                    middleware.push('qq', '', account['user_id'], '', msg)
                    middleware.push('qb', '', account['user_id'], '', msg)
                    middleware.push('wx', '', account['user_id'], '', msg)
                    notification_count += 1
                    
                except Exception as e:
                    print(f"通知用户 {account['user_id']} 失败: {e}")
            
            # 生成检测报告
            report = f"""=====太平通授权检测报告=====
📊 检测时间: {current_date.strftime('%Y-%m-%d %H:%M:%S')}
📈 总账号数: {total_accounts}个
✅ 正常账号: {normal_accounts}个
⚠️ 即将过期: {len(expiring_accounts)}个
❌ 已过期: {len(expired_accounts)}个
📤 发送通知: {notification_count}条

"""
            
            # 添加即将过期账号详情
            if expiring_accounts:
                report += "⚠️ 即将过期账号:\n"
                for account in expiring_accounts:
                    report += f"• {account['account_name']} (剩余{account['days_left']}天)\n"
                report += "\n"
            
            # 添加已过期账号详情
            if expired_accounts:
                report += "❌ 已过期账号:\n"
                for account in expired_accounts:
                    report += f"• {account['account_name']} (过期{account['days_overdue']}天)\n"
                report += "\n"
            
            report += "========================"
            
            # 发送报告给管理员
            self.sender.reply(report)
            
            # 同时通过管理员通知渠道发送
            notify = middleware.bucketGet('bd_tptconfig', 'notify')
            if notify:
                tsqd = notify.split(',')
                middleware.notifyMasters(report, tsqd)
                
        except Exception as e:
            error_msg = f"❌ 检测过程中发生错误: {str(e)}"
            self.sender.reply(error_msg)
            print(f"太平检测错误: {e}")


class TPT:
    def __init__(self, u, qd, n, c, uid, qyinfo):
        self.qd = qd
        self.user = u
        self.qyinfo = qyinfo
        self.usid = uid
        self.name = n
        self.ck = c
        self.llzx = None
        self.hyyd = None
        self.ydlisturl = None
        self.zldatas = []
        self.ydname = None
        self.ydid = None
        self.taskid = None
        self.rwname = None
        self.joinPoint = None
        self.htid = None
        self.validDate = None
        # 获取授权时间
        try:
            user_data = middleware.bucketGet('bd_tptcks', u)
            if user_data:
                user_data = eval(user_data)
                self.sqsj = user_data[str(uid)]['sqsj']
            else:
                self.sqsj = None
        except:
            self.sqsj = None
        self.headers = {
            'Host': 'ecustomer.cntaiping.com',
            'x-ac-black-box': 'jWPVu1713323931keU0txvxzkc',
            'x-ac-token-ticket': self.ck,
            'x-ac-channel-id': 'KHT',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'application/json;charset=UTF-8',
            'Origin': 'https://ecustomercdn.itaiping.com',
            'User-Agent': "Mozilla/5.0 (Linux; Android 13; Pixel 4 XL Build/TP1A.220905.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/119.0.6045.163 Mobile Safari/537.36;yuangongejia#android#kehutong;webank/h5face;webank/1.0;netType:NETWORK_WIFI;appVersion:334;packageName:com.cntaiping.tpapp",
            'Connection': 'keep-alive',
            'Referer': 'https://ecustomercdn.itaiping.com/',
            'x-ac-mc-type': 'gateway.user',
            'Content-Type': 'application/json'
        }

    def get_proxy(self):
        """获取代理IP"""
        try:
            proxy_api = middleware.bucketGet('bd_tptconfig', 'proxy_api')
            if not proxy_api:
                return None
                
            # 尝试获取代理池数据
            try:
                import requests as requests_original
                r = requests_original.get(proxy_api, timeout=10)
            except:
                r = requests.get(proxy_api, timeout=10)
                
            if r.status_code == 200:
                try:
                    # 获取响应文本并清理
                    data = r.text.strip()
                    if not data:
                        print("[太平通]代理API返回空数据")
                        return None
                    
                    # 按换行符分割获取所有代理
                    proxy_list = []
                    for line in data.split('\r\n'):
                        if ':' in line:
                            ip, port = line.split(':')
                            proxy_str = f'http://{ip}:{port}'
                            proxy_list.append({
                                'http': proxy_str,
                                'https': proxy_str
                            })
                    
                    # 如果有可用代理,随机返回一个
                    if proxy_list:
                        return random.choice(proxy_list)
                    else:
                        print("[太平通]未找到可用代理")
                        return None
                        
                except Exception as e:
                    print(f"[太平通]解析代理返回数据失败: {e}")
                    return None
            else:
                print(f"[太平通]获取代理失败,状态码: {r.status_code}")
                return None
        except Exception as e:
            print(f"[太平通]获取代理发生错误: {e}")
            return None

    def _make_request(self, method, url, **kwargs):
        """统一的请求方法"""
        try:
            # 只有特定任务才使用代理
            use_proxy = False
            if 'campaignsms/couponAndsign' in url:  # 签到任务
                use_proxy = True
            elif 'campaignsms/goldParty' in url:  # 金币任务
                use_proxy = True
            elif 'campaignsms/coinBubble' in url:  # 金币气泡
                use_proxy = True
            
            max_retries = 3 if use_proxy else 1  # 使用代理时最多重试3次
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    if use_proxy and retry_count < max_retries - 1:  # 最后一次重试不使用代理
                        proxies = self.get_proxy()  # 每次重试都获取新的代理
                        if proxies:
                            kwargs['proxies'] = proxies
                            kwargs['timeout'] = 15
                    else:
                        kwargs['timeout'] = 10
                        if 'proxies' in kwargs:
                            del kwargs['proxies']
                    
                    # 发起请求    
                    if method.lower() == 'get':
                        r = requests.get(url, **kwargs)
                    else:
                        r = requests.post(url, **kwargs)
                    
                    # 检查响应状态
                    if r.status_code == 200:
                        return r
                    else:
                        print(f"[太平通]请求失败,状态码: {r.status_code}")
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    if "timeout" in error_msg:
                        print(f"[太平通]第{retry_count + 1}次请求超时,尝试更换代理")
                    elif "proxy" in error_msg:
                        print(f"[太平通]第{retry_count + 1}次代理连接失败,尝试更换代理")
                    else:
                        print(f"[太平通]第{retry_count + 1}次请求错误: {e}")
                    
                    # 最后一次重试失败才返回None
                    if retry_count == max_retries - 1:
                        return None
                        
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2)  # 重试前等待2秒
                    
            return None
            
        except Exception as e:
            print(f"[太平通]请求发生未预期错误: {e}")
            return None

    def sign(self):
        try:
            # Android签到
            r = requests.post(
                "https://ecustomer.cntaiping.com/campaignsms/couponAndsign",
                headers=self.headers,
                json={}
            )
            # iOS签到
            self.headers[
                'User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;yuangongejia#ios#kehutong#CZBIOS'
            r = requests.post(
                "https://ecustomer.cntaiping.com/campaignsms/couponAndsign", 
                headers=self.headers,
                json={}
            )
            success = r.json().get('success', None)
            if success:
                # 恢复Android UA
                self.headers[
                    'User-Agent'] = "Mozilla/5.0 (Linux; Android 13; Pixel 4 XL Build/TP1A.220905.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/119.0.6045.163 Mobile Safari/537.36;yuangongejia#android#kehutong;webank/h5face;webank/1.0;netType:NETWORK_WIFI;appVersion:334;packageName:com.cntaiping.tpapp"
                return True
            elif not success and '已过期' in r.text:
                return '失效'
            else:
                return False
        except Exception as e:
            return e

    def get_rwlist(self):
        try:
            r = self._make_request(
                'post',
                "https://ecustomer.cntaiping.com/campaignsms/goldParty/task/list",
                headers=self.headers,
                json={
                    'activityNumber': 'goldCoinParty',
                    'rewardFlag': '1',
                    'openMsgRemind': 0,
                }
            )
            success = r.json().get('success', None)
            if success:
                data = r.json()['data']['taskList']
                return data
            else:
                return False
        except Exception as e:
            return e

    def finish(self):
        try:
            r = self._make_request(
                'post',
                "https://ecustomer.cntaiping.com/campaignsms/goldParty/task/finish",
                headers=self.headers,
                json={'taskIds': [self.taskid], })
            success = r.json().get('success', None)
            if success:
                return True
            else:
                return False
        except Exception as e:
            return e

    def add(self):
        try_count = 2
        while try_count > 0:
            try:
                r = self._make_request(
                    'post',
                    "https://ecustomer.cntaiping.com/campaignsms/goldParty/goldCoin/add",
                    headers=self.headers,
                    json={
                        'taskIds': [self.taskid]
                    }
                )
                success = r.json().get('success', None)
                if success:
                    return True
                elif '已经获取' in r.text:
                    return False
                elif not success and '火爆' in r.text:
                    try_count -= 1
                    if try_count == 0:
                        return False
                    self.headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;yuangongejia#ios#kehutong#CZBIOS'
                    continue
                else:
                    return False
            except Exception as e:
                return e

    def run_rw(self):
        data = self.get_rwlist()
        if isinstance(data, list):
            for i in data:
                time.sleep(random.randint(1, 3))
                taskStatus = i['taskStatus']
                self.taskid = i['taskId']
                self.rwname = i['name']
                if taskStatus == 2:
                    pass
                elif taskStatus == 0 and self.rwname != '浏览资讯':
                    if self.finish() is True:
                        time.sleep(random.randint(1, 3))
                        if self.add() is True:
                            time.sleep(random.randint(1, 3))
                        else:
                            return False
                    else:
                        return False
                elif taskStatus == 1 and self.rwname != '浏览资讯':
                    self.add()
                    time.sleep(random.randint(1, 3))
            return True
        else:
            return False

    def get_ydlist(self):
        try:
            r = self._make_request(
                'post',
                self.ydlisturl,
                headers=self.headers,
                json={
                    "plugInId": "701b3099297148a8ba979ad9c982b561",
                    "trackDesc": "赚金币任务",
                    "city": "1",
                    "pageSize": 20,
                    "type": "GENERAL_PLUGIN"
                }
            )
            success = r.json().get('success', None)
            if success:
                data = r.json()['data']
                return data
            else:
                return False
        except Exception as e:
            return e

    def coinInfoV2(self):
        try:
            r = self._make_request(
                'post',
                "https://ecustomer.cntaiping.com/informationms/app/v2/article/web/coinInfoV2",
                headers=self.headers,
                json={
                    'articleId': self.ydid,
                    'source': 'TPT',
                    'detailUrl': f'https://ecustomercdn.itaiping.com/static/newscontent/#/info?articleId={self.ydid}&source=TPT&x_utmId=10013&x_businesskey=articleId',
                    'deviceId': '',
                    'version': 'V2'
                }
            )
            success = r.json().get('success', None)
            if success:
                return True
            else:
                return False
        except Exception as e:
            return e

    def zl(self):
        try:
            for i in self.zldatas:
                time.sleep(random.randint(1, 3))
                r = self._make_request(
                    'post',
                    "https://ecustomer.cntaiping.com/informationms/app/v2/article/web/coinInfoV2",
                    headers={
                        'Host': 'ecustomer.cntaiping.com',
                        'accept': 'application/json', 'x-ac-channel-id': 'KHT',
                        'x-ac-black-box': 'iWPVl1701438414PrzwzjCHQw1',
                        'x-ac-mc-type': 'gateway.user',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6309092b) XWEB/9105 Flue',
                        'x-ac-token-ticket': '',
                        'content-type': 'application/json',
                        'Origin': 'https://ecustomercdn.itaiping.com',
                        'Sec-Fetch-Site': 'cross-site',
                        'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                        'Referer': 'https://ecustomercdn.itaiping.com/',
                        'Accept-Language': 'zh-CN,zh;q=0.9'
                    },
                    json=i
                )
                success = r.json().get('success', None)
                if success:
                    return True
                else:
                    return False
        except Exception as e:
            return e

    def gold(self):
        try:
            r = self._make_request(
                'post',
                "https://ecustomer.cntaiping.com/informationms/app/v2/read/gold",
                headers=self.headers,
                json={
                    "articleId": self.ydid,
                    "source": "TPT"
                }
            )
            success = r.json().get('success', None)
            if success:
                return True
            else:
                return False
        except Exception as e:
            return e

    def queryList(self):
        try:
            r = self._make_request(
                'post',
                'https://ecustomer.cntaiping.com/campaignsms/coinBubble/queryList',
                headers=self.headers,
                json={}
            )
            success = r.json().get('success', None)
            if success:
                data = r.json()['data']
                if data:
                    return True
                else:
                    return '没有待领取金币'
            else:
                return r.json()['msg']
        except Exception as e:
            return e

    def getAllCoins(self):
        try_count = 2
        while try_count > 0:
            try:
                r = self._make_request(
                    'post',
                    "https://ecustomer.cntaiping.com/campaignsms/coinBubble/getAllCoins",
                    headers=self.headers,
                    json={}
                )
                success = r.json().get('success', None)
                if success:
                    return True
                elif not success and '火爆' in r.text:
                    try_count -= 1
                    if try_count == 0:
                        return False
                    self.headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;yuangongejia#ios#kehutong#CZBIOS'
                    continue
                else:
                    return r.json()['msg']
            except Exception as e:
                return e

    def getShareInfo(self):
        try:
            r = self._make_request(
                'post',
                "https://ecustomer.cntaiping.com/informationms/app/v2/share/getShareInfo",
                headers=self.headers,
                json={
                    "articleId": self.ydid,
                    "source": "TPT",
                    "shareFlag": True
                }
            )
            success = r.json().get('success', None)
            if success:
                return r.json()['data']['tagUrl']
            else:
                return False
        except Exception as e:
            return e

    def run_yd(self):
        n = 0
        data = self.get_ydlist()
        if isinstance(data, list):
            for i in range(len(data)):
                time.sleep(random.randint(1, 3))
                n += 1
                d = data[i]['cell']['0'][0]
                self.ydname = d['title']
                self.ydid = d['contentId']

                if self.llzx < 14:
                    if self.coinInfoV2() is True:
                        time.sleep(random.randint(1, 3))
                        if self.gold() is True:
                            time.sleep(random.randint(1, 3))
                        else:
                            return False
                    else:
                        return False
                getShareInfo = self.getShareInfo()
                if isinstance(getShareInfo, str):
                    shareCode = getShareInfo.split('shareCode=')[1].split('&')[0]
                    articleId = getShareInfo.split('articleId=')[1].split('&')[0]
                    zldata = {
                        'articleId': articleId,
                        'source': 'TPT',
                        'detailUrl': getShareInfo,
                        'deviceId': '',
                        "shareCode": shareCode,
                        'version': 'V2'
                    }
                    self.zldatas.append(zldata)
                else:
                    return False
            return True
        else:
            return False

    def queryUserPoints(self):
        try:
            r = self._make_request(
                'post',
                "https://ecustomer.cntaiping.com/campaignsms/integral/queryUserPoints",
                headers=self.headers,
                json={
                    "sourceOrganId": "932"
                }
            )
            success = r.json().get('success', None)
            if success:
                return r.json()['data']['scoreAccountInfo']['availableScore']
            else:
                return False
        except Exception as e:
            return e

    def is_in_current_month(self):
        date = datetime.strptime(self.validDate, '%Y-%m-%d 00:00:00')
        current_date = datetime.now()
        return date.year == current_date.year and date.month == current_date.month

    def cx(self):
        try:
            r = self._make_request(
                'post',
                'https://ecustomer.cntaiping.com/campaignsms/integral/queryIntegralDetailList',
                headers=self.headers,
                json={
                    'pageNo': 1,
                    'pageSize': 100,
                    'typePo': '3',
                }
            )
            success = r.json().get('success', None)
            if success:
                dqjb = self.queryUserPoints()
                data = r.json()['data']['list']
                today = datetime.now().strftime('%Y-%m-%d')
                coins = 0
                llzx = 0
                hyyd = 0
                rcrw = 0
                for i in data:
                    coin = i['num']
                    effectDate = i['effectDate']
                    memo = i['memo']
                    if effectDate == today:
                        if memo == '浏览资讯':
                            llzx += 1
                        elif memo == '好友阅读':
                            hyyd += 1
                        elif memo in ['给太平树浇水', '分享海报', '回执签收', '邀请注册']:
                            rcrw += 1
                        coins += coin
                        continue
                    else:
                        break
                return dqjb, coins, llzx, hyyd, rcrw
            else:
                return r.json()['msg']
        except Exception as e:
            return e

    def exhibitionTopic(self):
        try:
            r = self._make_request(
                'post',
                "https://ecustomer.cntaiping.com/campaignsms/tPkTopicAppointment/exhibitionTopic",
                headers=self.headers,
                json={
                    "pageNo": 1,
                    "pageSize": 200
                }
            )
            success = r.json().get('success', None)
            if success:
                return r.json()['data']
            else:
                msg = r.json()['msg']
                return msg
        except Exception as e:
            return e

    def standInLineTopic(self):
        try:
            r = self._make_request(
                'post',
                "https://ecustomer.cntaiping.com/campaignsms/tPkTopicAppointment/standInLineTopic",
                headers=self.headers,
                json={
                    "joinPoint": self.joinPoint,
                    "id": self.htid,
                    "dataFrom": 0
                }
            )
            success = r.json().get('success', None)
            print(r.json())
            if success:
                return True
            else:
                msg = r.json()['msg']
                return msg
        except Exception as e:
            return e

    def main(self):
        try:
            # 初始化变量
            jrjb = 0
            dqjb = 0
            
            sign = self.sign()
            if sign is True:
                cxjg = self.cx()
                if isinstance(cxjg, tuple):
                    dqjb, jrjb, self.llzx, self.hyyd, rcrw = cxjg
                    if self.queryList() is True:
                        self.getAllCoins()
                    sender.reply(f'🔔开始运行: {self.name}\n💰今日金币: {jrjb}\n💰当前金币: {dqjb}')
                else:
                    sender.reply(f'🔔{self.name}: 查询金币时异常\n🔔{cxjg}')
                    return self.name, '异常'
                
                exhibitionTopic = self.exhibitionTopic()
                if isinstance(exhibitionTopic, list):
                    for i in exhibitionTopic:
                        self.htid = i['id']
                        self.joinPoint = i['joinWin']
                        isParticipateIn = i['isParticipateIn']
                        prizeStatus = i['prizeStatus']
                        if isParticipateIn is None and prizeStatus == 0:
                            self.standInLineTopic()
                            time.sleep(random.randint(5, 10))
                            continue
                        else:
                            continue

                a = 0
                while True:
                    cxjg = self.cx()
                    if isinstance(cxjg, tuple):
                        dqjb, jrjb, self.llzx, self.hyyd, rcrw = cxjg
                    else:
                        sender.reply(f'🔔{self.name}: 查询金币时异常\n🔔{cxjg}')
                        return self.name, '异常'
                    a += 1
                    if rcrw < 3:
                        if not self.run_rw():
                            # 运行完成后检查金币
                            cxjg_end = self.cx()
                            if isinstance(cxjg_end, tuple):
                                dqjb_end, jrjb_end = cxjg_end[0], cxjg_end[1]
                                # 修改判断条件，金币小于10就算火爆
                                if jrjb_end < 10:
                                    msg = f"⚠️ 账号【{self.name}】运行异常，今日金币为{jrjb_end}，请打开太平通APP后再试！"
                                    
                                    # 获取火爆推送开关配置
                                    hbtz = middleware.bucketGet('bd_tptconfig', 'hbtz')
                                    if hbtz and hbtz.lower() == 'true':
                                        # 通过多个渠道推送给用户 
                                        try:
                                            if self.user:  # 确保self.user存在
                                                # 对账号名称进行部分隐藏
                                                push_msg = f"🔔账号【{self.name}】运行异常，今日金币为{jrjb_end}，请打开太平通APP后再试！"
                                                
                                                # 通过多个渠道推送
                                                middleware.push('wb', '', self.user, '', push_msg)
                                                middleware.push('tg', '', self.user, '', push_msg) 
                                                middleware.push('qq', '', self.user, '', push_msg)
                                                middleware.push('qb', '', self.user, '', push_msg)
                                                middleware.push('wx', '', self.user, '', push_msg)
                                                
                                        except Exception as e:
                                            print(f"通知用户失败: {e}")
                                    
                                    # 如果当前操作者不是账号所有者，也通知当前操作者
                                    if sender.getUserID() != self.user:
                                        sender.reply(msg)
                                    
                                    sender.reply(f'🎉运行完成: {self.name}\n💰今日金币: {jrjb_end}(账号火爆)\n💰当前金币: {dqjb_end}')
                                    return self.name, '火爆'
                            sender.reply(f'🎉运行完成: {self.name}\n💰今日金币: {jrjb}\n💰当前金币: {dqjb}')
                            return self.name, jrjb, dqjb

                    if self.llzx >= 14 and self.hyyd >= 6:
                        sender.reply(f'🎉运行完成: {self.name}\n💰今日金币: {jrjb}\n💰当前金币: {dqjb}')
                        return self.name, jrjb, dqjb

                    elif a >= 3:
                        sender.reply(f'🎉运行完成: {self.name}\n💰今日金币: {jrjb}\n💰当前金币: {dqjb}')
                        return self.name, jrjb, dqjb
                    else:
                        self.ydlisturl = f"https://ecustomer.cntaiping.com/informationms/app/config/get/{a}"
                        self.run_yd()
                        a = 0
                        for zl_data in self.zldatas:
                            a += 1
                            time.sleep(random.randint(1, 3))
                            r = self._make_request(
                                'post',
                                "https://ecustomer.cntaiping.com/informationms/app/v2/article/web/coinInfoV2",
                                headers={
                                    'Host': 'ecustomer.cntaiping.com',
                                    'accept': 'application/json', 'x-ac-channel-id': 'KHT',
                                    'x-ac-black-box': 'iWPVl1701438414PrzwzjCHQw1',
                                    'x-ac-mc-type': 'gateway.user',
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6309092b) XWEB/9105 Flue',
                                    'x-ac-token-ticket': '',
                                    'content-type': 'application/json',
                                    'Origin': 'https://ecustomercdn.itaiping.com',
                                    'Sec-Fetch-Site': 'cross-site',
                                    'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                                    'Referer': 'https://ecustomercdn.itaiping.com/',
                                    'Accept-Language': 'zh-CN,zh;q=0.9'
                                },
                                json=zl_data
                            )
                            success = r.json().get('success', None)
                            if success:
                                pass
                            else:
                                return False
                        self.zldatas = []
                        if self.queryList() is True:
                            self.getAllCoins()
                        continue
                else:
                    sender.reply(f'🔔{self.name}: 运行任务时异常\n🔔{sign}')
                    return self.name, sign
            
            # 在运行完成后，添加授权到期检查
            try:
                # 检查授权时间
                if self.sqsj:
                    sqsj_date = datetime.strptime(self.sqsj, "%Y-%m-%d")
                    now = datetime.now()
                    days_left = (sqsj_date - now).days
                    
                    # 如果剩余天数小于等于3天
                    if 0 <= days_left <= 3:
                        msg = f"⚠️ 账号【{self.name}】授权即将到期!\n剩余时间: {days_left}天\n到期时间: {self.sqsj}\n请及时续费以免影响使用"
                        
                        # 只通知用户
                        if self.user:
                            try:
                                user_sender = middleware.Sender(self.user)
                                user_sender.reply(msg)
                            except:
                                pass
                                
                    elif days_left < 0:
                        msg = f"⚠️ 账号【{self.name}】授权已经过期!\n到期时间: {self.sqsj}\n请及时续费以继续使用"
                        
                        # 只通知用户
                        if self.user:
                            try:
                                user_sender = middleware.Sender(self.user)
                                user_sender.reply(msg)
                            except:
                                pass
                                
            except Exception as e:
                print(f"检查授权到期时发生错误: {e}")
            
            sender.reply(f'🎉运行完成: {self.name}\n💰今日金币: {jrjb}\n💰当前金币: {dqjb}')
            return self.name, jrjb, dqjb
            
        except Exception as e:
            sender.reply(f'🔔{self.name}: 运行任务时异常\n🔔{e}')
            return self.name, e


if __name__ == '__main__':
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    user = sender.getUserID()
    message = sender.getMessage()
    atm_tpt = ATM_tpt(user, sender)
    if message == '太平上车':
        atm_tpt.tpsc()
    elif message == '太平管理':
        atm_tpt.tpgl()
    elif message == '太平查询':
        atm_tpt.tpcx()
    elif message == '太平运行':
        if sender.isAdmin():
            atm_tpt.tpyx()
    elif message == '太平配置':
        if sender.isAdmin():
            atm_tpt.tppz()
    elif message == '太平教程':
        jcurl = middleware.bucketGet('bd_tptconfig', 'jcurl')
        if jcurl == '':
            jcurl = 'https://www.yuque.com/yuqueyonghulzdzov/fuzugi/xvy3lp28apxnpvoq?singleDoc#'
        
        sender.reply(f"""=====太平通使用教程=====
验证码登录和抓包登录二选一
💰 收益说明:
- 每天约100金币 ≈ 1RMB
- 可兑换话费、e卡、会员等

📖 详细教程: {jcurl}

🔑 常用指令:
- 太平上车: 添加账号
- 太平管理: 管理账号
- 太平查询: 查询收益
========================""")
    elif message == '太平版本':
        if sender.isAdmin():
            sender.reply(
                f"""=====太平通插件信息=====
📌 当前版本: V6.60

🆕 更新内容:
• 支持批量授权用户
• 新增火爆推送通知
• 新增授权过期提醒
• 新增定时检测功能
• 支持积分开通功能
• 新增代理IP功能
• 修复验证码登录

📱 用户指令:
• 太平上车: 添加账号
• 太平管理: 管理账号
• 太平查询: 查询收益

⚙️ 管理员指令:
• 太平配置: 插件配置
• 太平运行: 一键运行
• 太平授权: 账号授权
• 太平检测: 授权过期检测
========================""")
    elif message == '太平授权':
        if sender.isAdmin():
            atm_tpt.tpsq()
    elif message == '太平检测':
        if sender.isAdmin():
            atm_tpt.tpjc()
    else:
        pass
        exit(0)
