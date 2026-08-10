#[title: 甬派注册机]
# [rule: ^甬音注册$|^甬音注册查询$|^甬音专属注册$|^甬音专属列表$|^甬音状态$|^甬音注册清理$]
# [disable:true]
# [platform: qq,wx]
# [public:true]
# [open_source: false]
# [class: 工具类]
# [version: 1.5.5]
# [price: 8.88]
# [admin: false]
# [icon: https://i.mji.rip/2025/07/11/0cd0134e7522d7633360ab7dc8131f27.jpeg]
# [author: linzixuan]
# [service: 2661320550]
# [description: 甬音平台批量注册账号插件<br>支持普通项目ID:910196对接和自定义专属对接码<br>支持甬派专属对接码配置自动对接<br>适配呆呆积分支付<br><br>指令：<br>甬音注册：执行普通项目批量注册<br>甬音专属注册：使用专属对接码注册<br>甬音专属列表：查看已对接的专属项目<br>甬音状态：查询平台余额<br>甬音注册查询：查询用户注册账号<br>甬音注册清理：清理用户的注册记录<br>版本：1.5.3 更换接口<br>版本：1.5.4 优化注册逻辑，优化注册返回日志，专属没返回验证码就是，手机号下卡，平台没下号，会自动处理，也可以换专属<br>版本：1.5.5 优化积分返回逻辑]

# 插件参数配置
# [param: {"required":true,"key":"G_yongyinreg_config.username","name":"椰汁平台账号","placeholder":"请输入椰汁平台账号","desc":"椰汁平台的登录账号"}]
# [param: {"required":true,"key":"G_yongyinreg_config.password","name":"椰汁平台密码","placeholder":"请输入椰汁平台密码","desc":"椰汁平台的登录密码"}]
# [param: {"required":false,"key":"G_yongyinreg_config.zsm","name":"收款码","placeholder":"http://example.com/pay.jpg"}]
# [param: {"required":false,"key":"G_yongyinreg_config.price","name":"普通项目售价","placeholder":"0.88","desc":"向用户收取的普通项目价格"}]
# [param: {"required":false,"key":"G_yongyinreg_config.special_price","name":"专属项目售价","placeholder":"0.50","value":"0.50","desc":"向用户收取的专属项目价格"}]
# [param: {"required":false,"key":"G_yongyinreg_config.points_per_month","name":"普通项目积分/号","placeholder":"100","value":"100","desc":"普通项目每个账号所需积分数量"}]
# [param: {"required":false,"key":"G_yongyinreg_config.special_points","name":"专属项目积分/号","placeholder":"60","value":"60","desc":"专属项目每个账号所需积分数量"}]
# [param: {"required":false,"key":"G_yongyinreg_config.max_project_price","name":"专属成本价上限","placeholder":"0.15","value":"0.15","desc":"允许使用的专属项目最大成本价，超过此价格将拒绝对接"}]
# [param: {"required":false,"key":"G_yongyinreg_config.yongpai_code","name":"甬派专属对接码","placeholder":"910196----ZW5I2J","desc":"甬派专属对接码，填写后将自动对接此项目"}]

import middleware
import requests
import json
import time
import hashlib
import random
import uuid
import string
import re
from datetime import datetime, timedelta

# 获取发送者信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

# ===== 配置区 =====
# 注册设置
DEFAULT_PASSWORD = "Abc123456"  # 默认注册密码，如不使用自定义密码时将使用此密码
REGISTER_COUNT = 5  # 需要注册的账号数量
USE_PROXY = False  # 是否使用代理IP
RELEASE_WAIT_TIME = 200  # 释放手机号前等待的秒数，建议不少于200秒
# ==================

# 日志函数
def log_message(message, level="info"):
    """输出日志信息"""
    prefix = "ℹ"
    if level == "error":
        prefix = "❌"
    elif level == "success":
        prefix = "✅"
    elif level == "warning":
        prefix = "⚠"
    print(f"{prefix} {message}")

# 获取椰汁平台账号密码
def get_platform_credentials():
    """获取椰汁平台账号密码"""
    username = middleware.bucketGet(bucket='G_yongyinreg_config', key='username') or ""
    password = middleware.bucketGet(bucket='G_yongyinreg_config', key='password') or ""
    return username, password

# 中国主要城市经纬度范围
CHINA_REGIONS = [
    # 北京
    {"name": "北京", "lat_min": 39.4, "lat_max": 41.0, "lng_min": 115.7, "lng_max": 117.4},
    # 上海
    {"name": "上海", "lat_min": 30.7, "lat_max": 31.5, "lng_min": 120.9, "lng_max": 122.0},
    # 广州
    {"name": "广州", "lat_min": 22.8, "lat_max": 23.3, "lng_min": 112.9, "lng_max": 114.0},
    # 深圳
    {"name": "深圳", "lat_min": 22.4, "lat_max": 22.8, "lng_min": 113.8, "lng_max": 114.6},
    # 杭州
    {"name": "杭州", "lat_min": 29.8, "lat_max": 30.5, "lng_min": 119.9, "lng_max": 120.5},
    # 南京
    {"name": "南京", "lat_min": 31.7, "lat_max": 32.2, "lng_min": 118.5, "lng_max": 119.2},
    # 成都
    {"name": "成都", "lat_min": 30.4, "lat_max": 31.0, "lng_min": 103.8, "lng_max": 104.4},
    # 重庆
    {"name": "重庆", "lat_min": 29.4, "lat_max": 29.9, "lng_min": 106.3, "lng_max": 107.0},
    # 武汉
    {"name": "武汉", "lat_min": 30.4, "lat_max": 30.8, "lng_min": 114.0,
      "lng_max": 114.6},
    # 西安
    {"name": "西安", "lat_min": 34.1, "lat_max": 34.5, "lng_min": 108.7, "lng_max": 109.1},
    # 郑州
    {"name": "郑州", "lat_min": 34.6, "lat_max": 34.9, "lng_min": 113.5, "lng_max": 113.9},
    # 合肥
    {"name": "合肥", "lat_min": 31.7, "lat_max": 32.0, "lng_min": 117.1, "lng_max": 117.5},
    # 南昌
    {"name": "南昌", "lat_min": 28.6, "lat_max": 28.8, "lng_min": 115.8, "lng_max": 116.0},
    # 长沙
    {"name": "长沙", "lat_min": 28.1, "lat_max": 28.3, "lng_min": 112.8, "lng_max": 113.1},
    # 福州
    {"name": "福州", "lat_min": 25.9, "lat_max": 26.2, "lng_min": 119.1, "lng_max": 119.5},
    # 济南
    {"name": "济南", "lat_min": 36.6, "lat_max": 36.8, "lng_min": 116.9, "lng_max": 117.2},
    # 太原
    {"name": "太原", "lat_min": 37.7, "lat_max": 38.0, "lng_min": 112.5, "lng_max": 112.7},
    # 沈阳
    {"name": "沈阳", "lat_min": 41.7, "lat_max": 42.0, "lng_min": 123.3, "lng_max": 123.6},
    # 哈尔滨
    {"name": "哈尔滨", "lat_min": 45.7, "lat_max": 45.9, "lng_min": 126.5, "lng_max": 126.7},
    # 长春
    {"name": "长春", "lat_min": 43.8, "lat_max": 44.0, "lng_min": 125.2, "lng_max": 125.4}
]

