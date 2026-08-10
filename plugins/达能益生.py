# [title: 达能益生]
# [language: python]
# [class: 工具类]
# [author: rujingxianghai]
# [rule: ^(达能)(登录|登陆)$|^登(录|陆)(达能)$|^(达能)(查询|管理)$|^(查询|管理)(达能)$|^清理达能$|^达能授权$|^达能教程$|^达能检测$|^达能一键运行$]
# [cron: 0 0 0 0 0]
# [priority: 0]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://img-upload.vorto.cc/1181250c1b48a6c8f51286678358529f.jpg]
# [version: 1.0.1]
# [public: true]
# [price: 3.88]
# [description: 达能益生(每周0.3r)<br>指令：达能登录、管理、查询、授权、教程<br>内置脚本]
# [param: {"required":true,"key":"S_DNYS_CONFIG.zsm","bool":false,"placeholder":"http://xxxx.co/xxx.jpg","name":"收款码链接","desc":"微信收款码/赞赏码链接"}]
# [param: {"required":true,"key":"S_DNYS_CONFIG.sqje","bool":false,"placeholder":"例:6.6,不填为0元","name":"授权价格","desc":"授权价格(单位:元)/月"}]
# [param: {"required":true,"key":"S_DNYS_CONFIG.sqsj","bool":false,"placeholder":"例:30,不填为30天","name":"授权天数","desc":"授权天数，默认30天/月"}]
# [param: {"required":false,"key":"S_DNYS_CONFIG.coin","bool":false,"placeholder":"不填为关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数）"}]
# [param: {"required":false,"key":"S_DNYS_CONFIG.notify","bool":false,"placeholder":"例:qq,wx,tb 多个用英文逗号分隔","name":"通知渠道","desc":"配置检测通知推送渠道"}]
# [param: {"required":false,"key":"S_DNYS_CONFIG.ma_pay_switch","bool":true,"placeholder":"","name":"码支付功能","desc":"开启后使用码支付，关闭则使用扫码支付"}]
# [param: {"required":false,"key":"S_DNYS_CONFIG.wxpusher_uids","bool":false,"placeholder":"例:UID_xxx,UID_yyy 多个用英文逗号分隔","name":"WxPusher推送UID","desc":"配置WxPusher的UID列表，用于推送任务统计"}]

import json
import time
import uuid
import hashlib
import random
import requests
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import middleware

# 获取用户信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

# 数据桶配置
BUCKET_USER = 'S_DNYS_USER'  # 用户账号列表
BUCKET_TOKEN = 'S_DNYS_TOKEN'  # 账号token信息
BUCKET_AUTH = 'S_DNYS_AUTH'  # 账号授权信息
BUCKET_CONFIG = 'S_DNYS_CONFIG'  # 插件配置

# 获取用户绑定的账号
uservalue = middleware.bucketGet(bucket=BUCKET_USER, key=userid)

# 支付方式中文名称映射
PAY_TYPE_NAMES = {
    'alipay': '支付宝',
    'wxpay': '微信支付',
    'qqpay': 'QQ钱包',
}

def mask_user_id(user_id):
    """user_id脱敏处理"""
    if not user_id or len(user_id) < 8:
        return user_id
    return f"{user_id[:4]}****{user_id[-4:]}"

def get_config(key, default=''):
    """获取配置"""
    return middleware.bucketGet(BUCKET_CONFIG, key) or default

