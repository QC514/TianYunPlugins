# [disable:false]
# [rule: ^粉象(.*)$]
# [admin: false]
# [service: 2661320550]
# [price: 15.88]
# [version: V6.35]
# [public: true]
# [title: 粉象生活]
# [author: sky2022]
# [icon: https://zhengxin-pub.cdn.bcebos.com/logopic/3b7566ad294edf58d055f514ca1fbd79_fullsize.jpg?x-bce-process=image/resize,m_lfit,w_200]
# [description: 《粉象插件指令说明》https://www.yuque.com/yuqueyonghulzdzov/ddxbk/mwehi1sxq06g1ffk?singleDoc#，插件自带任务! 使用前请先配参。用户指令: 粉象上车,粉象管理,粉象查询,粉象教程；管理员指令: 粉象版本,粉象运行,粉象配置。运行在定时推送里面设置自动运行时间。建议每天21点前运行一次，22点左右运行一次!]
# [param: {"required":true,"key":"bd_fxconfig.wxzsm","bool":false,"placeholder":"http://127.0.0.1/赞赏码.png","name":"赞赏码链接","desc":"你的wx机器人赞赏码链接"}]
# [param: {"required":true,"key":"bd_fxconfig.sqje","bool":false,"placeholder":"1","name":"授权金额(元)","desc":"设置授权需要支付金额为多少元，默认不设置为1元"}]
# [param: {"required":true,"key":"bd_fxconfig.sqsj","bool":false,"placeholder":"30","name":"授权时间(天)","desc":"设置授权金额的授权天数，默认不设置为30天"}]
# [param: {"required":true,"key":"bd_fxconfig.yqurl","bool":false,"placeholder":"你的邀请下载地址","name":"邀请连接","desc":"app-我的-上面邀好友-复制链接 不设置默认是作者的哦！"}]
# [param: {"required":true,"key":"bd_fxconfig.notify","bool":false,"placeholder":"qq,wx","name":"管理员通知","desc":"设置接受管理员通知的渠道，如 qq,wx,tg  用英文逗号分割,不设置不推送"}]
# [param: {"required":false,"key":"bd_fxconfig.sdyx","bool":true,"placeholder":"","name":"手动运行","desc":"是否允许用户手动执行任务(默认否)"}]
# [param: {"required":true,"key":"bd_fxconfig.jfsl","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":false,"key":"bd_fxconfig.use_ma_pay","bool":true,"placeholder":"false","name":"启用码支付","desc":"开启后默认使用码支付+积分支付，并隐藏微信支付"}]


import hashlib
import json
import random
import time
from datetime import datetime, timedelta
import middleware
import requests
import uuid


# AT_AgR8xHwaSH8JHRKqptylzJZw26rEqT2S
def random_string(s, length):
    return ''.join(random.choices(s, k=length))