class YongyinClient:
    """甬音平台客户端"""
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None
        self.base_url = "http://api.sqhyw.net:90/api"
        self.session = requests.Session()

    def login(self):
        """
        登录接口
        :return: 登录结果
        """
        # 请求URL - 使用logins而非login端点
        url = f"{self.base_url}/logins"
        
        # 请求参数
        params = {
            "username": self.username,
            "password": self.password
        }
        
        # 发送GET请求
        try:
            response = self.session.get(url, params=params, timeout=10)
            result = response.json()
            
            if "token" in result:
                self.token = result["token"]
                # 保存余额信息
                self.balance_data = result.get("data", [{}])[0] if "data" in result and result["data"] else {}
                return {"success": True, "token": self.token, "data": result}
            else:
                return {"success": False, "message": result.get("message", "登录失败，请检查账号密码是否正确"), "data": result}
        except Exception as e:
            return {"success": False, "message": f"请求异常: {str(e)}", "error": e}

    def get_balance(self):
        """
        获取用户余额
        :return: 用户信息结果
        """
        # 如果已经有登录时获取的余额信息，直接返回
        if hasattr(self, 'balance_data') and self.balance_data:
            return {"success": True, "data": [self.balance_data]}
            
        # 否则再调用接口获取
        if not self.token:
            return {"success": False, "message": "未登录，请先登录"}
            
        # 请求URL
        url = f"{self.base_url}/get_myinfo"
        
        # 请求参数
        params = {
            "token": self.token
        }
        
        # 发送GET请求
        try:
            response = self.session.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get("message") == "ok":
                return {"success": True, "data": result}
            else:
                return {"success": False, "message": result.get("message", "获取余额失败"), "data": result}
        except Exception as e:
            return {"success": False, "message": f"请求异常: {str(e)}", "error": e}

    def get_mobile(self, project_id="910196"):
        """
        获取手机号
        :param project_id: 项目ID，默认为910196 (甬音普通项目)
        :return: 获取手机号结果
        """
        if not self.token:
            return {"success": False, "message": "未登录，请先登录"}
            
        # 请求URL
        url = f"{self.base_url}/get_mobile"
        
        # 请求参数 - 使用普通项目ID
        params = {
            "token": self.token,
            "project_id": project_id,  # 普通项目ID
            "operator": "4",     # 实卡
            "loop": "1"          # 过滤项目
        }
        
        # 发送GET请求
        try:
            response = self.session.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get("message") == "ok" and "mobile" in result:
                return {"success": True, "mobile": result["mobile"], "data": result}
            else:
                return {"success": False, "message": result.get("message", "获取手机号失败"), "data": result}
        except Exception as e:
            return {"success": False, "message": f"请求异常: {str(e)}", "error": e}

    def get_message(self, project_id, phone_num, max_attempts=12, delay=5, timeout=300):
        """
        获取短信验证码
        :param project_id: 项目ID
        :param phone_num: 手机号
        :param max_attempts: 最大尝试次数
        :param delay: 每次尝试间隔时间(秒)
        :param timeout: 获取短信超时时间(秒)
        :return: 短信验证码结果
        """
        if not self.token:
            return {"success": False, "message": "未登录，请先登录"}
            
        # 请求URL
        url = f"{self.base_url}/get_message"
        
        # 请求参数
        params = {
            "token": self.token,
            "project_id": project_id,
            "phone_num": phone_num
        }
        
        print(f"获取短信请求URL: {url}")
        print(f"获取短信请求参数: {params}")
        
        # 记录开始时间
        start_time = time.time()
        
        # 尝试获取短信
        for attempt in range(1, max_attempts + 1):
            print(f"正在获取短信，第 {attempt}/{max_attempts} 次尝试...")
            
            # 检查是否超时
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time > timeout:
                print(f"获取短信超时，已尝试 {int(elapsed_time)} 秒")
                return {"success": False, "message": "获取短信超时", "timeout": True}
            
            # 发送GET请求
            try:
                response = self.session.get(url, params=params, timeout=10)
                result = response.json()
                
                print(f"获取短信响应: {result}")
                
                # 根据API文档，验证码直接在根级别的code字段
                if result.get("message") == "ok" and "code" in result and result["code"]:
                    print(f"成功获取到验证码: {result['code']}")
                    return {"success": True, "code": result["code"], "data": result}
                
                # 如果没有验证码，等待一段时间后重试
                print(f"未获取到验证码，等待 {delay} 秒后重试...")
                if attempt < max_attempts:
                    time.sleep(delay)
            except Exception as e:
                print(f"请求异常: {str(e)}")
                time.sleep(delay)
        
        # 达到最大尝试次数仍未获取到验证码
        return {"success": False, "message": "达到最大尝试次数", "timeout": False}

    def release_mobile(self, phone_num=None, project_id=None, project_type=None):
        """
        释放手机号
        :param phone_num: 需要释放的手机号，None表示释放所有号码
        :param project_id: 项目ID，None表示不指定项目
        :param project_type: 项目类型，None表示不指定类型
        :return: 释放结果
        """
        if not self.token:
            return {"success": False, "message": "未登录，请先登录"}
            
        # 请求URL
        url = f"{self.base_url}/free_mobile"
        
        # 请求参数
        params = {
            "token": self.token
        }
        
        # 如果指定了手机号，添加到参数中
        if phone_num:
            params["phone_num"] = phone_num
        
        # 如果指定了项目ID，添加到参数中
        if project_id:
            params["project_id"] = project_id
        
        # 如果指定了项目类型，添加到参数中
        if project_type:
            params["project_type"] = project_type
        
        # 发送GET请求
        try:
            response = self.session.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get("message") == "ok":
                return {"success": True, "data": result}
            else:
                return {"success": False, "message": result.get("message", "释放手机号失败"), "data": result}
        except Exception as e:
            return {"success": False, "message": f"请求异常: {str(e)}", "error": e}

    def get_joined_projects(self):
        """
        获取已对接专属项目列表
        :return: 专属项目列表
        """
        if not self.token:
            return {"success": False, "message": "未登录，请先登录"}
        
        # 请求URL
        url = f"{self.base_url}/get_join"
        
        # 请求参数
        params = {
            "token": self.token
        }
        
        # 发送GET请求
        try:
            response = self.session.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get("message") == "ok" and "data" in result:
                return {"success": True, "projects": result["data"]}
            else:
                return {"success": False, "message": result.get("message", "获取专属项目失败"), "data": result}
        except Exception as e:
            return {"success": False, "message": f"请求异常: {str(e)}", "error": e}

    def sub_join_project(self, key):
        """
        重新对接专属项目
        :param key: 专属对接码或专属ID
        :return: 对接结果
        """
        if not self.token:
            return {"success": False, "message": "未登录，请先登录"}
        
        # 请求URL
        url = f"{self.base_url}/sub_join"
        
        # 请求参数
        params = {
            "token": self.token,
            "key_": key  # 专属对接码或ID
        }
        
        # 发送GET请求
        try:
            response = self.session.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get("message") == "ok":
                return {"success": True, "data": result}
            else:
                return {"success": False, "message": result.get("message", "重新对接失败"), "data": result}
        except Exception as e:
            return {"success": False, "message": f"请求异常: {str(e)}", "error": e}

    def add_to_blacklist(self, project_id, phone_num, special=None):
        """
        将号码加入黑名单
        :param project_id: 项目ID
        :param phone_num: 手机号
        :param special: 是否为专属项目，如果是则传入"1"
        :return: 拉黑结果
        """
        if not self.token:
            return {"success": False, "message": "未登录，请先登录"}
        
        # 请求URL
        url = f"{self.base_url}/add_blacklist"
        
        # 请求参数
        params = {
            "token": self.token,
            "project_id": project_id,
            "phone_num": phone_num
        }
        
        # 如果是专属项目，添加special参数
        if special:
            params["special"] = special
        
        # 发送GET请求
        try:
            response = self.session.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get("message") == "ok":
                return {"success": True, "data": result}
            else:
                return {"success": False, "message": result.get("message", "拉黑号码失败"), "data": result}
        except Exception as e:
            return {"success": False, "message": f"请求异常: {str(e)}", "error": e}

    def get_mobile_with_special(self, project_id, special=None, operator="4", loop="1"):
        """
        获取手机号，支持专属项目
        :param project_id: 项目ID或专属对接码
        :param special: 是否从专属取卡，None表示取普通项目的卡，"1"表示取专属项目的卡
        :param operator: 运营商 (0=默认 1=移动 2=联通 3=电信 4=实卡 5=虚卡)
        :param loop: 是否过滤项目 1过滤 2不过滤
        :return: 获取手机号结果
        """
        if not self.token:
            return {"success": False, "message": "未登录，请先登录"}
        
        # 请求URL
        url = f"{self.base_url}/get_mobile"
        
        # 请求参数
        params = {
            "token": self.token,
            "project_id": project_id,
            "operator": operator,
            "loop": loop
        }
        
        # 如果是专属项目，添加special参数
        if special:
            params["special"] = special
        
        # 发送GET请求
        try:
            response = self.session.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get("message") == "ok" and "mobile" in result:
                # 检查剩余取卡数
                remaining_count = result.get("1分钟内剩余取卡数")
                if remaining_count and int(remaining_count) < 10:
                    print(f"⚠ 注意：1分钟内剩余取卡数为 {remaining_count}，小于10，建议暂停取卡")
                
                return {"success": True, "mobile": result["mobile"], "data": result}
            else:
                return {"success": False, "message": result.get("message", "获取手机号失败"), "data": result}
        except Exception as e:
            return {"success": False, "message": f"请求异常: {str(e)}", "error": e}

    def get_message_with_special(self, project_id, phone_num, special=None, max_attempts=12, delay=5, timeout=300):
        """
        获取短信验证码，支持专属项目
        :param project_id: 项目ID或专属对接码
        :param phone_num: 手机号
        :param special: 是否为专属项目，如果是则传入"1"
        :param max_attempts: 最大尝试次数
        :param delay: 每次尝试间隔时间(秒)
        :param timeout: 获取短信超时时间(秒)
        :return: 短信验证码结果
        """
        if not self.token:
            return {"success": False, "message": "未登录，请先登录"}
        
        # 请求URL
        url = f"{self.base_url}/get_message"
        
        # 请求参数
        params = {
            "token": self.token,
            "project_id": project_id,
            "phone_num": phone_num
        }
        
        # 如果是专属项目，添加special参数
        if special:
            params["special"] = special
        
        print(f"获取短信请求URL: {url}")
        print(f"获取短信请求参数: {params}")
        
        # 记录开始时间
        start_time = time.time()
        
        # 尝试获取短信
        for attempt in range(1, max_attempts + 1):
            print(f"正在获取短信，第 {attempt}/{max_attempts} 次尝试...")
            
            # 检查是否超时
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time > timeout:
                print(f"获取短信超时，已尝试 {int(elapsed_time)} 秒")
                return {"success": False, "message": "获取短信超时", "timeout": True}
            
            # 发送GET请求
            try:
                response = self.session.get(url, params=params, timeout=10)
                result = response.json()
                
                print(f"获取短信响应: {result}")
                
                # 根据API文档，验证码直接在根级别的code字段
                if result.get("message") == "ok" and "code" in result and result["code"]:
                    print(f"成功获取到验证码: {result['code']}")
                    return {"success": True, "code": result["code"], "data": result}
                
                # 如果没有验证码，等待一段时间后重试
                print(f"未获取到验证码，等待 {delay} 秒后重试...")
                if attempt < max_attempts:
                    time.sleep(delay)
            except Exception as e:
                print(f"请求异常: {str(e)}")
                time.sleep(delay)
        
        # 达到最大尝试次数仍未获取到验证码
        return {"success": False, "message": "达到最大尝试次数", "timeout": False}

    def release_mobile_with_special(self, phone_num=None, project_id=None, special=None):
        """
        释放手机号，支持专属项目
        :param phone_num: 需要释放的手机号，None表示释放所有号码
        :param project_id: 项目ID或专属对接码，None表示不指定项目
        :param special: 是否为专属项目，如果是则传入"1"
        :return: 释放结果
        """
        if not self.token:
            return {"success": False, "message": "未登录，请先登录"}
        
        # 请求URL
        url = f"{self.base_url}/free_mobile"
        
        # 请求参数
        params = {
            "token": self.token
        }
        
        # 如果指定了手机号，添加到参数中
        if phone_num:
            params["phone_num"] = phone_num
        
        # 如果指定了项目ID，添加到参数中
        if project_id:
            params["project_id"] = project_id
        
        # 如果是专属项目，添加special参数
        if special:
            params["special"] = special
        
        # 发送GET请求
        try:
            response = self.session.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get("message") == "ok":
                return {"success": True, "data": result}
            else:
                return {"success": False, "message": result.get("message", "释放手机号失败"), "data": result}
        except Exception as e:
            return {"success": False, "message": f"请求异常: {str(e)}", "error": e}

