
# [title: app_甬派]
# [author: 601712460]
# [pin: true]
# [version: 0]
# [class: 工具类]
# [rule: ^甬派登陆$]
# [rule: ^甬派登录$]
# [rule: ^甬派签到$]
# [rule: ^甬派管理$]
# [rule: ^甬派超管$]
# [rule: ^甬派配置$]
# [rule: ^ypfk$]
# [disable:true]
# [public: true]
# [admin: false]
# [cron: 12 9 * * *]
# [icon: http://www.cnnb.com.cn/favicon.ico]
# [service: -]
# [description: 甬派，自动阅读，自动抽奖，自动提现支付宝，设置收费模式韭菜登陆认授权一个月，到期续费！需要重新安装依赖，运行【一键安装依赖】插件！]
# =======================
# 脚本及其中涉及的任何解锁和解密分析脚本，仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断。 您必须在下载后的24小时内从计算机或手机中完全删除此脚本

import re
import json
import string
import time
import uuid
import random
import requests
import hashlib
from datetime import datetime, timedelta
from urllib.parse import quote,urlparse,parse_qs

import hook
import middleware
import execjs

    
attr_arr = [
            {
                "title": "手机号",
                "key": "name",
                "timeOut": 60000,
                "tip":""
            },
            {
                "title": "密码",
                "key": "pwd",
                "timeOut": 60000,
                "tip":""
            },
            {
                "title": "支付宝姓名",
                "key": "zfb_name",
                "timeOut": 60000,
                "tip":""
            },
            {
                "title": "支付宝账号",
                "key": "zfb_account",
                "timeOut": 60000,
                "tip":""
            },
            {
                "title": "设备ID",
                "key": "deviceId",
                "timeOut": 60000,
                "tip":"抓包ypapp.cnnb.com.cn下请求头中的【deviceid】，真实设备id必须填写，否则阅读/点赞/分享文章不会成功"
            },
            {
                "title": "是否禁用账号（y/n）",
                "key": "disable",
                "timeOut": 60000,
                "tip":""
            }

        ]