def calculate_md5(text):
    """计算字符串的MD5值"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def sort_dict_by_key(data):
    """对字典按照键名排序"""
    return dict(sorted(data.items(), key=lambda x: x[0]))

def generate_qrcode(url):
    """生成二维码图片（支持本地API和第三方API）"""
    # 优先使用本地二维码API（如果配置了）
    qrcode_api_url = "https://qrcode.vorto.cn"
    qrcode_api_key = "4jpC3Cgd0zA7Z3HTJ6aDfW9QjtzitDGI"
    
    if qrcode_api_url:
        try:
            # 调用本地二维码API
            api_endpoint = f"{qrcode_api_url}/api/qrcode/generate"
            headers = {}
            if qrcode_api_key:
                headers['X-API-Key'] = qrcode_api_key
            
            response = requests.post(
                api_endpoint,
                json={'content': url},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data', {}).get('url'):
                    return result['data']['url']
        except Exception as e:
            # 如果本地API失败，降级使用第三方API
            pass
    
     #降级方案：使用第三方二维码API
    try:
        encoded_url = requests.utils.quote(url)
        api_url = f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M"
        return api_url
    except Exception as e:
        return None

def create_mapi_payment(config, amount, out_trade_no, name, user_id, pay_type, sitename=""):
    """创建支付订单 (mapi接口)"""
    try:
        params = {
            'pid': config['pid'],
            'type': pay_type,
            'out_trade_no': out_trade_no,
            'notify_url': config['notify_url'],
            'return_url': config['return_url'],
            'name': name,
            'money': str(amount),
            'sitename': sitename,
            'param': user_id
        }
        params = {k: v for k, v in params.items() if v}
        sorted_params = sort_dict_by_key(params)
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
        sign = calculate_md5(sign_str + config['key']).lower()
        params['sign'] = sign
        params['sign_type'] = 'MD5'
        
        mapi_url = config['gateway']
        if mapi_url.endswith('/'):
            mapi_url = mapi_url[:-1]
        mapi_url = f"{mapi_url}/mapi.php"
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(mapi_url, data=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return False, None, f"创建支付订单失败，HTTP状态码: {response.status_code}"
        
        try:
            result = response.json()
        except:
            return False, None, "创建支付订单失败，返回数据格式错误"
        
        code = result.get('code', 0)
        msg = result.get('msg', '未知状态')
        
        if code == 1:
            return True, result, msg
        else:
            return False, None, msg
            
    except Exception as e:
        return False, None, f"创建订单失败: {str(e)}"

def query_mapi_order(config, order_no, is_trade_no=False):
    """查询订单状态"""
    try:
        api_url = config['gateway']
        if api_url.endswith('/'):
            api_url = api_url[:-1]
        
        query_url = f"{api_url}/xpay/epay/api.php"
        params = {
            'act': 'order',
            'pid': config['pid'],
            'key': config['key']
        }
        
        if is_trade_no:
            params['trade_no'] = order_no
        else:
            params['out_trade_no'] = order_no
        
        response = requests.get(query_url, params=params, timeout=10)
        
        if response.status_code != 200:
            return False, None, f"查询订单失败，HTTP状态码: {response.status_code}"
        
        try:
            result = response.json()
        except:
            return False, None, "查询订单失败，返回数据格式错误"
        
        code = result.get('code', 0)
        if code == 1:
            return True, result, "查询成功"
        else:
            return False, None, result.get('msg', '查询失败')
            
    except Exception as e:
        return False, None, f"查询订单失败: {str(e)}"

def poll_mapi_payment_status(config, order_no, max_tries=30):
    """轮询MAPI支付状态"""
    for i in range(max_tries):
        success, data, msg = query_mapi_order(config, order_no, is_trade_no=False)
        
        if success and isinstance(data, dict) and data.get('status') == 1:
            return True, msg, data
        
        result = sender.listen(5000)
        if result == 'q':
            return False, "用户取消", None
    
    return False, "查询超时，订单可能尚未支付", None

# ========== 推送系统 ==========
def push_notification(title, content):
    """推送通知"""
    WXPUSHER_APP_TOKEN = 'AT_v7dTqxoP9PqVeosNzy2RrWZxmKIm5x4q'
    WXPUSHER_UIDS = get_config('wxpusher_uids', '')
    
    if not WXPUSHER_APP_TOKEN or not WXPUSHER_UIDS:
        print("未配置WxPusher推送参数，跳过推送")
        return False
    
    try:
        url = "http://wxpusher.zjiecode.com/api/send/message"
        uid_list = [uid.strip() for uid in WXPUSHER_UIDS.split(',') if uid.strip()]
        data = {
            "appToken": WXPUSHER_APP_TOKEN,
            "content": content,
            "summary": title,
            "contentType": 2,
            "uids": uid_list
        }
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("推送成功")
                return True
            else:
                print(f"推送失败：{result.get('msg', '未知错误')}")
                return False
        else:
            print(f"推送失败：HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"推送异常：{str(e)}")
        return False

def push_task_statistics(stats_data):
    """推送任务统计（表格样式）"""
    if not stats_data:
        print("没有统计数据，跳过推送")
        return False
    
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    current_day = datetime.now().strftime("%Y年%m月%d日")
    
    # 生成推送内容（参考图片样式）
    push_content = f"""
    <div style="font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
        <!-- 标题 -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
            <h2 style="margin: 0; font-size: 24px; font-weight: bold;">📊 达能益生 {current_day}</h2>
        </div>
        
        <!-- 今日统计卡片 -->
        <div style="background: linear-gradient(135deg, #67e8a8 0%, #20c997 100%); padding: 20px; margin: 15px; border-radius: 10px;">
            <h3 style="margin: 0 0 15px 0; text-align: center; color: white; font-size: 20px;">今日统计</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                <div style="flex: 1; min-width: 120px; background: rgba(255,255,255,0.95); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="color: #666; font-size: 14px; margin-bottom: 5px;">运行账号数</div>
                    <div style="font-size: 24px; font-weight: bold; color: #667eea;">{len(stats_data['account_details'])}个</div>
                </div>
                <div style="flex: 1; min-width: 120px; background: rgba(255,255,255,0.95); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="color: #666; font-size: 14px; margin-bottom: 5px;">成功执行</div>
                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">{stats_data['success_count']}个</div>
                </div>
            </div>
        </div>
        
        <!-- 账号明细表格 -->
        <div style="padding: 0 15px 15px 15px;">
            <h3 style="text-align: center; color: #333; font-size: 18px; margin-bottom: 15px;">账号明细</h3>
            <table style="width: 100%; border-collapse: collapse; background: #fff;">
                <thead>
                    <tr style="background: linear-gradient(135deg, #67e8a8 0%, #20c997 100%);">
                        <th style="padding: 12px 8px; text-align: center; color: white; font-size: 14px; border: 1px solid #ddd;">序号</th>
                        <th style="padding: 12px 8px; text-align: center; color: white; font-size: 14px; border: 1px solid #ddd;">用户备注</th>
                        <th style="padding: 12px 8px; text-align: center; color: white; font-size: 14px; border: 1px solid #ddd;">执行状态</th>
                        <th style="padding: 12px 8px; text-align: center; color: white; font-size: 14px; border: 1px solid #ddd;">任务数</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # 添加账号明细行
    for account in stats_data['account_details']:
        status_color = '#28a745' if account['status'] == '成功' else '#e74c3c'
        push_content += f"""
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 10px 8px; text-align: center; border: 1px solid #ddd; font-size: 13px;">{account['account_num']}</td>
                        <td style="padding: 10px 8px; text-align: center; border: 1px solid #ddd; font-size: 13px;">{account['remark']}</td>
                        <td style="padding: 10px 8px; text-align: center; border: 1px solid #ddd; font-size: 13px; color: {status_color}; font-weight: bold;">{account['status']}</td>
                        <td style="padding: 10px 8px; text-align: center; border: 1px solid #ddd; font-size: 13px;">{account['task_count']}个</td>
                    </tr>
        """
    
    # 添加总计行
    push_content += f"""
                    <tr style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); font-weight: bold;">
                        <td colspan="2" style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-size: 14px;">总计</td>
                        <td style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-size: 14px; color: #28a745;">成功{stats_data['success_count']}个</td>
                        <td style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-size: 14px;">-</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- 页脚 -->
        <div style="display: flex; justify-content: center; align-items: center; background: #f8f9fa; padding: 15px; color: #6c757d; font-size: 12px; border-top: 1px solid #dee2e6;">
            <p style="margin: 0;">🤖 达能益生任务系统<br>统计时间: {current_time}</p>
        </div>
    </div>
    """
    
    # 发送推送
    return push_notification(f"📊 达能益生 {current_day}", push_content)