# 通用函数
def get_config():
    """获取插件配置"""
    try:
        price_str = middleware.bucketGet(bucket='G_yongyinreg_config', key='price') or '0.88'
        price = float(price_str) if price_str.replace('.', '', 1).isdigit() else 0.88
        
        special_price_str = middleware.bucketGet(bucket='G_yongyinreg_config', key='special_price') or '0.50'
        special_price = float(special_price_str) if special_price_str.replace('.', '', 1).isdigit() else 0.50
            
        zsm = middleware.bucketGet(bucket='G_yongyinreg_config', key='zsm') or ''
        points_per_month_str = middleware.bucketGet(bucket='G_yongyinreg_config', key='points_per_month') or '100'
        points_per_month = int(points_per_month_str) if points_per_month_str.isdigit() else 100
        
        special_points_str = middleware.bucketGet(bucket='G_yongyinreg_config', key='special_points') or '60'
        special_points = int(special_points_str) if special_points_str.isdigit() else 60
        
        max_project_price_str = middleware.bucketGet(bucket='G_yongyinreg_config', key='max_project_price') or '0.15'
        max_project_price = float(max_project_price_str) if max_project_price_str.replace('.', '', 1).isdigit() else 0.15
        
        yongpai_code = middleware.bucketGet(bucket='G_yongyinreg_config', key='yongpai_code') or ''
        
        return {
            'price': price,
            'special_price': special_price,
            'zsm': zsm,
            'points_per_month': points_per_month,
            'special_points': special_points,
            'max_project_price': max_project_price,
            'yongpai_code': yongpai_code
        }
    except Exception as e:
        sender.reply(f"❌ 配置获取失败: {str(e)}")
        return {
            'price': 0.88,
            'special_price': 0.50,
            'zsm': '',
            'points_per_month': 100,
            'special_points': 60,
            'max_project_price': 0.15,
            'yongpai_code': ''
        }

def get_user_accounts(user_id=None):
    """获取用户账号列表"""
    if user_id is None:
        user_id = userid
    
    uservalue = middleware.bucketGet('G_yongyinreg_user', user_id) or '[]'
    user_accounts = []
    
    if uservalue:
        try:
            accounts_list = json.loads(uservalue)
            if isinstance(accounts_list, list):
                user_accounts = accounts_list
            else:
                user_accounts = [str(accounts_list)]
        except json.JSONDecodeError:
            try:
                accounts_eval = eval(uservalue)
                if isinstance(accounts_eval, (list, tuple, set)):
                    user_accounts = list(accounts_eval)
                elif accounts_eval:
                    user_accounts = [str(accounts_eval)]
            except:
                user_accounts = []
    
    return [str(acc) for acc in user_accounts]

def get_user_points(user_id=None):
    """获取用户积分，只用用户积分（dd_sign_points）"""
    if not user_id:
        user_id = sender.getUserID()
    user_points = middleware.bucketGet('dd_sign_points', user_id) or "0"
    try:
        user_points_int = int(user_points) if user_points.isdigit() else 0
    except (ValueError, TypeError):
        user_points_int = 0
    return user_points_int

def set_user_points(user_id, points):
    """设置用户积分，只操作用户积分（dd_sign_points）"""
    middleware.bucketSet('dd_sign_points', user_id, str(points))
    return True

# 获取随机位置
def get_random_location():
    """获取随机位置"""
    # 随机选择一个城市
    region = random.choice(CHINA_REGIONS)
    
    # 在该城市范围内随机生成经纬度
    lat = round(random.uniform(region["lat_min"], region["lat_max"]), 6)
    lng = round(random.uniform(region["lng_min"], region["lng_max"]), 6)
    
    return lat, lng, region["name"]

# 生成随机设备ID
def generate_device_id():
    """生成随机设备ID"""
    # 生成一个随机的UUID作为基础
    base_id = str(uuid.uuid4()).replace("-", "")
    # 添加一些随机字符
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    # 组合成设备ID
    device_id = f"{base_id}{random_chars}"
    log_message(f"生成随机DeviceID: {device_id[:6]}...", "success")
    return device_id

# 发送短信验证码函数
def send_sms_code(phone, device_id, use_proxy=False):
    """
    发送短信验证码
    :param phone: 手机号
    :param device_id: 设备ID
    :param use_proxy: 是否使用代理
    :return: 发送结果
    """
    # 获取时间戳
    timestamp = str(int(time.time()))
    
    # 生成签名
    salt = "test_123456679890123456"  # 签名盐值
    sign = hashlib.md5(f"globalDatetime{timestamp}phone{phone}{salt}".encode()).hexdigest()
    
    # 请求URL
    url = f"https://ypapp.cnnb.com.cn/yongpai-service/api/sms/get_code"
    
    # 请求参数
    params = {
        "globalDatetime": timestamp,
        "phone": phone,
        "sign": sign
    }
    
    # 请求头
    headers = {
        "system": "iOS",
        "version": "17.6",
        "appversion": "11.3.2",
        "appbuild": "202505071",
        "deviceid": device_id,
        "model": "iPhone15,4",
        "user-agent": "PLYongPaiProject/11.3.2 (iPhone; iOS 17.6; Scale/3.00)",
        "accept": "*/*",
        "accept-language": "zh-Hans;q=1",
        "accept-encoding": "gzip, deflate, br",
        "module": "web-member"
    }
    
    # 代理设置
    proxies = None
    if use_proxy:
        # 简单代理获取，实际应用中需要替换为真实代理获取逻辑
        proxy_url = "http://127.0.0.1:7890"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
    
    # 发送GET请求
    try:
        response = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=10)
        return response.json()
    except Exception as e:
        return {"code": -1, "message": f"请求异常: {str(e)}", "data": None}

# 注册账号函数
def register_account(phone, password, code, device_id, nickname="用户", use_proxy=False):
    """
    注册账号
    :param phone: 手机号
    :param password: 密码
    :param code: 短信验证码
    :param device_id: 设备ID
    :param nickname: 昵称
    :param use_proxy: 是否使用代理
    :return: 注册结果
    """
    # 获取时间戳
    timestamp = str(int(time.time()))
    
    # 获取随机位置
    latitude, longitude, location_name = get_random_location()
    
    # 生成签名
    salt = "test_123456679890123456"  # 签名盐值
    sign = hashlib.md5(f"globalDatetime{timestamp}phone{phone}{salt}".encode()).hexdigest()
    
    # 请求URL
    url = "https://ypapp.cnnb.com.cn/yongpai-user/api/login2/register"
    
    # 请求参数
    params = {
        "code": code,
        "deviceId": device_id,
        "globalDatetime": timestamp,
        "latitude": latitude,
        "longitude": longitude,
        "nickname": nickname,
        "password": password,
        "phone": phone,
        "recommendCode": "",
        "sign": sign
    }
    
    # 请求头
    headers = {
        "system": "iOS",
        "version": "17.6",
        "appversion": "11.3.2",
        "appbuild": "202505071",
        "deviceid": device_id,
        "model": "iPhone15,4",
        "user-agent": "PLYongPaiProject/11.3.2 (iPhone; iOS 17.6; Scale/3.00)",
        "accept": "*/*",
        "accept-language": "zh-Hans;q=1",
        "accept-encoding": "gzip, deflate, br",
        "module": "web-member"
    }
    
    # 代理设置
    proxies = None
    if use_proxy:
        # 简单代理获取，实际应用中需要替换为真实代理获取逻辑
        proxy_url = "http://127.0.0.1:7890"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
    
    # 发送GET请求
    try:
        response = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=10)
        return response.json()
    except Exception as e:
        return {"code": -1, "message": f"请求异常: {str(e)}", "data": None}

def check_and_rejoin_project(client, project_code):
    """
    检查并重新对接专属项目
    :param client: YongyinClient实例
    :param project_code: 专属对接码
    :return: 是否对接成功, 项目ID, 错误信息
    """
    # 获取最大价格限制
    config = get_config()
    max_price = config['max_project_price']
    
    # 获取已对接专属项目列表
    joined_result = client.get_joined_projects()
    
    if not joined_result["success"]:
        error_msg = f"获取专属项目列表失败: {joined_result.get('message', '未知错误')}"
        print(error_msg)
        return False, None, error_msg
    
    # 检查是否已对接该专属项目
    projects = joined_result["projects"]
    project_id = None
    is_joined = False
    error_msg = ""
    project_name = "未知项目"
    
    for project in projects:
        if project.get("key_") == project_code:
            # 获取项目名称
            project_name = project.get("name", "未知项目")
            
            # 检查专属项目价格是否超过限制
            project_price = float(project.get("service_price", "0"))
            if project_price > max_price:
                error_msg = f"专属项目「{project_name}」成本价 {project_price}元 超过系统限制 {max_price}元，无法使用该专属项目"
                print(error_msg)
                return False, None, error_msg
                
            is_joined = True
            project_id = project.get("project_id")
            # 检查专属项目价格是否变化
            if float(project.get("price", 0)) != float(project.get("old_price", 0)):
                print(f"专属项目价格已变化，需要重新对接")
                is_joined = False
            break
    
    # 如果未对接，检查是否能对接
    if not is_joined:
        # 先判断是否是首次对接或需要重新对接
        need_join_msg = "首次对接" if project_id is None else "重新对接"
        print(f"{need_join_msg}专属项目: {project_code}")
        
        # 重新对接前，我们先获取项目信息
        rejoin_result = client.sub_join_project(project_code)
        
        if rejoin_result["success"]:
            print(f"{need_join_msg}成功")
            
            # 重新获取项目列表，获取project_id和检查价格
            joined_result = client.get_joined_projects()
            if joined_result["success"]:
                for project in joined_result["projects"]:
                    if project.get("key_") == project_code:
                        project_name = project.get("name", "未知项目")
                        # 检查价格是否超过限制
                        project_price = float(project.get("service_price", "0"))
                        if project_price > max_price:
                            error_msg = f"专属项目「{project_name}」成本价 {project_price}元 超过系统限制 {max_price}元，无法使用该专属项目"
                            print(error_msg)
                            return False, None, error_msg
                            
                        is_joined = True
                        project_id = project.get("project_id")
                        break
        else:
            error_msg = f"{need_join_msg}失败: {rejoin_result.get('message', '未知错误')}"
            print(error_msg)
    
    return is_joined, project_id, error_msg

