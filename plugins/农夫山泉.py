# [pin:false]
# [disable:false]
# [title: 农夫山泉]
# [author: sky2022]
# [icon: https://uapis.cn/static/uploads/9b1643baac_q1mBS7qtm3iX.webp]
# [rule: ^农夫(上车|批量|管理|查询|运行|配置|版本|授权|教程)$]
# [admin: false]
# [service: 2661320550]
# [price: 12.88]
# [version: V7.4]
# [public:true]
# [description: 介绍：农夫山泉插件 插件自带任务!<br>更新：V7.0适配新版API接口<br>更新：支持批量授权用户<br>更新：支持中奖实时通知<br>更新：支持并发运行任务]
# [param: {"required":true,"key":"dd_nfsqconfig.wxzsm","bool":false,"placeholder":"http://127.0.0.1/赞赏码.png","name":"赞赏码链接","desc":"你的机器人赞赏码链接"}]
# [param: {"required":true,"key":"dd_nfsqconfig.sqje","bool":false,"placeholder":"6.6","name":"授权金额(元)","desc":"设置授权需要支付金额为多少元，默认不设置为6.6元"}]
# [param: {"required":true,"key":"dd_nfsqconfig.sqsj","bool":false,"placeholder":"30","name":"授权时间(天)","desc":"设置授权金额的授权天数，默认不设置为30天"}]
# [param: {"required":true,"key":"dd_nfsqconfig.yxbf","bool":false,"placeholder":"1","name":"运行并发数","desc":"设置管理员一键运行所有账号同时最多多少账号一起运行,默认1"}]
# [param: {"required":true,"key":"dd_nfsqconfig.notify","bool":false,"placeholder":"qq,wx","name":"管理员通知","desc":"设置接受管理员通知的渠道，如 qq,wx,tg 用英文逗号分割,不设置不推送"}]
# [param: {"required":true,"key":"dd_nfsqconfig.jfsl","bool":false,"placeholder":"200","name":"积分单价","desc":"设置每月授权需要的积分数量,默认200积分"}]
# [param: {"required":true,"key":"dd_nfsqconfig.use_amap","bool":true,"placeholder":"","name":"使用高德地图","desc":"开启则使用高德API解析地址(需配置key)，关闭则使用农夫山泉自带接口"}]
# [param: {"required":true,"key":"dd_nfsqconfig.amap_key","bool":false,"placeholder":"高德地图API的key","name":"高德地图key","desc":"申请地址：https://console.amap.com/dev/key/app，选择Web服务"}]
# [param: {"required":true,"key":"dd_nfsqconfig.default_address","bool":false,"placeholder":"广东省广州市天河区珠江新城123号","name":"默认地址","desc":"设置默认运行地址，输入完整地址即可自动解析"}]
# [param: {"required":true,"key":"dd_nfsqconfig.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]
# [param: {"required":true,"key":"dd_nfsqconfig.follow_lottery","bool":true,"placeholder":"","name":"农夫跟抽","desc":"开启后，有人中一等奖时全部账号立即使用该经纬度地址进行抽奖"}]

import concurrent.futures
import json
import random
import time
import uuid
import hashlib
import urllib.parse
from datetime import datetime, timedelta
from io import StringIO
import sys
import middleware
import requests

# ==================== 常量配置 ====================
BASE_URL = "https://sxs-consumer.nfsq.com.cn"
ADDRESS_URL = "https://sxs-consumer.nfsq.com.cn/geement.utils/api/v1/address/conversion/inverse"  # 经纬度逆地理编码
SCENE_LIST = ["SCENE-2510301509021", "SCENE-2510301508361"]
MAX_TOTAL_TRY = 8
DELAY_MIN, DELAY_MAX = 2, 4

# ==================== 工具函数 ====================
def get_config(key, default=''):
    """获取配置"""
    val = middleware.bucketGet('dd_nfsqconfig', key)
    return val if val else default

def get_headers(apitoken, unique_id):
    """生成请求头"""
    return {
        "authority": "sxs-consumer.nfsq.com.cn",
        "apitoken": apitoken,
        "content-type": "application/json",
        "unique_identity": unique_id,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781 NetType/WIFI MiniProgramEnv/Windows",
        "xweb_xhr": "1"
    }

def parse_ck(ck):
    """解析ck为apitoken和unique_id"""
    if "&" in ck:
        # 兼容旧格式: apitoken&unique_identity
        return ck.split('&', 1)
    else:
        # 新格式: 只需要apitoken，自动生成unique_identity
        return ck, str(uuid.uuid4())

def verify_token(apitoken, unique_id):
    """验证Token有效性"""
    headers = get_headers(apitoken, unique_id)
    url = f'{BASE_URL}/geement.usercenter/api/v1/user/seniority?sencodes=SEN2510301505321'
    try:
        r = requests.get(url, headers=headers, timeout=5)
        return r.json().get('code') == 200
    except:
        return False

def parse_address_by_amap(address):
    """通过高德API解析地址"""
    amap_key = get_config('amap_key')
    if not amap_key:
        return None
    try:
        url = f"https://restapi.amap.com/v3/geocode/geo?key={amap_key}&address={address}"
        res = requests.get(url, timeout=10).json()
        if res.get("status") == "1" and int(res.get("count", 0)) > 0:
            geo = res["geocodes"][0]
            loc = geo.get("location", "").split(",")
            return {
                "provice_name": geo.get("province", ""),
                "city_name": geo.get("city", "") or geo.get("province", ""),
                "area_name": geo.get("district", ""),
                "address": geo.get("formatted_address", ""),
                "longitude": float(loc[0]) if len(loc) == 2 else 0,
                "dimension": float(loc[1]) if len(loc) == 2 else 0
            }
    except:
        pass
    return None

def parse_address_by_nfsq(longitude, latitude):
    """通过农夫山泉接口逆地理编码"""
    try:
        params = {"longitude": longitude, "dimension": latitude}
        res = requests.get(ADDRESS_URL, params=params, timeout=10).json()
        if res.get("code") == 200 and res.get("data"):
            data = res["data"]
            return {
                "provice_name": data.get("province", ""),
                "city_name": data.get("city", "") or data.get("province", ""),
                "area_name": data.get("district", ""),
                "address": data.get("address", ""),
                "longitude": float(longitude),
                "dimension": float(latitude)
            }
    except:
        pass
    return None