# ========== 达能益生业务逻辑 ==========
class DNYX:
    def __init__(self, remark, token, openId, unionId):
        self.session = requests.Session()
        self.base_url = "https://api.digital4danone.com.cn"
        self.remark = remark
        self.token = token
        self.openId = openId
        self.unionId = unionId
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.current_task_date = None
        self.FORCE_NEW_CHALLENGE = True

    def log(self, cnt):
        return cnt

    def getHeaders(self):
        return {
            'User-Agent': self.ua,
            'mini-path': "%2Fpages%2Fmine%2Fmine",
            'source': "wechat_default",
            'Content-Type': "application/json",
            'sdk': "3.3.5",
            'xweb_xhr': "1",
            'privacySource': "base",
            'platform': "wechat",
            'X-Access-Token': self.token,
            'Sec-Fetch-Site': "cross-site",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Dest': "empty",
            'Referer': "https://servicewechat.com/wx28fabbff88261f5f/93/page-frame.html",
            'Accept-Language': "zh-CN,zh;q=0.9"
        }

    def commonGet(self, url):
        full_url = f"{self.base_url}{url}"
        headers = self.getHeaders()
        response = self.session.get(full_url, headers=headers, timeout=10)
        return response.json()

    def commonPost(self, url, data=None):
        full_url = f"{self.base_url}{url}"
        headers = self.getHeaders()
        response = self.session.post(full_url, headers=headers, data=json.dumps(data) if data else None, timeout=10)
        return response.json()

    def _random_delay(self, min_ms=3000, max_ms=5000):
        delay = random.uniform(min_ms / 1000, max_ms / 1000)
        time.sleep(delay)

    def openNewChallenge(self):
        """开启新一轮挑战"""
        url = "/healthyaging/danone/wx/ha/selfcare/openChallenge"
        headers = {
            'User-Agent': self.ua,
            'X-Access-Token': self.token,
            'Content-Type': 'application/json',
            'mini-path': "%2Fpages%2Fchallenge3%2Fchallenge3",
            'source': 'wechat_default',
            'sdk': '3.8.9',
            'xweb_xhr': '1',
            'privacySource': 'base',
            'platform': 'wechat',
            'Referer': 'https://servicewechat.com/wx28fabbff88261f5f/91/page-frame.html'
        }
        try:
            response = self.session.post(
                f"{self.base_url}{url}",
                headers=headers,
                data=json.dumps({}),
                timeout=10
            )
            result = response.json()
            if result.get("code") == 200:
                return True, "✅ 已成功开启新一轮挑战"
            else:
                return False, f"⚠️ 开启挑战失败: {result.get('message', '未知错误')}"
        except Exception as e:
            return False, f"❌ 开启新一轮挑战异常: {str(e)}"

    def executeTask(self, ruleId, taskId, taskName="", ruleIds=None, taskDataValue=None):
        if ruleIds is None:
            ruleIds = [ruleId]
        payload = {
            "ruleIds": ruleIds,
            "taskDataCode": "Auto",
            "taskDataValue": taskDataValue,
            "userTaskDetailId": taskId
        }
        try:
            res = self.commonPost("/healthyaging/danone/wx/clockin/clickIn", data=payload)
            if res.get("code") == 200:
                return True, f"✅ 执行 {taskName or '任务'} 成功"
            else:
                return False, f"⚠️ 执行 {taskName or '任务'} 失败: {res.get('message', '未知错误')}"
        except Exception as e:
            return False, f"❌ 执行 {taskName or '任务'} 异常: {str(e)}"

    def executeTaskBasedOnType(self, task):
        try:
            ruleIds = []
            taskDataValue = None
            view_code = task.get("viewCode")
            option_list = task.get("optionList", [])
            rule_list = task.get("ruleList", [])

            if view_code == "PICKER":
                opt = next((o for o in option_list if o.get("checkinStatus") == 1), None)
                if opt:
                    ruleIds = [opt["id"]]
                    taskDataValue = opt.get("name")
            elif view_code == "WATER":
                if option_list:
                    opt = option_list[-1]
                    ruleIds = [opt["id"]]
                    taskDataValue = opt.get("name")
            elif view_code == "MULTI":
                opts = [o for o in option_list if o.get("checkinStatus") == 1]
                if opts:
                    ruleIds = [o["id"] for o in opts]
                    taskDataValue = ",".join(o.get("name", "") for o in opts)
            elif view_code in ["FOOD", "WERUN"]:
                if rule_list and rule_list[0].get("id"):
                    ruleIds = [rule_list[0]["id"]]
                else:
                    ruleIds = [task.get("id")]
            else:
                if rule_list and rule_list[0].get("id"):
                    ruleIds = [rule_list[0]["id"]]
                else:
                    ruleIds = [task.get("id")]

            if not ruleIds:
                ruleIds = [task.get("id")]

            return self.executeTask(
                ruleId=ruleIds[0],
                taskId=task.get("userTaskDetailId"),
                taskName=task.get("simpleName", ""),
                ruleIds=ruleIds,
                taskDataValue=taskDataValue
            )

        except Exception as e:
            return False, f"❌ 执行 {task.get('simpleName', '任务')} 异常: {str(e)}"

    def getUserTasks(self):
        """获取今日任务并自动完成"""
        max_retries = 2
        retry_count = 0
        results = []

        while retry_count < max_retries:
            try:
                res = self.commonGet("/healthyaging/danone/wx/ha/selfcare/getCalendar")
                should_open_challenge = self.FORCE_NEW_CHALLENGE

                if res.get("code") == 200 and res.get("result", {}).get("taskCalendarList"):
                    task_list = res["result"]["taskCalendarList"]
                    today_task = next((t for t in task_list if t.get("istoday")), None)

                    if today_task:
                        self.current_task_date = today_task.get("taskDate")
                        results.append(f"✅ 获取 {self.current_task_date} 任务成功")
                        tasks = today_task.get("taskDetailsVoList", [])
                        has_unfinished = False

                        for task in tasks:
                            if task.get("status") == 1:
                                success, msg = self.executeTaskBasedOnType(task)
                                results.append(msg)
                                self._random_delay(3000, 5000)
                                has_unfinished = True
                            else:
                                results.append(f"✅ 已完成 {task.get('simpleName', '')}")

                        should_open_challenge = should_open_challenge or (today_task.get("istoday") and has_unfinished)
                    else:
                        results.append("🔍 今日无可用任务")
                        should_open_challenge = should_open_challenge or self.FORCE_NEW_CHALLENGE
                else:
                    results.append("🔍 今日无可用任务")
                    should_open_challenge = should_open_challenge or self.FORCE_NEW_CHALLENGE

                if should_open_challenge:
                    time.sleep(5)
                    success, msg = self.openNewChallenge()
                    results.append(msg)
                    if success:
                        retry_count += 1
                        time.sleep(1.5)
                        continue
                    else:
                        break
                else:
                    break

            except Exception as e:
                results.append(f"❌ 任务获取异常: {str(e)}")
                break
        
        return results

    def reportEvent(self):
        payload = {
            "content": "挑战页-浏览",
            "name": "maievent-page-view",
            "type": "view",
            "mobile": "",
            "openId": self.openId,
            "unionId": self.unionId,
            "page": "/pages/challenge3/challenge3",
            "source": "wechat-default",
            "sdk": "ha-default"
        }
        try:
            res = self.commonPost("/healthyaging/danone/wx/config/eventReport", data=payload)
            if res.get("code") == 200:
                return True, "✅ 事件上报成功"
            else:
                return False, f"⚠️ 事件上报失败: {res.get('message', '未知错误')}"
        except Exception as e:
            return False, f"❌ 事件上报异常: {str(e)}"
    
    def getChallengeId(self):
        res = self.commonGet("/healthyaging/danone/wx/ha/selfcare/getCalendar")
        return res["result"]["lastChallengeId"]
    
    def submitQues(self, data, title):
        res = self.commonPost("/healthyaging/danone/wx/ha/csq/submit", data=data)
        if res.get("code") == 200:
            p = {
                "page": "/pages/challenge3/challenge3",
                "content": "挑战页-自护力调研弹窗-点击",
                "name": "maievent-page-operate",
                "mobile": "",
                "openId": self.openId,
                "unionId": self.unionId,
                "source": "wechat-default",
                "sdk": "wechat-default"
            }
            res1 = self.commonPost("/healthyaging/danone/wx/config/eventReport", data=p)
            if res1.get("code") == 200:
                return True, f"✅ 提交问题[{title}]成功"
            else:
                return False, f"⚠️ 问题事件上报失败: {res1.get('message', '未知错误')}"
        else:
            return False, f"⚠️ 提交问题失败: {res.get('message', '未知错误')}"

    def getQuestion(self):
        data = {
            "answers": [
                {
                    "questionId": "159",
                    "value": [
                        "1014"
                    ]
                }
            ],
            "csqId": 10,
            "challengeId": 167616
        }
        try:
            data["challengeId"] = self.getChallengeId()
            res = self.commonGet("/healthyaging/danone/wx/ha/csq/get?type=feedback_v3")
            ques = res.get("result", {}).get("csqQuestionList", [])
            if len(ques) > 0:
                q = ques[0]
                data["answers"][0]["questionId"] = q["id"]
                data["answers"][0]["value"][0] = q["optionList"][0]["id"]
                data["csqId"] = res["result"]["csqId"]
                return self.submitQues(data, q["title"])
            return True, "✅ 无需提交问题"
        except Exception as e:
            return False, f"❌ 问题处理异常: {str(e)}"
    
    def run(self):
        results = []
        success, msg = self.getQuestion()
        results.append(msg)
        success, msg = self.reportEvent()
        results.append(msg)
        task_results = self.getUserTasks()
        results.extend(task_results)
        return results