def auto_register_with_special_code():
    """使用专属对接码注册甬音账号"""
    # 获取配置中的椰汁平台账号密码
    platform_username, platform_password = get_platform_credentials()
    
    if not platform_username or not platform_password:
        sender.reply("❌ 未配置椰汁平台账号密码，请联系管理员配置")
        return
    
    # 先检查配置中是否已有甬派专属对接码
    project_code = middleware.bucketGet(bucket='G_yongyinreg_config', key='yongpai_code') or ""
    
    # 如果配置中没有甬派专属对接码，则询问用户输入
    if not project_code or "----" not in project_code:
        # 询问用户输入专属对接码
        sender.reply("请输入卡商提供的专属对接码(建议:910196----ZW5I2J)：")
        project_code = sender.input(60000, 1, False).strip()
        
        if not project_code or "----" not in project_code:
            sender.reply("❌ 对接码格式错误，请重新输入正确的专属对接码")
            return
    else:
        sender.reply(f"✅ 已使用配置中的甬派专属对接码: {project_code}")
    
    # 提前检查专属项目价格是否超过限制
    sender.reply("正在检查专属项目信息...")
    
    # 创建客户端并登录
    client = YongyinClient(platform_username, platform_password)
    login_result = client.login()
    
    if not login_result["success"]:
        sender.reply(f"""
❌ 登录失败
错误信息: {login_result.get('message', '未知错误')}
请联系管理员检查椰汁平台账号密码是否正确""")
        return
    
    # 先检查专属项目是否可用
    is_joined, project_id, error_msg = check_and_rejoin_project(client, project_code)
    
    if not is_joined or not project_id:
        # 专门处理价格超限的情况
        if "成本价" in error_msg and "超过系统限制" in error_msg:
            config = get_config()
            max_price = config['max_project_price']
            
            sender.reply(f"""
❌ 专属项目对接失败

{error_msg}

原因：根据系统设置，只能使用成本价低于{max_price}元的专属项目
建议：
1. 请联系管理员了解详情
2. 尝试使用其他价格更低的专属项目
3. 使用"甬音专属列表"命令查看可用专属项目

您也可以使用"甬音注册"命令选择普通项目注册
""")
        else:
            # 其他对接失败情况
            sender.reply(f"""
❌ 专属项目对接失败
错误信息: {error_msg}
请联系管理员检查对接码是否正确""")
        return
    
    # 获取项目名称和价格信息
    project_name = "专属项目"
    project_price = 0.0
    
    joined_result = client.get_joined_projects()
    if joined_result["success"]:
        for project in joined_result["projects"]:
            if project.get("key_") == project_code:
                project_name = project.get("name", "专属项目")
                project_price = float(project.get("service_price", "0"))
                break
    
    sender.reply(f"✅ 专属项目「{project_name}」对接成功")
    
    # 询问注册数量
    sender.reply("请输入需要成功注册的账号数量：")
    count_input = sender.input(60000, 1, False).strip()
    
    try:
        target_count = int(count_input) if count_input else REGISTER_COUNT
        if target_count <= 0:
            target_count = REGISTER_COUNT
    except ValueError:
        target_count = REGISTER_COUNT
    
    # 询问用户输入密码
    sender.reply("请输入需要注册的密码：\n(最少8位包含大小写字母数字和特殊字符)\n特殊符号请用.\n💡 回复 q 退出注册")
    
    custom_password = None
    while True:
        custom_password = sender.input(60000, 1, False).strip()
        
        # 检查是否退出
        if not custom_password or custom_password.lower() == 'q':
            sender.reply("✅ 已取消注册")
            return
        
        # 验证密码复杂度
        if len(custom_password) < 8:
            sender.reply("❌ 密码长度不足，请输入至少8位密码：\n💡 回复 q 退出注册")
            continue
        
        if not any(c.isupper() for c in custom_password):
            sender.reply("❌ 密码必须包含至少一个大写字母：\n💡 回复 q 退出注册")
            continue
        
        if not any(c.islower() for c in custom_password):
            sender.reply("❌ 密码必须包含至少一个小写字母：\n💡 回复 q 退出注册")
            continue
        
        if not any(c.isdigit() for c in custom_password):
            sender.reply("❌ 密码必须包含至少一个数字：\n💡 回复 q 退出注册")
            continue
            
        if not any(c in '!$%^&*()_+-={}[]|\\:;<>,.?/' for c in custom_password):
            sender.reply("❌ 密码必须包含至少一个特殊字符：\n💡 回复 q 退出注册")
            continue
            
        if '#' in custom_password or '@' in custom_password or ' ' in custom_password:
            sender.reply("❌ 密码不能包含#、@或空格：\n💡 回复 q 退出注册")
            continue
        
        # 密码验证通过
        break
    
    use_proxy = False
    
    # 获取配置
    config = get_config()
    
    # 计算支付金额 - 使用专属价格
    price_per_account = config['special_price']
    total_price = price_per_account * target_count
    
    # 显示支付信息
    pay_menu = f"""
=====甬音专属注册支付=====
📱 项目: {project_name}
🎯 注册数量: {target_count}个账号
💰 单价: ¥{price_per_account:.2f}/个
💰 总金额: ¥{total_price:.2f}
------------------
[1] 微信支付
[2] 积分支付
回复数字选择支付方式，回复q取消
=================="""
    sender.reply(pay_menu)
    
    # 等待用户选择支付方式
    pay_choice = sender.input(120000, 1, False)
    
    # 处理支付选择
    payment_success = False
    if pay_choice == '1' and config['zsm']:
        # 微信支付流程
        sender.reply(f"""
=====微信扫码支付=====
🎯 注册数量: {target_count}个账号
💰 总金额: ¥{total_price:.2f}
------------------
请扫描下方二维码支付
回复q取消支付
==================""")
        sender.replyImage(config['zsm'])
        
        payment_result = sender.waitPay(timeout=600000, exitcode='q')
        
        if payment_result == 'q':
            sender.reply("✅ 支付已取消")
            return
            
        # 解析支付结果
        Money, Time, From = None, "", ""
        try:
            if isinstance(payment_result, dict):
                if payment_result.get('type') in ['微信赞赏', '微信收款']:
                    Money = float(payment_result.get('money', 0))
                    Time = payment_result.get('time', '')
                    From = payment_result.get('from_name', '')
                else:
                    Money = float(payment_result.get('Money', 0))
                    Time = payment_result.get('Time', '')
            else:
                try:
                    data = json.loads(payment_result)
                    if data.get('type') in ['微信赞赏', '微信收款']:
                        Money = float(data.get('money', 0))
                        Time = data.get('time', '')
                        From = data.get('from_name', '')
                except:
                    if "二维码赞赏到账" in payment_result:
                        try:
                            amount_str = payment_result.split("收款金额￥")[1].split("\n")[0]
                            time_str = payment_result.split("到账时间")[1].split("\n")[0].strip()
                            Money = float(amount_str)
                            Time = time_str
                        except:
                            pass
        except Exception as e:
            sender.reply(f"❌ 解析支付结果失败: {str(e)}")
            return
            
        if Money is None:
            sender.reply("❌ 无法解析支付结果")
            return
            
        if float(Money) >= float(total_price):
            sender.reply(f"""
✅ 支付成功 ✅
💰 金额: ¥{Money}元
⏰ 时间: {Time}
{f'👤 付款人: {From}' if From else ''}
==================""")
            payment_success = True
        else:
            sender.reply(f"""
❌ 支付金额不足 ❌
应付: ¥{total_price:.2f}元 
实付: ¥{Money}元
==================""")
         
    elif pay_choice == '2':
        # 积分支付流程
        required_points = config['special_points'] * target_count
        user_points = get_user_points(userid)
        if user_points < required_points:
            sender.reply(f"""
❌ 积分不足！
需要: {required_points}积分
当前: {user_points}积分
请「联系管理员」充值积分
            """)
            return
        remaining_points = user_points - required_points
        if remaining_points < 0:
            remaining_points = 0
        sender.reply(f"""
⚠ 确认使用积分支付吗？
📊 扣除: {required_points}积分
📈 剩余: {remaining_points}积分
------------------
回复 [Y] 确认支付
回复 [N] 取消
        """)
        confirm = sender.input(60000, 1, False).lower()
        if confirm != 'y':
            sender.reply("✅ 积分支付已取消")
            return
        user_points -= required_points
        set_user_points(userid, user_points)
        # 记录交易流水
        transaction_data = {
            "userid": userid,
            "count": target_count,
            "points": required_points,
            "balance": user_points,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "甬音专属注册"
        }
        middleware.bucketSet('dd_sign_transactions', f"tx_{int(time.time())}", json.dumps(transaction_data))
        sender.reply(f"✅ 积分支付成功！扣除 {required_points}积分，剩余积分: {user_points}")
        payment_success = True
    elif pay_choice.lower() == 'q':
        sender.reply("✅ 已取消注册")
        return
    else:
        sender.reply("❌ 无效支付方式")
        return
    
    # 如果支付成功，开始注册流程
    if payment_success:
        sender.reply(f"⏳ 开始注册 {target_count} 个甬音账号，请稍候...")
        
        # 记录成功注册的账号数
        success_count = 0
        
        # 待释放的手机号列表，格式为 (手机号, 项目ID, 获取时间)
        phones_to_release = []
        
        # 拉黑的手机号列表
        blacklisted_phones = []
        
        # 注册日志
        register_logs = []
        
        # 最大尝试次数，避免无限循环
        max_attempts = target_count * 2
        attempt_count = 0
        
        # 循环注册直到成功注册目标数量的账号或达到最大尝试次数
        while success_count < target_count and attempt_count < max_attempts:
            attempt_count += 1
            register_logs.append(f"\n===== 开始注册第 {attempt_count} 次尝试 (已成功: {success_count}/{target_count}) =====")
            
            # 获取手机号
            register_logs.append("正在获取手机号...")
            mobile_result = client.get_mobile_with_special(project_code, special="1")
            
            # 提取手机号信息
            if mobile_result["success"]:
                phone_num = mobile_result["mobile"]
                get_time = time.time()  # 记录获取手机号的时间
                
                # 添加到待释放列表
                phones_to_release.append((phone_num, project_code, get_time))
                
                register_logs.append(f"✅ 获取手机号成功: {phone_num}")
                
                # 生成随机设备ID
                device_id = generate_device_id()
                register_logs.append(f"设备ID: {device_id}")
                
                # 发送短信验证码
                register_logs.append("正在发送短信验证码...")
                sms_result = send_sms_code(phone_num, device_id, use_proxy=use_proxy)
                
                if sms_result.get("code") == 0:
                    register_logs.append("✅ 短信验证码发送成功，等待接收...")
                    
                    # 获取短信验证码
                    register_logs.append("正在获取短信验证码，请稍候...")
                    message_result = client.get_message_with_special(project_code, phone_num, special="1", timeout=200)
                    
                    # 提取验证码
                    if message_result["success"]:
                        sms_code = message_result["code"]
                        register_logs.append(f"✅ 获取验证码成功: {sms_code}")
                        
                        # 注册账号
                        register_logs.append("正在注册账号...")
                        register_result = register_account(
                            phone=phone_num,
                            password=custom_password,
                            code=sms_code,
                            device_id=device_id,
                            nickname=f"用户{phone_num[-4:]}",
                            use_proxy=use_proxy
                        )
                        
                        if register_result.get("code") == 0:
                            success_count += 1
                            register_logs.append(f"✅ 注册成功 ({success_count}/{target_count})")
                            register_logs.append(f"手机号: {phone_num}")
                            register_logs.append(f"密码: {custom_password}")
                            
                            # 保存账号信息到文件和数据库
                            account_info = f"{phone_num}#{custom_password}"
                            middleware.bucketSet('G_yongyinreg_accounts', phone_num, account_info)
                            
                            # 同时保存到用户的微信ID下，方便用户查询自己注册的账号
                            user_accounts = json.loads(middleware.bucketGet('G_yongyinreg_user_accounts', userid) or '[]')
                            if account_info not in user_accounts:
                                user_accounts.append(account_info)
                                middleware.bucketSet('G_yongyinreg_user_accounts', userid, json.dumps(user_accounts))
                            
                            # 立即发送成功注册的账号信息给用户
                            sender.reply(f"✅ 账号注册成功！\n📱 手机号: {phone_num}\n🔑 密码: {custom_password}\n⏳ 进度: {success_count}/{target_count}")
                            
                            # 释放手机号
                            register_logs.append(f"正在释放手机号 {phone_num}")
                            release_result = client.release_mobile_with_special(phone_num, project_code, special="1")
                            
                            if release_result["success"]:
                                register_logs.append(f"✅ 手机号 {phone_num} 释放成功")
                                phones_to_release = [(p, pid, t) for p, pid, t in phones_to_release if p != phone_num]
                            else:
                                error_msg = release_result.get("message", "未知错误")
                                register_logs.append(f"❌ 手机号 {phone_num} 释放失败: {error_msg}")
                        else:
                            error_msg = register_result.get("message", "未知错误")
                            register_logs.append(f"❌ 注册失败: {error_msg}")
                            # 发送失败通知
                            sender.reply(f"❌ 账号注册失败！\n📱 手机号: {phone_num}\n❗ 原因: {error_msg}\n⏳ 进度: {success_count}/{target_count}")
                            
                            # 拉黑号码
                            register_logs.append(f"正在拉黑号码 {phone_num}")
                            blacklist_result = client.add_to_blacklist(project_code, phone_num, special="1")
                            
                            if blacklist_result["success"]:
                                register_logs.append(f"✅ 号码 {phone_num} 已拉黑")
                                blacklisted_phones.append(phone_num)
                            else:
                                register_logs.append(f"❌ 拉黑号码 {phone_num} 失败: {blacklist_result.get('message', '未知错误')}")
                    else:
                        register_logs.append("❌ 未能获取到验证码，跳过当前手机号")
                        
                        # 向用户发送获取验证码失败的通知
                        sender.reply(f"❌ 账号注册失败！\n📱 手机号: {phone_num}\n❗ 原因: 未能获取到验证码\n⏳ 进度: {success_count}/{target_count}")
                        
                        # 拉黑号码
                        register_logs.append(f"正在拉黑号码 {phone_num}")
                        blacklist_result = client.add_to_blacklist(project_code, phone_num, special="1")
                        
                        if blacklist_result["success"]:
                            register_logs.append(f"✅ 号码 {phone_num} 已拉黑")
                            blacklisted_phones.append(phone_num)
                        else:
                            register_logs.append(f"❌ 拉黑号码 {phone_num} 失败: {blacklist_result.get('message', '未知错误')}")
                        
                        # 检查是否是超时
                        if "timeout" in message_result and message_result["timeout"]:
                            register_logs.append(f"获取短信超时，准备释放手机号 {phone_num}")
                            
                            # 确保等待时间超过200秒
                            current_time = time.time()
                            elapsed_time = current_time - get_time
                            if elapsed_time < RELEASE_WAIT_TIME:
                                wait_time = RELEASE_WAIT_TIME - elapsed_time
                                register_logs.append(f"等待 {int(wait_time)} 秒后释放手机号 {phone_num}...")
                                time.sleep(wait_time)
                            
                            register_logs.append(f"释放手机号 {phone_num}")
                            release_result = client.release_mobile_with_special(phone_num, project_code, special="1")
                            
                            if release_result["success"]:
                                register_logs.append(f"✅ 手机号 {phone_num} 释放成功")
                                phones_to_release = [(p, pid, t) for p, pid, t in phones_to_release if p != phone_num]
                            else:
                                error_msg = release_result.get("message", "未知错误")
                                register_logs.append(f"❌ 手机号 {phone_num} 释放失败: {error_msg}")
                else:
                    error_msg = sms_result.get("message", "未知错误")
                    register_logs.append(f"❌ 发送短信验证码失败: {error_msg}")
                    
                    # 拉黑号码
                    register_logs.append(f"正在拉黑号码 {phone_num}")
                    blacklist_result = client.add_to_blacklist(project_code, phone_num, special="1")
                    
                    if blacklist_result["success"]:
                        register_logs.append(f"✅ 号码 {phone_num} 已拉黑")
                        blacklisted_phones.append(phone_num)
                    else:
                        register_logs.append(f"❌ 拉黑号码 {phone_num} 失败: {blacklist_result.get('message', '未知错误')}")
            else:
                error_msg = mobile_result.get("message", "未知错误")
                register_logs.append(f"❌ 获取手机号失败: {error_msg}")
                
                # 如果是余额不足，则退出循环
                if "余额不足" in error_msg:
                    register_logs.append("❌ 余额不足，无法继续注册")
                    break
            
            # 如果已经达到目标注册数量，退出循环
            if success_count >= target_count:
                register_logs.append(f"✅ 已达到目标注册数量: {success_count}/{target_count}")
                break
                
            # 等待一段时间再继续
            wait_time = random.randint(3, 8)
            register_logs.append(f"等待 {wait_time} 秒后继续下一次尝试...")
            time.sleep(wait_time)
        
        # 释放剩余的手机号
        if phones_to_release:
            register_logs.append("\n开始释放剩余的手机号...")
            
            for phone_info in phones_to_release:
                phone, proj_id, get_time = phone_info
                elapsed_time = time.time() - get_time
                
                # 如果还没到等待时间，则等待
                if elapsed_time < RELEASE_WAIT_TIME:
                    wait_time = RELEASE_WAIT_TIME - elapsed_time
                    register_logs.append(f"等待 {int(wait_time)} 秒后释放手机号 {phone}")
                    time.sleep(wait_time)
                
                register_logs.append(f"释放手机号 {phone}")
                release_result = client.release_mobile_with_special(phone, proj_id)
                
                if release_result["success"]:
                    register_logs.append(f"✅ 手机号 {phone} 释放成功")
                else:
                    error_msg = release_result.get("message", "未知错误")
                    register_logs.append(f"❌ 手机号 {phone} 释放失败: {error_msg}")
        
        # 注册完成，显示结果
        summary = f"""
=====注册完成=====
✅ 成功注册: {success_count}/{target_count}
❌ 失败注册: {target_count - success_count}/{target_count}
==================
"""
        
        # 保存完整注册日志
        log_time = datetime.now().strftime("%Y%m%d%H%M%S")
        log_key = f"register_log_{log_time}"
        middleware.bucketSet('G_yongyinreg_logs', log_key, "\n".join(register_logs))
        
        # 创建简化版日志
        simplified_logs = []
        
        # 获取所有成功的账号
        successful_accounts = []
        for log in register_logs:
            if "✅ 注册成功" in log and "手机号:" in register_logs[register_logs.index(log) + 1]:
                phone = register_logs[register_logs.index(log) + 1].replace("手机号: ", "")
                successful_accounts.append(f"{phone}#{custom_password}")
        
        # 添加成功账号到日志
        for i, account in enumerate(successful_accounts[:target_count], 1):
            simplified_logs.append(f"✅ 账号{i}: {account}")
        
        # 添加失败记录
        for i in range(success_count + 1, target_count + 1):
            simplified_logs.append(f"❌ 账号{i}: 注册失败")
        
        # 发送简化的注册结果
        result_msg = f"""
=====注册完成=====
✅ 成功: {success_count}/{target_count}
❌ 失败: {target_count - success_count}/{target_count}

【注册账号】
{chr(10).join(simplified_logs)}
==================
"""
        sender.reply(result_msg)
        
        # 如果注册失败，提供主要失败原因
        if success_count < target_count:
            # 分析主要失败原因
            main_reason = "未知原因"
            
            if "余额不足" in "\n".join(register_logs):
                main_reason = "椰汁平台余额不足"
            elif any("用户已存在" in log for log in register_logs):
                main_reason = "部分手机号已被注册"
            elif any("未能获取到验证码" in log for log in register_logs):
                main_reason = "获取验证码超时"
            
            sender.reply(f"❌ 注册未全部完成：{main_reason}")
        
        # 注册流程结束后统一处理所有支付方式的退还逻辑
        fail_count = target_count - success_count
        if payment_success and pay_choice in ('1', '2') and fail_count > 0:
            # 判断注册类型，选择正确的积分配置
            if 'special_points' in config:
                refund_per = config['special_points'] if '专属' in usermessage or 'special' in usermessage else config['points_per_month']
            else:
                refund_per = config['points_per_month']
            refund_points = fail_count * refund_per
            user_points = get_user_points()
            user_points += refund_points
            set_user_points(userid, user_points)
            transaction_data = {
                "userid": userid,
                "count": fail_count,
                "points": refund_points,
                "balance": user_points,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "注册失败退还"
            }
            middleware.bucketSet('dd_sign_transactions', f"refund_{int(time.time())}", json.dumps(transaction_data))
            if success_count == 0:
                sender.reply(f"❌ 本次全部注册失败，已退还 {refund_points} 积分（{fail_count}个失败账号，每个{refund_per}积分），请稍后重试。")
            else:
                sender.reply(f"❌ 本次注册有失败，已退还 {refund_points} 积分（{fail_count}个失败账号，每个{refund_per}积分），请稍后重试。")
    
    # 确保函数返回
    return True