class ATM_FX:
    def __init__(self, u, s):
        self.ktxje = None
        self.zhzt = None
        self.user = u
        self.sender = s
        self.phone = None
        self.code = None
        self.usid = None
        self.ck = None
        self.name = None
        self.sqsj = None
        self.did = str(uuid.uuid4()).upper()
        self.oaid = random_string("1234567890abcdef", 16)
        self.headers = {
            'User-Agent': "okhttp-okgo/jeasonlzy",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
            'accept-language': "zh-CN,zh;q=0.8",
            'traceid': '',
            'platform': "android",
            'noncestr': '',
            'did': f'{self.did}',
            'timestamp': '',
            'version': "6.7.1",
            'oaid': f'{self.oaid}',
            'imei': "",
            'sign': '',
            'android_id': "",
            'meid': "",
            'serial': "",
            'uuid': f'{self.did}',
            'sti-data': "{}"
        }
        self.finger = random_string("1234567890abcdef", 32)
        self.web_headers = {
            'Host': "fenxiang-lottery-api.fenxianglife.com",
            'User-Agent': "Mozilla/5.0 (Linux; Android 11; Redmi Note 8 Pro Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36 AgentWeb/5.0.0  UCBrowser/11.6.4.950",
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip, deflate",
            'Content-Type': "application/json",
            'timestamp': '',
            'traceid': '',
            'finger': f'{self.finger}',
            'did': f'',
            'oaid': f'{self.oaid}',
            'noncestr': '',
            'platform': "h5",
            'token': '',
            'sign': '',
            'version': "1.0.0",
            'origin': "https://m.fenxianglife.com",
            'x-requested-with': "com.n_add.android",
            'sec-fetch-site': "same-site",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        self.rwname = None
        self.rwid = None
        self.Imtype = None
        self.ktxjes = None

    def set_name(self):
        self.sender.reply("🤖欢迎使用粉象系统, 请先设置您的备注名(1-6个字符)。退出输入'q'!")
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

    def fxsc(self):
        self.name = self.set_name()
        if self.name:
            self.sender.reply('========粉象登录========\n1、短信登录\n2、ck登录\n回复序号选择,退出【q】！')
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

    def dx_login(self):
        self.sender.reply(f"🔔{self.name},你好！\n请输入您的手机号码:\n退出输入'q'! ")
        self.phone = self.sender.input(60000, 1000, False)
        if self.phone == 'q' or self.phone == 'Q':
            self.sender.reply("退出！")

        elif self.phone is None:
            self.sender.reply(f'超时退出！')

        elif len(self.phone) == 11:
            if self.post_yzm():
                self.sender.reply("🔔请输入您的验证码: ")
                code = self.sender.listen(180000)
                if code == 'q' or code == 'Q':
                    self.sender.reply("退出！")

                elif code is None:
                    self.sender.reply(f'超时退出！')

                elif len(code) == 5:
                    self.code = code
                    if self.get_token():
                        ts = middleware.bucketGet('bd_fxcks', self.user)
                        imType = self.sender.getImtype()
                        if not ts:
                            data = {
                                f'{self.usid}': {
                                    'name': self.name,
                                    'ck': self.ck,
                                    'did': self.did,
                                    'Imtype': f'{imType}#{self.user}',
                                    'sqsj': f'{datetime.now().strftime("%Y-%m-%d")}'
                                }
                            }
                            middleware.bucketSet('bd_fxcks', self.user, f'{data}')
                            self.sender.reply(f'{self.name}>>>🔔首次登录成功!中奖推送默认已开启!发送"粉象管理"对账号进行管理!')
                        else:
                            ts = eval(ts)
                            if self.usid in ts:
                                for k, y in ts.items():
                                    if self.usid == k:
                                        Imtype = y.get('Imtype', '')
                                        # 如果旧账号没有sqsj，添加999天授权
                                        sqsj = y.get('sqsj', (datetime.now() + timedelta(days=999)).strftime("%Y-%m-%d"))
                                        ts[f'{k}'] = {'name': self.name, 'ck': self.ck, 'did': self.did,
                                                      'Imtype': f'{Imtype}', 'sqsj': sqsj}
                                        middleware.bucketSet('bd_fxcks', self.user, f'{ts}')
                                        self.sender.reply(
                                            f'{self.name}>>>🔔账号更新成功！发送"粉象管理"对账号进行管理!')
                                        break
                                    else:
                                        continue
                            else:
                                imType = self.sender.getImtype()
                                ts[f'{self.usid}'] = {
                                    'name': self.name,
                                    'ck': self.ck,
                                    'did': self.did,
                                    'Imtype': f'{imType}#{self.user}',
                                    'sqsj': f'{datetime.now().strftime("%Y-%m-%d")}'
                                }
                                middleware.bucketSet('bd_fxcks', self.user, f'{ts}')
                                self.sender.reply(f'{self.name}>>>🔔新增登录成功!中奖推送默认已开启!发送"粉象管理"对账号进行管理!')
                else:
                    self.sender.reply(f'输入有误，退出！')
        else:
            self.sender.reply(f'输入有误，退出！')

    def post_yzm(self):
        timestamp = f'{int(time.time() * 1000)}'
        self.headers['timestamp'] = timestamp

        traceid = f'{random_string("1234567890abcdef", 32)}'
        self.headers['traceid'] = traceid

        noncestr = random_string("1234567890abcdefghijklmnopqrstuvwxyz", 8)
        self.headers['noncestr'] = noncestr

        encode_str = f"粉象好牛逼nb3b16f5a02479a0e34df78d14aefe76mobile={self.phone}&mobileArea=86&type=1&validateType=1did={self.did}&imei=&noncestr={noncestr}&oaid={self.oaid}&platform=android&timestamp={timestamp}&traceid={traceid}&version=6.7.1"
        sign = hashlib.md5(encode_str.encode()).hexdigest()
        self.headers['sign'] = sign
        try:
            r = requests.post(
                "https://api.fenxianglife.com/njia/util/sms/code",
                headers=self.headers,
                json={
                    "validateType": 1,
                    "mobileArea": "86",
                    "mobile": f"{self.phone}",
                    "type": 1
                }
            )
            success = r.json().get('success', None)
            if success:
                self.sender.reply(f'✅验证码发送成功!')
                return True
            else:
                self.sender.reply(f"❌验证码发送失败!\n{r.json().get('message', None)}")
                return False

        except Exception as e:
            self.sender.reply(f'⛔验证码发送异常!\n{e}')
            return False

    def get_token(self):
        smsCode = hashlib.md5(self.code.encode()).hexdigest()
        timestamp = f'{int(time.time() * 1000)}'
        self.headers['timestamp'] = timestamp

        traceid = f'{random_string("1234567890abcdef", 32)}'
        self.headers['traceid'] = traceid

        noncestr = random_string("1234567890abcdefghijklmnopqrstuvwxyz", 8)
        self.headers['noncestr'] = noncestr

        encode_str = f"粉象好牛逼nb3b16f5a02479a0e34df78d14aefe76mobile={self.phone}&mobileArea=86&smsCode={smsCode}did={self.did}&imei=&noncestr={noncestr}&oaid={self.oaid}&platform=android&timestamp={timestamp}&traceid={traceid}&version=6.7.1"
        sign = hashlib.md5(encode_str.encode()).hexdigest()
        self.headers['sign'] = sign
        try:
            r = requests.post(
                "https://api.fenxianglife.com/njia/login/mobile",
                headers=self.headers,
                json={
                    "mobileArea": "86",
                    "smsCode": f'{smsCode}',
                    "mobile": f'{self.phone}'
                }
            )
            success = r.json().get('success', None)
            if success:
                self.usid = r.json()['data']['userInfo']['id']
                self.usid = str(self.usid)
                self.ck = r.json()['data']['token']
                return True
            else:
                self.sender.reply(f"❌登录失败!\n{r.json().get('message', None)}")
                return False

        except Exception as e:
            self.sender.reply(f'⛔登录异常!\n{e}')
            return False

    def ck_login(self):
        self.sender.reply(
            f"{self.name}! 你好!\n抓包: 粉象生活app\n域名: api.fenxianglife.com\n请求头里面的token和did的值\n请在120s内发送你的'token的值#did的值',用 # 隔开两个参数\n退出回复'q'!")
        ck = self.sender.input(120000, 1000, False)
        if ck == 'q' or ck == 'Q':
            self.sender.reply("退出！")

        elif ck is None:
            self.sender.reply(f'超时退出！')

        elif '#' in ck:
            self.ck = ck.split('#')[0]
            self.headers['token'] = self.ck
            self.did = ck.split('#')[1]
            self.headers['did'] = self.did
            try:
                login = self.get_info()
                if login is True:
                    ts = middleware.bucketGet('bd_fxcks', self.user)
                    imType = self.sender.getImtype()
                    if not ts:
                        data = {
                            f'{self.usid}': {
                                'name': self.name,
                                'ck': self.ck,
                                'did': self.did,
                                'Imtype': f'{imType}#{self.user}',
                                'sqsj': f'{datetime.now().strftime("%Y-%m-%d")}'
                            }
                        }
                        middleware.bucketSet('bd_fxcks', self.user, f'{data}')
                        self.sender.reply(f'{self.name}>>>🔔首次登录成功!中奖推送默认已开启!发送"粉象管理"对账号进行管理!')
                    else:
                        ts = eval(ts)
                        if self.usid in ts:
                            for k, y in ts.items():
                                if self.usid == k:
                                    Imtype = y.get('Imtype', '')
                                    # 如果旧账号没有sqsj，添加999天授权
                                    sqsj = y.get('sqsj', (datetime.now() + timedelta(days=999)).strftime("%Y-%m-%d"))
                                    ts[f'{k}'] = {
                                        'name': self.name,
                                        'ck': self.ck,
                                        'did': self.did,
                                        'Imtype': f'{Imtype}',
                                        'sqsj': sqsj
                                    }
                                    middleware.bucketSet('bd_fxcks', self.user, f'{ts}')
                                    self.sender.reply(
                                        f'{self.name}>>>🔔账号更新成功！发送"粉象管理"对账号进行管理!')
                                    break
                                else:
                                    continue
                        else:
                            imType = self.sender.getImtype()
                            ts[f'{self.usid}'] = {
                                'name': self.name,
                                'ck': self.ck,
                                'did': self.did,
                                'Imtype': f'{imType}#{self.user}',
                                'sqsj': f'{datetime.now().strftime("%Y-%m-%d")}'
                            }
                            middleware.bucketSet('bd_fxcks', self.user, f'{ts}')
                            self.sender.reply(f'{self.name}>>>🔔新增登录成功!中奖推送默认已开启!发送"粉象管理"对账号进行管理!')
                else:
                    self.sender.reply(f'{login}')
            except Exception as e:
                self.sender.reply(f'{self.name}登录错误>>>{e}')
        else:
            self.sender.reply(f'输入有误，退出！')

    def get_info(self):
        timestamp = f'{int(time.time() * 1000)}'
        self.headers['timestamp'] = timestamp

        traceid = f'{random_string("1234567890abcdef", 32)}'
        self.headers['traceid'] = traceid

        noncestr = random_string("1234567890abcdefghijklmnopqrstuvwxyz", 8)
        self.headers['noncestr'] = noncestr

        encode_str = f"粉象好牛逼nb3b16f5a02479a0e34df78d14aefe76did={self.did}&imei=&noncestr={noncestr}&oaid={self.oaid}&platform=android&timestamp={timestamp}&token={self.ck}&traceid={traceid}&version=6.7.1"
        sign = hashlib.md5(encode_str.encode()).hexdigest()
        self.headers['sign'] = sign
        try:
            r = requests.get(
                "https://api.fenxianglife.com/njia/users/info",
                headers=self.headers,
            )
            success = r.json().get('success', None)
            if success:
                self.usid = r.json()['data']['userInfo']['id']
                self.usid = str(self.usid)
                self.ck = r.json()['data']['token']
                return True
            else:
                return f"{self.name}>>>❌登录失败!\n{r.json().get('message', None)}"
        except Exception as e:
            return f'{self.name}>>>⛔登录异常!\n{e}'

    def fxgl(self):
        ts = middleware.bucketGet('bd_fxcks', self.user)
        if ts == '' or ts == '{}':
            self.sender.reply("🔔粉象系统未查询到您的信息! 请先上车! ")
        else:
            ts = eval(ts)
            n = 0
            id_dict = {}
            msg = '========粉象管理========\n'
            zhszt = {}
            for k, y in ts.items():
                n += 1
                self.ck = y['ck']
                id_dict[n] = {
                    'usid': k,
                    'name': y['name'],
                    'ck': y['ck'],
                    'did': y['did'],
                    'Imtype': y['Imtype'],
                    'sqsj': y.get('sqsj', datetime.now().strftime("%Y-%m-%d"))
                }
                self.ck = y['ck']
                self.headers['token'] = self.ck
                self.did = y['did']
                self.headers['did'] = self.did
                self.Imtype = y['Imtype']
                # 如果账号没有sqsj字段（旧免费版），添加999天授权
                if 'sqsj' not in y:
                    future_date = (datetime.now() + timedelta(days=999)).strftime("%Y-%m-%d")
                    y['sqsj'] = future_date
                    # 更新到数据库
                    ts[k]['sqsj'] = future_date
                    middleware.bucketSet('bd_fxcks', self.user, f'{ts}')
                self.sqsj = y['sqsj']
                if self.Imtype == '':
                    tszt = '❌关闭'
                else:
                    tszt = '✅开启'
                login = self.get_info()
                # 检查授权是否到期
                if self.sqsj <= datetime.now().strftime("%Y-%m-%d"):
                    self.sqsj += '(已到期)'
                if login is True:
                    zhzt = '✅有效'
                    msg += f'{n}、{y["name"]}\n账号状态: {zhzt}\n中奖推送: {tszt}\n授权时间: ⏰{self.sqsj}\n======================\n'
                else:
                    zhzt = '❌失效'
                    msg += f'{n}、{y["name"]}\n账号状态: {zhzt}\n中奖推送: {tszt}\n授权时间: ⏰{self.sqsj}\n======================\n'
                zhszt[n] = {'zhzt': zhzt}
            msg += f'0、批量授权\n回复序号选择账号,退出【q】！'
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
                self.batch_auth(id_dict)
            elif int(xz) in xz_list:
                zh = id_dict[int(xz)]
                self.usid = zh['usid']
                self.ck = zh['ck']
                self.did = zh['did']
                self.name = zh['name']
                self.web_headers['token'] = self.ck
                self.web_headers['did'] = self.did
                self.Imtype = zh['Imtype']
                self.zhzt = zhszt[int(xz)]['zhzt']
                self.sqsj = zh['sqsj']
                self.gl_zh()
            else:
                self.sender.reply(f'输入有误，退出！')

    def batch_auth(self, id_dict):
        n = len(id_dict)
        account_list = '\n'.join([f"{k}、{v['name']} ⏰{v['sqsj']}" for k, v in id_dict.items()])
        self.sender.reply(
            f'========批量授权========\n{account_list}\n======================\n'
            f'请输入要授权的账号序号，多个用英文逗号分隔\n例如: 1,2,3\n输入 all 选择全部 ({n}个)\n退出【q】！'
        )
        xz = self.sender.listen(60000)
        if not xz or xz.lower() == 'q':
            self.sender.reply('退出！')
            return

        if xz.lower() == 'all':
            selected = list(id_dict.keys())
        else:
            try:
                selected = [int(x.strip()) for x in xz.split(',') if x.strip()]
                invalid = [x for x in selected if x not in id_dict]
                if invalid:
                    self.sender.reply(f'序号 {invalid} 不存在，退出！')
                    return
            except ValueError:
                self.sender.reply('输入有误，退出！')
                return

        if not selected:
            self.sender.reply('未选择任何账号，退出！')
            return

        sqje = float(middleware.bucketGet('bd_fxconfig', 'sqje') or '1')
        sqsj = int(middleware.bucketGet('bd_fxconfig', 'sqsj') or '30')
        months = sqsj / 30
        total_money = sqje * len(selected)
        jfsl = middleware.bucketGet('bd_fxconfig', 'jfsl')
        total_points = int(jfsl) * len(selected) if jfsl else 0
        user_points = int(middleware.bucketGet('dd_sign_points', self.user) or '0')
        use_ma_pay = (middleware.bucketGet('bd_fxconfig', 'use_ma_pay') or 'false').lower() == 'true'
        ma_pay_config = None
        if use_ma_pay:
            ma_pay_config = {
                'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
                'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
                'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
                'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
                'type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay,qqpay',
                'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url'),
                'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url')
            }
            if ma_pay_config['switch'].lower() != 'true' or not all([ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
                ma_pay_config = None
        zsm = middleware.bucketGet('bd_fxconfig', 'wxzsm')
        show_wechat_pay = bool(zsm) and not use_ma_pay
        show_ma_pay = use_ma_pay and bool(ma_pay_config)

        selected_names = '、'.join([id_dict[k]['name'] for k in selected])
        pay_menu = (
            f'=====批量授权确认=====\n'
            f'📋 已选账号: {len(selected)}个\n'
            f'📝 账号列表: {selected_names}\n'
            f'⏰ 授权时长: {months}月/个\n'
            f'======================'
        )
        options_map = {}
        option_num = 1
        if total_points > 0:
            pay_menu += f'\n{option_num}️⃣ 积分支付\n   💰 所需积分: {total_points}\n   💎 当前积分: {user_points}'
            options_map[str(option_num)] = 'points'
            option_num += 1
        if show_wechat_pay:
            pay_menu += f'\n{option_num}️⃣ 微信支付\n   💰 所需金额: {total_money}元（{sqje}元×{len(selected)}个）'
            options_map[str(option_num)] = 'wechat'
            option_num += 1
        if show_ma_pay:
            pay_menu += f'\n{option_num}️⃣ 码支付\n   💰 所需金额: {total_money}元（{sqje}元×{len(selected)}个）'
            options_map[str(option_num)] = 'ma'
        if not options_map:
            self.sender.reply('❌ 未配置可用收款方式，请联系管理员！')
            return
        pay_menu += '\n------------------\n请选择支付方式(回复序号，q退出):'
        self.sender.reply(pay_menu)
        choice = self.sender.listen(60000)
        if not choice or choice in ['q', 'Q']:
            self.sender.reply('已取消支付')
            return
        selected_method = options_map.get(choice)
        if not selected_method:
            self.sender.reply('输入有误，已取消支付')
            return

        if selected_method == 'points':
            if user_points < total_points:
                self.sender.reply(f'积分不足\n当前:{user_points}\n需要:{total_points}')
                return
            self.sender.reply(
                f'=====批量积分支付=====\n'
                f'📋 账号数: {len(selected)}个\n'
                f'💎 当前积分: {user_points}\n'
                f'💰 所需积分: {total_points}\n'
                f'📊 剩余积分: {user_points - total_points}\n'
                f'是否确认支付?\n[y]确认 | [n]取消'
            )
            confirm = self.sender.listen(60000)
            if not confirm or confirm.lower() != 'y':
                self.sender.reply('已取消支付')
                return
            new_balance = user_points - total_points
            middleware.bucketSet('dd_sign_points', self.user, str(new_balance))
            new_sqsj = self._batch_update_auth_time(id_dict, selected, months)
            self.sender.reply(
                f'=====批量授权成功=====\n'
                f'🎈 商品: 粉象生活批量授权\n'
                f'📋 账号数: {len(selected)}个\n'
                f'📝 账号: {selected_names}\n'
                f'💰 支付: {total_points}积分\n'
                f'💎 剩余: {new_balance}积分\n'
                f'⏰ 时长: {months}月/个\n'
                f'📅 到期: {new_sqsj}\n'
                f'==================='
            )
            return

        if selected_method == 'wechat':
            if self.sender.atWaitPay():
                self.sender.reply('当前有人正在支付,请稍后再试！')
                return
            self.sender.reply(f'======订单信息=====\n🎈名称:粉象批量授权\n🎉数量:{len(selected)}个账号 {months}月\n💰应付:{total_money}元')
            self.sender.replyImage(zsm)
            result = self.sender.waitPay('q', 100 * 1000)
            if str(result) == 'q':
                self.sender.reply('退出支付')
                return
            try:
                if isinstance(result, str):
                    result = json.loads(result)
                Money = float(result.get('Money') or result.get('money', 0))
                pay_time = result.get('Time') or result.get('time', '').replace('T', ' ').split('.')[0]
                if not pay_time:
                    pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if Money >= total_money:
                    new_sqsj = self._batch_update_auth_time(id_dict, selected, months)
                    self.sender.reply(
                        f'=====批量授权成功=====\n'
                        f'🎈 商品: 粉象生活批量授权\n'
                        f'📋 账号数: {len(selected)}个\n'
                        f'📝 账号: {selected_names}\n'
                        f'💰 支付: {Money}元\n'
                        f'⏰ 支付时间: {pay_time}\n'
                        f'📅 到期时间: {new_sqsj}\n'
                        f'==================='
                    )
                else:
                    self.sender.reply(f'支付金额错误\n应付:{total_money}元\n实付:{Money}元\n请联系管理员处理退款！')
            except Exception as e:
                self.sender.reply(f'处理支付结果时出错: {str(e)}')
            return

        if selected_method == 'ma':
            out_trade_no = f"FX{int(time.time())}{self.user}"
            params = {
                'pid': ma_pay_config['pid'],
                'type': (ma_pay_config.get('type') or 'alipay,wxpay,qqpay').split(',')[0],
                'out_trade_no': out_trade_no,
                'name': f"{self.user}-粉象批量授权-{str(total_money)}",
                'money': str(total_money),
                'param': self.user
            }
            if ma_pay_config.get('notify_url'):
                params['notify_url'] = ma_pay_config['notify_url']
            if ma_pay_config.get('return_url'):
                params['return_url'] = ma_pay_config['return_url']
            params = {k: v for k, v in params.items() if v}
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
            sign = hashlib.md5((sign_str + ma_pay_config['key']).encode()).hexdigest().lower()
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            gateway = ma_pay_config['gateway'].rstrip('/')
            submit_url = gateway + '/mapi.php'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            try:
                response = requests.post(submit_url, data=params, headers=headers, timeout=10)
                if response.status_code != 200:
                    self.sender.reply(f'❌ 创建支付订单失败，HTTP状态码: {response.status_code}')
                    return
                result = response.json()
                if result.get('code') != 1:
                    self.sender.reply(f"❌ 创建支付订单失败: {result.get('msg', '未知错误')}")
                    return
                pay_url = result.get('payurl', '')
                if not pay_url:
                    self.sender.reply('❌ 未获取到支付链接')
                    return
                self.sender.reply(
                    f'=====码支付=====\n'
                    f'🎫 商品: 粉象批量授权\n'
                    f'💰 金额: {total_money}元\n'
                    f'⏰ 有效期: 5分钟\n'
                    f'------------------\n'
                    f'请点击链接完成支付:\n{pay_url}\n\n'
                    f'💡 支付过程中输入"q"可取消支付\n'
                    f'==================='
                )
                for _ in range(60):
                    result_input = self.sender.listen(5000)
                    if result_input in ['q', 'Q']:
                        self.sender.reply('✅ 已取消支付')
                        return
                    check_url = gateway
                    if '/xpay/epay/api.php' not in check_url:
                        check_url = f"{check_url}/xpay/epay/api.php"
                    check_params = {
                        'act': 'order',
                        'pid': ma_pay_config['pid'],
                        'key': ma_pay_config['key'],
                        'out_trade_no': out_trade_no
                    }
                    try:
                        check_resp = requests.get(check_url, params=check_params, timeout=10)
                        check_result = check_resp.json()
                        if check_result.get('code') == 1 and check_result.get('status') == 1:
                            new_sqsj = self._batch_update_auth_time(id_dict, selected, months)
                            self.sender.reply(
                                f'=====批量授权成功=====\n'
                                f'🎈 商品: 粉象生活批量授权\n'
                                f'📋 账号数: {len(selected)}个\n'
                                f'📝 账号: {selected_names}\n'
                                f'💰 支付: {total_money}元\n'
                                f'📅 到期时间: {new_sqsj}\n'
                                f'==================='
                            )
                            return
                    except:
                        continue
                self.sender.reply('❌ 支付超时,请重新发起支付!')
            except Exception as e:
                self.sender.reply(f'{e}或者超时了！')

    def _batch_update_auth_time(self, id_dict, selected, months):
        days = int(months * 30)
        ts = middleware.bucketGet('bd_fxcks', self.user)
        ts = eval(ts)
        dqsj = datetime.now().strftime("%Y-%m-%d")
        last_sqsj = ''
        for idx in selected:
            zh = id_dict[idx]
            usid = zh['usid']
            sqsj_str = zh['sqsj']
            if sqsj_str and sqsj_str > dqsj:
                base_date = datetime.strptime(sqsj_str, "%Y-%m-%d")
            else:
                base_date = datetime.now()
            new_sqsj = (base_date + timedelta(days=days)).strftime("%Y-%m-%d")
            last_sqsj = new_sqsj
            if usid in ts:
                ts[usid]['sqsj'] = new_sqsj
        middleware.bucketSet('bd_fxcks', self.user, f'{ts}')
        return last_sqsj

    def gl_zh(self):
        """管理账号"""
        msg = f'========账号管理========\n账号: {self.name}\n1、账号授权\n2、任务运行\n3、余额提现\n4、中奖推送\n5、删除账号\n======================\n回复序号,退出【q】！'
        self.sender.reply(msg)
        zh = self.sender.listen(60000)
        if zh == 'q' or zh == 'Q':
            self.sender.reply("退出！")
        elif zh is None:
            self.sender.reply(f'超时退出！')
        elif zh == '1':
            self.dssq()
        elif zh == '2':
            sdyx = middleware.bucketGet('bd_fxconfig', 'sdyx')
            if sdyx == '':
                sdyx = 'false'
            if sdyx == 'false':
                self.sender.reply('管理员未开启手动运行!')
            elif sdyx == 'true':
                if '有效' in self.zhzt:
                    if self.sqsj <= datetime.now().strftime("%Y-%m-%d"):
                        self.sender.reply(f'🔔{self.name}: 粉象系统检测到您的授权已经到期,请及时续费!')
                    else:
                        self.rwyx()
                else:
                    self.sender.reply(f'🔔你都失效了！先去上车更新一下吧！')
        elif zh == '3':
            ktxje = self.get_ktxje()
            if isinstance(ktxje, dict):
                self.ktxjes = ktxje['data']['maxWithdrawAmount']
                if self.ktxjes < 10:
                    self.sender.reply(f'🔔{self.name}---可提现金额为: {self.ktxjes / 100}\n小于最低提现金额！无法提现！')
                else:
                    self.sender.reply(f'🔔{self.name}---可提现金额为: {self.ktxjes / 100}\n是否提现(y/n)?')
                    zh = self.sender.listen(60000)
                    if zh == 'n' or zh == 'N':
                        self.sender.reply("退出！")
                    elif zh is None:
                        self.sender.reply(f'超时退出！')
                    elif zh == 'y' or zh == 'Y':
                        tx = self.tx()
                        if isinstance(tx, dict):
                            msg = tx['data']['title']
                            msg1 = tx['data']['subTitle']
                            self.sender.reply(f'🔔{self.name}--提现{self.ktxjes / 100}成功！\n{msg},{msg1}')
                    else:
                        self.sender.reply(f'输入有误!!')
            else:
                self.sender.reply(f'{ktxje}')

        elif zh == '4':
            self.set_Imtype()
        elif zh == '5':
            self.del_zh()
        else:
            self.sender.reply(f'输入有误!!')

    def set_Imtype(self):
        self.sender.reply(f'🔔是否开启运行推送【y/n】？退出【q】！')
        zh = self.sender.listen(60000)
        if zh == 'q' or zh == 'Q':
            self.sender.reply("退出！")

        elif zh is None:
            self.sender.reply(f'超时退出！')

        elif zh == 'y' or zh == 'Y':
            ts = middleware.bucketGet('bd_fxcks', self.user)
            ts = eval(ts)
            imType = self.sender.getImtype()
            if self.usid in ts:
                for k, y in ts.items():
                    if self.usid == k:
                        # 如果旧账号没有sqsj，添加999天授权
                        sqsj = y.get('sqsj', (datetime.now() + timedelta(days=999)).strftime("%Y-%m-%d"))
                        ts[f'{k}'] = {
                            'name': self.name,
                            'ck': self.ck,
                            'did': self.did,
                            'Imtype': f'{imType}#{self.user}',
                            'sqsj': sqsj
                        }
                        middleware.bucketSet('bd_fxcks', self.user, f'{ts}')
                        self.sender.reply(f'{self.name}>>>🔔中奖推送已开启')
                        break
                    else:
                        continue
        elif zh == 'n' or zh == 'N':
            ts = middleware.bucketGet('bd_fxcks', self.user)
            ts = eval(ts)
            if self.usid in ts:
                for k, y in ts.items():
                    if self.usid == k:
                        # 如果旧账号没有sqsj，添加999天授权
                        sqsj = y.get('sqsj', (datetime.now() + timedelta(days=999)).strftime("%Y-%m-%d"))
                        ts[f'{k}'] = {
                            'name': self.name,
                            'ck': self.ck,
                            'did': self.did,
                            'Imtype': '',
                            'sqsj': sqsj
                        }
                        middleware.bucketSet('bd_fxcks', self.user, f'{ts}')
                        self.sender.reply(f'{self.name}>>>🔔中奖推送已关闭')
                        break
                    else:
                        continue
        else:
            self.sender.reply(f'输入有误，退出！')

    def rwyx(self):
        self.sender.reply(f'{self.name} 🔔开始运行粉象任务')
        rw_json = self.get_rwinfo()
        if isinstance(rw_json, dict):
            issign = rw_json['data']['signInModule']
            if issign['status'] == 1:
                rwqd = self.reward()
                if rwqd is True:
                    pass
                else:
                    self.sender.reply(f'⛔{self.name}\n{rwqd}')
            else:
                pass
            rws = rw_json['data']['taskModule']['taskResult']
            for rw in rws:
                self.rwname = rw['title']
                self.rwid = rw['id']
                taskStatus = rw['taskStatus']
                if taskStatus == 0:
                    self.finish()
                    time.sleep(5)
            cx = self.get_rwinfo()
            zjjg = self.get_zjinfo()
            if isinstance(cx, dict) and isinstance(zjjg, dict):
                dateStr = cx['data']['openLotteryModule']['now']['dateStr']
                today = datetime.today().strftime("%y%m%d")
                tomorrow = datetime.today() + timedelta(days=1)
                tomorrow = tomorrow.strftime("%y%m%d")
                md = zjjg['data']['freeItem']
                if md is None:
                    mdsp = '无免单商品'
                else:
                    mdsp = md['itemTitle']
                    itemPicUrl = md['itemPicUrl']
                    self.sender.replyImage(itemPicUrl)
                if today == dateStr:
                    dateStr = cx['data']['openLotteryModule']['now']['dateStr']
                    jms = cx['data']['openLotteryModule']['now']['rewardCodes']
                    rewardCodes = cx['data']['openLotteryModule']['prev']['rewardCodes']
                    zjje = 0
                    for jg in rewardCodes:
                        zjje += jg['rewardAmount']
                        zjje += jg['subsidyAmount']
                    zjxx = f'========粉象运行========\n{self.name}-{dateStr}期(未开奖)\n当前奖码: 🏆{len(jms)}个\n昨日中奖: 🧧{zjje / 100}\n免单商品: 🎁{mdsp}'
                    self.sender.reply(zjxx)
                elif tomorrow == dateStr:
                    dateStr = cx['data']['openLotteryModule']['prev']['dateStr']
                    jms = cx['data']['openLotteryModule']['now']['rewardCodes']
                    rewardCodes = cx['data']['openLotteryModule']['prev']['rewardCodes']
                    zjje = 0
                    for jg in rewardCodes:
                        zjje += jg['rewardAmount']
                        zjje += jg['subsidyAmount']
                    zjxx = f'========粉象运行========\n{self.name}-{dateStr}期(已开奖)\n当前奖码: 🏆{len(jms)}个\n今日中奖: 🧧{zjje / 100}\n免单商品: 🎁{mdsp}'
                    self.sender.reply(zjxx)
                    if mdsp != '无免单商品':
                        notify = middleware.bucketGet('bd_fxconfig', 'notify')
                        if notify == '':
                            pass
                        else:
                            tsqd = notify.split(',')
                            middleware.notifyMasters(f"{zjxx}", tsqd)

                        if self.Imtype == '':
                            pass
                        else:
                            qd = self.Imtype.split('#')[0]
                            users = self.Imtype.split('#')[1]
                            middleware.push(f'{qd}', '', f'{users}', 'cs', zjxx)
                    receiveAll = self.receiveAll()
                    if receiveAll is True:
                        pass
                    else:
                        self.sender.reply(f'⛔{self.name}\n{receiveAll}')
            else:
                self.sender.reply(f'========粉象运行========\n{self.name}\n运行错误: ⛔{cx}')

        else:
            self.sender.reply(f'⛔{self.name}\n{rw_json}')

    def reward(self):
        try:
            body = ''
            timestamp = f'{int(time.time() * 1000)}'
            self.web_headers['timestamp'] = timestamp

            traceid = f'{random_string("1234567890abcdef", 32)}'
            self.web_headers['traceid'] = traceid

            noncestr = f'{random.randint(1, 9)}{random_string("1234567890", 7)}'
            self.web_headers['noncestr'] = noncestr

            s = f'{body}did={self.did}&finger={self.finger}&noncestr={noncestr}&oaid={self.oaid}&platform=h5&timestamp={timestamp}&token={self.ck}&traceid={traceid}&version=1.0.0粉象好牛逼a8c19d8267527ea4c7d2f011acf7766f'

            md5 = hashlib.md5()
            md5.update(s.encode('utf-8'))
            encrypted_str = md5.hexdigest()
            self.web_headers['sign'] = f'{encrypted_str}'

            r = requests.post(
                "https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/user/sign/reward",
                json={},
                headers=self.web_headers
            )
            success = r.json().get('success', None)
            message = r.json().get('message', None)
            if success or '重复' in message:
                return True
            else:
                return message
        except Exception as e:
            return e

    def finish(self):
        try:
            body = f'taskId={self.rwid}'
            timestamp = f'{int(time.time() * 1000)}'
            self.web_headers['timestamp'] = timestamp

            traceid = f'{random_string("1234567890abcdef", 32)}'
            self.web_headers['traceid'] = traceid

            noncestr = f'{random.randint(1, 9)}{random_string("1234567890", 7)}'
            self.web_headers['noncestr'] = noncestr

            s = f'{body}did={self.did}&finger={self.finger}&noncestr={noncestr}&oaid={self.oaid}&platform=h5&timestamp={timestamp}&token={self.ck}&traceid={traceid}&version=1.0.0粉象好牛逼a8c19d8267527ea4c7d2f011acf7766f'

            md5 = hashlib.md5()
            md5.update(s.encode('utf-8'))
            encrypted_str = md5.hexdigest()
            self.web_headers['sign'] = f'{encrypted_str}'
            r = requests.post(
                "https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/lotteryCode/task/finish",
                json={
                    "taskId": self.rwid
                },
                headers=self.web_headers
            )
            print(r.json())
            success = r.json().get('success', None)
            if success:
                return True
            else:
                return r.json().get('message', None)
        except Exception as e:
            return e

    def del_zh(self):
        """删除账号"""
        self.sender.reply(f'是否删除账号【{self.name}】及授权信息？(y/n)')
        zh = self.sender.listen(60000)
        if zh == 'n' or zh == 'N':
            self.sender.reply("退出！")

        elif zh is None:
            self.sender.reply(f'超时退出！')

        elif zh == 'y' or zh == 'Y':
            ts = middleware.bucketGet('bd_fxcks', self.user)
            ts = eval(ts)
            del ts[f'{self.usid}']
            middleware.bucketSet('bd_fxcks', self.user, f'{ts}')
            self.sender.reply(f'{self.name}>>>删除成功！')
        else:
            self.sender.reply(f'输入有误，退出！')

    def dssq(self):
        """打赏授权"""
        try:
            if self.sender.atWaitPay():
                self.sender.reply('当前有人正在支付,请稍后再试！')
                return

            # 获取配置的授权金额和时间
            sqje = middleware.bucketGet('bd_fxconfig', 'sqje')
            if sqje == '':
                sqje = 1
            sqje = float(sqje)

            sqsj = middleware.bucketGet('bd_fxconfig', 'sqsj')
            if sqsj == '':
                sqsj = 30
            sqsj = int(sqsj)

            project = "粉象授权"
            months = sqsj / 30
            total = sqje

            # 积分配置
            jfsl = middleware.bucketGet('bd_fxconfig', 'jfsl')
            total_points = int(jfsl) if jfsl else 0
            user_points = int(middleware.bucketGet('dd_sign_points', self.user) or '0')

            # 码支付配置
            use_ma_pay = (middleware.bucketGet('bd_fxconfig', 'use_ma_pay') or 'false').lower() == 'true'
            ma_pay_config = None
            if use_ma_pay:
                ma_pay_config = {
                    'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
                    'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
                    'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
                    'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
                    'type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay,qqpay',
                    'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url'),
                    'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url')
                }
                if ma_pay_config['switch'].lower() != 'true' or not all([ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
                    ma_pay_config = None

            zsm = middleware.bucketGet('bd_fxconfig', 'wxzsm')
            show_wechat_pay = bool(zsm) and not use_ma_pay
            show_ma_pay = use_ma_pay and bool(ma_pay_config)

            if not show_wechat_pay and not show_ma_pay and total_points <= 0:
                self.sender.reply('❌ 未配置可用收款方式,请联系管理员!')
                return

            pay_menu = "=====支付方式====="
            options_map = {}
            option_num = 1

            if total_points > 0:
                pay_menu += (
                    f"\n{option_num}️⃣ 积分支付"
                    f"\n   💰 所需积分: {total_points}"
                    f"\n   💎 当前积分: {user_points}"
                )
                options_map[str(option_num)] = 'points'
                option_num += 1

            if show_wechat_pay:
                pay_menu += (
                    f"\n{option_num}️⃣ 微信支付"
                    f"\n   💰 所需金额: {total}元"
                )
                options_map[str(option_num)] = 'wechat'
                option_num += 1

            if show_ma_pay:
                pay_menu += (
                    f"\n{option_num}️⃣ 码支付"
                    f"\n   💰 所需金额: {total}元"
                )
                options_map[str(option_num)] = 'ma'

            pay_menu += "\n------------------\n请选择支付方式(回复序号，q退出):"
            self.sender.reply(pay_menu)

            choice = self.sender.listen(60000)
            if not choice or choice in ['q', 'Q']:
                self.sender.reply('已取消支付')
                return

            selected = options_map.get(choice)
            if not selected:
                self.sender.reply('输入有误，已取消支付')
                return

            if selected == 'points':
                if user_points < total_points:
                    self.sender.reply(f'积分不足\n当前:{user_points}\n需要:{total_points}')
                    return
                self.sender.reply(
                    "=====积分支付=====\n"
                    f"💰 当前积分: {user_points}\n"
                    f"💵 所需积分: {total_points}\n"
                    f"💡 购买时长: 1月\n"
                    "是否确认支付?\n"
                    "[y]确认 | [n]取消"
                )
                confirm = self.sender.listen(60000)
                if not confirm or confirm.lower() != 'y':
                    self.sender.reply('已取消支付')
                    return

                new_balance = user_points - total_points
                middleware.bucketSet('dd_sign_points', self.user, str(new_balance))
                new_sqsj = self.update_auth_time(1)
                if not new_sqsj:
                    self.sender.reply('更新授权时间失败')
                    return
                self.sender.reply(f"""=====支付成功=====
🎈 商品: 粉象生活授权
🎉 时长: 1月
💰 支付: {total_points}积分
💎 剩余: {new_balance}积分
⏰ 到期: {new_sqsj}
===================""")
                return

            if selected == 'wechat':
                self.sender.reply(f'======订单信息=====\n🎈名称:{project}\n🎉数量:{months}月\n💰应付:{total}元')
                self.sender.replyImage(zsm)
                result = self.sender.waitPay("q", 100 * 1000)

                if str(result) == 'q':
                    self.sender.reply('退出支付')
                    return

                try:
                    if isinstance(result, str):
                        result = json.loads(result)

                    Money = float(result.get('Money') or result.get('money', 0))
                    pay_time = result.get('Time') or result.get('time', '').replace('T', ' ').split('.')[0]
                    if not pay_time:
                        pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if Money >= total:
                        new_sqsj = self.update_auth_time(months)
                        if not new_sqsj:
                            self.sender.reply("更新授权时间失败")
                            return

                        msg = f"""=====支付成功=====
🎈 商品: {project}
🎉 时长: {months}月
💰 支付: {Money}元
⏰ 支付时间: {pay_time}
📅 到期时间: {new_sqsj}
==================="""
                        self.sender.reply(msg)
                    else:
                        self.sender.reply(f'支付金额错误\n应付:{total}元\n实付:{Money}元\n请联系管理员处理退款！')
                except Exception as e:
                    self.sender.reply(f"处理支付结果时出错: {str(e)}")
                return

            if selected == 'ma':
                out_trade_no = f"FX{int(time.time())}{self.user}"
                params = {
                    'pid': ma_pay_config['pid'],
                    'type': (ma_pay_config.get('type') or 'alipay,wxpay,qqpay').split(',')[0],
                    'out_trade_no': out_trade_no,
                    'name': f"{self.user}-粉象授权-{str(total)}",
                    'money': str(total),
                    'param': self.user
                }
                if ma_pay_config.get('notify_url'):
                    params['notify_url'] = ma_pay_config['notify_url']
                if ma_pay_config.get('return_url'):
                    params['return_url'] = ma_pay_config['return_url']

                params = {k: v for k, v in params.items() if v}
                sorted_params = sorted(params.items(), key=lambda x: x[0])
                sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
                sign = hashlib.md5((sign_str + ma_pay_config['key']).encode()).hexdigest().lower()
                params['sign'] = sign
                params['sign_type'] = 'MD5'

                gateway = ma_pay_config['gateway'].rstrip('/')
                submit_url = gateway + '/mapi.php'

                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                response = requests.post(submit_url, data=params, headers=headers, timeout=10)
                if response.status_code != 200:
                    self.sender.reply(f"❌ 创建支付订单失败，HTTP状态码: {response.status_code}")
                    return

                result = response.json()
                if result.get('code') != 1:
                    self.sender.reply(f"❌ 创建支付订单失败: {result.get('msg', '未知错误')}")
                    return

                pay_url = result.get('payurl', '')
                if not pay_url:
                    self.sender.reply("❌ 未获取到支付链接")
                    return

                self.sender.reply(f"""=====码支付=====
🎫 商品: 粉象授权
💰 金额: {total}元
⏰ 有效期: 5分钟
------------------
请点击链接完成支付:
{pay_url}

💡 支付过程中输入"q"可取消支付
===================""")

                for _ in range(60):
                    result_input = self.sender.listen(5000)
                    if result_input in ['q', 'Q']:
                        self.sender.reply("✅ 已取消支付")
                        return

                    check_url = gateway
                    if '/xpay/epay/api.php' not in check_url:
                        check_url = f"{check_url}/xpay/epay/api.php"
                    check_params = {
                        'act': 'order',
                        'pid': ma_pay_config['pid'],
                        'key': ma_pay_config['key'],
                        'out_trade_no': out_trade_no
                    }
                    try:
                        check_resp = requests.get(check_url, params=check_params, timeout=10)
                        check_result = check_resp.json()
                        if check_result.get('code') == 1 and check_result.get('status') == 1:
                            new_sqsj = self.update_auth_time(months)
                            if not new_sqsj:
                                self.sender.reply("更新授权时间失败")
                                return
                            self.sender.reply(f"""=====支付成功=====
🎈 商品: {project}
🎉 时长: {months}月
💰 支付: {total}元
📅 到期时间: {new_sqsj}
===================""")
                            return
                    except:
                        continue

                self.sender.reply("❌ 支付超时,请重新发起支付!")
                return
        except Exception as e:
            self.sender.reply(f"{e}或者超时了！")

    def update_auth_time(self, months):
        """更新授权时间
        Args:
            months (float): 授权月数
        Returns:
            str: 新的到期时间
        """
        try:
            ts = middleware.bucketGet('bd_fxcks', self.user)
            ts = eval(ts)
            
            # 计算新的到期时间
            days = int(months * 30)  # 将月转换为天数
            dqsj = datetime.now().strftime("%Y-%m-%d")
            
            if self.sqsj and self.sqsj > dqsj:
                # 如果现有授权未到期,在原到期时间基础上增加
                current_date = datetime.strptime(self.sqsj, "%Y-%m-%d") 
            else:
                # 如果已到期或无授权,从当前时间开始计算
                current_date = datetime.now()
                
            new_sqsj = current_date + timedelta(days=days)
            new_sqsj = new_sqsj.strftime("%Y-%m-%d")
            
            # 更新存储的授权时间
            if self.usid in ts:
                ts[self.usid]['sqsj'] = new_sqsj
                middleware.bucketSet('bd_fxcks', self.user, f'{ts}')
                
            return new_sqsj
            
        except Exception as e:
            self.sender.reply(f"更新授权时间失败: {str(e)}")
            return None

    def tx(self):
        ck = self.ck
        did = self.did
        oaid = random_string("1234567890abcdef", 16)
        data = {
            "orderType": 5,
            "withdrawAmount": self.ktxjes

        }
        headers = {
            'User-Agent': "okhttp-okgo/jeasonlzy",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
            'accept-language': "zh-CN,zh;q=0.8",
            'traceid': '',
            'platform': "android",
            'noncestr': '',
            'did': f'{did}',
            'timestamp': '',
            'version': "6.7.1",
            'oaid': f'{oaid}',
            'imei': "",
            'sign': '',
            'android_id': "",
            'meid': "",
            'serial': "",
            'uuid': f'{did}',
            'sti-data': "{}",
            'token': f'{ck}'
        }

        timestamp = f'{int(time.time() * 1000)}'
        headers['timestamp'] = timestamp

        traceid = f'{random_string("1234567890abcdef", 32)}'
        headers['traceid'] = traceid

        noncestr = random_string("1234567890abcdefghijklmnopqrstuvwxyz", 8)
        headers['noncestr'] = noncestr

        encode_str = f"粉象好牛逼nb3b16f5a02479a0e34df78d14aefe76orderType=5&withdrawAmount={self.ktxjes}did={did}&imei=&noncestr={noncestr}&oaid={oaid}&platform=android&timestamp={timestamp}&token={ck}&traceid={traceid}&version=6.7.1"

        sign = hashlib.md5(encode_str.encode()).hexdigest()
        headers['sign'] = sign

        try:
            r = requests.post(
                "https://api.fenxianglife.com/njia/order/withdraw/submit",
                headers=headers,
                json=data
            )
            success = r.json().get('success', None)
            if success:
                return r.json()
            else:
                return f"{self.name}>>>❌提现失败!\n{r.json().get('message', None)}"
        except Exception as e:
            return f'{self.name}>>>⛔提现异常!\n{e}'

    def get_ktxje(self):
        ck = self.ck
        did = self.did
        oaid = random_string("1234567890abcdef", 16)
        headers = {
            'User-Agent': "okhttp-okgo/jeasonlzy",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
            'accept-language': "zh-CN,zh;q=0.8",
            'traceid': '',
            'platform': "android",
            'noncestr': '',
            'did': f'{did}',
            'timestamp': '',
            'version': "6.7.1",
            'oaid': f'{oaid}',
            'imei': "",
            'sign': '',
            'android_id': "",
            'meid': "",
            'serial': "",
            'uuid': f'{did}',
            'sti-data': "{}",
            'token': f'{ck}'
        }

        timestamp = f'{int(time.time() * 1000)}'
        headers['timestamp'] = timestamp

        traceid = f'{random_string("1234567890abcdef", 32)}'
        headers['traceid'] = traceid

        noncestr = random_string("1234567890abcdefghijklmnopqrstuvwxyz", 8)
        headers['noncestr'] = noncestr

        encode_str = f"粉象好牛逼nb3b16f5a02479a0e34df78d14aefe76orderType=5did={did}&imei=&noncestr={noncestr}&oaid={oaid}&platform=android&timestamp={timestamp}&token={ck}&traceid={traceid}&version=6.7.1"

        sign = hashlib.md5(encode_str.encode()).hexdigest()
        headers['sign'] = sign

        try:
            r = requests.post(
                "https://api.fenxianglife.com/njia/order/withdraw/v4/create",
                headers=headers,
                json={
                    "orderType": 5
                }
            )
            success = r.json().get('success', None)
            if success:
                return r.json()
            else:
                return f"{self.name}>>>❌查询提现金额失败!\n{r.json().get('message', None)}"
        except Exception as e:
            return f'{self.name}>>>⛔查询提交金额异常!\n{e}'

    def fxyecx(self):
        """粉象余额查询 - 查询账号可提现金额"""
        ts = middleware.bucketGet('bd_fxcks', self.user)
        if ts == '' or ts == '{}':
            self.sender.reply("🔔粉象系统未查询到您的信息! 请先上车! ")
        else:
            ts = eval(ts)
            msg = '========粉象余额查询========\n'
            n = 0
            for k, y in ts.items():
                n += 1
                self.ck = y['ck']
                self.web_headers['token'] = self.ck
                self.did = y['did']
                self.web_headers['did'] = self.did
                self.name = y['name']
                # 如果旧账号没有sqsj，添加999天授权
                self.sqsj = y.get('sqsj', (datetime.now() + timedelta(days=999)).strftime("%Y-%m-%d"))
                
                if self.sqsj <= datetime.now().strftime("%Y-%m-%d"):
                    msg += f'{n}、{self.name}\n授权状态: ⏰已到期\n可提现额: --\n======================\n'
                else:
                    ktxje = self.get_ktxje()
                    if isinstance(ktxje, dict):
                        ktxjes = ktxje['data']['maxWithdrawAmount']
                        msg += f'{n}、{self.name}\n授权状态: ⏰{self.sqsj}\n可提现额: 💰{ktxjes / 100}元\n======================\n'
                    else:
                        msg += f'{n}、{self.name}\n授权状态: ⏰{self.sqsj}\n可提现额: ⛔查询失败\n======================\n'
            self.sender.reply(msg)

    def fxcx(self):
        ts = middleware.bucketGet('bd_fxcks', self.user)
        if ts == '' or ts == '{}':
            self.sender.reply("🔔粉象系统未查询到您的信息! 请先上车! ")
        else:
            ts = eval(ts)
            msg = '========粉象查询========\n'
            n = 0
            for k, y in ts.items():
                n += 1
                self.ck = y['ck']
                self.web_headers['token'] = self.ck
                self.did = y['did']
                self.web_headers['did'] = self.did
                self.usid = k
                self.name = y['name']
                # 如果旧账号没有sqsj，添加999天授权
                self.sqsj = y.get('sqsj', (datetime.now() + timedelta(days=999)).strftime("%Y-%m-%d"))
                if self.sqsj <= datetime.now().strftime("%Y-%m-%d"):
                    msg += f'{n}、{self.name}\n授权时间: ⏰{self.sqsj}(已到期)\n======================\n'
                else:
                    cx = self.get_rwinfo()
                    zjjg = self.get_zjinfo()
                    ktxje = self.get_ktxje()
                    if isinstance(cx, dict) and isinstance(zjjg, dict) and isinstance(ktxje, dict):
                        dateStr = cx['data']['openLotteryModule']['now']['dateStr']
                        ktxjes = ktxje['data']['maxWithdrawAmount']
                        today = datetime.today().strftime("%y%m%d")
                        tomorrow = datetime.today() + timedelta(days=1)
                        tomorrow = tomorrow.strftime("%y%m%d")
                        md = zjjg['data']['freeItem']
                        if md is None:
                            mdsp = '无免单商品'
                            itemPicUrl = None
                        else:
                            mdsp = md['itemTitle']
                            itemPicUrl = md['itemPicUrl']
                        if today == dateStr:
                            dateStr = cx['data']['openLotteryModule']['now']['dateStr']
                            jms = cx['data']['openLotteryModule']['now']['rewardCodes']
                            rewardCodes = cx['data']['openLotteryModule']['prev']['rewardCodes']
                            zjje = 0
                            for jg in rewardCodes:
                                zjje += jg['rewardAmount']
                                zjje += jg['subsidyAmount']
                            msg += f'{n}、{self.name}-{dateStr}期(未开奖)\n授权时间: ⏰{self.sqsj}\n当前余额: 💰{ktxjes / 100}\n当前奖码: 🏆{len(jms)}个\n昨日中奖: 🧧{zjje / 100}\n免单商品: 🎁{mdsp}\n======================\n'
                        elif tomorrow == dateStr:
                            dateStr = cx['data']['openLotteryModule']['prev']['dateStr']
                            jms = cx['data']['openLotteryModule']['now']['rewardCodes']
                            rewardCodes = cx['data']['openLotteryModule']['prev']['rewardCodes']
                            zjje = 0
                            for jg in rewardCodes:
                                zjje += jg['rewardAmount']
                                zjje += jg['subsidyAmount']
                            msg += f'{n}、{self.name}-{dateStr}期(已开奖)\n授权时间: ⏰{self.sqsj}\n当前余额: 💰{ktxjes / 100}\n当前奖码: 🏆{len(jms)}个\n今日中奖: 🧧{zjje / 100}\n免单商品: 🎁{mdsp}\n======================\n'
                            receiveAll = self.receiveAll()
                            if receiveAll is True:
                                pass
                            else:
                                self.sender.reply(f'⛔{self.name}\n{receiveAll}')
                        if itemPicUrl:
                            self.sender.reply(msg)
                            msg = '========粉象查询========\n'
                            self.sender.replyImage(itemPicUrl)
                    else:
                        msg += f'{n}、{self.name}\n查询失败: ⛔{cx}\n======================\n'
            if msg != '========粉象查询========\n':
                self.sender.reply(msg)

    def receiveAll(self):
        try:
            body = ''
            timestamp = f'{int(time.time() * 1000)}'
            self.web_headers['timestamp'] = timestamp

            traceid = f'{random_string("1234567890abcdef", 32)}'
            self.web_headers['traceid'] = traceid

            noncestr = f'{random.randint(1, 9)}{random_string("1234567890", 7)}'
            self.web_headers['noncestr'] = noncestr

            s = f'{body}did={self.did}&finger={self.finger}&noncestr={noncestr}&oaid={self.oaid}&platform=h5&timestamp={timestamp}&token={self.ck}&traceid={traceid}&version=1.0.0粉象好牛逼a8c19d8267527ea4c7d2f011acf7766f'

            md5 = hashlib.md5()
            md5.update(s.encode('utf-8'))
            encrypted_str = md5.hexdigest()
            self.web_headers['sign'] = f'{encrypted_str}'

            r = requests.post(
                "https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/periodical/open/result/receiveAll",
                json={},
                headers=self.web_headers
            )
            success = r.json().get('success', None)
            if success:
                return True
            else:
                return r.json().get('message', None)

        except Exception as e:
            return e

    def get_zjinfo(self):
        try:
            body = ''
            timestamp = f'{int(time.time() * 1000)}'
            self.web_headers['timestamp'] = timestamp

            traceid = f'{random_string("1234567890abcdef", 32)}'
            self.web_headers['traceid'] = traceid

            noncestr = f'{random.randint(1, 9)}{random_string("1234567890", 7)}'
            self.web_headers['noncestr'] = noncestr

            s = f'{body}did={self.did}&finger={self.finger}&noncestr={noncestr}&oaid={self.oaid}&platform=h5&timestamp={timestamp}&token={self.ck}&traceid={traceid}&version=1.0.0粉象好牛逼a8c19d8267527ea4c7d2f011acf7766f'

            md5 = hashlib.md5()
            md5.update(s.encode('utf-8'))
            encrypted_str = md5.hexdigest()
            self.web_headers['sign'] = f'{encrypted_str}'

            r = requests.get(
                "https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/withdraw/index",
                headers=self.web_headers
            )
            success = r.json().get('success', None)
            if success:
                return r.json()
            else:
                return r.json().get('message', None)

        except Exception as e:
            return e

    def get_rwinfo(self):
        try:
            body = 'plateform=android&version=6.7.1'
            timestamp = f'{int(time.time() * 1000)}'
            self.web_headers['timestamp'] = timestamp

            traceid = f'{random_string("1234567890abcdef", 32)}'
            self.web_headers['traceid'] = traceid

            noncestr = f'{random.randint(1, 9)}{random_string("1234567890", 7)}'
            self.web_headers['noncestr'] = noncestr

            s = f'{body}did={self.did}&finger={self.finger}&noncestr={noncestr}&oaid={self.oaid}&platform=h5&timestamp={timestamp}&token={self.ck}&traceid={traceid}&version=1.0.0粉象好牛逼a8c19d8267527ea4c7d2f011acf7766f'

            md5 = hashlib.md5()
            md5.update(s.encode('utf-8'))
            encrypted_str = md5.hexdigest()
            self.web_headers['sign'] = f'{encrypted_str}'

            r = requests.post(
                "https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/home/data/V2",
                json={
                    "plateform": "android",
                    "version": "6.7.1"
                },
                headers=self.web_headers
            )
            success = r.json().get('success', None)
            if success:
                return r.json()
            else:
                return r.json().get('message', None)

        except Exception as e:
            return e

    def fxyx(self):
        ts = middleware.bucketAllKeys('bd_fxcks')
        start_zhs = {}
        kong = 0
        wsqzhs = {}
        for i in ts:
            ts_data = middleware.bucketGet('bd_fxcks', f'{i}')
            ts_data = eval(ts_data)
            if ts_data == {}:
                kong += 1
                middleware.bucketDel('bd_fxcks', f'{i}')
                continue
            else:
                for k, y in ts_data.items():
                    sqsj = y.get('sqsj', datetime.now().strftime("%Y-%m-%d"))
                    if sqsj > datetime.now().strftime("%Y-%m-%d"):
                        start_zhs[k] = {
                            'name': y['name'],
                            'ck': y['ck'],
                            'did': y['did'],
                            'Imtype': y['Imtype'],
                            'sqsj': sqsj
                        }
                    else:
                        wsqzhs[i] = k
                        continue
        for k, y in wsqzhs.items():
            ts_data = middleware.bucketGet('bd_fxcks', f'{k}')
            ts_data = eval(ts_data)
            del ts_data[f'{y}']
            middleware.bucketSet('bd_fxcks', f'{k}', f'{ts_data}')

        notify = middleware.bucketGet('bd_fxconfig', 'notify')
        if notify == '':
            self.sender.reply(
                f"🔔粉象系统共获取到{len(start_zhs)}个账号！\n🔔删除未授权账号{len(wsqzhs)}个! \n🔔删除空账号{kong}个!\n🔔开始运行所有账号!")
        else:
            tsqd = notify.split(',')
            self.sender.reply(
                f"🔔粉象系统共获取到{len(start_zhs)}个账号！\n🔔删除未授权账号{len(wsqzhs)}个! \n🔔删除空账号{kong}个!\n🔔开始运行所有账号!")
            middleware.notifyMasters(
                f"🔔粉象系统共获取到{len(start_zhs)}个账号！\n🔔删除未授权账号{len(wsqzhs)}个! \n🔔删除空账号{kong}个!\n🔔开始运行所有账号!",
                tsqd)

        for k, y in start_zhs.items():
            self.ck = y['ck']
            self.web_headers['token'] = self.ck
            self.did = y['did']
            self.web_headers['did'] = self.did
            self.usid = k
            self.name = y['name']
            self.Imtype = y['Imtype']
            self.rwyx()
            time.sleep(1)

        if notify == '':
            self.sender.reply(f"🔔粉象系统所有账号运行完成!")
        else:
            tsqd = notify.split(',')
            self.sender.reply(f"🔔粉象系统所有账号运行完成")
            middleware.notifyMasters(
                f"🔔粉象系统所有账号运行完成",
                tsqd
            )

    def fxpz(self):
        yqurl = middleware.bucketGet('bd_fxconfig', 'yqurl')
        if yqurl == '':
            pz1 = '未配置'
        else:
            pz1 = '已配置'

        sdyx = middleware.bucketGet('bd_fxconfig', 'sdyx')
        if sdyx == '' or sdyx == 'false':
            sdyx = '否'
        elif sdyx == 'true':
            sdyx = '是'

        notify = middleware.bucketGet('bd_fxconfig', 'notify')
        if notify == '':
            notify = '未配置'

        wxzsm = middleware.bucketGet('bd_fxconfig', 'wxzsm')
        if wxzsm == '':
            pz4 = '未配置'
        else:
            pz4 = '已配置'

        sqje = middleware.bucketGet('bd_fxconfig', 'sqje')
        if sqje == '':
            sqje = 1

        sqsj = middleware.bucketGet('bd_fxconfig', 'sqsj')
        if sqsj == '':
            sqsj = 30

        msg = f'========粉象配置========\n1、邀请链接({pz1})\n2、管理员通知({notify})\n3、手动运行({sdyx})\n4、赞赏码({pz4})\n5、授权金额({sqje}元)\n6、授权时间({sqsj}天)\n======================\n回复序号,退出【q】！'
        self.sender.reply(msg)
        zh = self.sender.listen(60000)
        if zh == 'q' or zh == 'Q':
            self.sender.reply("退出！")
        elif zh is None:
            self.sender.reply(f'超时退出！')
        elif zh == '1':
            self.sender.reply('请发送您的邀请链接:app-我的-上面邀好友-复制链接')
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("退出！")
            elif pz is None:
                self.sender.reply(f'超时退出！')
            else:
                self.sender.replyImage(pz)
                middleware.bucketSet('bd_fxconfig', 'yqurl', f'{pz}')
                self.sender.reply('邀请链接配置成功!')
        elif zh == '3':
            self.sender.reply('设置是否运行用户手动运行, 输入(true/false)')
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("退出！")
            elif pz is None:
                self.sender.reply(f'超时退出！')
            else:
                middleware.bucketSet('bd_fxconfig', 'sdyx', f'{pz}')
                self.sender.reply(f'是否用户手动运行配置成功: {pz}')
        elif zh == '2':
            self.sender.reply('设置接受管理员通知的渠道，如 qq,wx,tg  用英文"，"符号分割,不设置不推送')
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("退出！")
            elif pz is None:
                self.sender.reply(f'超时退出！')
            else:
                middleware.bucketSet('bd_fxconfig', 'notify', f'{pz}')
                self.sender.reply(f'设置接受管理员通知的渠道: {pz}')
        elif zh == '4':
            self.sender.reply('请发送您的wx机器人赞赏码:')
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("退出！")
            elif pz is None:
                self.sender.reply(f'超时退出！')
            else:
                self.sender.replyImage(pz)
                middleware.bucketSet('bd_fxconfig', 'wxzsm', f'{pz}')
                self.sender.reply('赞赏码配置成功!')
        elif zh == '5':
            self.sender.reply('设置授权金额:')
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("退出！")
            elif pz is None:
                self.sender.reply(f'超时退出！')
            else:
                middleware.bucketSet('bd_fxconfig', 'sqje', f'{pz}')
                self.sender.reply(f'授权金额配置成功: {pz}元')
        elif zh == '6':
            self.sender.reply('设置授权时间:')
            pz = self.sender.listen(60000)
            if pz == 'q' or pz == 'Q':
                self.sender.reply("退出！")
            elif pz is None:
                self.sender.reply(f'超时退出！')
            else:
                middleware.bucketSet('bd_fxconfig', 'sqsj', f'{pz}')
                self.sender.reply(f'授权时间配置成功: {pz}天')
        else:
            self.sender.reply(f'输入有误!!')

    def fxsq(self):
        msg = f'========粉象授权========\n1、全部授权\n2、指定授权\n======================\n回复序号,退出【q】！'
        self.sender.reply(msg)
        zh = self.sender.listen(60000)
        if zh == 'q' or zh == 'Q':
            self.sender.reply("退出！")
        elif zh is None:
            self.sender.reply(f'超时退出！')
        elif zh == '1':
            self.qbsq()
        elif zh == '2':
            self.zdsq()
        else:
            self.sender.reply(f'输入有误!!')

    def qbsq(self):
        self.sender.reply(f"请输入给所有账号授权的天数！！\n回复序号,退出【q】！")
        sjts = self.sender.listen(60000)
        if sjts == 'q' or sjts == 'Q':
            self.sender.reply("退出！")

        elif sjts is None:
            self.sender.reply(f'超时退出！')

        elif isinstance(int(sjts), int):
            ts = middleware.bucketAllKeys('bd_fxcks')
            for i in ts:
                ts_data = middleware.bucketGet('bd_fxcks', f'{i}')
                ts_data = eval(ts_data)
                if ts_data == {}:
                    middleware.bucketDel('bd_fxcks', f'{i}')
                    continue
                else:
                    for k, y in ts_data.items():
                        sqsj = y.get('sqsj', datetime.now().strftime("%Y-%m-%d"))
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        if sqsj > dqsj:
                            sqsj = datetime.strptime(sqsj, "%Y-%m-%d")
                            new_sqsj = sqsj + timedelta(days=int(sjts))
                            new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                        else:
                            sj = datetime.now()
                            new_sqsj = sj + timedelta(days=int(sjts))
                            new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                        Imtype = y.get('Imtype', '')
                        ts_data[f'{k}'] = {
                            'name': y['name'],
                            'ck': y['ck'],
                            'did': y['did'],
                            'Imtype': f'{Imtype}',
                            'sqsj': f'{new_sqsj}'
                        }
                        middleware.bucketSet('bd_fxcks', f'{i}', f'{ts_data}')
            self.sender.reply(f"🔔粉象系统授权所有账号{int(sjts)}天全部完成！")

        else:
            self.sender.reply(f'{sjts} 输入有误，退出！')

    def zdsq(self):
        msg = f'请输入需要授权的账号id\n通过给机器人发送myuid获得\n退出【q】！'
        self.sender.reply(msg)
        myuid = self.sender.listen(60000)
        if myuid == 'q' or myuid == 'Q':
            self.sender.reply("退出！")
        elif myuid is None:
            self.sender.reply(f'超时退出！')
        else:
            ts = middleware.bucketGet('bd_fxcks', myuid)
            if ts == '' or ts == '{}':
                self.sender.reply(f"🔔粉象系统未查询到{myuid}的信息! 请先上车! ")
            else:
                ts = eval(ts)
                n = 0
                id_dict = {}
                msg = '========粉象授权========\n'
                for k, y in ts.items():
                    n += 1
                    self.ck = y['ck']
                    self.did = y['did']
                    self.Imtype = y.get('Imtype', '')
                    self.sqsj = y.get('sqsj', datetime.now().strftime("%Y-%m-%d"))
                    id_dict[n] = {
                        'usid': k,
                        'name': y['name'],
                        'ck': y['ck'],
                        'did': y['did'],
                        'Imtype': y['Imtype'],
                        'sqsj': self.sqsj
                    }
                    msg += f'{n}、{y["name"]}\n授权时间: ⏰{self.sqsj}\n======================\n'
                msg += f'0、全部授权\n======================\n回复序号选择账号,退出【q】！'
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
                    # 全部授权逻辑
                    msg = f'请输入给所有账号授权的天数！！\n回复序号,退出【q】！'
                    self.sender.reply(msg)
                    sjts = self.sender.listen(60000)
                    if sjts == 'q' or sjts == 'Q':
                        self.sender.reply("退出！")
                    elif sjts is None:
                        self.sender.reply(f'超时退出！')
                    elif isinstance(int(sjts), int):
                        # 遍历当前用户的所有账号进行授权
                        for k, y in ts.items():
                            sqsj = y.get('sqsj', datetime.now().strftime("%Y-%m-%d"))
                            dqsj = datetime.now().strftime("%Y-%m-%d")
                            if sqsj > dqsj:
                                sqsj = datetime.strptime(sqsj, "%Y-%m-%d")
                                new_sqsj = sqsj + timedelta(days=int(sjts))
                                new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                            else:
                                sj = datetime.now()
                                new_sqsj = sj + timedelta(days=int(sjts))
                                new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                            Imtype = y.get('Imtype', '')
                            ts[f'{k}'] = {
                                'name': y['name'],
                                'ck': y['ck'],
                                'did': y['did'],
                                'Imtype': f'{Imtype}',
                                'sqsj': f'{new_sqsj}'
                            }
                        middleware.bucketSet('bd_fxcks', myuid, f'{ts}')
                        self.sender.reply(f'========粉象授权========\n当前用户: {myuid}\n授权天数: {int(sjts)}天\n到期时间: {new_sqsj}\n已为该用户的所有账号授权成功！')
                    else:
                        self.sender.reply(f'{sjts} 输入有误，退出！')

                elif int(xz) in xz_list:
                    zh = id_dict[int(xz)]
                    self.usid = zh['usid']
                    self.ck = zh['ck']
                    self.did = zh['did']
                    self.name = zh['name']
                    self.Imtype = zh['Imtype']
                    self.sqsj = zh['sqsj']

                    msg = f'请输入给【{self.name}】授权的天数！！\n回复序号,退出【q】！'
                    self.sender.reply(msg)
                    sjts = self.sender.listen(60000)
                    if sjts == 'q' or sjts == 'Q':
                        self.sender.reply("退出！")

                    elif sjts is None:
                        self.sender.reply(f'超时退出！')

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
                        ts = middleware.bucketGet('bd_fxcks', f'{myuid}')
                        ts = eval(ts)
                        for k, y in ts.items():
                            if self.usid == k:
                                ts[f'{k}'] = {
                                    'name': self.name,
                                    'ck': self.ck,
                                    'did': self.did,
                                    'Imtype': self.Imtype,
                                    'sqsj': f'{new_sqsj}'
                                }
                                middleware.bucketSet('bd_fxcks', myuid, f'{ts}')
                                msg = f'========粉象授权========\n当前用户: {myuid}\n授权用户: {self.name}\n授权id: {self.usid}\n授权天数: {int(sjts)}天\n到期时间: {new_sqsj}'
                                self.sender.reply(msg)
                                break
                            else:
                                continue

                    else:
                        self.sender.reply(f'{sjts} 输入有误，退出！')
                else:
                    self.sender.reply(f'{xz} 输入有误，退出！')


if __name__ == '__main__':
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    user = sender.getUserID()
    message = sender.getMessage()
    atm_fx = ATM_FX(user, sender)
    if message == '粉象上车':
        atm_fx.fxsc()
    elif message == '粉象管理':
        atm_fx.fxgl()
    elif message == '粉象查询':
        atm_fx.fxcx()
    elif message == '粉象余额查询':
        atm_fx.fxyecx()
    elif message == '粉象运行':
        if sender.isAdmin():
            atm_fx.fxyx()
    elif message == '粉象配置':
        if sender.isAdmin():
            atm_fx.fxpz()
    elif message == '粉象授权':
        if sender.isAdmin():
            atm_fx.fxsq()
    elif message == '粉象教程':
        yqurl = middleware.bucketGet('bd_fxconfig', 'yqurl')
        if yqurl == '':
            yqurl = 'https://m.fenxianglife7.com/act/persistent/downloadFxApp/index.html?invitationCode=82XWGY'
        sender.reply(
            f"========粉象教程========\n"
            f"【登录方式】\n"
            f"1️⃣ 短信登录：不需要抓包，但会挤掉app\n"
            f"2️⃣ CK登录：需抓包粉象生活app\n"
            f"   域名：api.fenxianglife.com\n"
            f"   参数：token和did的值\n"
            f"======================\n"
            f"【用户指令】\n"
            f"🔹 粉象上车 - 登录/添加账号\n"
            f"🔹 粉象管理 - 管理账号(授权/运行/提现/推送)\n"
            f"🔹 粉象查询 - 查询账号信息\n"
            f"🔹 粉象余额查询 - 查询可提现金额\n"
            f"🔹 粉象教程 - 查看使用教程\n"
            f"🔹 粉象版本 - 查看版本信息\n"
            f"======================\n"
            f"【管理员指令】\n"
            f"🔸 粉象配置 - 配置插件参数\n"
            f"🔸 粉象运行 - 一键运行所有账号\n"
            f"🔸 粉象授权 - 手动授权管理\n"
            f"======================\n"
            f"💡 提示：目前一天3-6个奖码，中奖随缘！\n"
            f"📥 下载地址：{yqurl}\n"
        )
    elif message == '粉象版本':
        if sender.isAdmin():
            sender.reply(
                f"========粉象版本========\n🔔当前版本V6.32\n1、粉象管理新增手动提现\n2、修复粉象查询余额\n3、新增积分开通\n======================\n用户指令:\n上车指令: 粉象上车\n管理指令: 粉象管理\n查询指令: 粉象查询\n教程指令: 粉象教程\n======================\n管理员指令:\n插件配置: 粉象配置\n一键运行: 粉象运行\n版本查询: 粉象版本\n手动授权: 粉象授权\n======================")
    else:
        pass
        exit(0)