def verify_account(token, openId, unionId):
    """验证账号是否有效"""
    try:
        dnyx = DNYX("验证", token, openId, unionId)
        res = dnyx.commonGet("/healthyaging/danone/wx/ha/selfcare/getCalendar")
        return res.get("code") == 200
    except:
        return False

# ========== 插件功能函数 ==========
def bind_account():
    """绑定达能益生账号（支持批量）"""
    sender.reply("""
=====达能益生登录=====
请按照格式输入账号信息
------------------
📝 格式: 备注#X-Access-Token#openId#unionId
📝 示例: 
张三#token123#openid456#unionid789
李四#token234#openid567#unionid890
------------------
💡 支持批量登录，每行一个账号
💡 回复"q"随时退出操作
==================""")
    
    input_text = sender.input(120000, 10000, False)
    
    if not input_text:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif input_text.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return
    
    accounts_list = []
    for line in input_text.split('\n'):
        line = line.strip()
        if '#' in line:
            parts = line.split('#')
            if len(parts) == 4:
                remark = parts[0].strip()
                token = parts[1].strip()
                openId = parts[2].strip()
                unionId = parts[3].strip()
                if remark and token and openId and unionId:
                    accounts_list.append({
                        'remark': remark,
                        'token': token,
                        'openId': openId,
                        'unionId': unionId
                    })
    
    if not accounts_list:
        sender.reply("""
=====格式错误=====
❌ 未检测到有效账号
------------------
请按照格式输入: 备注#token#openId#unionId
==================""")
        return
    
    success_count = 0
    fail_count = 0
    results = []
    
    current_accounts = eval(uservalue) if uservalue else []

    for idx, acc in enumerate(accounts_list, 1):
        remark = acc['remark']
        token = acc['token']
        openId = acc['openId']
        unionId = acc['unionId']
        
        try:
            if not verify_account(token, openId, unionId):
                fail_count += 1
                results.append(f"❌ {remark} - 账号验证失败")
                continue
            
            account_key = f"{openId}_{unionId}"
            if account_key not in current_accounts:
                current_accounts.append(account_key)
            
            account_info = {
                "token": token,
                "openId": openId,
                "unionId": unionId,
                "remark": remark,
                "create_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            middleware.bucketSet(BUCKET_TOKEN, account_key, json.dumps(account_info))
            
            dqsj = datetime.now().strftime("%Y-%m-%d")
            accountVip = middleware.bucketGet(BUCKET_AUTH, account_key)
            
            if accountVip and accountVip > dqsj:
                success_count += 1
                results.append(f"✅ {remark} - 已授权至{accountVip}")
            else:
                success_count += 1
                results.append(f"✅ {remark} - 登录成功，需授权")
            
            time.sleep(0.3)
        
        except Exception as e:
            fail_count += 1
            results.append(f"❌ {remark} - 异常: {str(e)}")
    
    middleware.bucketSet(BUCKET_USER, userid, str(current_accounts))
    
    result_msg = f"""
=====批量登录完成=====
📊 总数: {len(accounts_list)}个
✅ 成功: {success_count}个
❌ 失败: {fail_count}个
==================
"""
    for result in results:
        result_msg += result + "\n"
    
    result_msg += """==================
💡 发送"达能管理"可授权账号
💡 发送"达能查询"可查询信息
=================="""
    
    sender.reply(result_msg)

def query_accounts():
    """查询账号信息"""
    if not uservalue:
        sender.reply("""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送"达能登录"绑定
==================""")
        return
    
    accounts = eval(uservalue)
    account_list = """
========选择账号=======
[0] 全部账号"""
    
    for i, account_key in enumerate(accounts, 1):
        try:
            account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, account_key))
            remark = account_info.get('remark', account_key)
            auth_time = middleware.bucketGet(BUCKET_AUTH, account_key)
            
            if not auth_time:
                auth_status = '未授权'
            elif auth_time < str(datetime.now().date()):
                auth_status = '已过期'
            else:
                auth_status = f'到期:{auth_time}'
            
            account_list += f"""
[{i}]{remark}({auth_status})"""
        except:
            account_list += f"""
[{i}]{account_key}(信息异常)"""
    
    account_list += """
=====================
支持多选，用英文逗号分隔
例如: 1,2,3
回复"q"退出操作
====================="""
    
    sender.reply(account_list)
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出查询")
        return
    
    try:
        selected_accounts = []
        
        if choice == '0':
            selected_accounts = accounts.copy()
        else:
            indices = choice.split(',')
            for idx in indices:
                idx = idx.strip()
                if not idx.isdigit():
                    continue
                
                index = int(idx) - 1
                if 0 <= index < len(accounts):
                    selected_accounts.append(accounts[index])
        
        if not selected_accounts:
            sender.reply("❌ 未选择有效账号")
            return
        
        sender.reply(f"✅ 已选择 {len(selected_accounts)} 个账号，正在查询...")

        query_count = 0
        for account_key in selected_accounts:
            try:
                account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, account_key))
                auth_time = middleware.bucketGet(BUCKET_AUTH, account_key)
                auth_status = '已授权' if auth_time and auth_time >= str(datetime.now().date()) else '未授权'
                
                account_info_msg = f"""
=====账号信息[{query_count+1}/{len(selected_accounts)}]=====
📝 备注: {account_info.get('remark')}
🔐 授权状态: {auth_status}"""
                
                if auth_time:
                    account_info_msg += f"\n⏰ 到期时间: {auth_time}"
                
                account_info_msg += "\n=================="
                
                sender.reply(account_info_msg)
                query_count += 1
                
                if query_count < len(selected_accounts) and len(selected_accounts) > 3:
                    time.sleep(0.5)
            
            except Exception as e:
                sender.reply(f"""
=====查询失败[{query_count+1}/{len(selected_accounts)}]=====
🆔 账号: {account_key}
❌ 错误: {str(e)}
==================""")
                query_count += 1
        
        if query_count > 0:
            sender.reply(f"✅ 查询完成，共查询了 {query_count} 个账号")
    
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")