def list_special_projects():
    """查看已对接的专属项目列表"""
    # 获取配置中的椰汁平台账号密码
    platform_username, platform_password = get_platform_credentials()
    
    if not platform_username or not platform_password:
        sender.reply("❌ 未配置椰汁平台账号密码，请联系管理员配置")
        return
        
    # 创建客户端并登录
    client = YongyinClient(platform_username, platform_password)
    login_result = client.login()
    
    if not login_result["success"]:
        sender.reply(f"""
❌ 登录失败
错误信息: {login_result.get('message', '未知错误')}
请联系管理员检查椰汁平台账号密码是否正确""")
        return
    
    # 获取已对接专属项目列表
    joined_result = client.get_joined_projects()
    
    if not joined_result["success"]:
        sender.reply(f"❌ 获取专属项目列表失败: {joined_result.get('message', '未知错误')}")
        return
    
    projects = joined_result["projects"]
    
    if not projects:
        sender.reply("📋 暂无已对接的专属项目")
        return
    
    # 获取最大价格限制和售价
    config = get_config()
    max_price = config['max_project_price']
    sell_price = config['special_price']
    
    # 格式化输出专属项目列表
    project_list = []
    available_projects = []
    unavailable_projects = []
    
    for project in projects:
        project_name = project.get("name", "未知项目")
        project_key = project.get("key_", "")
        cost_price = float(project.get("service_price", "0"))
        online_count = project.get("在线", "0")
        card_type = project.get("卡类型", "未知")
        
        # 计算利润
        profit = round(sell_price - cost_price, 2)
        profit_rate = round((profit / cost_price) * 100, 1) if cost_price > 0 else 0
        
        profit_display = f"⚡ 利润: {profit}元 ({profit_rate}%)"
        if profit <= 0:
            profit_display = f"⚠️ 亏损: {profit}元 ({profit_rate}%)"
        
        project_info = f"""📱 {project_name}
🔑 对接码: {project_key}
💰 成本价: {cost_price}元
💸 售价: {sell_price}元
{profit_display}
📊 在线数量: {online_count}
📋 卡类型: {card_type}"""
        
        # 检查价格是否超过限制
        if cost_price <= max_price:
            available_projects.append(project_info)
        else:
            unavailable_projects.append(f"{project_info}\n⚠️ 超过成本价上限({max_price}元)")
    
    # 组合可用和不可用项目
    if available_projects:
        project_list.append("✅ 可用专属项目:")
        project_list.extend(available_projects)
    
    if unavailable_projects:
        if available_projects:
            project_list.append("\n❌ 不可用专属项目:")
        else:
            project_list.append("❌ 不可用专属项目:")
        project_list.extend(unavailable_projects)
    
    # 发送专属项目列表
    sender.reply("\n\n".join(project_list))