def parse_address(address):
    """解析地址，根据配置选择使用高德或农夫山泉接口"""
    use_amap = get_config('use_amap', 'false').lower() == 'true'
    
    if use_amap:
        # 使用高德API
        return parse_address_by_amap(address)
    else:
        # 使用农夫山泉接口，需要先通过高德获取经纬度（或直接输入经纬度）
        # 这里先尝试用高德获取经纬度，再用农夫山泉接口获取详细地址
        amap_key = get_config('amap_key')
        if amap_key:
            try:
                url = f"https://restapi.amap.com/v3/geocode/geo?key={amap_key}&address={address}"
                res = requests.get(url, timeout=10).json()
                if res.get("status") == "1" and int(res.get("count", 0)) > 0:
                    loc = res["geocodes"][0].get("location", "").split(",")
                    if len(loc) == 2:
                        return parse_address_by_nfsq(loc[0], loc[1])
            except:
                pass
        # 如果没有高德key，尝试直接解析经纬度格式 "经度,纬度"
        if "," in address:
            parts = address.split(",")
            if len(parts) == 2:
                try:
                    return parse_address_by_nfsq(float(parts[0]), float(parts[1]))
                except:
                    pass
        return None

def get_location_data(user_info=None):
    """获取位置数据，优先使用用户自定义地址"""
    # 1. 优先使用用户自定义地址（已解析的）
    if user_info and all([user_info.get(k) for k in ['province', 'city', 'district', 'address', 'longitude', 'latitude']]):
        return {
            "provice_name": user_info['province'],
            "city_name": user_info['city'],
            "area_name": user_info['district'],
            "address": user_info['address'],
            "longitude": float(user_info['longitude']),
            "dimension": float(user_info['latitude'])
        }
    
    # 2. 使用全局默认地址配置
    default_address = get_config('default_address')
    if default_address:
        return parse_address(default_address)
    
    return None

def calc_new_expire(current_sqsj, days):
    """计算新的到期时间"""
    today = datetime.now().strftime("%Y-%m-%d")
    if current_sqsj and current_sqsj > today:
        base = datetime.strptime(current_sqsj, "%Y-%m-%d")
    else:
        base = datetime.now()
    return (base + timedelta(days=days)).strftime("%Y-%m-%d")

def notify_masters(msg):
    """发送管理员通知"""
    notify = get_config('notify')
    if notify:
        middleware.notifyMasters(msg, notify.split(','))

def pushplus_notify(title, content):
    """发送PushPlus通知到群组"""
    token = "3ed980ed47ab4c20aded07fe519fa864"
    topic = "1"  # 群组编码
    try:
        url = "http://www.pushplus.plus/send"
        data = {
            "token": token,
            "title": title,
            "content": content,
            "template": "html",
            "topic": topic  # 推送到群组
        }
        res = requests.post(url, json=data, timeout=10).json()
        return res.get('code') == 200
    except:
        return False

def parse_payment_result(result):
    """解析支付结果"""
    try:
        if isinstance(result, str):
            result = json.loads(result)
        # 支持多种格式
        if result.get('Type') == '微信赞赏' or result.get('Type') == '微信收款':
            return float(result.get('Money', 0)), result.get('Time', '').split('.')[0].replace('T', ' '), result.get('FromName', '')
        elif result.get('Money'):
            return float(result.get('Money', 0)), result.get('Time', '').replace('T', ' ').split('.')[0], result.get('FromName', '')
        elif result.get('money'):
            return float(result.get('money', 0)), result.get('time', '').replace('T', ' ').split('.')[0], result.get('fromName', '')
        return 0, '', ''
    except:
        return 0, '', ''