def manage_account():
    """账号管理功能"""
    if not uservalue:
        sender.reply("""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送"达能登录"绑定
==================""")
        return
    
    accounts = eval(uservalue)
    
    menu = """
=====账号管理=====
[1] 授权账号
[2] 删除账号
[3] 执行任务
------------------
回复数字选择功能
回复"q"退出操作
=================="""
    sender.reply(menu)
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    
    account_list = """
========选择账号=======
[0] 全部账号"""
    
    for i, account_key in enumerate(accounts, 1):
        try:
            account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, account_key))
            remark = account_info.get('remark', account_key)
            auth_time = middleware.bucketGet(BUCKET_AUTH, account_key)
            
            if not auth_time:
                auth_status = '未授权'
            elif auth_time < str(datetime.now().date()):
                auth_status = '已过期'
            else:
                auth_status = f'到期:{auth_time}'
            
            account_list += f"""
[{i}]{remark}({auth_status})"""
        except:
            account_list += f"""
[{i}]{account_key}(信息异常)"""
    
    account_list += """
=====================
支持多选，用英文逗号分隔
例如: 1,2,3
回复"q"退出操作
====================="""
    
    sender.reply(account_list)
    
    account_choice = sender.input(120000, 1, False)
    if not account_choice or account_choice.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return

    try:
        selected_accounts = []
        
        if account_choice == '0':
            selected_accounts = accounts.copy()
        else:
            indices = account_choice.split(',')
            for idx in indices:
                idx = idx.strip()
                if not idx.isdigit():
                    continue
                
                index = int(idx) - 1
                if 0 <= index < len(accounts):
                    selected_accounts.append(accounts[index])
        
        if not selected_accounts:
            sender.reply("❌ 未选择有效账号")
            return
        
        sender.reply(f"✅ 已选择 {len(selected_accounts)} 个账号")
        
        if choice == '1':
            authorize_multiple_accounts(selected_accounts)
        
        elif choice == '2':
            confirm = """
=====确认删除=====
⚠️ 此操作不可恢复
------------------
回复 y 确认删除
回复 n 取消操作
=================="""
            sender.reply(confirm)
            
            confirm_input = sender.input(120000, 1, False)
            if confirm_input and confirm_input.lower() == 'y':
                success_count = 0
                for account_key in selected_accounts:
                    try:
                        if account_key in accounts:
                            accounts.remove(account_key)
                        
                        middleware.bucketDel(BUCKET_TOKEN, account_key)
                        middleware.bucketDel(BUCKET_AUTH, account_key)
                        success_count += 1
                    except Exception as e:
                        print(f"删除账号失败: {account_key}, 错误: {str(e)}")
                
                if accounts:
                    middleware.bucketSet(BUCKET_USER, userid, str(accounts))
                else:
                    middleware.bucketDel(BUCKET_USER, userid)
                
                sender.reply(f"✅ 已成功删除 {success_count}/{len(selected_accounts)} 个账号")
            else:
                sender.reply("✅ 已取消删除")

        elif choice == '3':
            success_count = 0
            for account_key in selected_accounts:
                try:
                    account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, account_key))
                    remark = account_info.get('remark', account_key)
                    token = account_info.get('token')
                    openId = account_info.get('openId')
                    unionId = account_info.get('unionId')
                    
                    task_msg = f"""
=====任务执行: {remark}====="""
                    
                    dnyx = DNYX(remark, token, openId, unionId)
                    results = dnyx.run()
                    
                    for result in results:
                        task_msg += f"\n{result}"
                    
                    task_msg += "\n===================="
                    
                    sender.reply(task_msg)
                    
                    success_count += 1
                    
                    if success_count < len(selected_accounts):
                        time.sleep(2)
                
                except Exception as e:
                    sender.reply(f"""
=====任务执行失败=====
👤 账号: {remark}
❌ 错误: {str(e)}
=====================""")
            
            sender.reply(f"✅ 任务执行完成，共处理 {success_count}/{len(selected_accounts)} 个账号")
        
        else:
            sender.reply("❌ 无效的选择")
    
    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")

def authorize_multiple_accounts(account_keys):
    """授权多个账号"""
    account_infos = []
    for account_key in account_keys:
        try:
            account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, account_key))
            account_infos.append({
                'account_key': account_key,
                'info': account_info
            })
        except Exception as e:
            sender.reply(f"""
⚠️ 账号处理异常:
🆔 账号: {account_key}
❌ 原因: {str(e)}""")
    
    if not account_infos:
        sender.reply("❌ 没有有效的账号可授权")
        return
    
    auth_guide = """
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
    sender.reply(auth_guide)
    
    months = sender.input(120000, 1, False)
    if not months or months.lower() == 'q':
        sender.reply("✅ 已取消授权")
        return
    
    try:
        months = int(months)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return
        
        sqje = float(get_config('sqje', '6.6'))
        sqsj = int(get_config('sqsj', '30'))
        coin = int(get_config('coin', '0'))
        
        # 使用 Decimal 进行精确的货币计算
        total_money = float(
            (Decimal(str(len(account_infos))) * Decimal(str(months)) * Decimal(str(sqje)))
            .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        )
        
        available_payments = []
        
        ma_pay_switch = get_config('ma_pay_switch', 'false')
        
        if ma_pay_switch.lower() == 'true':
            ma_pay_type = middleware.bucketGet('dd_sign_config', 'ma_pay_type') or ''
            ma_pay_pid = middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or ''
            ma_pay_key = middleware.bucketGet('dd_sign_config', 'ma_pay_key') or ''
            ma_pay_gateway = middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or ''
            
            if ma_pay_gateway and ma_pay_pid and ma_pay_key:
                pay_types_str = ma_pay_type.strip() or "alipay,wxpay"
                pay_types = [p.strip() for p in pay_types_str.split(',') if p.strip()]
                
                for pay_type in pay_types:
                    name = PAY_TYPE_NAMES.get(pay_type, pay_type)
                    available_payments.append((name, f"mapay_{pay_type}"))
            else:
                zsm = get_config('zsm')
                if zsm:
                    available_payments.append(("微信支付", "wxpay"))
        else:
            zsm = get_config('zsm')
            if zsm:
                available_payments.append(("微信支付", "wxpay"))
        
        if coin > 0:
            available_payments.append(("积分兑换", "coin"))

        if not available_payments:
            sender.reply("""
=====授权失败=====
❌ 未配置任何支付方式
------------------
请联系管理员配置支付方式
==================""")
            return
        
        if len(available_payments) == 1:
            selected_payment = available_payments[0][1]
        else:
            payment_menu = f"""
=====选择支付方式=====
📊 账号数量: {len(account_infos)}个
⏰ 授权时长: {months}月
💰 总金额: {total_money:.2f}元
------------------"""
            
            for i, (name, _) in enumerate(available_payments, 1):
                if name == "积分兑换":
                    need_coin = coin * months * len(account_infos)
                    user_coin = middleware.bucketGet('dd_sign_points', userid) or '0'
                    payment_menu += f"\n[{i}] {name} ({need_coin}积分, 剩余:{user_coin})"
                else:
                    payment_menu += f"\n[{i}] {name}"
            
            payment_menu += """
------------------
回复数字选择支付方式
回复"q"退出操作
=================="""
            
            sender.reply(payment_menu)
            
            pay_choice = sender.input(120000, 1, False)
            if not pay_choice or pay_choice.lower() == 'q':
                sender.reply("✅ 已取消授权")
                return
            
            try:
                pay_index = int(pay_choice) - 1
                if 0 <= pay_index < len(available_payments):
                    selected_payment = available_payments[pay_index][1]
                else:
                    sender.reply("❌ 无效的选择")
                    return
            except:
                sender.reply("❌ 请输入有效的数字")
                return

        if selected_payment == "coin":
            need_coin = coin * months * len(account_infos)
            user_coin = int(middleware.bucketGet('dd_sign_points', userid) or '0')
            
            if user_coin < need_coin:
                sender.reply(f"""