def check_platform_status():
    """查询平台状态和余额"""
    # 获取配置中的椰汁平台账号密码
    platform_username, platform_password = get_platform_credentials()
    
    if not platform_username or not platform_password:
        sender.reply("❌ 未配置椰汁平台账号密码，请联系管理员配置")
        return
        
    # 创建客户端并登录
    client = YongyinClient(platform_username, platform_password)
    login_result = client.login()
    
    if not login_result["success"]:
        sender.reply(f"""
❌ 登录失败
错误信息: {login_result.get('message', '未知错误')}
请联系管理员检查椰汁平台账号密码是否正确""")
        return
    
    # 获取用户信息和余额
    balance_result = client.get_balance()
    
    if not balance_result["success"]:
        sender.reply(f"❌ 获取平台余额失败: {balance_result.get('message', '未知错误')}")
        return
    
    # 获取当前配置
    config = get_config()
    
    # 提取余额信息
    try:
        balance_data = balance_result["data"][0] if balance_result.get("data") and len(balance_result["data"]) > 0 else {}
        balance = balance_data.get("money", "0")
        
        # 检查是否配置了甬派专属对接码
        yongpai_info = ""
        if config['yongpai_code'] and "----" in config['yongpai_code']:
            yongpai_info = f"- 甬派专属对接码: {config['yongpai_code']}"
        
        sender.reply(f"""
📊 平台状态: ✅ 正常
💰 账户余额: {balance}元

🔧 当前配置:
- 普通项目售价: {config['price']}元
- 专属项目售价: {config['special_price']}元
- 专属成本价上限: {config['max_project_price']}元
- 普通项目积分: {config['points_per_month']}积分/号
- 专属项目积分: {config['special_points']}积分/号
{yongpai_info}

🔄 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    except Exception as e:
        sender.reply(f"❌ 解析余额信息失败: {str(e)}")

def clean_user_accounts():
    """清理用户的注册账号记录"""
    user_id = userid
    
    # 获取用户的账号记录
    user_accounts = json.loads(middleware.bucketGet('G_yongyinreg_user_accounts', user_id) or '[]')
    
    if not user_accounts:
        sender.reply("您目前没有任何注册记录")
        return
    
    # 显示当前账号记录并确认是否清理
    account_count = len(user_accounts)
    sender.reply(f"""
===== 账号清理 =====
您当前有 {account_count} 个注册记录
请确认是否清理？

回复 [Y] 确认清理
回复其他内容取消
==================
""")
    
    # 等待用户确认
    confirm = sender.input(60000, 1, False).lower()
    if confirm != 'y':
        sender.reply("✅ 已取消清理操作")
        return
    
    # 清理用户账号记录
    try:
        middleware.bucketSet('G_yongyinreg_user_accounts', user_id, '[]')
        
        # 记录清理日志
        clean_log = {
            "userid": user_id,
            "cleaned_count": account_count,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        middleware.bucketSet('G_yongyinreg_clean_logs', f"clean_{user_id}_{int(time.time())}", json.dumps(clean_log))
        
        sender.reply(f"""
✅ 清理成功
已清理 {account_count} 个注册记
清理时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

注意：此操作只清理了您的注册记录，不影响实际注册的账号
==================
""")
    except Exception as e:
        sender.reply(f"❌ 清理失败: {str(e)}")

def auto_register_accounts():
    """使用普通项目ID注册甬音账号"""
    # 获取配置中的椰汁平台账号密码
    platform_username, platform_password = get_platform_credentials()
    
    if not platform_username or not platform_password:
        sender.reply("❌ 未配置椰汁平台账号密码，请联系管理员配置")
        return
    
    # 使用普通项目ID
    project_id = "910196"  # 甬音普通项目ID
    
    # 创建客户端并登录
    sender.reply("欢迎使用！")
    client = YongyinClient(platform_username, platform_password)
    login_result = client.login()
    
    if not login_result["success"]:
        sender.reply(f"""
❌ 登录失败
错误信息: {login_result.get('message', '未知错误')}
请联系管理员检查椰汁平台账号密码是否正确""")
        return
    
    sender.reply("✅ 登录成功")
    
    # 询问注册数量
    sender.reply("请输入需要成功注册的账号数量：")
    count_input = sender.input(60000, 1, False).strip()
    
    try:
        target_count = int(count_input) if count_input else REGISTER_COUNT
        if target_count <= 0:
            target_count = REGISTER_COUNT
    except ValueError:
        target_count = REGISTER_COUNT
    
    # 询问用户输入密码
    sender.reply("请输入需要注册的密码：\n(最少8位包含大小写字母数字和特殊字符)\n特殊符号请用.\n💡 回复 q 退出注册")
    
    custom_password = None
    while True:
        custom_password = sender.input(60000, 1, False).strip()
        
        # 检查是否退出
        if not custom_password or custom_password.lower() == 'q':
            sender.reply("✅ 已取消注册")
            return
        
        # 验证密码复杂度
        if len(custom_password) < 8:
            sender.reply("❌ 密码长度不足，请输入至少8位密码：\n💡 回复 q 退出注册")
            continue
        
        if not any(c.isupper() for c in custom_password):
            sender.reply("❌ 密码必须包含至少一个大写字母：\n💡 回复 q 退出注册")
            continue
        
        if not any(c.islower() for c in custom_password):
            sender.reply("❌ 密码必须包含至少一个小写字母：\n💡 回复 q 退出注册")
            continue
        
        if not any(c.isdigit() for c in custom_password):
            sender.reply("❌ 密码必须包含至少一个数字：\n💡 回复 q 退出注册")
            continue
            
        if not any(c in '!$%^&*()_+-={}[]|\\:;<>,.?/' for c in custom_password):
            sender.reply("❌ 密码必须包含至少一个特殊字符：\n💡 回复 q 退出注册")
            continue
            
        if '#' in custom_password or '@' in custom_password or ' ' in custom_password:
            sender.reply("❌ 密码不能包含#、@或空格：\n💡 回复 q 退出注册")
            continue
        
        # 密码验证通过
        break
    
    use_proxy = False
    
    # 获取配置
    config = get_config()
    
    # 计算支付金额 - 使用普通项目价格
    price_per_account = config['price']
    total_price = price_per_account * target_count
    
    # 显示支付信息
    pay_menu = f"""
=====甬音注册支付=====
📱 项目: 甬音普通项目
🎯 注册数量: {target_count}个账号
💰 单价: ¥{price_per_account:.2f}/个
💰 总金额: ¥{total_price:.2f}
------------------
[1] 微信支付
[2] 积分支付
回复数字选择支付方式，回复q取消
=================="""
    sender.reply(pay_menu)
    
    # 等待用户选择支付方式
    pay_choice = sender.input(120000, 1, False)
    
    # 处理支付选择
    payment_success = False
    if pay_choice == '1' and config['zsm']:
        # 微信支付流程
        sender.reply(f"""
=====微信扫码支付=====
🎯 注册数量: {target_count}个账号
💰 总金额: ¥{total_price:.2f}
------------------
请扫描下方二维码支付
回复q取消支付
==================""")
        sender.replyImage(config['zsm'])
        
        payment_result = sender.waitPay(timeout=600000, exitcode='q')
        
        if payment_result == 'q':
            sender.reply("✅ 支付已取消")
            return
            
        # 解析支付结果
        Money, Time, From = None, "", ""
        try:
            if isinstance(payment_result, dict):
                if payment_result.get('type') in ['微信赞赏', '微信收款']:
                    Money = float(payment_result.get('money', 0))
                    Time = payment_result.get('time', '')
                    From = payment_result.get('from_name', '')
                else:
                    Money = float(payment_result.get('Money', 0))
                    Time = payment_result.get('Time', '')
            else:
                try:
                    data = json.loads(payment_result)
                    if data.get('type') in ['微信赞赏', '微信收款']:
                        Money = float(data.get('money', 0))
                        Time = data.get('time', '')
                        From = data.get('from_name', '')
                except:
                    if "二维码赞赏到账" in payment_result:
                        try:
                            amount_str = payment_result.split("收款金额￥")[1].split("\n")[0]
                            time_str = payment_result.split("到账时间")[1].split("\n")[0].strip()
                            Money = float(amount_str)
                            Time = time_str
                        except:
                            pass
        except Exception as e:
            sender.reply(f"❌ 解析支付结果失败: {str(e)}")
            return
            
        if Money is None:
            sender.reply("❌ 无法解析支付结果")
            return
            
        if float(Money) >= float(total_price):
            sender.reply(f"""
✅ 支付成功 ✅
💰 金额: ¥{Money}元
⏰ 时间: {Time}
{f'👤 付款人: {From}' if From else ''}
==================""")
            payment_success = True
        else:
            sender.reply(f"""
❌ 支付金额不足 ❌
应付: ¥{total_price:.2f}元 
实付: ¥{Money}元
==================""")
         
    elif pay_choice == '2':
        # 积分支付流程
        required_points = config['points_per_month'] * target_count
        user_points = get_user_points()
        if user_points < required_points:
            sender.reply(f"""
❌ 积分不足！
需要: {required_points}积分
当前: {user_points}积分
请「联系管理员」充值积分
            """)
            return
        remaining_points = user_points - required_points
        if remaining_points < 0:
            remaining_points = 0
        sender.reply(f"""
⚠ 确认使用积分支付吗？
📊 扣除: {required_points}积分
📈 剩余: {remaining_points}积分
------------------
回复 [Y] 确认支付
回复 [N] 取消
        """)
        confirm = sender.input(60000, 1, False).lower()
        if confirm != 'y':
            sender.reply("✅ 积分支付已取消")
            return
        user_points -= required_points
        set_user_points(userid, user_points)
        # 记录交易流水
        transaction_data = {
            "userid": userid,
            "count": target_count,
            "points": required_points,
            "balance": user_points,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "甬音普通注册"
        }
        middleware.bucketSet('dd_sign_transactions', f"tx_{int(time.time())}", json.dumps(transaction_data))
        sender.reply(f"✅ 积分支付成功！扣除 {required_points}积分，剩余积分: {user_points}")
        payment_success = True
    elif pay_choice.lower() == 'q':
        sender.reply("✅ 已取消注册")
        return
    else:
        sender.reply("❌ 无效支付方式")
        return
    
    # 如果支付成功，开始注册流程
    if payment_success:
        sender.reply(f"⏳ 开始注册 {target_count} 个甬音账号，请稍候...")
        
        # 记录成功注册的账号数
        success_count = 0
        
        # 待释放的手机号列表，格式为 (手机号, 项目ID, 获取时间)
        phones_to_release = []
        
        # 拉黑的手机号列表
        blacklisted_phones = []
        
        # 注册日志
        register_logs = []
        
        # 最大尝试次数，避免无限循环
        max_attempts = target_count * 2
        attempt_count = 0
        
        # 循环注册直到成功注册目标数量的账号或达到最大尝试次数
        while success_count < target_count and attempt_count < max_attempts:
            attempt_count += 1
            register_logs.append(f"\n===== 开始注册第 {attempt_count} 次尝试 (已成功: {success_count}/{target_count}) =====")
            
            # 获取手机号
            register_logs.append("正在获取手机号...")
            mobile_result = client.get_mobile(project_id)
            
            # 提取手机号信息
            if mobile_result["success"]:
                phone_num = mobile_result["mobile"]
                get_time = time.time()  # 记录获取手机号的时间
                
                # 添加到待释放列表
                phones_to_release.append((phone_num, project_id, get_time))
                
                register_logs.append(f"✅ 获取手机号成功: {phone_num}")
                
                # 生成随机设备ID
                device_id = generate_device_id()
                register_logs.append(f"设备ID: {device_id}")
                
                # 发送短信验证码
                register_logs.append("正在发送短信验证码...")
                sms_result = send_sms_code(phone_num, device_id, use_proxy=use_proxy)
                
                if sms_result.get("code") == 0:
                    register_logs.append("✅ 短信验证码发送成功，等待接收...")
                    
                    # 获取短信验证码
                    register_logs.append("正在获取短信验证码，请稍候...")
                    message_result = client.get_message(project_id, phone_num, timeout=200)
                    
                    # 提取验证码
                    if message_result["success"]:
                        sms_code = message_result["code"]
                        register_logs.append(f"✅ 获取验证码成功: {sms_code}")
                        
                        # 注册账号
                        register_logs.append("正在注册账号...")
                        register_result = register_account(
                            phone=phone_num,
                            password=custom_password,
                            code=sms_code,
                            device_id=device_id,
                            nickname=f"用户{phone_num[-4:]}",
                            use_proxy=use_proxy
                        )
                        
                        if register_result.get("code") == 0:
                            success_count += 1
                            register_logs.append(f"✅ 注册成功 ({success_count}/{target_count})")
                            register_logs.append(f"手机号: {phone_num}")
                            register_logs.append(f"密码: {custom_password}")
                            
                            # 保存账号信息到文件和数据库
                            account_info = f"{phone_num}#{custom_password}"
                            middleware.bucketSet('G_yongyinreg_accounts', phone_num, account_info)
                            
                            # 同时保存到用户的微信ID下，方便用户查询自己注册的账号
                            user_accounts = json.loads(middleware.bucketGet('G_yongyinreg_user_accounts', userid) or '[]')
                            if account_info not in user_accounts:
                                user_accounts.append(account_info)
                                middleware.bucketSet('G_yongyinreg_user_accounts', userid, json.dumps(user_accounts))
                            
                            # 立即发送成功注册的账号信息给用户
                            sender.reply(f"✅ 账号注册成功！\n📱 手机号: {phone_num}\n🔑 密码: {custom_password}\n⏳ 进度: {success_count}/{target_count}")
                            
                            # 释放手机号
                            register_logs.append(f"正在释放手机号 {phone_num}")
                            release_result = client.release_mobile(phone_num, project_id)
                            
                            if release_result["success"]:
                                register_logs.append(f"✅ 手机号 {phone_num} 释放成功")
                                phones_to_release = [(p, pid, t) for p, pid, t in phones_to_release if p != phone_num]
                            else:
                                error_msg = release_result.get("message", "未知错误")
                                register_logs.append(f"❌ 手机号 {phone_num} 释放失败: {error_msg}")
                        else:
                            error_msg = register_result.get("message", "未知错误")
                            register_logs.append(f"❌ 注册失败: {error_msg}")
                            # 发送失败通知
                            sender.reply(f"❌ 账号注册失败！\n📱 手机号: {phone_num}\n❗ 原因: {error_msg}\n⏳ 进度: {success_count}/{target_count}")
                            
                            # 拉黑号码
                            register_logs.append(f"正在拉黑号码 {phone_num}")
                            blacklist_result = client.add_to_blacklist(project_id, phone_num)
                            
                            if blacklist_result["success"]:
                                register_logs.append(f"✅ 号码 {phone_num} 已拉黑")
                                blacklisted_phones.append(phone_num)
                            else:
                                register_logs.append(f"❌ 拉黑号码 {phone_num} 失败: {blacklist_result.get('message', '未知错误')}")
                    else:
                        register_logs.append("❌ 未能获取到验证码，跳过当前手机号")
                        
                        # 向用户发送获取验证码失败的通知
                        sender.reply(f"❌ 账号注册失败！\n📱 手机号: {phone_num}\n❗ 原因: 未能获取到验证码\n⏳ 进度: {success_count}/{target_count}")
                        
                        # 拉黑号码
                        register_logs.append(f"正在拉黑号码 {phone_num}")
                        blacklist_result = client.add_to_blacklist(project_id, phone_num)
                        
                        if blacklist_result["success"]:
                            register_logs.append(f"✅ 号码 {phone_num} 已拉黑")
                            blacklisted_phones.append(phone_num)
                        else:
                            register_logs.append(f"❌ 拉黑号码 {phone_num} 失败: {blacklist_result.get('message', '未知错误')}")
                        
                        # 检查是否是超时
                        if "timeout" in message_result and message_result["timeout"]:
                            register_logs.append(f"获取短信超时，准备释放手机号 {phone_num}")
                            
                            # 确保等待时间超过200秒
                            current_time = time.time()
                            elapsed_time = current_time - get_time
                            if elapsed_time < RELEASE_WAIT_TIME:
                                wait_time = RELEASE_WAIT_TIME - elapsed_time
                                register_logs.append(f"等待 {int(wait_time)} 秒后释放手机号 {phone_num}...")
                                time.sleep(wait_time)
                            
                            register_logs.append(f"释放手机号 {phone_num}")
                            release_result = client.release_mobile(phone_num, project_id)
                            
                            if release_result["success"]:
                                register_logs.append(f"✅ 手机号 {phone_num} 释放成功")
                                phones_to_release = [(p, pid, t) for p, pid, t in phones_to_release if p != phone_num]
                            else:
                                error_msg = release_result.get("message", "未知错误")
                                register_logs.append(f"❌ 手机号 {phone_num} 释放失败: {error_msg}")
                else:
                    error_msg = sms_result.get("message", "未知错误")
                    register_logs.append(f"❌ 发送短信验证码失败: {error_msg}")
                    
                    # 拉黑号码
                    register_logs.append(f"正在拉黑号码 {phone_num}")
                    blacklist_result = client.add_to_blacklist(project_id, phone_num)
                    
                    if blacklist_result["success"]:
                        register_logs.append(f"✅ 号码 {phone_num} 已拉黑")
                        blacklisted_phones.append(phone_num)
                    else:
                        register_logs.append(f"❌ 拉黑号码 {phone_num} 失败: {blacklist_result.get('message', '未知错误')}")
            else:
                error_msg = mobile_result.get("message", "未知错误")
                register_logs.append(f"❌ 获取手机号失败: {error_msg}")
                
                # 如果是余额不足，则退出循环
                if "余额不足" in error_msg:
                    register_logs.append("❌ 余额不足，无法继续注册")
                    break
            
            # 如果已经达到目标注册数量，退出循环
            if success_count >= target_count:
                register_logs.append(f"✅ 已达到目标注册数量: {success_count}/{target_count}")
                break
                
            # 等待一段时间再继续
            wait_time = random.randint(3, 8)
            register_logs.append(f"等待 {wait_time} 秒后继续下一次尝试...")
            time.sleep(wait_time)
        
        # 释放剩余的手机号
        if phones_to_release:
            register_logs.append("\n开始释放剩余的手机号...")
            
            for phone_info in phones_to_release:
                phone, proj_id, get_time = phone_info
                elapsed_time = time.time() - get_time
                
                # 如果还没到等待时间，则等待
                if elapsed_time < RELEASE_WAIT_TIME:
                    wait_time = RELEASE_WAIT_TIME - elapsed_time
                    register_logs.append(f"等待 {int(wait_time)} 秒后释放手机号 {phone}")
                    time.sleep(wait_time)
                
                register_logs.append(f"释放手机号 {phone}")
                release_result = client.release_mobile(phone, proj_id)
                
                if release_result["success"]:
                    register_logs.append(f"✅ 手机号 {phone} 释放成功")
                else:
                    error_msg = release_result.get("message", "未知错误")
                    register_logs.append(f"❌ 手机号 {phone} 释放失败: {error_msg}")
        
        # 注册完成，显示结果
        summary = f"""
=====注册完成=====
✅ 成功注册: {success_count}/{target_count}
❌ 失败注册: {target_count - success_count}/{target_count}
==================
"""
        
        # 保存完整注册日志
        log_time = datetime.now().strftime("%Y%m%d%H%M%S")
        log_key = f"register_log_{log_time}"
        middleware.bucketSet('G_yongyinreg_logs', log_key, "\n".join(register_logs))
        
        # 创建简化版日志
        simplified_logs = []
        
        # 获取所有成功的账号
        successful_accounts = []
        for log in register_logs:
            if "✅ 注册成功" in log and "手机号:" in register_logs[register_logs.index(log) + 1]:
                phone = register_logs[register_logs.index(log) + 1].replace("手机号: ", "")
                successful_accounts.append(f"{phone}#{custom_password}")
        
        # 添加成功账号到日志
        for i, account in enumerate(successful_accounts[:target_count], 1):
            simplified_logs.append(f"✅ 账号{i}: {account}")
        
        # 添加失败记录
        for i in range(success_count + 1, target_count + 1):
            simplified_logs.append(f"❌ 账号{i}: 注册失败")
        
        # 发送简化的注册结果
        result_msg = f"""
=====注册完成=====
✅ 成功: {success_count}/{target_count}
❌ 失败: {target_count - success_count}/{target_count}

【注册账号】
{chr(10).join(simplified_logs)}
==================
"""
        sender.reply(result_msg)
        
        # 如果注册失败，提供主要失败原因
        if success_count < target_count:
            # 分析主要失败原因
            main_reason = "未知原因"
            
            if "余额不足" in "\n".join(register_logs):
                main_reason = "椰汁平台余额不足"
            elif any("用户已存在" in log for log in register_logs):
                main_reason = "部分手机号已被注册"
            elif any("未能获取到验证码" in log for log in register_logs):
                main_reason = "获取验证码超时"
            
            sender.reply(f"❌ 注册未全部完成：{main_reason}")
        
        # 注册流程结束后统一处理所有支付方式的退还逻辑
        fail_count = target_count - success_count
        if payment_success and pay_choice in ('1', '2') and fail_count > 0:
            # 判断注册类型，选择正确的积分配置
            if 'special_points' in config:
                refund_per = config['special_points'] if '专属' in usermessage or 'special' in usermessage else config['points_per_month']
            else:
                refund_per = config['points_per_month']
            refund_points = fail_count * refund_per
            user_points = get_user_points()
            user_points += refund_points
            set_user_points(userid, user_points)
            transaction_data = {
                "userid": userid,
                "count": fail_count,
                "points": refund_points,
                "balance": user_points,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "注册失败退还"
            }
            middleware.bucketSet('dd_sign_transactions', f"refund_{int(time.time())}", json.dumps(transaction_data))
            if success_count == 0:
                sender.reply(f"❌ 本次全部注册失败，已退还 {refund_points} 积分（{fail_count}个失败账号，每个{refund_per}积分），请稍后重试。")
            else:
                sender.reply(f"❌ 本次注册有失败，已退还 {refund_points} 积分（{fail_count}个失败账号，每个{refund_per}积分），请稍后重试。")
    
    # 确保函数返回
    return True

# 主入口函数 - 处理用户指令
try:
    usermessage = sender.getMessage()
except AttributeError:
    usermessage = ""

if re.search(r'^甬音注册$', usermessage):
    auto_register_accounts()
elif re.search(r'^甬音专属注册$', usermessage):
    auto_register_with_special_code()
elif re.search(r'^甬音专属列表$', usermessage):
    list_special_projects()
elif re.search(r'^甬音状态$', usermessage):
    check_platform_status()
elif re.search(r'^甬音注册清理$', usermessage):
    clean_user_accounts()
elif re.search(r'^甬音注册查询$', usermessage):
    # 查询用户自己的注册账号
    try:
        user_accounts = json.loads(middleware.bucketGet('G_yongyinreg_user_accounts', userid) or '[]')
        
        if not user_accounts:
            sender.reply("您暂无任何注册成功的账号")
        else:
            # 分组显示账号列表，每组最多50个账号
            group_size = 50
            total_groups = (len(user_accounts) + group_size - 1) // group_size
            
            for group in range(total_groups):
                start_idx = group * group_size
                end_idx = min((group + 1) * group_size, len(user_accounts))
                group_accounts = user_accounts[start_idx:end_idx]
                
                account_list = "\n".join(group_accounts)
                result_msg = f"""
===== 甬音注册账号 ({group+1}/{total_groups})=====
💰总账号: {len(user_accounts)}个
{account_list}
==================
💡 回复 q 退出查看"""
                sender.reply(result_msg)
                
                # 如果不是最后一组，等待用户输入
                if group < total_groups - 1:
                    user_input = sender.input(30000, 1, False)  # 30秒超时
                    if not user_input or user_input.lower() == 'q':
                        sender.reply("已退出查看")
                        break
    except Exception as e:
        sender.reply(f"❌ 查询账号时出错: {str(e)}")
else:
    sender.setContinue()