class ACCOUNT:
    def __init__(self):
        self.bucket =  f"{tool.plugin_pre}conf"
        self.common_bucket= f"vhook_common"
        self.conf={
            "paid": self.bucketGet(self.bucket, "paid","n"),
            "fee": self.bucketGet(self.bucket, "fee" ,0),
            "proxy_status":self.bucketGet(self.bucket, "proxy_status", "0"),
            "qr_code":self.bucketGet(self.bucket, "qr_code", ""),
            "delay":self.bucketGet(self.bucket, "delay","10"),
            
            "ocr_host":self.bucketGet(self.common_bucket, "ocr_host", ""),
            "proxy":self.bucketGet(self.common_bucket, "proxy", ""),
            "proxy_api":self.bucketGet(self.common_bucket, "proxy_api", "0"),
            
            "sync_ql":self.bucketGet(self.bucket,"sync_ql", "n"),
            "env_name":self.bucketGet(self.bucket,"env_name", ""),
            "host":self.bucketGet(self.bucket, "host", "n"),
            "client_id":self.bucketGet(self.bucket, "client_id", ""),
            "client_secret":self.bucketGet(self.bucket, "client_secret", ""),
            "tip":self.bucketGet(self.bucket, "tip",""),
        }
        
        
        
    def bucketGet(self,bucket,key,value):
        return tool.bucketGet(bucket,key) or value
    
    def edit_conf(self):
        proxy_map ={
            "0":"关闭",
            "1":"代理池",
            "2":"代理api"
        }
        status_map={
            "y":"已开启",
            "n":"已关闭"
        }
        options = [
            {
                "text": "收费开关",
                "bucket": self.bucket,
                "key": "paid",
                "value": status_map[self.bucketGet(self.bucket,"paid","n")],
                "tips": "是否收费（y：是，n：否）"
            },
            {
                "text": "收费金额(元/月)",
                "bucket": self.bucket,
                "key": "fee",
                "value": self.bucketGet(self.bucket,"fee", "0"),
                "tips": "收费金额（单位：元，例如：0.3）"
            },
            {
                "text": "微信机器人收款码",
                "bucket": self.bucket,
                "key": "qr_code",
                "value": self.bucketGet(self.bucket,"qr_code",""),
                "tips": "微信机器人收款码图片链接（公网地址url）"
            },
            {
                "text": "邀请入口",
                "bucket": self.bucket,
                "key": "invited",
                "value": self.bucketGet(self.bucket,"invited",""),
                "tips": "邀请入口"
            },
            {
                "text": "运行间隔",
                "bucket": self.bucket,
                "key": "delay",
                "value": self.bucketGet(self.bucket,"delay", "10"),
                "tips": "运行间隔（默认10秒），单位：秒，输入数字即可"
            },
            {
                "text": "代理模式",
                "bucket": self.bucket,
                "key": "proxy_status",
                "value": proxy_map[self.bucketGet(self.bucket,"proxy_status","0")],
                "tips": "请输入代理模式序号\n0、关闭代理\n1、代理池\n2、代理api"
            },
            {
                "text": "代理池",
                "bucket": self.common_bucket,
                "key": "proxy",
                "value": self.bucketGet(self.common_bucket,"proxy", ""),
                "tips": "代理池地址"
            },
            {
                "text": "代理api",
                "bucket": self.common_bucket,
                "key": "proxy_api",
                "value": self.bucketGet(self.common_bucket,"proxy_api","") ,
                "tips": "代理池地址"
            },
            {
                "text": "滑块接口地址",
                "bucket": self.common_bucket,
                "key": "ocr_host",
                "value": self.bucketGet(self.common_bucket,"ocr_host",""),
                "tips": "搭建的ddddocr地址"
            },
            {
                "text": "是否同步青龙",
                "bucket": self.bucket,
                "key": "sync_ql",
                "value": status_map[self.bucketGet(self.bucket,"sync_ql", "n")],
                "tips": "是否同步青龙（y：是，n：否）"
            },
            {
                "text": "青龙变量名",
                "bucket": self.bucket,
                "key": "env_name",
                "value": self.bucketGet(self.bucket,"env_name", ""),
                "tips": "青龙变量名"
            },
            {
                "text": "青龙地址",
                "bucket": self.bucket,
                "key": "host",
                "value": self.bucketGet(self.bucket,"host",""),
                "tips": "青龙地址"
            },
            {
                "text": "青龙client_id",
                "bucket": self.bucket,
                "key": "client_id",
                "value": self.bucketGet(self.bucket,"client_id", ""),
                "tips": "青龙client_id"
            },
            {
                "text": "青龙client_secret",
                "bucket": self.bucket,
                "key": "client_secret",
                "value": self.bucketGet(self.bucket,"client_secret", ""),
                "tips": "青龙client_secret"
            },
            {
                "text": "小尾巴",
                "bucket": self.bucket,
                "key": "tip",
                "value": self.bucketGet(self.bucket,"tip", ""),
                "tips": "登陆小尾巴 可自定义添加"
            }
        ]
            
        content = "配置如下，请在【60】秒内输入对应序号编辑（q:退出）：\n"
        for i, option in enumerate(options, start=1):
            content += f"{i}、{option['text']}：{option['value']}\n"
        content+=f"\n------\n插件版本：V{tool.plugin_ver}"
        tool.replyMsg(content)

        value = tool.sender.listen(60000)
        if not value or value == "q" or value == "error":
            tool.replyMsg("已退出！")
            exit()

        option = options[int(value) - 1]
        if option:
            tool.replyMsg(f"请输入{option['tips']}：")
            value = tool.sender.listen(60000)
            if not value or value == "q" or value == "error":
                tool.replyMsg("已退出！")
                exit()
            tool.bucketSet(option['bucket'],option['key'],value)
            tool.sender.breakIn(tool.msg)
        else:
            tool.replyMsg("请输入正确的序号")
            tool.sender.breakIn(tool.msg)

    def client_qinglong(self):
        if not self.conf['host'] or not self.conf['client_id'] or not self.conf['client_secret']:
            tool.replyMsg("青龙配置有误，请联系管理员正确配置！")
            exit()
        ql={
            "name":"ql",
            "host":self.conf['host'],
            "client_id":self.conf['client_id'],
            "client_secret":self.conf['client_secret']
        }
        tool.log_info(ql)
        tql = hook.QL(ql)
        if not tql.token:
            tool.replyMsg("青龙配置有误，请联系管理员正确配置！")
            exit()
        return tql

    def setVal(self, item, attr):
        print(self)
        tool.replyMsg(f"{tool.plugin_name}-请输入{attr['title']}({attr['tip']})：")
        value = tool.sender.listen(attr['timeOut'])
        tool.log_info(f"{attr['key']}==={value}")
        if not value or value == "error":
            tool.replyMsg("输入有误/超时，已退出！")
            exit()
        if value == "q":
            tool.replyMsg("已退出！")
            exit()
        item[attr['key']] = value
        return True
    
    def auth_time(self,timestamp,days):
        future_date = timestamp + timedelta(days=days)
        formatted_date = future_date.strftime("%Y-%m-%d")
        return formatted_date


    def add_or_update(self,acc,env_name=None):
        bucket = f"{tool.plugin_pre}{tool.imType}"
        user_str = tool.bucketGet(bucket, tool.userId)
        user_arr = json.loads(user_str) if user_str else None
         # 获取当前时间
        now = datetime.now()
        if not user_arr:
            user_acc = {
                "userId": str(acc['userId']),
                "token": acc['token'],
                "name": acc['name'],
                "disable":"n",
                "expire": self.auth_time(now,30)
            }
            tool.bucketSet(bucket, tool.userId, json.dumps([user_acc]))   
            tool.log_info(f"新增账号【{tool.hide_phone_number(acc['name'])}】成功✅")
            if env_name:
                self.sync_ql(user_acc,env_name)  
            return 1
        else:
            # 查找是否已有相同 userId 的记录
            exit = False
            for index,item in enumerate(user_arr):
                if str(item['userId']) == str(acc['userId']):
                    exit = True
                    tool.log_info(f"更新---------")
                    item['token'] = acc['token']
                    tool.log_info(f"更新账号【{tool.hide_phone_number(acc['name'])}】成功✅")
                    tool.bucketSet(bucket, tool.userId, json.dumps(user_arr))
                    if env_name:
                        self.sync_ql(item,env_name)
                    break
            if not exit:
                tool.log_info(f"新增---------")
                user_acc = {
                    "userId": str(acc['userId']),
                    "token": acc['token'],
                    "name": acc['name'],
                    "disable":"n",
                    "expire": self.auth_time(now,30)
                }
                user_arr.append(user_acc)
                tool.log_info(json.dumps(user_arr))
                tool.bucketSet(bucket, tool.userId, json.dumps(user_arr))
                tool.log_info(tool.bucketGet(bucket, tool.userId))
                tool.log_info(f"新增账号【{tool.hide_phone_number(acc['name'])}】成功✅")
                if env_name:
                    self.sync_ql(user_acc,env_name)  
                return 1

            
    def sync_ql(self, acc,env_name):
        envs_res = self.tql.envGet(env_name)
        if envs_res['code'] != 200:
            tool.replyMsg("获取环境变量失败，请联系管理员")
            return
        envs = envs_res.get('data', [])
        user_env = next((item for item in envs if item.get('remarks') == acc['userId']), None)
        if user_env:
            # 更新已有的环境变量
            data = {
                'id': user_env.get('id', user_env.get('_id')),
                'name': env_name,
                'value': f"@@{acc['cookie']}",
                'remarks': acc['userId'],
            }
            update_res = self.tql.envUpdate(json.dumps(data))
            tool.log_info(f"青龙更新变量结果===>{update_res}")
        else:
            # 添加新的环境变量
            data = [{
                'name': env_name,
                'value': f"@@{acc['cookie']}",
                'remarks': str(acc['userId']),
            }]
            add_res = self.tql.envSet(json.dumps(data))
            tool.log_info(f"青龙新增变量结果===>{add_res}")

                    
    # 新增账号信息
    def addCount(self,value=None):
        if tool.user_can_add():
            item = {}
            go = True
            for attr in attr_arr:
                if attr['key'] == "disable":
                    item['disable'] = "n"
                    continue
                if not self.setVal(item,attr):
                    go = False
                    break
            if not go:
                tool.log_info("数据配置有误，已退出！")
                return tool.replyMsg("数据配置有误，已退出！")
            item['expire'] = self.auth_time(datetime.now(),30)
            item_arr = []
            item_str = middleware.bucketGet(f"{tool.plugin_pre}{tool.imType}", tool.userId)
            if item_str:
                item_arr = json.loads(item_str)
            item_arr.append(item)
             # 扣除登陆费用 
            tool.update_user_balance()
            middleware.bucketSet(f"{tool.plugin_pre}{tool.imType}", tool.userId, json.dumps(item_arr))
            tool.replyMsg("账号添加成功！")
            item['push_user_id'] = tool.userId
            item['push_im_type'] = tool.imType
            item['index'] = 1
            item['total'] = 1
            TASK(0,item).run()
        
    
    def randomUuid(self):
        return hex(int(random.random() * 2147483648)).replace("0x", "")

    # 编辑账号信息
    def editCount(self, item_arr, no):
        item = item_arr[no]
        content = f"请在【2分钟】内输入 序号，编辑对应的属性（q：保存并退出）"
        content += f"\n--------------------"
        content += f"\n输入数字：0 删除此账号！"
        content += f"\n--------------------"
        for index, attr in enumerate(attr_arr):
            content += f"\n{index + 1}.【{attr['title']}】：{tool.hide_phone_number(item.get(attr['key']))}"
        tool.replyMsg(content)
        value = tool.sender.listen(120000)
        if value == "q" or value == "error" or value == "Q":
            middleware.bucketSet(f"{tool.plugin_pre}{tool.imType}", tool.userId, json.dumps(item_arr))
            return tool.sender.breakIn("甬派管理")
        if not value.isdigit():
            return self.editCount(item_arr, no)
        if 0 < int(value) <= len(attr_arr):
            attr = attr_arr[int(value) - 1]
            if self.setVal(item, attr):
                item_arr[no] = item
                self.editCount(item_arr, no)
        elif value == "0":
            item_arr.pop(no)
            if len(item_arr) == 0:
                # tool.pushMsg(f"{tool.plugin_pre}{tool.imType},{tool.userId}")
                middleware.bucketDel(f"{tool.plugin_pre}{tool.imType}", tool.userId)
            else:
                middleware.bucketSet(f"{tool.plugin_pre}{tool.imType}", tool.userId, json.dumps(item_arr))
            return tool.replyMsg(f"已删除第{no + 1}个账号信息！请重新发送：甬派管理 ！")
        else:
            return self.editCount(item_arr, no)
        
    def accoount_manager_all(self):
        tool.log_info("管理员-账号管理")
        plat_msg = "请输入要查看的用户所在的平台序号："
        platformArr = tool.platformArr()
        for index,plat in enumerate(platformArr):
            plat_msg += f"\n{index+1}、{plat['name']}（{plat['imType']}）"
        tool.replyMsg(plat_msg)
        value = tool.sender.listen(60000)
        if not value or value.casefold() == "q":
            tool.replyMsg("输入有误，已退出！")
        elif value.isdigit() and 0 < int(value) <= len(platformArr):
            self.editCount(platformArr, int(value) - 1)
        else:
            tool.replyMsg(f"[{tool.plugin_name}]:输入有误,请重新发送:甬派管理，并输入正确的序号！")

    # 账号管理
    def accoount_manager(self):
        tool.log_info("账号管理")
        item_str = middleware.bucketGet(f"{tool.plugin_pre}{tool.imType}", tool.userId)
        if not item_str or item_str == "":
            self.addCount()
            exit(1)
        item_arr = json.loads(item_str)
        content = f"[{tool.plugin_name}]请选择要账号查看详情：（0增加， q退出）\n"
        for index, item in enumerate(item_arr):
            tool.log_info(item)
            status =  "禁用" if item['disable']=="y" else "启用"
            item['expire'] = item['expire'] if "expire" in item else self.auth_time(datetime.now(),30)
            content = "".join([content, f"\n{index + 1}、{tool.hide_phone_number(item['name'])} ｜{status}｜{item['expire']}"])
        tool.bucketSet(f"{tool.plugin_pre}{tool.imType}", tool.userId, json.dumps(item_arr))
        tool.replyMsg(content)
        value = tool.sender.listen(60000)
        if not value or value.casefold() == "q":
            tool.replyMsg("输入有误，已退出！")
        elif value == "0":
            self.addCount()
        elif value.isdigit() and 0 < int(value) <= len(item_arr):
            self.editCount(item_arr, int(value) - 1)
        else:
            tool.replyMsg(f"[{tool.plugin_name}]:输入有误,请重新发送:甬派管理，并输入正确的序号！")

    def cron_account_arr(self):
        account_arr = []
        for plat in tool.platformArr():
            p = plat["platform"]
            user_id_arr = tool.bucketAllKeys(p)
            if not user_id_arr:
                continue
            for index, user_id in enumerate(user_id_arr):
                user_data_str = tool.bucketGet(p, user_id)
                if not user_data_str or user_id == '':
                    continue
                user_data_arr_temp = json.loads(user_data_str)
                for n, account_data in enumerate(user_data_arr_temp):
                    account_data["push_user_id"] = user_id
                    account_data["push_im_type"] = plat["imType"]
                    account_data['index'] = n + 1
                    account_data['total'] = len(user_data_arr_temp)
                    account_arr.append(account_data)
        return account_arr

    def account_task(self, item, no):
        print(self)
        read = TASK(no,item)
        # time.sleep(2)  # 延迟两秒
        read.run()