def get_payment_config():
    """获取支付配置"""
    zsm = get_config('wxzsm')
    use_ma_pay = get_config('use_ma_pay', 'false').lower() == 'true'
    
    ma_pay_config = None
    if use_ma_pay:
        # 从卡密系统获取码支付配置
        ma_pay_config = {
            'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
            'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
            'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
            'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
            'type': middleware.bucketGet('dd_sign_config', 'ma_pay_type'),
            'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url'),
            'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url')
        }
        # 验证配置完整性
        if ma_pay_config['switch'].lower() != 'true' or not all([ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
            use_ma_pay = False
            ma_pay_config = None
    
    return zsm, use_ma_pay, ma_pay_config

def generate_qrcode(url):
    """生成二维码图片"""
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        return f"https://api.qrtool.cn/?text={encoded_url}"
    except:
        return None

# ==================== 农夫山泉任务类 ====================
class NFSQ:
    def __init__(self, user, name, ck, usid):
        self.user = user
        self.name = name
        self.ck = ck
        self.usid = usid
        self.apitoken, self.unique_id = parse_ck(ck)
        self.headers = get_headers(self.apitoken, self.unique_id)

    def check_login(self):
        """检查登录状态"""
        url = f"{BASE_URL}/geement.usercenter/api/v1/user/seniority?sencodes=SEN2510301505321"
        try:
            res = requests.get(url, headers=self.headers, timeout=5).json()
            return res.get('code') == 200
        except:
            return False

    def do_tasks(self):
        """执行每日任务"""
        url = f'{BASE_URL}/geement.marketingplay/api/v1/task?pageNum=1&pageSize=10&task_status=2&status=1&group_id=2510301511011&is_db=1'
        try:
            h = self.headers.copy()
            h["content-type"] = "application/x-www-form-urlencoded"
            res = requests.get(url, headers=h, timeout=10).json()
            if res.get("code") == 200:
                tasks = res.get("data", [])
                print("🎯 扫描任务状态...")
                done = 0
                for t in tasks:
                    if t.get('complete_status') == 0:
                        self._join_task(t['id'], t['name'])
                        done += 1
                        time.sleep(1)
                if done == 0:
                    print("👌 任务已全部完成")
        except Exception as e:
            print(f"❌ 获取任务出错: {e}")

    def _join_task(self, task_id, name):
        """加入任务"""
        action_time = time.strftime("%Y-%m-%d %H:%M:%S")
        url = f'{BASE_URL}/geement.marketingplay/api/v1/task/join'
        params = {"action_time": action_time, "task_id": task_id}
        try:
            h = self.headers.copy()
            h["content-type"] = "application/x-www-form-urlencoded"
            res = requests.get(url, headers=h, params=params, timeout=10).json()
            if res.get('success'):
                print(f"✅ {name}: 完成")
            elif "已参与" in str(res.get("msg", "")):
                print(f"⏩ {name}: 已完成")
            else:
                print(f"❌ {name}: {res.get('msg', '未知错误')}")
        except Exception as e:
            print(f"❌ {name}: {e}")

    def receive_prize(self, log_id, goods_type=None):
        """领取奖品"""
        url = f"{BASE_URL}/geement.actjextra/api/v1/act/win/goods/youzan/receive"
        if goods_type == 160:
            url = f"{BASE_URL}/geement.actjextra/api/v1/act/win/goods/160goods/receive"
        try:
            h = self.headers.copy()
            h["content-type"] = "application/x-www-form-urlencoded"
            res = requests.post(url, headers=h, data=f"log_ids={log_id}", timeout=10).json()
            if res.get('code') == 200:
                print("🎁 奖品自动核销成功!")
            elif "160goods" not in url:
                url2 = f"{BASE_URL}/geement.actjextra/api/v1/act/win/goods/160goods/receive"
                requests.post(url2, headers=h, data=f"log_ids={log_id}", timeout=10)
        except:
            pass

    def lottery_once(self, scene_code, i, location_data):
        """单次抽奖"""
        url = f"{BASE_URL}/geement.marketinglottery/api/v1/marketinglottery"
        try:
            payload = {**location_data, "code": scene_code}
            res = requests.post(url, headers=self.headers, json=payload, timeout=10).json()
            
            if res.get('success'):
                prize = res.get('data', {}).get('prizedto')
                if prize:
                    name = prize.get('prize_name', '未知')
                    level = prize.get('prize_level', '')
                    icon = "🚨 欧皇!" if "一等奖" in str(level) else "🎉 中奖!"
                    print(f"{icon} [场景{scene_code[-5:]}] 第{i}次: [{level}] {name}")
                    
                    # 领取奖品
                    goods = prize.get('goods', [])
                    if goods:
                        self.receive_prize(goods[0].get('log_id'), goods[0].get('goods_type'))
                    
                    # 大奖通知
                    if "一等奖" in str(level):
                        self._send_win_notify(level, name, location_data)
                else:
                    print(f"💨 未中奖 [场景{scene_code[-5:]}] 第{i}次")
                return True
            else:
                msg = res.get('msg', '未知')
                if "请登录" in str(msg) or "token" in str(msg).lower():
                    print(f"🚫 Token失效，停止运行 ({msg})")
                    return "INVALID_TOKEN"
                if "不足" in str(msg) or "资格" in str(msg):
                    return False
                if "达到最大" in str(msg) or "上限" in str(msg):
                    print(f"🛑 每日额度已满 ({msg})")
                    return "STOP_ALL"
                print(f"⭕ 异常: {msg}")
                return True
        except Exception as e:
            print(f"❌ 抽奖出错: {e}")
            return True

    def _send_win_notify(self, level, name, location_data):
        """发送中奖通知"""
        msg = f"🎈农夫山泉中奖通知\n用户: {self.user}\n账号: {self.name}\n中奖: [{level}] {name}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        notify_masters(msg)
        
        # 一等奖推送PushPlus
        if "一等奖" in str(level):
            pushplus_content = f"""
            <h2>🎉 农夫山泉一等奖中奖通知</h2>
            <p><b>账号:</b> {self.name}</p>
            <p><b>奖品:</b> [{level}] {name}</p>
            <p><b>地址:</b> {location_data.get('provice_name', '')}{location_data.get('city_name', '')}{location_data.get('area_name', '')}</p>
            <p><b>经纬度:</b> {location_data.get('longitude', '')},{location_data.get('dimension', '')}</p>
            <p><b>时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            """
            pushplus_notify("🎉农夫山泉一等奖", pushplus_content)
        
        # 跟抽功能：中一等奖时保存经纬度并触发全员跟抽
        if "一等奖" in str(level) and get_config('follow_lottery', 'false').lower() == 'true':
            self._trigger_follow_lottery(location_data)

    def _trigger_follow_lottery(self, location_data):
        """触发全员跟抽"""
        print(f"🔥 触发跟抽! 经纬度: {location_data['longitude']},{location_data['dimension']}")
        notify_masters(f"🔥 农夫跟抽触发!\n中奖账号: {self.name}\n经纬度: {location_data['longitude']},{location_data['dimension']}\n正在为所有账号跟抽...")
        
        # 获取所有用户的所有账号
        today = datetime.now().strftime("%Y-%m-%d")
        all_users = middleware.bucketAllKeys('dd_nfsqcks') or []
        
        success_count = 0
        for user_key in all_users:
            if user_key == self.user:
                continue  # 跳过当前用户（已经中奖了）
            
            user_data = middleware.bucketGet('dd_nfsqcks', user_key)
            if not user_data:
                continue
            
            try:
                accounts = eval(user_data)
                for usid, info in accounts.items():
                    # 检查授权是否有效
                    if info.get('sqsj', '') <= today:
                        continue
                    
                    ck = info.get('ck', '')
                    if not ck:
                        continue
                    
                    try:
                        apitoken, unique_id = parse_ck(ck)
                        headers = get_headers(apitoken, unique_id)
                        
                        # 使用中奖的经纬度进行抽奖
                        for scene in SCENE_LIST:
                            url = f"{BASE_URL}/geement.marketinglottery/api/v1/marketinglottery"
                            payload = {**location_data, "code": scene}
                            res = requests.post(url, headers=headers, json=payload, timeout=10).json()
                            
                            if res.get('success'):
                                prize = res.get('data', {}).get('prizedto')
                                if prize:
                                    prize_name = prize.get('prize_name', '未知')
                                    prize_level = prize.get('prize_level', '')
                                    print(f"🎯 跟抽[{info['name']}]: [{prize_level}] {prize_name}")
                                    
                                    # 领取奖品
                                    goods = prize.get('goods', [])
                                    if goods:
                                        log_id = goods[0].get('log_id')
                                        goods_type = goods[0].get('goods_type')
                                        receive_url = f"{BASE_URL}/geement.actjextra/api/v1/act/win/goods/youzan/receive"
                                        if goods_type == 160:
                                            receive_url = f"{BASE_URL}/geement.actjextra/api/v1/act/win/goods/160goods/receive"
                                        h = headers.copy()
                                        h["content-type"] = "application/x-www-form-urlencoded"
                                        requests.post(receive_url, headers=h, data=f"log_ids={log_id}", timeout=10)
                                    
                                    # 如果跟抽也中大奖，通知管理员
                                    if "一等奖" in str(prize_level):
                                        notify_masters(f"🎉 跟抽大奖!\n账号: {info['name']}\n奖品: [{prize_level}] {prize_name}")
                                    
                                    success_count += 1
                                break  # 一个账号只抽一次
                            time.sleep(0.5)
                    except:
                        continue
            except:
                continue
        
        print(f"✅ 跟抽完成，共 {success_count} 个账号参与")
        notify_masters(f"✅ 跟抽完成，共 {success_count} 个账号参与抽奖")

    def run_lottery(self, location_data):
        """运行双通道混合抽奖"""
        print(f"🚀 开始双通道混合抽奖 (上限 {MAX_TOTAL_TRY} 次)...")
        current_try = 0
        while current_try < MAX_TOTAL_TRY:
            current_try += 1
            scene_active = False
            for scene in SCENE_LIST:
                result = self.lottery_once(scene, current_try, location_data)
                if result == "INVALID_TOKEN":
                    return False
                if result == "STOP_ALL":
                    print("🛑 触发每日上限，停止运行")
                    return True
                if result is True:
                    scene_active = True
                    break
            if not scene_active:
                print("💤 所有场景资格不足，结束")
                break
            time.sleep(random.randint(DELAY_MIN, DELAY_MAX))
        return True

    def query_prizes(self):
        """查询中奖信息（显示近5条）"""
        url = f'{BASE_URL}/geement.actjextra/api/v1/act/win/goods/simple?act_codes=ACT2510301507191%2CACT2510301505581'
        try:
            res = requests.get(url, headers=self.headers, timeout=10).json()
            if res.get("success") or res.get("code") == 200:
                data = res.get("data") or []
                if not data:
                    print("📭 暂无中奖记录")
                    return
                # 只显示近5条记录
                for i in data[:5]:
                    level = i.get("win_prize_level", '')
                    name = i.get('win_prize_name', '')
                    scan_time = i.get('scan_time', '')
                    if ("一等奖" in str(level) or "特等奖" in str(level)) and "十一等奖" not in str(level):
                        print(f"🌈{level} {name}")
                    else:
                        print(f"🎁{level} {name} ({scan_time})")
            else:
                print(f"❌ 查询失败: {res.get('msg', '未知错误')}")
        except Exception as e:
            print(f"❌ 查询出错: {e}")

    def main(self):
        """主任务"""
        try:
            print(f"\n============= 🌊 {self.name} =============")
            if not self.check_login():
                print("🚫 Token已失效，请重新抓包!")
                return False
            
            # 获取位置数据
            ts = middleware.bucketGet('dd_nfsqcks', self.user)
            user_info = eval(ts).get(self.usid, {}) if ts else {}
            location_data = get_location_data(user_info)
            
            if not location_data:
                print("⚠️ 请先配置运行地址!")
                return False
            
            print(f"📍 运行地址: {location_data['provice_name']}{location_data['city_name']}{location_data['area_name']}")
            
            print("\n----------- 📝 每日任务 -----------")
            self.do_tasks()
            time.sleep(1)
            
            print("\n----------- 🎲 双通道抽奖 -----------")
            self.run_lottery(location_data)
            
            print("\n----------- 🎁 中奖查询 -----------")
            self.query_prizes()
            
            print(f"\n============= 🏁 {self.name} 结束 =============\n")
            return True
        except Exception as e:
            print(f"\n❌ 运行出错: {e}")
            return False

# ==================== 管理类 ====================
class ATM_nfsq:
    def __init__(self, user, sender):
        self.user = user
        self.sender = sender
        self.usid = None
        self.ck = None
        self.name = None
        self.sqsj = None

    def _get_user_input(self, timeout=60000, allow_quit=True):
        """获取用户输入"""
        result = self.sender.listen(timeout)
        if result is None:
            self.sender.reply("⏰ 超时退出！")
            return None
        if allow_quit and result.lower() == 'q':
            self.sender.reply("✅ 已退出")
            return None
        return result

    def _get_user_data(self):
        """获取用户数据"""
        data = middleware.bucketGet('dd_nfsqcks', self.user)
        return eval(data) if data and data != '{}' else None

    def _save_user_data(self, data):
        """保存用户数据"""
        middleware.bucketSet('dd_nfsqcks', self.user, str(data))

    def _check_token(self, ck):
        """检查Token有效性"""
        try:
            apitoken, unique_id = parse_ck(ck)
            return verify_token(apitoken, unique_id)
        except:
            return False

    # ========== 上车 ==========
    def nfsc(self):
        """农夫上车"""
        self.sender.reply("欢迎使用农夫山泉系统，请先设置备注名(1-6字符)，退出输入'q'")
        name = self._get_user_input()
        if not name:
            return
        if len(name) > 6 or len(name) < 1:
            self.sender.reply("❌ 备注名不符合要求！")
            return

        self.sender.reply(f"""{name}! 你好!
抓包微信小程序: 农夫山泉生肖水
域名: sxs-consumer.nfsq.com.cn
请求头获取: apitoken
格式: 直接发送apitoken即可
请在120s内发送，退出回复'q'""")
        
        ck = self.sender.input(120000, 1000, False)
        if not ck or ck.lower() == 'q':
            self.sender.reply("已退出！")
            return

        try:
            apitoken, unique_id = parse_ck(ck)
            if not verify_token(apitoken, unique_id):
                self.sender.reply(f"❌ {name} Token验证失败，请检查后重试！")
                return

            data = self._get_user_data() or {}
            # 查找同名账号
            existing_usid = next((k for k, v in data.items() if v['name'] == name), None)
            
            if existing_usid:
                data[existing_usid]['ck'] = ck
                self._save_user_data(data)
                self.sender.reply(f"✅ {name} 更新成功！发送'农夫管理'管理账号")
            else:
                new_usid = str(uuid.uuid4())
                data[new_usid] = {'name': name, 'ck': ck, 'sqsj': datetime.now().strftime("%Y-%m-%d")}
                self._save_user_data(data)
                self.sender.reply(f"✅ {name} 登录成功！发送'农夫管理'管理账号")
        except ValueError as e:
            self.sender.reply(f"❌ {e}")
        except Exception as e:
            self.sender.reply(f"❌ 登录错误: {e}")

    def nfplsc(self):
        """农夫批量上车"""
        self.sender.reply("""========批量登录========
📝 格式说明:
每行一个账号，格式为: 备注名#apitoken
例如:
账号1#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
账号2#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
账号3#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

⚠️ 注意事项:
1. 备注名1-6个字符
2. 使用#号分隔备注名和token
3. 每行一个账号
4. 请在120s内发送，退出回复'q'
======================
请发送账号信息:""")
        
        content = self.sender.input(120000, 1000, False)
        if not content or content.lower() == 'q':
            self.sender.reply("已退出！")
            return

        lines = content.strip().split('\n')
        if not lines:
            self.sender.reply("❌ 未检测到账号信息！")
            return

        data = self._get_user_data() or {}
        success_count = 0
        fail_count = 0
        result_msg = "========批量登录结果========\n"
        
        for line in lines:
            line = line.strip()
            if not line or line.lower() == 'q':
                continue
            
            # 解析格式: 备注名#apitoken
            if '#' not in line:
                result_msg += f"❌ 格式错误: {line[:20]}...\n"
                fail_count += 1
                continue
            
            parts = line.split('#', 1)
            if len(parts) != 2:
                result_msg += f"❌ 格式错误: {line[:20]}...\n"
                fail_count += 1
                continue
            
            name = parts[0].strip()
            ck = parts[1].strip()
            
            # 验证备注名
            if len(name) > 6 or len(name) < 1:
                result_msg += f"❌ {name}: 备注名不符合要求(1-6字符)\n"
                fail_count += 1
                continue
            
            # 验证Token
            try:
                apitoken, unique_id = parse_ck(ck)
                if not verify_token(apitoken, unique_id):
                    result_msg += f"❌ {name}: Token验证失败\n"
                    fail_count += 1
                    continue
                
                # 查找同名账号
                existing_usid = next((k for k, v in data.items() if v['name'] == name), None)
                
                if existing_usid:
                    data[existing_usid]['ck'] = ck
                    result_msg += f"✅ {name}: 更新成功\n"
                else:
                    new_usid = str(uuid.uuid4())
                    data[new_usid] = {'name': name, 'ck': ck, 'sqsj': datetime.now().strftime("%Y-%m-%d")}
                    result_msg += f"✅ {name}: 登录成功\n"
                
                success_count += 1
            except Exception as e:
                result_msg += f"❌ {name}: {str(e)[:30]}\n"
                fail_count += 1
        
        # 保存数据
        if success_count > 0:
            self._save_user_data(data)
        
        result_msg += f"======================\n📊 成功: {success_count}个\n📊 失败: {fail_count}个\n发送'农夫管理'管理账号"
        self.sender.reply(result_msg)

    # ========== 管理 ==========
    def nfgl(self):
        """农夫管理"""
        data = self._get_user_data()
        if not data:
            self.sender.reply("❌ 未找到账号信息，请先上车！")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        msg = "========农夫管理========\n0、一键授权所有账号\n9999、一键运行所有账号\n======================\n"
        id_map = {}
        status_map = {}
        
        for i, (usid, info) in enumerate(data.items(), 1):
            self.ck = info['ck']
            status = '✅有效' if self._check_token(info['ck']) else '❌失效'
            expired = "(已到期)" if info['sqsj'] <= today else ""
            msg += f"{i}、{info['name']}\n状态: {status}\n授权: ⏰{info['sqsj']}{expired}\n======================\n"
            id_map[i] = {'usid': usid, **info}
            status_map[i] = status

        msg += "回复序号选择账号，退出【q】"
        self.sender.reply(msg)
        
        choice = self._get_user_input()
        if not choice:
            return

        if choice == '9999':
            self._run_all_accounts(data)
        elif choice == '0':
            self._batch_auth(data)
        elif choice.isdigit() and int(choice) in id_map:
            acc = id_map[int(choice)]
            self.usid, self.ck, self.name, self.sqsj = acc['usid'], acc['ck'], acc['name'], acc['sqsj']
            if '有效' in status_map[int(choice)]:
                self._manage_account()
            else:
                self.sender.reply("❌ 账号已失效，请先更新！")
        else:
            self.sender.reply("❌ 输入有误！")

    def _manage_account(self):
        """管理单个账号"""
        self.sender.reply(f"""========账号管理========
账号: {self.name}
1、账号授权
2、任务运行
3、删除账号
4、设置地址
======================
回复序号，退出【q】""")
        
        choice = self._get_user_input()
        if not choice:
            return
        
        actions = {'1': self._auth_account, '2': self._run_account, '3': self._delete_account, '4': self._set_address}
        if choice in actions:
            actions[choice]()
        else:
            self.sender.reply("❌ 输入有误！")

    def _run_account(self):
        """运行单个账号"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.sqsj <= today:
            self.sender.reply(f"❌ {self.name} 授权已到期，请先续费！")
            return

        self.sender.reply(f"🎮 开始为【{self.name}】运行任务...")
        
        old_stdout = sys.stdout
        output = StringIO()
        sys.stdout = output
        
        try:
            nfsq = NFSQ(self.user, self.name, self.ck, self.usid)
            nfsq.main()
            self.sender.reply(output.getvalue())
        except Exception as e:
            self.sender.reply(f"❌ 运行出错: {e}")
        finally:
            sys.stdout = old_stdout
            output.close()

    def _run_all_accounts(self, data):
        """运行所有账号"""
        yxbf = int(get_config('yxbf', '1'))
        today = datetime.now().strftime("%Y-%m-%d")
        valid = [(usid, info) for usid, info in data.items() if info['sqsj'] > today]
        
        self.sender.reply(f"🎮 开始运行\n⚡ 并发: {yxbf}\n✅ 有效账号: {len(valid)}个")
        
        for usid, info in valid:
            old_stdout = sys.stdout
            output = StringIO()
            sys.stdout = output
            try:
                nfsq = NFSQ(self.user, info['name'], info['ck'], usid)
                nfsq.main()
                self.sender.reply(output.getvalue())
            except Exception as e:
                self.sender.reply(f"❌ {info['name']} 出错: {e}")
            finally:
                sys.stdout = old_stdout
                output.close()
            time.sleep(1)
        
        self.sender.reply(f"🎉 运行完成，共 {len(valid)} 个账号")

    def _delete_account(self):
        """删除账号"""
        self.sender.reply(f"确认删除【{self.name}】？(y/n)")
        if self._get_user_input(allow_quit=False) == 'y':
            data = self._get_user_data()
            del data[self.usid]
            self._save_user_data(data)
            self.sender.reply(f"✅ {self.name} 删除成功！")
        else:
            self.sender.reply("已取消")

    def _set_address(self):
        """设置地址"""
        self.sender.reply("请输入详细地址(如:广东省广州市天河区xxx)，退出【q】")
        address = self._get_user_input()
        if not address:
            return

        # 调用高德API
        amap_key = get_config('amap_key')
        if not amap_key:
            self.sender.reply("❌ 请先配置高德地图API key")
            return

        try:
            url = f"https://restapi.amap.com/v3/geocode/geo?key={amap_key}&address={address}"
            res = requests.get(url, timeout=10).json()
            if res["status"] == "1" and int(res["count"]) > 0:
                geo = res["geocodes"][0]
                loc = geo.get("location", "").split(",")
                addr_info = {
                    'province': geo.get("province", ""),
                    'city': geo.get("city", "") or geo.get("province", ""),
                    'district': geo.get("district", ""),
                    'address': geo.get("formatted_address", ""),
                    'longitude': loc[0] if len(loc) == 2 else "",
                    'latitude': loc[1] if len(loc) == 2 else ""
                }
                
                data = self._get_user_data()
                data[self.usid].update(addr_info)
                self._save_user_data(data)
                
                self.sender.reply(f"""✅ 地址设置成功!
📍 {addr_info['province']}{addr_info['city']}{addr_info['district']}
📍 {addr_info['address']}
📍 经纬度: {addr_info['longitude']},{addr_info['latitude']}""")
            else:
                self.sender.reply("❌ 地址解析失败")
        except Exception as e:
            self.sender.reply(f"❌ 设置失败: {e}")

    # ========== 授权 ==========
    def _auth_account(self):
        """账号授权"""
        sqje = get_config('sqje', '6.6')
        sqsj = int(get_config('sqsj', '30'))
        jfsl = int(get_config('jfsl', '200'))

        if self.sender.isAdmin():
            self.sender.reply(f"=====管理员授权=====\n每月{sqsj}天\n请输入月数，退出【q】")
            months = self._get_user_input()
            if not months or not months.isdigit() or int(months) <= 0:
                self.sender.reply("❌ 输入无效！")
                return
            self._do_auth(int(months), sqsj, is_admin=True)
        else:
            # 获取用户积分
            user_points = int(middleware.bucketGet('dd_sign_points', self.user) or '0')
            zsm, use_ma_pay, _ = get_payment_config()
            
            # 构建支付选项菜单
            pay_menu = "=====授权开通====="
            option_num = 1
            options_map = {}
            
            if zsm:
                pay_menu += f"\n{option_num}️⃣ 微信支付: {sqje}元/{sqsj}天"
                options_map[str(option_num)] = 'wechat'
                option_num += 1
            
            if use_ma_pay:
                pay_menu += f"\n{option_num}️⃣ 码支付: {sqje}元/{sqsj}天"
                options_map[str(option_num)] = 'ma'
                option_num += 1
            
            if jfsl > 0:
                pay_menu += f"\n{option_num}️⃣ 积分支付: {jfsl}积分/{sqsj}天"
                pay_menu += f"\n   💫 当前积分: {user_points}"
                options_map[str(option_num)] = 'points'
            
            pay_menu += "\n------------------\n回复数字选择方式\n退出【q】"
            
            if not options_map:
                self.sender.reply("❌ 未配置任何支付方式，请联系管理员！")
                return
            
            self.sender.reply(pay_menu)
            choice = self._get_user_input()
            if not choice or choice not in options_map:
                self.sender.reply("❌ 输入无效！")
                return
            
            selected_pay = options_map[choice]

            self.sender.reply("请输入月数，退出【q】")
            months = self._get_user_input()
            if not months or not months.isdigit() or int(months) <= 0:
                self.sender.reply("❌ 输入无效！")
                return

            months = int(months)
            
            if selected_pay == 'points':
                total = jfsl * months
                if self._points_pay(total, sqsj * months):
                    self._do_auth(months, sqsj)
            elif selected_pay == 'wechat':
                total = float(sqje) * months
                if self._wechat_pay(total, sqsj * months):
                    self._do_auth(months, sqsj)
            elif selected_pay == 'ma':
                _, _, ma_pay_config = get_payment_config()
                total = float(sqje) * months
                if self._ma_pay(total, sqsj * months, ma_pay_config):
                    self._do_auth(months, sqsj)

    def _batch_auth(self, data):
        """批量授权"""
        sqje = get_config('sqje', '6.6')
        sqsj = int(get_config('sqsj', '30'))
        jfsl = int(get_config('jfsl', '200'))
        count = len(data)
        user_points = int(middleware.bucketGet('dd_sign_points', self.user) or '0')
        zsm, use_ma_pay, _ = get_payment_config()

        # 构建支付选项菜单
        pay_menu = f"=====批量授权=====\n📊 账号数: {count}个"
        option_num = 1
        options_map = {}
        
        if zsm:
            pay_menu += f"\n{option_num}️⃣ 微信支付: {sqje}元/{sqsj}天/账号"
            options_map[str(option_num)] = 'wechat'
            option_num += 1
        
        if use_ma_pay:
            pay_menu += f"\n{option_num}️⃣ 码支付: {sqje}元/{sqsj}天/账号"
            options_map[str(option_num)] = 'ma'
            option_num += 1
        
        if jfsl > 0:
            pay_menu += f"\n{option_num}️⃣ 积分支付: {jfsl}积分/{sqsj}天/账号"
            pay_menu += f"\n   💫 当前积分: {user_points}"
            options_map[str(option_num)] = 'points'
        
        pay_menu += "\n------------------\n回复数字选择方式\n退出【q】"
        
        if not options_map:
            self.sender.reply("❌ 未配置任何支付方式！")
            return
        
        self.sender.reply(pay_menu)
        choice = self._get_user_input()
        if not choice or choice not in options_map:
            return
        
        selected_pay = options_map[choice]

        self.sender.reply("请输入月数，退出【q】")
        months = self._get_user_input()
        if not months or not months.isdigit():
            return

        months = int(months)
        pay_success = False
        
        if selected_pay == 'points':
            total = jfsl * months * count
            pay_success = self._points_pay(total, sqsj * months)
        elif selected_pay == 'wechat':
            total = float(sqje) * months * count
            pay_success = self._wechat_pay(total, sqsj * months)
        elif selected_pay == 'ma':
            _, _, ma_pay_config = get_payment_config()
            total = float(sqje) * months * count
            pay_success = self._ma_pay(total, sqsj * months, ma_pay_config)

        if pay_success:
            for usid, info in data.items():
                data[usid]['sqsj'] = calc_new_expire(info['sqsj'], sqsj * months)
            self._save_user_data(data)
            self.sender.reply(f"✅ 批量授权成功！{count}个账号，{sqsj * months}天")
            notify_masters(f"批量授权: {self.user} 授权{count}个账号 {sqsj * months}天")

    def _do_auth(self, months, sqsj, is_admin=False):
        """执行授权"""
        data = self._get_user_data()
        if not data or self.usid not in data:
            self.sender.reply("❌ 账号不存在！")
            return
        
        new_sqsj = calc_new_expire(data[self.usid]['sqsj'], sqsj * months)
        data[self.usid]['sqsj'] = new_sqsj
        self._save_user_data(data)
        
        msg = f"✅ 授权成功\n账号: {self.name}\n天数: {sqsj * months}天\n到期: {new_sqsj}"
        self.sender.reply(msg)
        notify_masters(f"农夫授权: {self.name} {sqsj * months}天 到期{new_sqsj}")

    def _wechat_pay(self, total, days):
        """微信支付"""
        if total == 0:
            return True
        
        zsm = get_config('wxzsm')
        if not zsm:
            self.sender.reply("❌ 未配置收款码，请联系管理员！")
            return False

        # 检查支付状态
        if self.sender.atWaitPay():
            self.sender.reply("⚠️ 当前有人正在支付，请稍后再试！")
            return False

        self.sender.reply(f"""=====微信扫码支付=====
🎫 商品: 农夫山泉授权
📅 时长: {days}天
💰 金额: {total:.2f}元
------------------
请使用微信扫码支付
回复"q"取消支付""")
        self.sender.replyImage(zsm)

        result = self.sender.waitPay("q", 120000)
        if str(result).lower() == 'q' or result is None:
            self.sender.reply("❌ 已取消支付" if str(result).lower() == 'q' else "❌ 支付超时")
            return False

        money, pay_time, from_name = parse_payment_result(result)
        # 四舍五入到小数点后一位，避免浮点数精度问题
        if round(money, 1) >= round(total, 1):
            self.sender.reply(f"""=====支付成功=====
💰 金额: {money}元
⏰ 时间: {pay_time}
{f'👤 付款人: {from_name}' if from_name else ''}""")
            return True
        else:
            self.sender.reply(f"❌ 金额错误！应付: {round(total, 1)}元，实付: {round(money, 1)}元\n请联系管理员处理！")
            return False

    def _ma_pay(self, total, days, ma_pay_config):
        """码支付"""
        senderID = middleware.getSenderID()
        out_trade_no = f"NFSQ{int(time.time())}{self.user}"
        
        # 构造支付参数
        params = {
            'pid': ma_pay_config['pid'],
            'type': ma_pay_config['type'].split(',')[0] if ma_pay_config.get('type') else 'alipay',
            'out_trade_no': out_trade_no,
            'name': f"{senderID}-农夫山泉授权-{total}",
            'money': str(total),
            'notify_url': ma_pay_config['notify_url'] or '',
            'return_url': ma_pay_config['return_url'] or '',
            'param': self.user
        }
        
        # 按ASCII码排序并签名
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign = hashlib.md5((sign_str + ma_pay_config['key']).encode()).hexdigest().lower()
        params['sign'] = sign
        params['sign_type'] = 'MD5'
        
        # 构建mapi接口URL
        gateway = ma_pay_config['gateway'].rstrip('/')
        mapi_url = f"{gateway}/mapi.php"
        
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(mapi_url, data=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.sender.reply(f"❌ 创建支付订单失败，状态码: {response.status_code}")
                return False
            
            result = response.json()
            if result.get('code') == 1:
                payurl = result.get('payurl', '')
                if not payurl:
                    self.sender.reply("❌ 未获取到支付链接")
                    return False
                
                # 生成并发送二维码
                qrcode_url = generate_qrcode(payurl)
                pay_type = ma_pay_config['type'].split(',')[0] if ma_pay_config.get('type') else 'alipay'
                pay_type_names = {'alipay': '支付宝', 'wxpay': '微信', 'qqpay': 'QQ钱包'}
                pay_type_name = pay_type_names.get(pay_type, pay_type)
                
                if qrcode_url:
                    self.sender.replyImage(qrcode_url)
                    self.sender.reply(f"""=====码支付=====
🎫 商品: 农夫山泉授权
📅 时长: {days}天
💰 金额: {total}元
------------------
请使用【{pay_type_name}】扫码支付
回复"q"取消支付""")
                else:
                    self.sender.reply(f"支付链接: {payurl}\n请复制到浏览器完成支付")
                
                # 轮询订单状态
                for i in range(60):  # 最多等待5分钟
                    check_url = f"{gateway}/xpay/epay/api.php" if '/xpay/epay/api.php' not in gateway else gateway
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
                            self.sender.reply(f"""=====支付成功=====
🎫 商品: 农夫山泉授权
💰 金额: {total}元
📅 时长: {days}天""")
                            return True
                    except:
                        pass
                    
                    # 等待用户输入或超时
                    user_input = self.sender.listen(5000)
                    if user_input and user_input.lower() == 'q':
                        self.sender.reply("✅ 已取消支付")
                        return False
                
                self.sender.reply("❌ 支付超时，请重新发起支付！")
                return False
            else:
                msg = result.get('msg', '未知错误')
                self.sender.reply(f"❌ 创建订单失败: {msg}")
                return False
        except Exception as e:
            self.sender.reply(f"❌ 支付请求失败: {e}")
            return False

    def _points_pay(self, total, days):
        """积分支付"""
        # 使用 dd_sign_points 数据桶
        user_points = int(middleware.bucketGet('dd_sign_points', self.user) or '0')
        if user_points < total:
            self.sender.reply(f"❌ 积分不足！当前: {user_points}，需要: {int(total)}")
            return False
        
        self.sender.reply(f"""=====积分支付确认=====
💰 当前积分: {user_points}
💵 消耗积分: {int(total)}
📦 授权时长: {days}天
确认支付？[y]确认 [n]取消""")
        
        confirm = self._get_user_input(allow_quit=False)
        if confirm and confirm.lower() == 'y':
            new_balance = user_points - int(total)
            middleware.bucketSet('dd_sign_points', self.user, str(new_balance))
            self.sender.reply(f"✅ 支付成功！剩余积分: {new_balance}")
            return True
        self.sender.reply("已取消")
        return False

    # ========== 查询 ==========
    def nfcx(self):
        """农夫查询"""
        data = self._get_user_data()
        if not data:
            self.sender.reply("❌ 未找到账号信息，请先上车！")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        msg = "========农夫查询========\n"
        for usid, info in data.items():
            self.ck = info['ck']
            status = '✅有效' if self._check_token(info['ck']) else '❌失效'
            expired = "(已到期)" if info['sqsj'] <= today else ""
            msg += f"账号: {info['name']}\n状态: {status}\n授权: ⏰{info['sqsj']}{expired}\n"
            
            # 查询近5条中奖记录
            if '有效' in status:
                prizes = self._query_prizes_list(info['ck'])
                if prizes:
                    msg += "-------近5条中奖-------\n"
                    for p in prizes[:5]:
                        level = p.get("win_prize_level", '')
                        name = p.get('win_prize_name', '')
                        if ("一等奖" in str(level) or "特等奖" in str(level)) and "十一等奖" not in str(level):
                            msg += f"🌈{level} {name}\n"
                        else:
                            msg += f"🎁{level} {name}\n"
                else:
                    msg += "📭 暂无中奖记录\n"
            msg += "======================\n"
        self.sender.reply(msg)

    def _query_prizes_list(self, ck):
        """查询中奖列表（返回数据）"""
        try:
            apitoken, unique_id = parse_ck(ck)
            headers = get_headers(apitoken, unique_id)
            url = f'{BASE_URL}/geement.actjextra/api/v1/act/win/goods/simple?act_codes=ACT2510301507191%2CACT2510301505581'
            res = requests.get(url, headers=headers, timeout=10).json()
            if res.get("success") or res.get("code") == 200:
                return res.get("data") or []
        except:
            pass
        return []

    # ========== 配置 ==========
    def nfpz(self):
        """农夫配置"""
        configs = [
            ('wxzsm', '赞赏码'),
            ('sqje', '授权金额'),
            ('sqsj', '授权时间'),
            ('yxbf', '运行并发'),
            ('notify', '管理员通知'),
            ('jfsl', '积分单价'),
            ('amap_key', '高德地图key'),
            ('default_address', '默认地址'),
        ]
        
        msg = "========农夫配置========\n"
        for i, (key, name) in enumerate(configs, 1):
            val = get_config(key) or '未配置'
            if key in ['wxzsm', 'amap_key']:
                val = '已配置' if val != '未配置' else '未配置'
            msg += f"{i}、{name}({val})\n"
        msg += "======================\n回复序号修改，退出【q】"
        
        self.sender.reply(msg)
        choice = self._get_user_input()
        if not choice or not choice.isdigit():
            return

        idx = int(choice) - 1
        if 0 <= idx < len(configs):
            key, name = configs[idx]
            
            # 地址配置特殊处理
            if key == 'default_address':
                self.sender.reply("请输入完整地址(如: 广东省广州市天河区珠江新城123号)：")
                val = self._get_user_input()
                if val:
                    # 验证地址是否可解析
                    location = parse_address_by_amap(val)
                    if location:
                        middleware.bucketSet('dd_nfsqconfig', key, val)
                        self.sender.reply(f"""✅ 地址设置成功！
📍 省份: {location['provice_name']}
📍 城市: {location['city_name']}
📍 区域: {location['area_name']}
📍 详细: {location['address']}
📍 经纬度: {location['longitude']},{location['dimension']}""")
                    else:
                        self.sender.reply("❌ 地址解析失败，请检查高德key是否配置正确！")
            else:
                self.sender.reply(f"请输入新的{name}：")
                val = self._get_user_input()
                if val:
                    middleware.bucketSet('dd_nfsqconfig', key, val)
                    self.sender.reply(f"✅ {name}设置成功！")

    # ========== 一键运行(管理员) ==========
    def nfyx(self):
        """一键运行所有用户"""
        yxbf = int(get_config('yxbf', '1'))
        all_keys = middleware.bucketAllKeys('dd_nfsqcks')
        if not all_keys:
            self.sender.reply("❌ 没有用户数据！")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        total_valid = 0
        
        for uid in all_keys:
            data = middleware.bucketGet('dd_nfsqcks', uid)
            if not data or data == '{}':
                continue
            data = eval(data)
            for usid, info in data.items():
                if info['sqsj'] > today:
                    total_valid += 1

        self.sender.reply(f"🎮 开始运行\n⚡ 并发: {yxbf}\n✅ 有效账号: {total_valid}个")

        for uid in all_keys:
            data = middleware.bucketGet('dd_nfsqcks', uid)
            if not data or data == '{}':
                continue
            data = eval(data)
            for usid, info in data.items():
                if info['sqsj'] <= today:
                    continue
                old_stdout = sys.stdout
                output = StringIO()
                sys.stdout = output
                try:
                    nfsq = NFSQ(uid, info['name'], info['ck'], usid)
                    nfsq.main()
                    self.sender.reply(output.getvalue())
                except Exception as e:
                    self.sender.reply(f"❌ {info['name']} 出错: {e}")
                finally:
                    sys.stdout = old_stdout
                    output.close()
                time.sleep(1)

        self.sender.reply(f"🎉 全部运行完成！")

    # ========== 授权管理(管理员) ==========
    def nfsq(self):
        """管理员授权"""
        self.sender.reply("""========农夫授权========
1、一键授权所有用户
2、单独授权用户
======================
回复序号，退出【q】""")
        
        choice = self._get_user_input()
        if choice == '1':
            self._admin_batch_auth()
        elif choice == '2':
            self._admin_single_auth()

    def _admin_batch_auth(self):
        """管理员批量授权"""
        all_keys = middleware.bucketAllKeys('dd_nfsqcks')
        if not all_keys:
            self.sender.reply("❌ 没有用户数据！")
            return

        self.sender.reply("请输入授权天数，退出【q】")
        days = self._get_user_input()
        if not days or not days.isdigit():
            return

        days = int(days)
        count = 0
        for uid in all_keys:
            data = middleware.bucketGet('dd_nfsqcks', uid)
            if not data or data == '{}':
                continue
            data = eval(data)
            for usid in data:
                data[usid]['sqsj'] = calc_new_expire(data[usid]['sqsj'], days)
                count += 1
            middleware.bucketSet('dd_nfsqcks', uid, str(data))

        self.sender.reply(f"✅ 批量授权完成！{count}个账号，{days}天")

    def _admin_single_auth(self):
        """管理员单独授权"""
        self.sender.reply("请输入用户ID(myuid)，退出【q】")
        uid = self._get_user_input()
        if not uid:
            return

        data = middleware.bucketGet('dd_nfsqcks', uid)
        if not data or data == '{}':
            self.sender.reply("❌ 未找到该用户！")
            return

        data = eval(data)
        msg = "========用户账号========\n0、全部授权\n"
        id_map = {}
        for i, (usid, info) in enumerate(data.items(), 1):
            msg += f"{i}、{info['name']} (到期: {info['sqsj']})\n"
            id_map[i] = usid
        msg += "======================\n回复序号选择，退出【q】"
        
        self.sender.reply(msg)
        choice = self._get_user_input()
        if not choice or not choice.isdigit():
            return
        
        choice_num = int(choice)
        if choice_num != 0 and choice_num not in id_map:
            self.sender.reply("❌ 输入有误！")
            return

        self.sender.reply("请输入授权天数，退出【q】")
        days = self._get_user_input()
        if not days or not days.isdigit():
            return

        days = int(days)
        if choice_num == 0:
            # 全部授权
            for usid in data:
                data[usid]['sqsj'] = calc_new_expire(data[usid]['sqsj'], days)
            middleware.bucketSet('dd_nfsqcks', uid, str(data))
            self.sender.reply(f"✅ 授权成功！该用户全部账号({len(data)}个) {days}天")
        else:
            # 单个授权
            usid = id_map[choice_num]
            data[usid]['sqsj'] = calc_new_expire(data[usid]['sqsj'], days)
            middleware.bucketSet('dd_nfsqcks', uid, str(data))
            self.sender.reply(f"✅ 授权成功！{data[usid]['name']} {days}天，到期: {data[usid]['sqsj']}")

# ==================== 主入口 ====================
if __name__ == '__main__':
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    user = sender.getUserID()
    message = sender.getMessage()
    
    atm = ATM_nfsq(user, sender)
    
    commands = {
        '农夫上车': atm.nfsc,
        '农夫批量': atm.nfplsc,
        '农夫管理': atm.nfgl,
        '农夫查询': atm.nfcx,
        '农夫运行': lambda: atm.nfyx() if sender.isAdmin() else None,
        '农夫配置': lambda: atm.nfpz() if sender.isAdmin() else None,
        '农夫授权': lambda: atm.nfsq() if sender.isAdmin() else None,
        '农夫版本': lambda: sender.reply("""当前版本V7.0
🔔功能介绍:
1、V7.0适配新版API接口
2、支持批量授权用户
3、支持中奖实时通知
4、支持并发运行任务
5、支持自定义地址
======================
📱用户指令: 农夫上车/批量/管理/查询
⚙️管理员: 农夫配置/运行/授权
======================
🎯每日任务:
✨ 每日签到
🎲 双通道混合抽奖
📝 中奖查询""") if sender.isAdmin() else None,
        '农夫教程': lambda: sender.reply("""📖 农夫山泉使用教程
🔍 抓包说明:
1、打开微信小程序：农夫山泉生肖水
2、抓包域名: sxs-consumer.nfsq.com.cn
3、请求头获取: apitoken 
4、数据有效期为三天！

💡 使用说明:
• 发送【农夫上车】绑定单个账号
• 发送【农夫批量】绑定多个账号
• 发送【农夫批量】批量绑定账号
• 发送【农夫管理】管理账号
• 发送【农夫查询】查询状态

✨ 功能介绍:
• 每日签到任务
• 双通道混合抽奖
• 中奖实时推送
• 奖品自动核销

📝 批量登录格式:
每行一个账号: 备注名#apitoken
例如:
账号1#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
账号2#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...""")
    }
    
    if message in commands:
        cmd = commands[message]
        if cmd:
            cmd()