=====积分不足=====
❌ 当前积分: {user_coin}
💡 需要积分: {need_coin}
==================""")
                return
            
            new_balance = user_coin - need_coin
            middleware.bucketSet('dd_sign_points', userid, str(new_balance))
            
            success_count = process_batch_authorization(account_infos, months, sqsj)
            
            sender.reply(f"""
=====支付成功=====
🎫 商品: 达能批量授权
💰 支付方式: 积分支付
💫 消耗积分: {need_coin}
💰 剩余积分: {new_balance}
📊 成功: {success_count}/{len(account_infos)}个账号
==================""")
        
        elif selected_payment == "wxpay":
            zsm = get_config('zsm')
            if not zsm:
                sender.reply("❌ 未配置收款码")
                return
            
            status = sender.atWaitPay()
            if status == "True" or status or status == "true":
                sender.reply("🔔目前有其他用户正在付款，请稍后再试！！")
                return
            
            sender.replyImage(zsm)
            sender.reply(f"""
=====微信扫码支付====
🎫 商品: 达能批量授权
📊 账号数量: {len(account_infos)}个
⏰ 时长: {months}月
💰 总金额: {total_money}元
------------------
请使用微信扫码支付
回复"q"取消支付
==================""")
            
            waitPay = sender.waitPay("q", 120000)
            
            if waitPay == 'q':
                sender.reply("✅ 已取消支付")
                return
            
            if isinstance(waitPay, str):
                waitPay = json.loads(waitPay)
            
            Money = float(waitPay['Money'])
            
            if Money >= total_money:
                success_count = process_batch_authorization(account_infos, months, sqsj)
                
                sender.reply(f"""
=====支付成功=====
💰 金额: {Money}元
📊 成功: {success_count}/{len(account_infos)}个账号
==================""")
            else:
                sender.reply(f"❌ 支付金额不足，应付{total_money}元，实付{Money}元")

        elif selected_payment.startswith("mapay_"):
            pay_type = selected_payment.replace("mapay_", "")
            
            config = {
                'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or '',
                'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or '',
                'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key') or '',
                'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or 'http://localhost/notify',
                'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url') or 'http://localhost/return'
            }
            
            if not (config['gateway'] and config['pid'] and config['key']):
                sender.reply("❌ 码支付配置不完整，请联系管理员")
                return
            
            amount = total_money  # total_money 已经是精确的浮点数
            out_trade_no = f"达能{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
            pay_type_name = PAY_TYPE_NAMES.get(pay_type, pay_type)
            
            try:
                success, result, msg = create_mapi_payment(
                    config=config,
                    amount=amount,
                    out_trade_no=out_trade_no,
                    name=f"达能益生批量授权-{str(amount)}",
                    user_id=userid,
                    pay_type=pay_type
                )
            except Exception as e:
                sender.reply(f'❌ 创建订单时出错: {str(e)}')
                return
            
            if not success:
                sender.reply(f'❌ 创建订单失败: {msg}')
                return
            
            trade_no = result.get('trade_no')
            if not trade_no:
                sender.reply('❌ 获取支付订单号失败')
                return
            
            gateway = config['gateway']
            if gateway.endswith('/'):
                gateway = gateway[:-1]
            pay_url = f"{gateway}/pay/{trade_no}"
            
            try:
                encoded_url = requests.utils.quote(pay_url)
                headers = {
                    'sec-ch-ua-platform': 'Windows',
                    'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'sec-ch-ua-mobile': '?0',
                    'Origin': 'https://www.mrw.so',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://www.mrw.so/',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
                }
                data = {
                    'urlStr': encoded_url,
                    'domain': 'mrw.so',
                    'expireType': '1',
                    'key': '5d7798c491d2c423c8c33d2d@631d0a6ffd3fbca7c2728bebc6602f98',
                    'random': str(int(time.time() * 1000))
                }
                response = requests.post('https://create.mrw.so/pageHome/createBySingle.htm', headers=headers, data=data, timeout=5)
                short_url = response.json().get('data')
                if short_url:
                    pay_url = short_url
            except:
                pass
            
            sender.reply(f'请使用【{pay_type_name}】扫描下方二维码完成支付:')
            sender.replyImage(generate_qrcode(pay_url))
            sender.reply('注意：实际金额可能有细微偏差，必须按页面实际金额付款！\n支付过程可输入"q"取消支付')
            
            is_paid, msg_result, data_result = poll_mapi_payment_status(config, out_trade_no)
            
            if is_paid:
                success_count = process_batch_authorization(account_infos, months, sqsj)
                
                sender.reply(f"""
=====支付成功=====
🎫 商品: 达能益生批量授权
💰 支付方式: {pay_type_name}
💰 金额: {amount}元
📊 成功: {success_count}/{len(account_infos)}个账号
==================""")
            else:
                sender.reply(f"❌ 支付未完成: {msg_result}")
        
        else:
            sender.reply("❌ 暂不支持该支付方式")
    
    except ValueError:
        sender.reply("❌ 请输入有效的数字")
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")

def process_batch_authorization(account_infos, months, sqsj):
    """处理批量授权"""
    success_count = 0
    today = datetime.now().strftime("%Y-%m-%d")
    
    for acc in account_infos:
        try:
            account_key = acc['account_key']
            current_auth = middleware.bucketGet(BUCKET_AUTH, account_key)
            
            if current_auth and current_auth > today:
                auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
                new_auth = auth_date + timedelta(days=sqsj * months)
            else:
                new_auth = datetime.now() + timedelta(days=sqsj * months)
            
            new_auth_str = new_auth.strftime("%Y-%m-%d")
            middleware.bucketSet(BUCKET_AUTH, account_key, new_auth_str)
            success_count += 1
        except:
            continue
    
    return success_count

def admin_authorize():
    """管理员授权功能"""
    if not sender.isAdmin():
        sender.reply("""
=====权限不足=====
❌ 此功能仅限管理员使用
==================""")
        return
    
    auth_menu = """
=====管理员授权=====
[1] 批量授权
[2] 单独授权
------------------
回复数字选择功能
回复"q"退出操作
=================="""
    sender.reply(auth_menu)
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消操作")
        return
    
    if choice == '1':
        all_users = []
        for key in middleware.bucketAllKeys(BUCKET_USER):
            userdata = middleware.bucketGet(BUCKET_USER, key)
            if userdata:
                user_accounts = eval(userdata)
                all_users.append({
                    'id': key,
                    'accounts': user_accounts
                })
        
        if not all_users:
            sender.reply("❌ 未找到任何用户")
            return
        
        total_accounts = sum(len(user['accounts']) for user in all_users)
        sender.reply(f"✅ 共找到 {len(all_users)} 个用户，{total_accounts} 个账号")

        sender.reply("""
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
==================""")
        
        months = sender.input(120000, 1, False)
        if not months or months.lower() == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        try:
            months = int(months)
            if months <= 0:
                sender.reply("❌ 月数必须大于0")
                return
            
            sender.reply(f"""
