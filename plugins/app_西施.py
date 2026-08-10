
# [title: app_西施]
# [author: 601712460]
# [pin: true]
# [version: 0]
# [class: 工具类]
# [rule: ^西施登陆$]
# [rule: ^西施登录$]
# [rule: ^西施签到$]
# [rule: ^西施管理$]
# [rule: ^西施超管$]
# [rule: ^西施配置$]
# [rule: ^xishifk$]
# [disable:true]
# [public: true]
# [admin: false]
# [cron: 0 8 * * *]
# [icon: https://img.tmuyun.com/assets/20240407/1712463980445_6612206c79f6be6b2230e399.png
# [service: -]
# [description: 西施眼（https://app.tmuyun.com/webChannels/invite?inviteCode=WUHRL6&tenantId=34&accountId=66a0faeb6744794e97a729a4），自动阅读，自动抽奖，自动提现，设置收费模式韭菜登陆认授权一个月，到期续费！需要重新安装依赖，运行【一键安装依赖】插件！]
# =======================
# 脚本及其中涉及的任何解锁和解密分析脚本，仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断。 您必须在下载后的24小时内从计算机或手机中完全删除此脚本

import json
import time
import hmac
import uuid
import base64
import random
import requests
import hashlib
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from datetime import datetime, timedelta
from urllib.parse import quote, urlparse,parse_qs

import hook
import middleware


def qls():
    if middleware.version()['sn'] > "2.6.5":
        qls = []
        ql_id_arr = tool.bucketAllKeys("qls")
        if not ql_id_arr:
            return []
        for ql_id in ql_id_arr:
            value = tool.bucketGet("qls", ql_id)
            if value:
                qls.append(json.loads(value))
        return qls
    else:
        qls = tool.bucketGet("qinglong", "QLS")
        if qls:
            return json.loads(qls)
        return []
    