class TASK:
    def __init__(self,index,account):
        self.index = index
        self.name = account.get('name', None)
        self.pwd = account.get('pwd', None)
        self.zfb_name = account.get('zfb_name', None)
        self.zfb_account = account.get('zfb_account', None)
        self.deviceId = account.get('deviceId', None)
        self.model = self.generate_random_device()['model']
        self.user_id = None
        self.nick_name = None
        self.ua = None
        self.token = None
        self.query_token = None
        self.jwtToken = None
        self.news_id = None
        self.lottery_id = None
        self.lottery_cookie = None
        self.consumerId = None
        self.wdata = ""
        self.msg = ""
        self.push_user_id = account.get("push_user_id",None)
        self.push_im_type = account.get("push_im_type",None)
         # 插件配置
        self.conf = {
            "paid": tool.bucketGet(f"{tool.plugin_pre}conf", "paid") or "n",
            "fee": tool.bucketGet(f"{tool.plugin_pre}conf", "fee") or 0,
            "qr_code":tool.bucketGet(f"vhook_common", "qr_code") or "",
            "invited":tool.bucketGet(f"{tool.plugin_pre}conf", "invited") or "n",
            "proxy_status":tool.bucketGet(f"{tool.plugin_pre}conf", "proxy_status") or "n",
            "proxy":tool.bucketGet(f"{tool.plugin_pre}conf", "proxy") or "",
            "proxy_api":tool.bucketGet(f"{tool.plugin_pre}conf", "proxy_api") or "",
            "ocr_host":tool.bucketGet(f"{tool.plugin_pre}conf", "ocr_host") or None,
            "tip":tool.bucketGet(f"{tool.plugin_pre}conf", "tip") or "",
        }
        
    
    def get_proxies(self): 
        if self.conf['proxy_status'] == "1":
            res = self.conf['proxy']
            self.log_info(f"-------使用代理池-------{res}")  
            proxy = {
                    "http": f"{res}",
                    "https": f"{res}",
                    }
        elif self.conf['proxy_status'] == "2":
            res = requests.get(self.conf['proxy_api']).text
            if "先添加白名单" in res:
                self.log_info(f"【{tool.plugin_name}】提示: 代理api：{self.conf['proxy_api']},提取失败！原因：{res}")
                exit(0)
            self.log_info(f"提取代理api结果：{res}")
            if "@" in res:  
                proxy = {
                    "http": f"http://{res.split('@')[0]}@{res.split('@')[1]}",
                    "https": f"https://{res.split('@')[0]}@{res.split('@')[1]}"
                    }  
            else:   
                proxy = {
                    "http": f"http://{res.split(':')[0]}:{res.split(':')[1]}",
                    "https": f"https://{res.split(':')[0]}:{res.split(':')[1]}"
                    }
        else:
            self.log_info(f"-------使用直连模式-------")
            return None
        return proxy

    @staticmethod
    def generate_device_code():
        device_code = ''
        chars = 'abcdef0123456789'
        for _ in range(16):
            device_code += random.choice(chars)
        return device_code
        
    def generate_uuid(self):
        return str(uuid.uuid4())

    
    def log_info(self, msg):
        tool.log_info(f"用户{self.index}【{tool.hide_phone_number(self.name)}】：{msg}")
        
    def log_err(self, msg):
        tool.log_err(f"用户{self.index}【{tool.hide_phone_number(self.name)}】：{msg}")
    
    def pushMsg(self, msg):
        if tool.chatId:
            tool.pushMsg(None, tool.chatId, self.push_im_type, "", msg)
        else:
            tool.pushMsg(self.push_user_id, None, self.push_im_type, "", msg)

    def generate_random_device(self):
        device_id = self.generate_device_id()
        models = [
            "M1903F2A", "M2001J2E", "M2001J2C", "M2001J1E", "M2001J1C",
            "M2002J9E", "M2011K2C", "M2102K1C", "M2101K9C", "2107119DC",
            "2201123C", "2112123AC", "2201122C", "2211133C", "2210132C",
            "2304FPN6DC", "23127PN0CC", "24031PN0DC", "23090RA98C",
            "2312DRA50C", "2312CRAD3C", "2312DRAABC", "22101316UCP",
            "22101316C"
        ]
        model = self.get_random_element(models)
        return {"deviceId": device_id, "model": model}

    def get_random_element(self,arr):
        return random.choice(arr)

    def generate_device_id(self,length=16):
        characters = string.ascii_lowercase + string.digits
        return ''.join(random.choice(characters) for _ in range(int(length)))

    def is_today(self,datetime_str, datetime_format="%Y-%m-%d %H:%M:%S"):
        """
        判断给定的时间字符串是否是今天。
        
        :param datetime_str: 时间字符串
        :param datetime_format: 时间字符串的格式，默认为"%Y-%m-%d %H:%M:%S"
        :return: 如果是今天，返回True，否则返回False
        """
        # 将时间字符串转换为日期时间对象
        dt = datetime.strptime(datetime_str, datetime_format)
        # 获取今天的日期
        today = datetime.today().date()
        # 判断日期是否为今天
        return dt.date() == today
        
    def format_cookies(self,cookie_string):
        cookies = cookie_string.split(', ')
        formatted_cookies = [cookie.split(';')[0].strip() for cookie in cookies]
        return '; '.join(formatted_cookies)

        
    def common_get(self,path):
        headers = {
            'system': 'android',
            'version': '30',
            'model': self.model,
            'appversion': '10.1.6',
            'appbuild': '202401111',
            'deviceid': self.deviceId,
            'ticket': self.token,
            'module':"web-member",
            'Authorization':f"Bearer {self.jwtToken}",
            'userid':self.user_id,  
            'accept-encoding': 'gzip',
            'user-agent': 'PLYongPaiProject/10.1.6 (iPhone; iOS 15.4.1; Scale/3.00)',
        }
        res = requests.get(f"https://ypapp.cnnb.com.cn{path}",headers=headers)
        # self.log_info(f"{path} res {res.text}")
        if res.status_code == 200:
            return res.json()
        return None
        
    def login(self):
        now = str(int(time.time() * 1000))
        raw = f'globalDatetime{now}username{self.name}test_123456679890123456'
        sign = hashlib.md5(raw.encode("utf-8")).hexdigest()

        params={
            "username":self.name,
            "password":quote(self.pwd),
            "deviceId":self.deviceId,
            "globalDatetime":int(time.time()*1000),
            "sign":sign
        }
        headers =  {
            'system': 'android',
            'version': '30',
            'model': self.model,
            'appversion': '11.0.0',
            'appbuild': '202407040',
            'deviceid': self.deviceId,
            'ticket': '',
            'accept-encoding': 'gzip',
            'user-agent': 'okhttp/4.9.1',
        }
        # res = requests.get(f"https://ypapp.cnnb.com.cn/yongpai-user/api/login2/local3?username={self.name}&password={quote(self.pwd)}&deviceId=${self.deviceId}&globalDatetime={now}&sign={sign}",headers=headers)
        res = requests.get(f"https://ypapp.cnnb.com.cn/yongpai-user/api/login2/local3",headers=headers,params=params)
        self.log_info(f"local3 res {res.text}")
        if res.status_code == 200:
            rj =res.json()
            if "OK" in rj['message']:
                self.msg += f"\n【登陆检测】：检测通过✅"
                self.msg += f"\n【用户昵称】：{rj['data']['nickname']}"
                self.msg += f"\n【绑定手机】：{tool.hide_phone_number(rj['data']['mobile'])}"
                self.user_id = rj['data']['userId']
                self.query_token = rj['data']['token']
                self.nick_name = rj['data']['nickname']
                self.jwtToken = rj['data']['jwtToken']
                return True
        self.log_info(f"login  {res.text}")
        
    def login_get(self):
        data_string = f"/member/login{{loginName:{self.name},name:{self.nick_name},phone:{self.name},userId:{self.user_id}}}"
        sign = hashlib.md5(data_string.encode("utf-8")).hexdigest()
        params = {
            "userId":self.user_id,
            "loginName":self.name,
            "name":quote(self.nick_name),
            "phone":self.name
            
        }
        headers = {
            'content-type': 'application/json',
            'module': 'web-member',
            'sign': sign,
            'accept-encoding': 'gzip',
            'user-agent': 'okhttp/4.9.1',
        }
        res = requests.get(f"https://ypapp.cnnb.com.cn/web-nbcc/member/login",headers=headers,params=params)
        self.log_info(f"login_get  {res.text}")
        if res.status_code == 200:
            rj =res.json()
            if "OK" in rj['message']:
                self.msg += f"\n【登陆结果】：登陆成功✅"
                self.token = rj['data']
                return True
        return False
    
    def news_list(self):
        res = self.common_get(f"/yongpai-news/api/news/list?channelId=4&currentPage=1&timestamp=0")
        if res:
            for news in res['data']['content']:
                # 条件列表
                conditions = [
                    '转盘' in news.get('keywords', ''),
                    '转盘' in news.get('title', ''),
                    '转盘' in news.get('detailTitle', ''),
                    '转一转' in news.get('detailTitle', ''),
                    '赚' in news.get('detailTitle', ''),
                    '转盘' in news.get('subtitle', '')
                ]
                # 使用 any 函数检查是否有任何一个条件为 True
                if any(conditions):
                    self.msg += f"\n【获取抽奖】：抓取抽奖活动成功✅"
                    self.log_info(f"成功获取抽奖活动：{news['id']}")
                    self.news_id = news['id']
                    return True
        return False
    
    def news_detail(self):
        res = self.common_get(f"/yongpai-news/api/news/detail?newsId={self.news_id}&userId={self.user_id}&deviceId={self.deviceId}")
        self.log_info(f"get_lottery_id  {res}")
        if res and res['data']:
            match = re.search(r'\?id=(\d+)&?', res['data']['body'])
            if match:
                self.lottery_id = re.search(r'\?id=(\d+)&?', res['data']['body']).group(1)
                self.msg += f"\n【抽奖ID】：解析抽奖ID成功✅"
                self.log_info(f"【抽奖ID】：解析抽奖ID成功✅{self.lottery_id}")
                return True
            else:
                self.log_info(f"查找转盘id失败：{res}")
        return False
    
    def task_list(self):
        self.msg += f"\n---------阅读----------"
        path = f"/yongpai-user/api/user/my_level?userId={self.user_id}"
        res = self.common_get(path)
        if not res :
            return
        readFinish = True
        likeFinish = True
        shareFinish = True
        for task in res['data']['scoreRule']:
            self.log_info(f"{task['type']}  {task['dayscore']} {task['usedScore']}")
            self.msg += f"\n{task['type']}：{task['usedScore']}/{task['dayscore']}"
            if task['dayscore']== task['usedScore']:
                continue
            if task['type'] == '阅读新闻':
                readFinish = False
            if task['type'] == '点赞':
                likeFinish = False
            if task['type'] == '分享新闻':
                shareFinish = False
        if not readFinish or not likeFinish or not shareFinish:
            channelIds = [2,20183,20184,4,32]
            count = 1
            read_count = 0 
            like_count = 0 
            share_count = 0 
            for channelId in channelIds:
                article_list_res = self.common_get(f"/yongpai-news/api/news/list?channelId={channelId}&currentPage=1&timestamp=0")
                if not article_list_res:
                    continue
                for index ,article in enumerate(article_list_res['data']['content']):
                    if not self.is_today(article.get('sourcetime',"2024-07-20 00:00:00")):
                        continue
                    if count > 30:
                        break
                    id = article['id']
                    time.sleep(random.randint(1, 2))
                    if not readFinish:
                        read_res = self.common_get(f"/yongpai-news/api/news/detail?newsId={id}&userId={self.user_id}&deviceId={self.deviceId}")
                        if read_res:
                            read_count +=1
                            self.log_info(f"阅读第{count}篇：{res.get('message')}")
                            # self.msg += f"\n阅读文章【{id}】:{read_res.get('message')}"
                    if not likeFinish:
                        time.sleep(random.randint(1, 2))
                        like_res = self.common_get(f"/yongpai-ugc/api/praise/save_news?userId={self.user_id}&newsId={id}&deviceId={self.deviceId}")
                        self.log_info(f"点赞第{count}篇文章【{id}】：{like_res}")
                        if like_res and like_res.get('code') == 0:
                            count  +=1
                            like_count +=1
                            self.log_info(f"点赞获得：{like_res['message']}")
                            # self.msg += f"\n点赞文章【{id}】: {like_res['message']}"
                        else:
                            self.log_info(f"文章【{id}】已点赞")
                    if not shareFinish:
                        time.sleep(random.randint(1, 2))
                        share_res = self.common_get(f"/yongpai-ugc/api/forward/news?userId={self.user_id}&newsId={id}&source=4")
                        self.log_info(f"分享第{count}篇文章【{id}】：{share_res}")
                        if share_res and share_res.get('code') == 0:
                            share_count += 1
                            self.log_info(f"分享获得：{share_res['data']}积分")
                            # self.msg += f"\n分享文章【{id}】:获得{share_res['data']}积分"
                        else:
                            self.log_info(f"文章【{id}】已分享")
            self.msg += f"\n 阅读成功：{read_count}篇"
            self.msg += f"\n 点赞成功：{like_count}篇"
            self.msg += f"\n 分享成功：{share_count}篇"
        
    def lottery_Login_get(self):
        params ={
            "userId":self.user_id,
            "dbredirect":f"https://92722.activity-12.m.duiba.com.cn/hdtool/index?id={self.lottery_id}&dbnewopen"
        }
        headers =  {
            'accept-encoding': 'gzip',
            'user-agent': 'okhttp/4.9.1',
        }
        url = "https://ypapp.cnnb.com.cn/yongpai-user/api/duiba/autologin?${url}"
        res = requests.get(url,headers=headers, params=params)
        self.log_info(f"lottery_Login_get {res.text}")
        if res.status_code == 200:
            rj = res.json()
            if "OK" in rj['message']:
                headers = {
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'x-requested-with': 'io.dcloud.H55BDF6BE',
                    'sec-fetch-site': 'none',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-user': '?1',
                    'sec-fetch-dest': 'document',
                    'accept-encoding': 'gzip, deflate',
                    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                }
                res = requests.get(rj['data'],headers=headers,allow_redirects=False)
                self.lottery_cookie = self.format_cookies(res.headers['Set-Cookie'])
                self.log_info(f"获取key")
                self.msg += f"\n---------抽奖----------"
                self.key_get(f"https://92722.activity-12.m.duiba.com.cn/hdtool/index?id={self.lottery_id}&dbnewopen&from=login&spm=92722.1.1.1")
                # self.get_key_api(f"https://92722.activity-12.m.duiba.com.cn/hdtool/index?id={self.lottery_id}&dbnewopen&from=login&spm=92722.1.1.1")
                res = self.lottery_post(f"/hdtool/ajaxElement?_={int(time.time()*1000)}",{"hdType":"dev","hdToolId":"","preview":False,"actId":self.lottery_id,"adslotId":""})
                if res and res['success']:
                    self.msg += f"\n【抽奖次数】：{res['element']['freeLimit']}"
                    count = res['element']['freeLimit']
                    self.log_info(count)
                    for no in range(0,1):
                        token_data = {
                            "timestamp":int(time.time()*1000),
                            "activityId":self.lottery_id,
                            "activityType":"hdtool",
                            "consumerId":self.consumerId
                            }
                        res = self.lottery_post(f"/hdtool/ctoken/getTokenNew",token_data)
                        if res and res['success']:
                            token = self.get_token(self.key_str,res['token'])
                            join_data ={
                                "actId":self.lottery_id,
                                "oaId":self.lottery_id,
                                "activityType":"hdtool",
                                "consumerId":self.consumerId,
                                "token":token
                            }
                            self.log_info(f"抽奖参数：{join_data}")
                            res = self.lottery_post(f"/hdtool/doJoin?dpm=92722.3.1.0&activityId={self.lottery_id}&_={int(time.time()*1000)}",join_data)
                            if res and res.get('success'):
                                self.log_info(f"第{no+1}次抽奖：{res}")
                                orderId = res.get('orderId',"2713157983293370443")
                                if not orderId:
                                    continue
                                order_data = {
                                    "orderId":orderId,
                                    "adslotId":""
                                }
                                order_status = 0
                                while order_status == 0:
                                    order_res = self.lottery_post(f"/hdtool/getOrderStatus?_={int(time.time()*1000)}",order_data)
                                    if order_res and order_res['success']:
                                        order_status = order_res.get("result",0)
                                        if order_status == 0:
                                            self.log_info(f"查询订单{orderId}状态：{res.get('message')}")
                                            continue
                                        if order_res['lottery']['type'] == "thanks":
                                            self.msg += f"\n第{no+1}次抽奖：谢谢惠顾"
                                            continue
                                        if order_res['lottery']['type'] == "alipay":
                                            self.log_info(f"获得支付宝红包：{order_res['lottery']['title']}")
                                            self.msg += f"\n第{no+1}次抽奖：{order_res['lottery']['title']}"
                                            url = order_res['lottery']['link']
                                            parsed_url = urlparse(url)
                                            query_params = parse_qs(parsed_url.query)
                                            result = {k: v[0] for k, v in query_params.items()}
                                            recordId= result['recordId']
                                            self.log_info(f"开始提现-{self.zfb_account}")
                                            if self.zfb_account and self.zfb_name:
                                                self.key_get(f"https://92722.activity-12.m.duiba.com.cn/activity/takePrizeNew?recordId={recordId}&dbnewopen")
                                                getToken_res = self.lottery_post(f"/ctoken/getToken.do")
                                                if getToken_res:
                                                    token = self.get_token(self.key_str,getToken_res.get('token'))
                                                    doTakePrize_data={
                                                        "alipay":self.zfb_account,
                                                        "realname":quote(self.zfb_name),
                                                        "recordId":recordId,
                                                        "token":token                                    
                                                    }
                                                    self.log_info(f"提现参数：{doTakePrize_data}")
                                                    res = self.lottery_post(f"/activity/doTakePrize",doTakePrize_data)
                                                    self.log_info(f"提现结果：{res}")
                                                    if res:
                                                        self.log_info(f"自动体现支付宝结果：{res}")
                                                        self.msg += f"\n提现结果：{res.get('message')}"
                            else:
                                self.log_info(f"抽奖失败：{res}")
                                self.msg += f"\n抽奖结果：{res.get('message','未知错误')}"
                else:
                    self.log_info(f"活动异常：{res}")
                
                
                
        
    def key_get(self,url):
        headers = {
             'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
            'x-requested-with': 'io.dcloud.H55BDF6BE',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cookie': self.lottery_cookie
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            time.sleep(2)  # Wait for 2 seconds
            regex = r"consumerId:'(\d+)'"
            match = re.search(regex, res.text)
            if match:
                self.consumerId = match.group(1)
            else:
                self.consumerId = '4136126583'

            self.log_info(f"consumerId {self.consumerId}")
            js_str = """
            function deal(res){
                let code = /<script\\b[^>]*>\s*var([\s\S]*?)<\/script>/.exec(res)[1];
                eval(code)
                key = /var\s+key\s+=\s+'([^']+)';/.exec(getDuibaToken.toString())[1];
                console.log(key)
                return key;
            }
            """
            ctx = execjs.compile(js_str)
            self.key_str = ctx.call("deal", res.text)
            self.log_info(self.key_str)
           

    def js_key(self):
        js_str = """
        function deal(key,res){
            window={}
            let code = /<script\\b[^>]*>\s*var([\s\S]*?)<\/script>/.exec(res)[1];
            eval(code)
            key = /var\s+key\s+=\s+'([^']+)';/.exec(getDuibaToken.toString())[1];
            return window[key];
        }
        """
        res = self.lottery_post(f"/ctoken/getToken.do")
        if res:
            ctx = execjs.compile(js_str)
            return ctx.call("deal",self.key_str, res['token'])



    def get_token(self,key,code):
        js_str = """
        function deal(key,code){
            window={}
            eval(code)
            return window[key];
        }
        """
        ctx = execjs.compile(js_str)
        token =  ctx.call("deal", key,code)
        self.log_info(f"get_token  {token}")
        return token


        
    def lottery_post(self,path,body=None):
        url  = f"https://92722.activity-12.m.duiba.com.cn{path}"
        headers = {
            'accept': 'application/json',
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36 agentweb/4.0.2  UCBrowser/11.6.4.950 yongpai',
            'x-requested-with': 'XMLHttpRequest',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://92722.activity-12.m.duiba.com.cn',
            'cookie': self.lottery_cookie,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': "https://92722.activity-12.m.duiba.com.cn/hdtool/index?id=${lotteryId}&dbnewopen&from=login&spm=92722.1.1.1",
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        res = requests.post(url,headers=headers,data=body)
        self.log_info(f"lottery_post {path} res  {res.text}")
        if res.status_code == 200:
            rj = res.json()
            return rj
        return None
            
    def user_info(self):
        res = self.common_get(f"/yongpai-user/api/user/client?userId={self.user_id}&deviceId={self.deviceId}&token={self.query_token}") 
        if res:
            self.msg += f"\n---------资产----------"
            self.msg += f"\n【当前积分】：{res['data']['score']}"
    

    
    def run(self):  
        self.msg = f"【账号备注】：{tool.hide_phone_number(self.name)}" 
        self.login()
        self.login_get()
        if self.news_list():
            self.news_detail() 
            self.task_list()
            self.lottery_Login_get()
            self.user_info()
        else:
            self.msg += f"\n【获取抽奖】：抓取抽奖活动失败❌，请改日再来"
            
        self.pushMsg(self.msg)

if __name__=="__main__":
    sender = middleware.Sender(middleware.getSenderID())
    plugin={
        "key":"vhook_yongpai_",
        "name":sender.getPluginName(),
        "ver": sender.getPluginVersion(),
        "sender":sender,
    }
    tool = hook.TOOL(sender,plugin)
    account = ACCOUNT()
    if tool.msg == "甬派超管" and tool.isAdmin:
        tool.account_manger_admin()
        exit(0)
    if tool.msg == '甬派配置':
        if tool.isAdmin:
            account.edit_conf()
        exit(1)
    if tool.msg == '甬派管理':
        account.accoount_manager()
        exit(1)
    if tool.msg == '甬派登陆' or tool.msg == "甬派登录":
        account.addCount()
        exit()
    if tool.imType == "fake" :
        user_data_arr = account.cron_account_arr()
    elif tool.msg == "ypfk" and tool.isAdmin:
        user_data_arr = account.cron_account_arr()
    else:
        user_str = middleware.bucketGet(f"{tool.plugin_pre}{tool.imType}", tool.userId)
        if not user_str or user_str == "":
            account.addCount()
            exit(1)
        user_data_arr = json.loads(user_str)
        for i, user_data in enumerate(user_data_arr):
            user_data["push_user_id"] = tool.userId
            user_data["push_im_type"] = tool.imType
            user_data['index'] = i + 1
            user_data['total'] = len(user_data_arr)
    if len(user_data_arr) == 0:
        tool.replyMsg("账号全部被禁用，请启用后再查询！")
        exit(0)
    tool.log_info(f"开始运行，共{len(user_data_arr)}个账号")
    tool.replyMsg("任务开始执行，请稍后......")
    for index, user_data in enumerate(user_data_arr,start=1):
        current = account.auth_time(datetime.now(),0)
        if user_data['disable'] !="n":
            tool.log_info(f"**********{tool.plugin_name} 账号禁用状态*********跳过执行")
            continue
        if(user_data['expire']<=current):
            tool.replyMsg(f"**********{tool.plugin_name}过期提醒*********\n账号：{user_data['name']}：已过期！请重新登陆")
            continue
        TASK(index,user_data).run()
        if index > 1:
            tool.log_info(f"延迟运行{account.conf['delay']}秒")
            time.sleep(int(account.conf['delay']))  # 延迟两秒
    exit(0)
        