=====确认批量授权=====
⚠️ 将为全部 {total_accounts} 个账号授权 {months} 个月
------------------
回复 y 确认授权
回复 n 取消操作
==================""")
            
            confirm = sender.input(120000, 1, False)
            if confirm and confirm.lower() != 'y':
                sender.reply("✅ 已取消授权")
                return
            
            sqsj = int(get_config('sqsj', '30'))
            success_count = 0
            today = datetime.now().strftime("%Y-%m-%d")
            
            for user in all_users:
                for account_key in user['accounts']:
                    try:
                        current_auth = middleware.bucketGet(BUCKET_AUTH, account_key)
                        
                        if current_auth and current_auth > today:
                            start_date = datetime.strptime(current_auth, "%Y-%m-%d")
                        else:
                            start_date = datetime.now()
                        
                        new_expire = start_date + timedelta(days=sqsj * months)
                        middleware.bucketSet(BUCKET_AUTH, account_key, new_expire.strftime("%Y-%m-%d"))
                        success_count += 1
                    except:
                        continue
            
            sender.reply(f"""
=====批量授权结果=====
📊 总账号: {total_accounts}个
✅ 成功: {success_count}个
❌ 失败: {total_accounts - success_count}个
------------------
⏰ 授权: {months}个月
==================""")
        
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
    
    elif choice == '2':
        sender.reply("""
=====输入用户ID=====
请输入需要授权的用户ID
------------------
回复"q"退出操作
==================""")
        
        target_id = sender.input(120000, 1, False)
        if not target_id or target_id.lower() == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        userdata = middleware.bucketGet(BUCKET_USER, target_id)
        if not userdata:
            sender.reply("❌ 未找到该用户")
            return
        
        user_accounts = eval(userdata)
        sender.reply(f"✅ 用户 {target_id} 有 {len(user_accounts)} 个账号")
        
        account_list = """
========选择账号=======
[0] 全部账号"""
        
        for i, account_key in enumerate(user_accounts, 1):
            try:
                account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, account_key))
                remark = account_info.get('remark', account_key)
                auth_time = middleware.bucketGet(BUCKET_AUTH, account_key)
                
                if not auth_time:
                    auth_status = '未授权'
                elif auth_time < str(datetime.now().date()):
                    auth_status = '已过期'
                else:
                    auth_status = f'到期:{auth_time}'
                
                account_list += f"""
[{i}]{remark}({auth_status})"""
            except:
                account_list += f"""
[{i}]{account_key}(信息异常)"""
        
        account_list += """
=====================
支持多选，用英文逗号分隔
例如: 1,2,3
回复"q"退出操作
====================="""
        
        sender.reply(account_list)
        
        account_choice = sender.input(120000, 1, False)
        if not account_choice or account_choice.lower() == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        try:
            selected_accounts = []
            
            if account_choice == '0':
                selected_accounts = user_accounts.copy()
            else:
                indices = account_choice.split(',')
                for idx in indices:
                    idx = idx.strip()
                    if not idx.isdigit():
                        continue
                    
                    index = int(idx) - 1
                    if 0 <= index < len(user_accounts):
                        selected_accounts.append(user_accounts[index])
            
            if not selected_accounts:
                sender.reply("❌ 未选择有效账号")
                return
            
            sender.reply("""
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
==================""")
            
            months = sender.input(120000, 1, False)
            if not months or months.lower() == 'q':
                sender.reply("✅ 已取消授权")
                return
            
            months = int(months)
            if months <= 0:
                sender.reply("❌ 月数必须大于0")
                return
            
            sqsj = int(get_config('sqsj', '30'))
            success_count = 0
            today = datetime.now().strftime("%Y-%m-%d")
            
            for account_key in selected_accounts:
                try:
                    current_auth = middleware.bucketGet(BUCKET_AUTH, account_key)
                    
                    if current_auth and current_auth > today:
                        start_date = datetime.strptime(current_auth, "%Y-%m-%d")
                    else:
                        start_date = datetime.now()
                    
                    new_expire = start_date + timedelta(days=sqsj * months)
                    middleware.bucketSet(BUCKET_AUTH, account_key, new_expire.strftime("%Y-%m-%d"))
                    success_count += 1
                except:
                    continue
            
            sender.reply(f"""
=====授权结果=====
📊 选择账号: {len(selected_accounts)}个
✅ 成功: {success_count}个
❌ 失败: {len(selected_accounts) - success_count}个
------------------
⏰ 授权: {months}个月
==================""")
        
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
    
    else:
        sender.reply("❌ 无效的选择")

def check_auth_status():
    """检测所有账号的授权状态"""
    if not sender.isAdmin():
        sender.reply("""
=====权限不足=====
❌ 此功能仅限管理员使用
==================""")
        return
    
    try:
        notify_channels = get_config('notify', '')
        if not notify_channels:
            sender.reply("❌ 未配置通知渠道，请在插件配置中设置notify参数")
            return
        
        channels = [channel.strip() for channel in notify_channels.split(',') if channel.strip()]
        if not channels:
            sender.reply("❌ 通知渠道配置格式错误")
            return
        
        all_users = middleware.bucketAllKeys(BUCKET_USER)
        if not all_users:
            sender.reply("❌ 没有找到任何用户绑定的账号")
            return
        
        current_date = str(datetime.now().date())
        total_checked = 0
        total_notified = 0
        
        for user_id in all_users:
            try:
                accounts = eval(middleware.bucketGet(BUCKET_USER, user_id) or '[]')
                if not accounts:
                    continue
            except:
                continue
            
            expired_accounts = []
            invalid_accounts = []
            
            for account_key in accounts:
                total_checked += 1
                
                auth_time = middleware.bucketGet(BUCKET_AUTH, account_key)
                if not auth_time or auth_time <= current_date:
                    try:
                        account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, account_key))
                        remark = account_info.get('remark', account_key)
                        expired_accounts.append({
                            'remark': remark,
                            'auth_time': auth_time or '未授权'
                        })
                    except:
                        expired_accounts.append({
                            'remark': account_key,
                            'auth_time': auth_time or '未授权'
                        })
            
            if expired_accounts or invalid_accounts:
                notify_msg = "=====达能账号检测报告====="
                
                if expired_accounts:
                    notify_msg += "\n\n🚨 授权过期账号:"
                    notify_msg += "\n" + "-" * 25
                    for acc in expired_accounts:
                        notify_msg += f"\n📝 {acc['remark']} (到期:{acc['auth_time']})"
                
                if invalid_accounts:
                    notify_msg += "\n\n❌ 账号失效:"
                    notify_msg += "\n" + "-" * 20
                    for acc in invalid_accounts:
                        notify_msg += f"\n📝 {acc['remark']} ({acc['reason']})"
                
                notify_msg += "\n" + "-" * 20
                notify_msg += "\n💡 发送\"达能管理\"进行处理"
                notify_msg += "\n" + "=" * 14
                
                for channel in channels:
                    try:
                        middleware.push(
                            imType=channel,
                            groupCode='',
                            userID=user_id,
                            title="",
                            content=notify_msg
                        )
                        total_notified += 1
                    except Exception as e:
                        print(f"推送通知失败: {channel}, 用户: {user_id}, 错误: {str(e)}")
        
        sender.reply(f"✅ 检测完成，共检测 {total_checked} 个账号，发送 {total_notified} 条通知")
    
    except Exception as e:
        sender.reply(f"❌ 检测失败: {str(e)}")

def clean_expired_accounts():
    """清理过期账号"""
    if not sender.isAdmin():
        sender.reply("""