attr_arr =  [
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
            
            
            "ocr_host":self.bucketGet(self.common_bucket, "ocr_host", ""),
            "qr_code":self.bucketGet(self.bucket, "qr_code", ""),
            "proxy":self.bucketGet(self.bucket, "proxy", "0"),
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
        if not tool.conf['host'] or not tool.conf['client_id'] or not tool.conf['client_secret']:
            tool.replyMsg("青龙配置有误，请联系管理员正确配置！")
            exit()
        ql={
            "name":"ql",
            "host":tool.conf['host'],
            "client_id":tool.conf['client_id'],
            "client_secret":tool.conf['client_secret']
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
            content += f"\n{index + 1}.【{attr['title']}】：{tool.hide_phone_number(item[attr['key']])}"
        tool.replyMsg(content)
        value = tool.sender.listen(120000)
        if value == "q" or value == "error" or value == "Q":
            middleware.bucketSet(f"{tool.plugin_pre}{tool.imType}", tool.userId, json.dumps(item_arr))
            return tool.replyMsg("已退出！")
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
            return tool.replyMsg(f"已删除第{no + 1}个账号信息！请重新发送：西施管理 ！")
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
            tool.replyMsg(f"[{tool.plugin_name}]:输入有误,请重新发送:西施管理，并输入正确的序号！")

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
            tool.replyMsg(f"[{tool.plugin_name}]:输入有误,请重新发送:西施管理，并输入正确的序号！")

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
        self.user_id = None
        self.ua = None
        self.common_ua = None
        self.push_user_id = account.get("push_user_id",None)
        self.push_im_type = account.get("push_im_type",None)
        self.msg = ""
        self.host = "https://vapp.tmuyun.com"
        self.key = "nNo7464SYE6kUHjL"
        self.tenantId = "34"
        self.clientId = "50"
        self.signatureSalt = "FR*r!isE5W"
        self.signature_key = ""
        self.public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXizPqQeXv68i5vqw9pFREsrqiBTRcg7wB0RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXFc+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlTHMlluw4ZYmnOwg+thwIDAQAB
-----END PUBLIC KEY-----"""
        self.code = ""
        self.uuid = None
        self.accountId = None
        self.sessionId = None
        self.device_id = None
        self.id = None
        self.jinhuaAppId = 'uhzfzpj5l78yq6di'
        self.jinhuaKey = '35c782a2'
        self.jinhuaToken = ''
        self.lotteryId = None
        
        self.proxies = self.get_proxies()
    
    def get_proxies(self): 
        if account.conf['proxy_status'] == "1":
            res = account.conf['proxy']
            self.log_info(f"-------使用代理池-------{res}")  
            proxy = {
                    "http": f"{res}",
                    "https": f"{res}",
                    }
        elif account.conf['proxy_status'] == "2":
            res = requests.get(account.conf['proxy_api']).text
            if "先添加白名单" in res:
                self.log_info(f"【{tool.plugin_name}】提示: 代理api：{account.conf['proxy_api']},提取失败！原因：{res}")
                return None
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

    
    def generate_random_ua(self):
        version = "1.7.0"
        uuid_value = str(uuid.uuid4())
        device_ids = [
            "M1903F2A", "M2001J2E", "M2001J2C", "M2001J1E", "M2001J1C",
            "M2002J9E", "M2102K1C", "M2101K9C", "2107119DC", "2201123C",
            "2112123AC", "2201122C", "2211133C", "2210132C", "2304FPN6DC",
            "23127PN0CC", "24031PN0DC", "23090RA98C", "2312DRA50C",
            "2312CRAD3C", "2312DRAABC", "22101316UCP", "22101316C"
        ]
        # 假设clientId是预先定义好的变量，如果未定义，请相应地添加或修改
        deviceId = random.choice(device_ids)
        device = f"Xiaomi {deviceId}"
        os = "Android"
        os_version = "11"
        os_type = "Release"
        app_version = "6.12.0"

        self.ua = f"{os.upper()};{os_version};{self.clientId};{version};1.0;null;{deviceId}"
        self.common_ua = f"{version};{uuid_value};{device};{os};{os_version};{os_type};{app_version}"
        self.uuid = uuid_value
        self.device_id = uuid_value
    
    def get_params(self,url):
        current_time = int(time.time() * 1000)
        uuid = self.generate_uuid()
        print(current_time)
        
        if '?' in url:
            url = url.split('?')[0]

        signature_base = f"{url}&&{self.sessionId}&&{uuid}&&{current_time}&&{self.signatureSalt}&&{self.tenantId}"
        signature = hashlib.sha256(signature_base.encode()).hexdigest()
        
        return {
            "uuid": uuid,
            "time": current_time,
            "signature": signature
        }
    
    def encrypt(self, data):
        public_key = "-----BEGIN PUBLIC KEY-----\n" \
        "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXizPqQeXv68i5vqw9pFREsrqiBTRcg7wB0RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXFc+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlTHMlluw4ZYmnOwg+thwIDAQAB\n" \
        "-----END PUBLIC KEY-----"

        # 解码公钥
        key = RSA.importKey(public_key)

        # 创建RSA对象
        cipher = PKCS1_v1_5.new(key)

        # 进行加密并返回加密后的结果
        encrypted_data = cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def aes_encrypt(self,e, r):
        key = r.encode('utf-8')  # Convert the key to bytes
        data = e.encode('utf-8')  # Convert the plaintext to bytes

        cipher = AES.new(key, AES.MODE_ECB)  # Create a new AES cipher in ECB mode
        padded_data = pad(data, AES.block_size)  # Pad the plaintext to the block size
        encrypted = cipher.encrypt(padded_data)  # Encrypt the padded plaintext

        return base64.b64encode(encrypted).decode('utf-8')  # Return the encrypted data as a base64-encoded string

    
    def get_body(self):
        password_encrypted = self.encrypt(self.pwd)
        
        # 构造原始body字符串，不进行urlencode
        raw_body = f"client_id={self.clientId}&password={password_encrypted}&phone_number={self.name}"
        str_to_sign = f"post%%/web/oauth/credential_auth?{raw_body}%%{self.uuid}%%"
        
        # 使用urllib.parse.quote对密码进行编码，以符合URL标准
        body = f"client_id={self.clientId}&password={quote(password_encrypted)}&phone_number={self.name}"
        
        # 计算HMAC-SHA256签名
        hash_digest = hmac.new(self.signature_key.encode(), str_to_sign.encode(), hashlib.sha256).digest()
        signature = hash_digest.hex()
        
        return {"uuid": self.uuid, "signature": signature, "body": body}
    
    def get_jinhua_params(self,params):
        current_time = int(time.time() * 1000)
        nonce_str = self.generate_uuid()
        
        config = {
            'app_id': self.jinhuaAppId,
            'device_id': self.device_id,
            'nonce_str': nonce_str,
            'source_type': 'app',
            'timestamp': current_time,
            'auth_id': self.accountId,
            'token': self.sessionId
        }
        
        # Update config with params
        config.update(params)
        
        # Sort keys and create the result string
        sorted_keys = sorted(config.keys())
        result = '&&'.join([f"{key}={config[key]}" for key in sorted_keys])
        result += '&&' + self.jinhuaKey
        
        # Generate the signature
        signature = hashlib.sha256(result.encode()).hexdigest()
        
        return {
            "uuid": nonce_str,
            "time": current_time,
            "signature": signature
        }
    
    def common_get(self,path):
        params = self.get_params(path)
        headers = {
            'Connection': 'Keep-Alive',
            'X-TIMESTAMP': str(params['time']),
            'X-SESSION-ID': self.sessionId,
            'X-REQUEST-ID': params['uuid'],
            'X-SIGNATURE': params['signature'],
            'X-TENANT-ID': self.tenantId,
            'X-ACCOUNT-ID': self.accountId,
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip',
            'user-agent': self.common_ua,
        }
        res = requests.get(f"{self.host}{path}",headers=headers)
        if res.status_code == 200:
            return res.json()
        return None
    
    def common_post(self,path,body=None):
        params = self.get_params(path)
        headers = {
            'Connection': 'Keep-Alive',
            'X-TIMESTAMP': str(params['time']),
            'X-SESSION-ID': self.sessionId,
            'X-REQUEST-ID': params['uuid'],
            'X-SIGNATURE': params['signature'],
            'X-TENANT-ID': self.tenantId,
            'X-ACCOUNT-ID': self.accountId,
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'user-agent': self.common_ua,
        }
        res = requests.post(f"{self.host}{path}",headers=headers,data=body)
        if res.status_code == 200:
            return res.json()
        return None
    
    def jihua_get(self,path,body):
        params = self.get_jinhua_params(body)
        headers = {
            'access-type': 'app',
            'access-module': 'study',
            'access-device-id': self.device_id,
            'access-auth-id': self.accountId,
            'access-api-signature': params['signature'],
            'access-nonce-str': params['uuid'],
            'authorization': self.jinhuaToken,
            'access-app-id': self.jinhuaAppId,
            'access-timestamp': str(params['time']),
            'access-api-token': self.sessionId,
            'accept': 'application/json, text/plain, */*',
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36;xsb_yuecheng;xsb_yuecheng;1.7.0;native_app;6.12.0',
            'content-type': 'application/json; charset=UTF-8',
            'origin': 'https://op-h5.cloud.jinhua.com.cn',
            'x-requested-with': 'com.zjonline.zhuji',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://op-h5.cloud.jinhua.com.cn/',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        res = requests.get(f"https://op-api.cloud.jinhua.com.cn{path}",headers=headers)
        if res.status_code == 200:
            return res.json()
        return None
    
    def jihua_post(self,path,body):
        params = self.get_jinhua_params(body)
        headers = {
            'access-type': 'app',
            'access-module': 'study',
            'access-device-id': self.device_id,
            'access-auth-id': self.accountId,
            'access-api-signature': params['signature'],
            'access-nonce-str': params['uuid'],
            'authorization': self.jinhuaToken,
            'access-app-id': self.jinhuaAppId,
            'access-timestamp': str(params['time']),
            'access-api-token': self.sessionId,
            'accept': 'application/json, text/plain, */*',
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36;xsb_zhuji;xsb_zhuji;1.3.2;native_app;6.10.0',
            'content-type': 'application/json; charset=UTF-8',
            'origin': 'https://op-h5.cloud.jinhua.com.cn',
            'x-requested-with': 'com.zjonline.zhuji',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://op-h5.cloud.jinhua.com.cn/',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        res = requests.post(f"https://op-api.cloud.jinhua.com.cn{path}",headers=headers,data=json.dumps(body),proxies=self.proxies)
        if res.status_code == 200:
            return res.json()
        return None
    
    def slide_post(self,body):
        headers = {
             'Content-Type': 'application/json',
        }
        res = requests.post(f"{account.conf['ocr_host']}/capcode",headers=headers, data=json.dumps(body))
        if res.status_code == 200:
            return res.json()
        return None
    


    
    def init(self):
        path = "/api/account/init"
        res = self.common_post(path,None)
        self.log_info(f"【init】：{res}")
        if res:
            if res['code'] == 0:
                self.sessionId = res['data']['session']['id']
                return True
        return False

    def gete_signature_key (self):
        path = f"/web/init?client_id={self.clientId}"
        headers = {
                'Connection': 'Keep-Alive',
                'Cache-Control': 'no-cache',
                'X-REQUEST-ID':str(uuid.uuid4()),
                'Accept-Encoding': 'gzip',
                'user-agent': self.ua,
        }
        res = requests.get(f"https://passport.tmuyun.com{path}",headers=headers)
        self.log_info(f"gete_signature_key=>{res.text}")
        if res.status_code == 200 :
            rj = res.json()
            if rj['code'] == 0:
                self.signature_key = rj['data']['client']['signature_key']
                return True
        return False

    def credential_auth(self):
        path = "/web/oauth/credential_auth"
        params = self.get_body()
        headers = {
            'Connection': 'Keep-Alive',
            'X-REQUEST-ID': params['uuid'],
            'X-SIGNATURE': params['signature'],
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Accept-Encoding': 'gzip',
            'user-agent': self.ua,
        }
        res = requests.post(f"https://passport.tmuyun.com{path}",headers=headers,data=params['body'])
        self.log_info(f"credential_auth=>{res.text}")
        if res.status_code == 200 :
            rj = res.json()
            if rj['code'] == 0:
                self.code = rj['data']['authorization_code']['code']
                return True
        return False
    
    def login(self):
        path = "/api/zbtxz/login"
        data = {
            "check_token":"",
            "code":self.code,
            "token":"",
            "type":-1,
            "union_id":"",
        }
        res = self.common_post(path,data)
        self.log_info(f"login=>{data}=>{res}")
        if res:
            if res['code'] == 0:
                self.accountId = res['data']['session']['account_id']
                self.sessionId = res['data']['session']['id']
            
                self.msg += f"\n【登陆状态】：登陆成功✅"
                self.msg += f"\n【用户昵称】：{res['data']['account']['nick_name']}"
                self.msg += f"\n【用户编码】：{res['data']['account']['ref_user_code']}"
                self.msg += f"\n【绑定手机】：{tool.hide_phone_number(res['data']['account']['mobile'])}"
                self.msg += f"\n【邀请数量】：{res['data']['account']['invitation_number']}"
                # self.msg += f"\n【下载地址】：{res['data']['download_link']}"
               
                return True
        self.msg+=f"\n【登陆状态】：登陆失败{res}"
        return False

    def config(self):
        res = self.common_get(f"/api/article/channel_list?channel_id=5de768411b011b48a65b772f&isDiFangHao=false&is_new=true&list_count=0&size=30")
        if res:
            article_id = res['data']['focus_list'][0]["channel_article_id"]
            detail_res = self.common_get(f"/api/article/detail?id={article_id}")
            if detail_res:
                url = detail_res['data']['article']['share_url']
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                result = {k: v[0] for k, v in query_params.items()}
                self.id = result['id']

    def jihua_login(self):
        res = self.jihua_post("/api/member/login",{"debug":0,"userId":""})
        self.log_info(f"【jihua_login】=>{res}")
        if res :
            if res['code'] == 0:
                self.jinhuaKey = res['data']['key']
                self.jinhuaToken = f"Bearer {res['data']['token']}"
                return True
        return False

    def jihua_detail(self):
        
        res = self.jihua_get(f"/api/study/detail?id={self.id}",{"id":self.id})
        self.log_info(f"【jihua_detail-{self.id}】=>{res}")
        if not res or res['code'] != 0:
            return False
        self.lotteryId = res['data']['lottery']['lottery_id']
        for item in res['data']['levels']:
            item_res = self.jihua_get(f"/api/study/level?id={item['id']}",{"id":item['id']})
            if not item_res or item_res['code'] != 0:
                continue
            self.msg += f"\n---------抽奖阅读----------"
            if item_res['data']['level']['task_num'] == len(item_res['data']['completedTasks']):
                self.log_info(f"{item['name']},已完成")
                self.msg += f"\n今日阅读已全部完成✅"
                continue
            for task in item_res['data']['tasks']:
                complete_res = self.jihua_post(f"/api/study/task/complete",{"id":task['id']})
                self.log_info(f'文章阅读结果：{complete_res.get("message","")}')
                self.msg += f'\n文章[{task["id"]}]：{complete_res.get("message","")}'
        self.msg += f"\n---------抽奖----------"
        lotter_res = self.jihua_post(f"/api/lotterybigwheel/_ac_lottery_count",{"id":self.lotteryId,"module":"study"})
        if not lotter_res or lotter_res['code'] != 0:
            return False
        self.log_info(f"当前剩余抽奖次数：{lotter_res['data']['count']}")
        self.msg += f"\n抽奖次数：{lotter_res['data']['count']}"
        for index  in range(lotter_res['data']['count']):
            ac_res = self.jihua_post(f"/api/lotterybigwheel/_ac_lottery",{"id":self.lotteryId,"app_id":self.jinhuaAppId,"module":"study","optionHash":""})
            self.log_info(ac_res)
            if not ac_res:
                continue
            if ac_res['code'] == 10000:
                self.log_info(f"本次抽奖遇到滑块，开始自动验证滑块")
                self.msg += f"本次抽奖遇到滑块，开始自动验证滑块"
                if not account.conf['ocr_host']:
                    self.log_err(f"请搭建dddocr自动滑块！请搭建ddddocr自动滑块！请搭建ddddocr自动滑块！")
                captcha_res = self.jihua_post(f"/api/captcha/get",{"activity_id":self.lotteryId,"module":"bigWheel"})
                if not captcha_res or captcha_res.get('code',None) !=0:
                    self.log_err(f"第{index+1}次抽奖获取验证码图片失败")
                    continue
                jigsawImageUrl = captcha_res['data']['jigsawImageUrl']
                originalImageUrl = captcha_res['data']['originalImageUrl']
                captchaToken = captcha_res['data']['token']
                secretKey = captcha_res['data']['secretKey']
                ocr_res = self.slide_post({'slidingImage': jigsawImageUrl, 'backImage': originalImageUrl})
                if not ocr_res:
                    self.log_err(f"第{index+1}次抽奖过滑块失败，ddddocr服务异常")
                    continue
                point = self.aes_encrypt(json.dumps({"x":ocr_res['result'],"y":5}),secretKey)
                cap_check_res = self.jihua_post(f"/api/captcha/check",{"activity_id":self.lotteryId,"module":"bigWheel","cap_token":captchaToken,"point":point})
                if not cap_check_res:
                    self.log_err(f"第{index+1}次抽奖过滑块check失败")
                if cap_check_res['message'] == "操作成功":
                    ac_res = None
                    ac_res = self.jihua_post(f"/api/lotterybigwheel/_ac_lottery",{"id":self.lotteryId,"app_id":self.jinhuaAppId,"module":"study","optionHash":""})
                    if ac_res and ac_res['code'] == 0:
                        self.log_info(f"第{index+1}次抽奖成功，获得{ac_res['data']['title']}")
                        self.msg += f"\n第{index+1}次抽奖成功，获得{ac_res['data']['title']}"
                        continue
            if ac_res['code'] == 0:
                self.log_info(f"第{index+1}次抽奖成功，获得{ac_res['data']['title']}")
                self.msg += f"\n第{index+1}次抽奖成功，获得{ac_res['data']['title']}"
                continue


    def task_list(self):
        path = "/api/user_center/task?type=1&current=1&size=20"
        res = self.common_get(path)
        self.log_info(res)
        if not res :
            return False
        readFinish = True
        likeFinish = True
        shareFinish = True
        for index,task in enumerate(res['data']['list'],start=1):
            self.log_info(f"【{task['name']}】：{'已完成' if task['completed'] ==1 else '未完成'}")
            self.msg+=f"\n【{task['name']}】：{'已完成' if task['completed'] ==1 else '未完成，开始去完成'}"
            if task['completed']==1:
                continue
            self.log_info(f"任务：{task['name']},进度：{task['finish_times']}/{task['frequency']}")
            if task['name'] == '新闻资讯阅读':
                readFinish = False
            if task['name'] == '新闻资讯点赞':
                likeFinish = False
            if task['name'] == '分享资讯给好友':
                shareFinish = False
        if not readFinish or not likeFinish or not shareFinish:
            channel_list_res = self.common_get("/api/article/channel_list?channel_id=5de768411b011b48a65b772f&isDiFangHao=false&is_new=true&list_count=0&size=80")
            if not channel_list_res:
                return
            for index ,article in enumerate(channel_list_res['data']['article_list']):
                id = article['id']
                if not readFinish:
                    read_res = self.common_get(f"/api/article/read_time?channel_article_id={id}&is_end=true&read_time=3051")
                    if read_res.get("score_notify"):
                        self.log_info(f"阅读获得：{read_res['data']['score_notify']['integral']}积分✅")
                        self.msg += f"\n阅读文章【{id}】:获得{read_res['data']['score_notify']['integral']}积分"
                    else:
                        self.log_info(f"文章【{id}】已阅读")
                if not likeFinish:
                    like_res = self.common_post(f"/api/favorite/like",{"action":True,"id":id})
                    self.log_info(f"点赞文章【{id}】：{like_res}")
                    if like_res.get("score_notify"):
                        self.log_info(f"点赞获得：{like_res['data']['score_notify']['integral']}积分")
                        self.msg += f"\n点赞文章【{id}】:获得{like_res['data']['score_notify']['integral']}积分"
                    else:
                        self.log_info(f"文章【{id}】已点赞")
                if not shareFinish:
                    share_res = self.common_post(f"/api/user_mumber/doTask",{"memberType":"3","member_type":"3","target_id":id})
                    self.log_info(f"分享文章【{id}】：{share_res}")
                    if share_res.get("score_notify"):
                        self.log_info(f"分享获得：{share_res['data']['score_notify']['integral']}积分")
                        self.msg += f"\n分享文章【{id}】:获得{share_res['data']['score_notify']['integral']}积分"
                    else:
                        self.log_info(f"文章【{id}】已分享")
    
    def account_detail(self):
        res = self.common_get(f"/api/user_mumber/account_detail")
        if res:
            self.msg += f"\n【积分余额】：{res['data']['rst']['total_integral']}"
    
    def run(self):  
        self.msg = f"【账号备注】：{tool.hide_phone_number(self.name)}" 
        self.generate_random_ua()
        if self.init() and self.gete_signature_key() and self.credential_auth() and self.login():
            self.config()
            if self.jihua_login():
                self.jihua_detail()
            self.msg += f"\n---------积分阅读----------"
            self.task_list()
            self.msg += f"\n---------查询资产----------"
            self.account_detail()
        self.pushMsg(self.msg)

if __name__=="__main__":
    sender = middleware.Sender(middleware.getSenderID())
    plugin={
        "key":"vhook_xishiyan_",
        "name":sender.getPluginName(),
        "ver": sender.getPluginVersion(),
        "sender":sender,
    }
    tool = hook.TOOL(sender,plugin)
    account = ACCOUNT()
    if tool.msg == "西施超管" and tool.isAdmin:
        tool.account_manger_admin()
        exit(0)
    if tool.msg == '西施配置':
        if tool.isAdmin:
            account.edit_conf()
        exit(1)

    if tool.msg == '西施管理':
        account.accoount_manager()
        exit(1)
    if tool.msg == '西施登陆' or tool.msg == "西施登录":
        account.addCount()
        exit()
    if tool.imType == "fake" :
        user_data_arr = account.cron_account_arr()
    elif tool.msg == "xishifk" and tool.isAdmin:
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
    exit(0)
        