=====权限不足=====
❌ 此功能仅限管理员使用
==================""")
        return
    
    try:
        sender.reply("🧹 开始清理过期账号...")
        
        expired_accounts = []
        dqsj = datetime.now().strftime("%Y-%m-%d")
        
        for account_key in middleware.bucketAllKeys(BUCKET_AUTH):
            auth_time = middleware.bucketGet(BUCKET_AUTH, account_key)
            if auth_time and auth_time < dqsj:
                expired_accounts.append(account_key)
        
        if not expired_accounts:
            sender.reply("✅ 没有找到过期账号")
            return
        
        sender.reply(f"🔍 找到 {len(expired_accounts)} 个过期账号，开始清理...")
        
        success_count = 0
        for account_key in expired_accounts:
            try:
                middleware.bucketDel(BUCKET_TOKEN, account_key)
                middleware.bucketDel(BUCKET_AUTH, account_key)
                
                for uid in middleware.bucketAllKeys(BUCKET_USER):
                    user_accounts = middleware.bucketGet(BUCKET_USER, uid)
                    if user_accounts:
                        try:
                            accounts_list = eval(user_accounts)
                            if account_key in accounts_list:
                                accounts_list.remove(account_key)
                                if accounts_list:
                                    middleware.bucketSet(BUCKET_USER, uid, str(accounts_list))
                                else:
                                    middleware.bucketDel(BUCKET_USER, uid)
                                break
                        except:
                            continue
                
                success_count += 1
            except Exception as e:
                print(f"清理账号异常: {account_key}, 错误: {str(e)}")
        
        sender.reply(f"""
=====清理完成=====
📊 过期账号: {len(expired_accounts)}个
✅ 清理成功: {success_count}个
==================""")
    
    except Exception as e:
        sender.reply(f"""
=====清理异常=====
❌ 错误: {str(e)}
==================""")

def run_all_accounts():
    """一键运行所有已授权账号"""
    if not sender.isAdmin():
        sender.reply("""
=====权限不足=====
❌ 此功能仅限管理员使用
==================""")
        return
    
    try:
        sender.reply("🔄 开始一键运行所有已授权账号...")
        
        all_users = middleware.bucketAllKeys(BUCKET_USER)
        if not all_users:
            sender.reply("❌ 未找到任何用户")
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        total_accounts = 0
        valid_accounts = 0
        success_count = 0
        
        # 统计数据收集
        account_details = []
        account_num = 0
        
        for user_id in all_users:
            try:
                user_accounts = middleware.bucketGet(BUCKET_USER, user_id)
                if not user_accounts:
                    continue
                
                accounts = eval(user_accounts)
                
                for account_key in accounts:
                    total_accounts += 1
                    
                    auth_time = middleware.bucketGet(BUCKET_AUTH, account_key)
                    if not auth_time or auth_time <= today:
                        continue
                    
                    valid_accounts += 1
                    account_num += 1
                    
                    try:
                        account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, account_key))
                        remark = account_info.get('remark', account_key)
                        token = account_info.get('token')
                        openId = account_info.get('openId')
                        unionId = account_info.get('unionId')
                        
                        task_msg = f"\n🔄 执行账号: {remark}"
                        
                        dnyx = DNYX(remark, token, openId, unionId)
                        results = dnyx.run()
                        
                        task_count = len(results)
                        for result in results:
                            task_msg += f"\n  {result}"
                        
                        sender.reply(task_msg)
                        
                        success_count += 1
                        
                        # 收集统计数据
                        account_details.append({
                            'account_num': account_num,
                            'remark': remark,
                            'status': '成功',
                            'task_count': task_count
                        })
                        
                        if success_count < valid_accounts:
                            time.sleep(2)
                    
                    except Exception as e:
                        sender.reply(f"\n❌ 账号执行失败: {remark}, 错误: {str(e)}")
                        
                        # 收集失败账号数据
                        account_details.append({
                            'account_num': account_num,
                            'remark': remark,
                            'status': '失败',
                            'task_count': 0
                        })
                        continue
            
            except Exception as e:
                print(f"处理用户失败: {user_id}, 错误: {str(e)}")
                continue
        
        result_msg = f"""
=====一键运行完成=====
📊 总账号数: {total_accounts}个
✅ 已授权: {valid_accounts}个
🎯 执行成功: {success_count}个
❌ 执行失败: {valid_accounts - success_count}个
=================="""
        sender.reply(result_msg)
        
        # 推送统计数据
        if account_details:
            stats_data = {
                'account_details': account_details,
                'success_count': success_count
            }
            push_task_statistics(stats_data)
            sender.reply("📤 已发送推送通知")
    
    except Exception as e:
        sender.reply(f"""
=====运行异常=====
❌ 错误: {str(e)}
==================""")

def show_tutorial():
    """显示教程"""
    tutorial = """
=====达能益生教程=====
📱 用户指令:
• 达能登录 - 绑定账号
• 达能管理 - 管理账号
• 达能查询 - 查询信息
• 达能教程 - 查看教程
------------------
🔧 管理员指令:
• 达能授权 - 管理员授权
• 达能检测 - 检测账号状态
• 清理达能 - 清理过期账号
• 达能一键运行 - 运行所有账号
------------------
💡 登录格式:
📝 格式: 备注#X-Access-Token#openId#unionId
📝 示例: 
张三#token123#openid456#unionid789
李四#token234#openid567#unionid890
💡 支持批量登录，每行一个账号
------------------
📝 如何获取参数:
1. 打开达能益生小程序
2. 使用抓包工具抓取请求
3. 在api.digital4danone.com.cn域名下
4. 找到请求头中的:
   - X-Access-Token
   - openId (可能在请求参数中)
   - unionId (可能在请求参数中)
------------------
💰 功能说明:
• 自动完成每日任务
• 自动开启新挑战
• 自动提交问题调研
• 事件上报
------------------
🎯 使用流程:
1. 发送"达能登录"绑定账号
2. 发送"达能管理"进行授权
3. 在管理中选择"执行任务"
4. 自动完成所有任务
=================="""
    sender.reply(tutorial)

if __name__ == '__main__':
    message = sender.getMessage()
    
    if '登录' in message or '登陆' in message:
        bind_account()
    
    elif '管理' in message:
        manage_account()
    
    elif '查询' in message:
        query_accounts()
    
    elif '授权' in message:
        admin_authorize()
    
    elif '检测' in message:
        check_auth_status()
    
    elif '清理' in message:
        clean_expired_accounts()
    
    elif '一键运行' in message:
        run_all_accounts()
    
    elif '教程' in message:
        show_tutorial()
