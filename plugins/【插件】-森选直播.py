# [rule: ^森选直播(登录|登陆)$|^登(录|陆)森选直播$|^森选直播(查询|管理)$|^(查询|管理)森选直播$|^森选直播授权$|^森选直播教程$|^森选直播清理$|^森选订阅$|^森选推送$]
# [disable:false]
# [platform: qq,wx]
# [cron: ]
# [public:true]
# [title: 【插件】-森选直播]
#[author: huawei]
#[service: 1603960061] 售后联系方式
# [open_source: false]
# [class: 工具类]
# [version: 1.5.3]
# [price: 8.88] 上架价格
# [admin: false]
# [icon: http://113.45.39.135:8080/admin/images/gallery/1750458890545208841.jpg]

# [description: vx小程序【森选】直播抢红包插件<br>适配呆呆积分支付<br><br>🎁 买插件送青龙脚本！购买后联系作者获取脚本<br><br>指令：<br>森选直播登录：绑定直播账号(格式：备注#token)<br>森选直播管理：账号管理与授权<br>森选直播查询：查询账号状态和授权信息<br>森选订阅：订阅/取消开播提醒<br>森选推送：手动触发开播推送<br>森选直播授权：管理员授权操作<br>森选直播教程：直播token获取指南<br>森选直播清理：清理过期和未授权账号(管理员)<br>脚本获取地址Q群:280458673]

# 插件参数配置
# [param: {"required":false,"key":"G_SXZB.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款码","desc":"微信/支付宝收款码链接"}]
# [param: {"required":false,"key":"G_SXZB.price","bool":false,"placeholder":"例:0.88,不填为0元","name":"月费价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":false,"key":"G_SXZB.points_per_month","bool":false,"placeholder":"例:100","name":"积分/月","value":"100","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":false,"key":"G_SXZB.ql_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割，这个符号是中文的竖(直接复制)"}]
# [param: {"required":false,"key":"G_SXZB.var_name","bool":false,"placeholder":"必填项,例:G_SXZB_TOKEN","name":"青龙变量名","desc":"提交到青龙面板的环境变量名称"}]
# [param: {"required":false,"key":"G_SXZB.push_admins","bool":false,"placeholder":"QQ号或微信ID，逗号分隔","name":"管理员列表","desc":"接收推送报告的管理员QQ/微信号"}]
# [param: {"required":false,"key":"G_SXZB.push_message","bool":false,"placeholder":"配置推送","name":"推送文字","desc":"开播推送的自定义文字，不填使用默认文字"}]

from datetime import datetime, timedelta
import middleware
import requests
import os
import json
import re
import time
import random
import hashlib
import urllib.parse
from typing import List, Dict, Any, Tuple

# 获取发送者信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

class SenxuanClient:
    """森选直播客户端"""
    def __init__(self, token_with_remark):
        # 分割Token和备注
        if '#' in token_with_remark:
            self.remark, self.raw_token = token_with_remark.split('#', 1)
            self.remark = self.remark.strip()
            self.raw_token = self.raw_token.strip()
        else:
            self.raw_token = token_with_remark.strip()
            self.remark = "默认账号"
        
        # 确保token不包含Bearer前缀，然后添加
        if self.raw_token.lower().startswith("bearer "):
            self.token = self.raw_token  # 保留原有格式
        else:
            self.token = f"Bearer {self.raw_token}"  # 添加Bearer前缀
        
        # 使用固定域名
        self.base_url = "https://n03.sentezhenxuan.com/api"
        self.session = requests.Session()
        
        # 设置请求头
        self.headers = {
            "Accept-Encoding": "gzip,compress,br,deflate",
            "content-type": "application/json",
            "Connection": "keep-alive",
            "Referer": "https://servicewechat.com/wx890e6dc32d83d24c/1/page-frame.html",
            "Authori-zation": self.token,  # 使用带Bearer前缀的token
            "Host": "n03.sentezhenxuan.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF",
            "Cb-lang": "zh-CN",
            "Form-type": "routine-sxfengshang",
            "xweb_xhr": "1"
        }
        self.session.headers.update(self.headers)

    def get_user_info(self):
        """获取用户信息"""
        url = f"{self.base_url}/user/detail"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == 200 and data.get("data"):
                return data.get("data")
            return None
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            # 尝试使用佣金接口验证
            try:
                commission_url = f"{self.base_url}/spread/commission/0?page=1&limit=5"
                comm_response = self.session.get(commission_url, timeout=10)
                comm_data = comm_response.json()
                if comm_data.get("status") == 200:
                    # 从佣金数据提取用户信息
                    user_transactions = comm_data.get("data", {}).get("list", [])
                    if user_transactions and len(user_transactions) > 0:
                        uid = user_transactions[0].get("uid")
                        if uid:
                            return {"id": uid, "nickname": self.remark}
            except:
                pass
            return None

    def get_user_info_new(self):
        """获取用户详细信息"""
        url = f"{self.base_url}/updateTxInfo"
        try:
            print("正在获取用户详细信息...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == 200 and data.get("data"):
                return data.get("data")
            return None
        except Exception as e:
            print(f"获取用户详细信息失败: {e}")
            return None

    def get_video_detail(self, vid: int) -> Dict[str, Any]:
        """获取单个视频详情"""
        url = f"{self.base_url}/video/getOneVideo?vid={vid}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == 200 and data.get("data"):
                return data.get("data")
            return None
        except Exception as e:
            return None

    def add_user_view_num(self, vid: int) -> Dict[str, Any]:
        """记录用户观看视频"""
        url = f"{self.base_url}/video/addUserViewNum"
        body = {
            "vid": vid,
            "baseVersion": "3.10.2",
            "playMode": 0
        }
        try:
            print(f"  正在记录观看，视频ID: {vid}")
            response = self.session.post(url, json=body, timeout=10)
            response.raise_for_status()
            result = response.json()
            print(f"  记录观看结果: {result.get('msg')}")
            return result
        except Exception as e:
            print(f"  记录观看请求异常: {e}")
            return {"status": 500, "msg": str(e)}

    def video_job(self, vid: int, wait_time: int) -> Dict[str, Any]:
        """提交视频观看完成"""
        url = f"{self.base_url}/video/videoJob"
        
        start_time = int(time.time() * 1000)
        end_time = start_time + (wait_time * 1000) + 1000
        
        body = {
            "vid": vid,
            "startTime": start_time,
            "endTime": end_time,
            "baseVersion": "3.10.2",
            "playMode": 0
        }
        
        try:
            print(f"  等待 {wait_time} 秒...")
            time.sleep(wait_time)
            
            print(f"  正在提交观看完成...")
            response = self.session.post(url, json=body, timeout=10)
            response.raise_for_status()
            result = response.json()
            print(f"  提交观看完成: {result.get('msg')}")
            return result
        except Exception as e:
            print(f"  提交观看完成失败: {e}")
            return {"status": 500, "msg": str(e)}

    def reward_user_small_change(self) -> Dict[str, Any]:
        """获取答题奖励"""
        url = f"{self.base_url}/video/rewardUserSmallChange"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            result = response.json()
            return result
        except Exception as e:
            return {"status": 500, "msg": str(e)}

    def get_video_ids(self) -> List[int]:
        """一次性获取所有视频ID"""
        try:
            print("正在请求视频列表...")
            url = f"{self.base_url}/video/list?page=1&limit=50&status=1&source=0&isXn=1"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == 200 and data.get("data"):
                video_list = data.get("data")
                if isinstance(video_list, list) and len(video_list) > 0:
                    video_ids = [video.get("id") for video in video_list if video.get("id")]
                    print(f"成功获取 {len(video_ids)} 个视频")
                    return video_ids
            
            print(f"获取失败: {data.get('msg')}")
            return []
            
        except Exception as e:
            print(f"请求异常: {e}")
            return []

    def watch_video(self, vid: int) -> Dict[str, Any]:
        """刷视频 - 使用原脚本逻辑"""
        url = f"{self.base_url}/video/videoJob"
        
        end_time = int(time.time() * 1000)
        start_time = end_time - 80000  # 假设观看了约80秒
        
        body = {
            "vid": vid,
            "startTime": start_time,
            "endTime": end_time,
            "baseVersion": "3.5.8",
            "playMode": 0
        }
        
        try:
            print(f"正在刷视频，ID: {vid}")
            response = self.session.post(url, json=body, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            print(f"刷视频结果: {result.get('msg')}")
            return result
        except Exception as e:
            print(f"刷视频请求异常: {e}")
            return {"status": 500, "msg": str(e)}

    def withdraw(self) -> Dict[str, Any]:
        """提现 - 使用原脚本逻辑"""
        url = f"{self.base_url}/userTx?"
        
        try:
            print("正在尝试提现...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            print(f"提现结果: {result.get('msg')}")
            return result
        except Exception as e:
            print(f"提现请求异常: {e}")
            return {"status": 500, "msg": str(e)}

    def get_commission_info(self):
        """获取佣金信息"""
        url = f"{self.base_url}/spread/commission/0?page=1&limit=5"
        try:
            print("正在获取佣金信息...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == 200 and data.get("data"):
                commission_data = data.get("data", {})
                commission_list = commission_data.get("list", [])
                return {
                    "success": True,
                    "records": commission_list,
                    "count": len(commission_list)
                }
            return {"success": False, "msg": data.get("msg", "未知错误")}
        except Exception as e:
            print(f"获取佣金信息失败: {e}")
            return {"success": False, "msg": str(e)}

    def run_daily_task(self) -> Dict[str, Any]:
        """运行每日任务 - 已禁用"""
        return {
            "video_count": 0,
            "success_videos": 0,
            "answer_videos": 0,
            "withdraw": None,
            "balance": 0,
            "commission": None
        }

    def get_withdraw_records(self):
        """获取提现记录 - 使用专用接口"""
        url = f"{self.base_url}/spread/commission/1?page=1&limit=15"
        try:
            print("正在获取提现记录...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == 200 and data.get("data"):
                withdraw_data = data.get("data", {})
                withdraw_list = withdraw_data.get("list", [])
                return {
                    "success": True,
                    "records": withdraw_list,
                    "count": len(withdraw_list)
                }
            return {"success": False, "msg": data.get("msg", "未知错误")}
        except Exception as e:
            print(f"获取提现记录失败: {e}")
            return {"success": False, "msg": str(e)}

# 通用函数
def get_config():
    """获取插件配置"""
    try:
        price_str = middleware.bucketGet(bucket='G_SXZB', key='price') or '0.88'
        price = float(price_str) if price_str.replace('.', '', 1).isdigit() else 0.88
        zsm = middleware.bucketGet(bucket='G_SXZB', key='zsm') or ''
        points_per_month_str = middleware.bucketGet(bucket='G_SXZB', key='points_per_month') or '100'
        points_per_month = int(points_per_month_str) if points_per_month_str.isdigit() else 100
        
        return {
            'price': price,
            'zsm': zsm,
            'points_per_month': points_per_month
        }
    except:
        return {'price': 0.88, 'zsm': '', 'points_per_month': 100}

class QingLongAPI:
    def __init__(self, url, client_id, client_secret):
        self.base_url = url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None

    def login(self):
        try:
            url = f"{self.base_url}/open/auth/token?client_id={self.client_id}&client_secret={self.client_secret}"
            r = requests.get(url, timeout=10)
            data = r.json()
            if data.get('code') == 200:
                self.token = data['data']['token']
                return True, "登录成功"
            return False, data.get('message', '登录失败')
        except Exception as e:
            return False, str(e)
    
    def get_envs(self, name=None):
        if not self.token: return []
        try:
            url = f"{self.base_url}/open/envs"
            if name: url += f"?searchValue={name}"
            r = requests.get(url, headers={"Authorization": f"Bearer {self.token}"}, timeout=10)
            return r.json().get('data', []) if r.json().get('code') == 200 else []
        except:
            return []
    
    def add_env(self, name, value, remarks=""):
        if not self.token: return False, "未登录"
        try:
            r = requests.post(f"{self.base_url}/open/envs", json=[{"name": name, "value": value, "remarks": remarks}], headers={"Authorization": f"Bearer {self.token}"}, timeout=10)
            return r.json().get('code') == 200, r.json().get('message', '')
        except Exception as e:
            return False, str(e)
    
    def update_env(self, env_id, name, value, remarks=""):
        if not self.token: return False, "未登录"
        try:
            r = requests.put(f"{self.base_url}/open/envs", json={"id": env_id, "name": name, "value": value, "remarks": remarks}, headers={"Authorization": f"Bearer {self.token}"}, timeout=10)
            return r.json().get('code') == 200, r.json().get('message', '')
        except Exception as e:
            return False, str(e)

def get_ql_config():
    ql_str = middleware.bucketGet(bucket='G_SXZB', key='ql_config') or ''
    if '丨' in ql_str:
        parts = ql_str.split('丨')
        return {
            'url': parts[0].strip() if len(parts) > 0 else '',
            'client_id': parts[1].strip() if len(parts) > 1 else '',
            'client_secret': parts[2].strip() if len(parts) > 2 else ''
        }
    return {'url': '', 'client_id': '', 'client_secret': ''}

def upload_to_qinglong():
    if not sender.isAdmin():
        sender.reply("❌ 仅管理员可使用此功能")
        return
    ql_config = get_ql_config()
    if not all([ql_config['url'], ql_config['client_id'], ql_config['client_secret']]):
        sender.reply("❌ 青龙配置不完整，请先配置青龙地址、ClientID、ClientSecret")
        return
    all_users = middleware.bucketKeys(bucket='G_sxzb_user') or []
    if not all_users:
        sender.reply("❌ 没有找到任何账号")
        return
    sender.reply("⏳ 正在连接青龙...")
    ql = QingLongAPI(ql_config['url'], ql_config['client_id'], ql_config['client_secret'])
    success, msg = ql.login()
    if not success:
        sender.reply(f"❌ 青龙连接失败: {msg}")
        return
    tokens = []
    for user in all_users:
        accounts = get_user_accounts(user)
        for account_id in accounts:
            auth_data = middleware.bucketGet('G_sxzb_auth', account_id)
            if not auth_data: continue
            try:
                auth_info = json.loads(auth_data)
                expire_date = auth_info.get('expire_time', '')
                if expire_date and datetime.strptime(expire_date, "%Y-%m-%d").date() < datetime.now().date(): continue
            except: continue
            token_data = middleware.bucketGet('G_sxzb_token', account_id)
            if token_data: tokens.append(token_data)
    if not tokens:
        sender.reply("❌ 没有找到有效授权的账号")
        return
    env_name = "G_SXZB_TOKEN"
    env_value = "\n".join(tokens)
    existing = ql.get_envs(env_name)
    target_env = next((e for e in existing if e.get('name') == env_name), None)
    if target_env:
        success, msg = ql.update_env(target_env['id'], env_name, env_value, f"森选Token-{len(tokens)}个")
        action = "更新"
    else:
        success, msg = ql.add_env(env_name, env_value, f"森选Token-{len(tokens)}个")
        action = "添加"
    if success:
        sender.reply(f"✅ 上传青龙成功！\n📦 变量名: {env_name}\n👥 账号数: {len(tokens)}个\n🔄 操作: {action}")
    else:
        sender.reply(f"❌ 上传失败: {msg}")

def auto_upload_qinglong(account_id=None):
    """自动上传token到青龙面板，统一变量名，通过remarks区分账号，返回(成功状态, 消息)"""
    ql_config = get_ql_config()
    if not all([ql_config['url'], ql_config['client_id'], ql_config['client_secret']]):
        return False, "青龙配置未完成"
    
    ql = QingLongAPI(ql_config['url'], ql_config['client_id'], ql_config['client_secret'])
    success, msg = ql.login()
    if not success:
        return False, f"青龙登录失败: {msg}"
    
    env_name = "G_SXZB_TOKEN"
    
    if account_id:
        token_data = middleware.bucketGet('G_sxzb_token', account_id)
        if not token_data:
            return False, "Token数据缺失"
        
        # 解析备注
        if '#' in token_data:
            remark = token_data.split('#', 1)[0].strip()
        else:
            remark = "默认账号"
        
        # 获取授权到期时间
        auth_data = middleware.bucketGet('G_sxzb_auth', account_id)
        if auth_data:
            try:
                auth_info = json.loads(auth_data)
                expire_time = auth_info.get('expire_time', '未知')
            except:
                expire_time = '未知'
        else:
            expire_time = '未知'
        
        # 构建remarks：森选直播:{account_id}丨用户:{userid}丨到期:{expire_time}丨备注:{remark}
        remarks = f"森选直播:{account_id}丨用户:{userid}丨到期:{expire_time}丨备注:{remark}"
        
        # 检查是否已存在该账号的变量（通过remarks中的account_id匹配）
        all_envs = ql.get_envs(env_name)
        existing_env = None
        for env in all_envs:
            env_remarks = env.get('remarks', '')
            env_envname = env.get('name', '')
            if env_envname == env_name and account_id in env_remarks:
                existing_env = env
                break
        
        if existing_env:
            # 已存在，更新变量
            success, msg = ql.update_env(existing_env['id'], env_name, token_data, remarks)
            if success:
                return True, f"已更新到青龙"
            else:
                return False, f"青龙更新失败: {msg}"
        else:
            # 不存在，添加新变量
            success, msg = ql.add_env(env_name, token_data, remarks)
            if success:
                return True, f"已上传到青龙"
            else:
                return False, f"青龙添加失败: {msg}"
    
    return False, "未指定账号ID"

def get_user_accounts(user_id=None):
    if user_id is None: user_id = userid
    uservalue = middleware.bucketGet('G_sxzb_user', user_id) or '[]'
    try:
        accounts_list = json.loads(uservalue)
        return [str(acc) for acc in accounts_list] if isinstance(accounts_list, list) else [str(accounts_list)]
    except:
        return []

def get_user_points(user_id=None):
    if not user_id: user_id = sender.getUserID()
    points = middleware.bucketGet('dd_sign_coin', user_id) or "0"
    user_points = middleware.bucketGet('dd_sign_points', user_id) or "0"
    result_points = {'dd_sign_coin': int(points), 'dd_sign_points': int(user_points), 'total': int(points) + int(user_points)}
    if points == "0":
        sign_key = f"sign_{user_id}"
        sign_points = middleware.bucketGet('dd_sign_coin', sign_key)
        if sign_points:
            result_points['dd_sign_coin'] = int(sign_points)
            result_points['total'] = int(sign_points) + int(user_points)
    return result_points

def set_user_points(user_id, points):
    """设置用户积分 - 适配呆呆积分数据结构"""
    # 尝试更新主积分值
    middleware.bucketSet('dd_sign_coin', user_id, str(points['dd_sign_coin']))
    middleware.bucketSet('dd_sign_points', user_id, str(points['dd_sign_points']))
    
    # 尝试更新带'sign_'前缀的积分值
    sign_key = f"sign_{user_id}"
    middleware.bucketSet('dd_sign_coin', sign_key, str(points['dd_sign_coin']))
    return True 

def verify_live_api(token: str) -> Dict[str, Any]:
    """使用直播接口验证token有效性"""
    url = "https://yh.sentezhenxuan.com/api/mobile/shop-live/room/getLiveRoomActivity"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "authorization": token,
        "app-sign": "wx1b482e08a5617509",
        "referer": "https://servicewechat.com/wx1b482e08a5617509/7/page-frame.html",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF"
    }
    params = {
        "source_type": 2314,
        "source_from": 2321,
        "source_lang": "zh_CN",
        "currency_id": 86,
        "site_id": "",
        "roomId": 2781
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0:
            user_id = None
            # 尝试从JWT token中解析user_id
            try:
                import base64
                token_without_bearer = token.replace("Bearer ", "").replace("bearer ", "")
                payload = token_without_bearer.split('.')[1]
                # 添加padding
                padding = len(payload) % 4
                if padding:
                    payload += '=' * (4 - padding)
                decoded = base64.b64decode(payload)
                jwt_data = json.loads(decoded)
                user_id = jwt_data.get('id')
            except:
                pass
            
            return {
                "success": True,
                "user_id": user_id,
                "data": data
            }
        else:
            return {
                "success": False,
                "msg": data.get('msg', '未知错误'),
                "data": data
            }
    except Exception as e:
        return {
            "success": False,
            "msg": str(e),
            "error": e
        }

def validate_token(token_with_remark):
    """验证Token有效性并返回账号信息"""
    try:
        # 处理带备注的token
        if '#' in token_with_remark:
            remark, raw_token = token_with_remark.split('#', 1)
            remark = remark.strip()
            token = raw_token.strip()
        else:
            token = token_with_remark.strip()
            remark = "默认账号"
            
        # 简单验证Token格式
        if len(token) < 10:  # 合理的最小长度
            return False, {'error': 'Token格式错误，长度不足'}
            
        # 确保token有Bearer前缀
        if token.lower().startswith("bearer "):
            full_token = token
        else:
            full_token = f"Bearer {token}" 
            
        # 使用直播API验证
        live_result = verify_live_api(full_token)
        if live_result["success"]:
            account_id = live_result.get("user_id")
            # 如果能获取到用户ID，就使用它
            if account_id:
                return True, {
                    'account_id': str(account_id),
                    'nickname': remark
                }
            # 如果验证成功但没有获取到用户ID，使用时间戳生成ID
            timestamp = int(time.time() * 1000)
            account_id = f"sxzb_{hashlib.md5(str(timestamp).encode()).hexdigest()[:10]}"
            return True, {
                'account_id': str(account_id),
                'nickname': remark
            }
        
        # 直播API验证失败
        return False, {'error': f'直播API验证失败: {live_result.get("msg", "未知错误")}'}
        
    except Exception as e:
        return False, {'error': f'验证失败: {str(e)}'}

def bindaccount():
    """森选登录绑定 - 支持批量登录"""
    welcome_msg = """
=====森选直播登录=====
请按格式输入: 备注#authorization
示例: 张三#eyJ0eXAiOi...

🔰 支持批量登录，一行一个账号
示例:
张三#eyJ0eXAiOi...
李四#eyJ0eXAiOi...

⚠️ 复制token时请勿包含Bearer前缀
------------------
回复「q」退出绑定
=================="""
    sender.reply(welcome_msg)
    ck_input = sender.input(120000, 1, False).strip()
    if ck_input.lower() == 'q': 
        sender.reply("✅ 已取消登录")
        return

    # 分割多行输入
    account_lines = ck_input.strip().split('\n')
    is_batch = len(account_lines) > 1
    
    if is_batch:
        sender.reply("⏳ 正在处理批量登录请求，请稍候...")
    
    success_count = 0
    fail_count = 0
    failed_accounts = []
    accounts = get_user_accounts()
    last_success_info = None
    
    for line in account_lines:
        line = line.strip()
        if not line:
            continue
        
        # 验证输入格式
        if '#' not in line:
            fail_count += 1
            failed_accounts.append({'account': line[:20] + '...' if len(line) > 20 else line, 'reason': '格式错误(缺少#分隔)'})
            continue
        
        remark, access_token = line.split('#', 1)
        remark = remark.strip()
        access_token = access_token.strip()
        
        # 去除可能包含的Bearer前缀和清理格式
        if access_token.lower().startswith("bearer "):
            access_token = access_token[7:].strip()
        access_token = access_token.strip('"\'').strip()
        
        # 确认token格式
        if len(access_token) < 20:
            fail_count += 1
            failed_accounts.append({'account': remark, 'reason': 'Token长度过短'})
            continue
        
        # 完整的token_with_remark
        token_with_remark = f"{remark}#{access_token}"
        
        # 验证token有效性
        is_valid, result = validate_token(token_with_remark)
        if not is_valid:
            fail_count += 1
            error_msg = result.get('error', '未知错误')
            failed_accounts.append({'account': remark, 'reason': error_msg[:30]})
            continue
        
        # 获取账号ID和用户信息
        account_id = result.get('account_id', "unknown")
        
        # 存储访问令牌（带备注）
        middleware.bucketSet(bucket='G_sxzb_token', key=str(account_id), value=token_with_remark)
        
        # 添加到账号列表
        if account_id not in accounts:
            accounts.append(account_id)
        
        # 检查是否已授权，如果已授权则自动上传青龙
        auth_data = middleware.bucketGet('G_sxzb_auth', account_id)
        if auth_data:
            try:
                auto_upload_qinglong(account_id)
            except:
                pass
        
        success_count += 1
        last_success_info = {'account_id': account_id, 'remark': remark}
    
    # 更新用户账号列表
    if accounts:
        middleware.bucketSet('G_sxzb_user', userid, json.dumps(accounts))
    
    # 显示结果
    if is_batch:
        result_msg = f"""
=====批量登录结果=====
✅ 成功: {success_count}个账号
❌ 失败: {fail_count}个账号"""
        
        if failed_accounts:
            result_msg += "\n------------------\n⚠️ 失败账号详情:"
            for idx, fail_info in enumerate(failed_accounts[:5], 1):
                result_msg += f"\n{idx}. {fail_info['account']}\n   原因: {fail_info['reason']}"
            if len(failed_accounts) > 5:
                result_msg += f"\n...还有{len(failed_accounts)-5}个失败"
        
        result_msg += "\n------------------\n💡 发送「森选直播管理」可管理账号\n=================="
        sender.reply(result_msg)
    elif success_count == 1 and last_success_info:
        sender.reply(f"""
✅ 登录成功
🆔 账号ID: {last_success_info['account_id']}
🏷️ 备注: {last_success_info['remark']}

发送「森选直播管理」进行账号授权""")
    else:
        sender.reply("❌ 登录失败")

def query_account_status():
    """查询账号状态"""
    accounts = get_user_accounts()
    
    if not accounts:
        sender.reply("❌ 您尚未绑定任何账号，请先绑定")
        return
    
    # 合并所有账号信息
    all_results = []
    
    for idx, account_id in enumerate(accounts, 1):
        # 获取账号的access token
        token_with_remark = middleware.bucketGet('G_sxzb_token', account_id)
        if not token_with_remark:
            all_results.append(f"账号 {idx}: ❌ Token缺失")
            continue
            
        # 获取备注
        if '#' in token_with_remark:
            remark, token = token_with_remark.split('#', 1)
            remark = remark.strip()
            token = token.strip()
        else:
            token = token_with_remark.strip()
            remark = "默认账号"
            
        display_name = remark
        
        # 构建账号结果消息
        result_msg = f"------ 森选详情 [{idx}] ------\n"
        result_msg += f"📱 账号: {display_name}\n"
        
        # 检查授权状态
        auth_data = middleware.bucketGet('G_sxzb_auth', key=account_id)
        expire_date = "未知"
        if auth_data:
            try:
                auth_info = json.loads(auth_data)
                expire_date = auth_info.get('expire_time', '未知')
                result_msg += f"🔐 授权状态: ✅ 已授权\n"
                result_msg += f"📅 到期时间: {expire_date}\n"
                
                # 检查是否即将到期（小于4天）
                if expire_date != "未知":
                    try:
                        expire_date_obj = datetime.strptime(expire_date, "%Y-%m-%d").date()
                        today = datetime.now().date()
                        days_left = (expire_date_obj - today).days
                        
                        if days_left < 0:
                            result_msg += "⚠️ 🚨 授权已过期，即将自动删除！\n"
                        elif days_left < 4:
                            result_msg += f"⚠️ 🔥 授权即将到期！还有{days_left}天\n"
                            result_msg += "💡 过期自动删除账号！\n"
                    except:
                        pass
            except:
                result_msg += "🔐 授权状态: ✅ 已授权\n"
                result_msg += "📅 到期时间: 未知\n"
        else:
            result_msg += "🔐 授权状态: ❌ 未授权\n"
        
        # 获取账号积分等信息
        try:
            client = SenxuanClient(token_with_remark)
            withdraw_info = client.get_withdraw_records()
            
            if withdraw_info and withdraw_info.get("success") and withdraw_info.get("records"):
                withdraw_records = withdraw_info.get("records")
                total_amount = sum(float(r.get("number", "0")) for r in withdraw_records)
                
                result_msg += f"💰 成功领取: {len(withdraw_records)}笔, 总计: {total_amount:.2f}元\n"
                
                if withdraw_records:
                    result_msg += "------ 🎁任务完成🎁 ------\n"
                    for record in withdraw_records[:5]:
                        amount = record.get("number", "0")
                        add_time = record.get("add_time", "未知")
                        result_msg += f"现金{amount}元-{add_time}\n"
            elif token:
                bearer_token = f"Bearer {token}" if not token.lower().startswith("bearer ") else token
                live_result = verify_live_api(bearer_token)
                if live_result.get("success"):
                    result_msg += "✅ Token有效\n"
                else:
                    result_msg += "❌ 你掉CK了,发森选管理更新CK\n"
        except Exception as e:
            result_msg += f"❌ 查询失败: {str(e)[:50]}\n"
        
        all_results.append(result_msg)
    
    # 一次性发送所有账号信息，末尾加上统一的结束分隔符
    final_result = "\n".join(all_results) + "\n------------------------"
    sender.reply(final_result)

def show_tutorial():
    """显示使用教程"""
    tutorial = """
=====森选直播使用教程=====
1️⃣ 「森选直播登录」绑定账号
   - 获取方法：微信小程序【银鱼质亨】直播间
   - 抓取域名：yh.sentezhenxuan.com
   - 抓取字段：authorization (去除Bearer前缀)
   - 格式：备注#token (例如：我的账号#eyJ0eXAiOi...)

2️⃣ 「森选直播管理」进行账号授权
   - 支持微信支付或积分支付
   - 可更新账号token（token过期时使用）
   - 授权后可自动抢直播间红包

3️⃣ 「森选直播查询」查询账号状态
   - 查看账号授权状态
   - 查看到期时间
   - 查看token有效性

👉 手动抓包教程:
1. 打开微信小程序【银鱼质亨】
2. 进入直播间页面
3. 使用抓包工具监听请求
4. 找到yh.sentezhenxuan.com域名请求
5. 推荐URL: /api/mobile/shop-live/room/getLiveRoomActivity
6. 复制请求头中的authorization值
7. 使用"备注#token"格式添加账号
   例如：张三#eyJ0eXAiOi...

💡 Token失效问题处理:
1. 在「森选直播管理」中选择账号后，选择"更新账号"
2. 重新打开小程序直播间并抓包获取新token
3. 输入新token（可保留原备注）
4. 系统会自动验证token有效性
=================="""
    sender.reply(tutorial)

def sz_manage():
    """账号管理 - 支持批量授权合并支付"""
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 您还没有绑定账号，请先发送【森选直播登录】绑定")
        return
    
    authorized_count = 0
    unauthorized_accounts = []
    account_list = []
    
    for idx, account_id in enumerate(accounts, 1):
        token_data = middleware.bucketGet('G_sxzb_token', account_id)
        if not token_data:
            continue
        
        remark = "默认账号"
        if '#' in token_data:
            remark = token_data.split('#', 1)[0].strip()
        
        auth_data = middleware.bucketGet('G_sxzb_auth', account_id)
        if auth_data:
            authorized_count += 1
            try:
                auth_info = json.loads(auth_data)
                expire_date = auth_info.get('expire_time', '未知')
                expire_date_obj = datetime.strptime(expire_date, "%Y-%m-%d").date()
                today = datetime.now().date()
                days_left = (expire_date_obj - today).days
                if days_left >= 0:
                    status = f"✅已授权({days_left}天)"
                else:
                    status = "⚠️已过期"
            except:
                status = "✅已授权"
        else:
            unauthorized_accounts.append(account_id)
            status = "❌未授权"
        
        account_list.append(f"[{idx}] {remark} {status}")
    
    # 添加批量操作选项
    batch_options = []
    if len(accounts) > 0:
        batch_options.append("[0] 授权所有账号")
    if unauthorized_accounts:
        batch_options.append("[9999] 授权未授权账号")
    
    if batch_options:
        account_list.append("")
        account_list.extend(batch_options)
    
    account_list_str = "\n".join(account_list)
    user_points = get_user_points()
    
    menu_msg = f"""=====森选直播管理=====
🔢 绑定账号: {len(accounts)}个
✅ 已授权: {authorized_count}个
❌ 未授权: {len(unauthorized_accounts)}个
💎 当前积分: {user_points['total']}
-------------------------
{account_list_str}
------------------
回复序号选择账号操作（q退出）
=================="""
    
    sender.reply(menu_msg)
    choice = sender.input(60000, 1, False).strip()
    
    if choice.lower() == 'q':
        sender.reply("✅ 已退出管理")
        return
    
    if choice == '0':
        # 授权所有账号
        batch_authorize_accounts(accounts)
        return
    elif choice == '9999':
        # 授权未授权账号
        batch_authorize_accounts(unauthorized_accounts)
        return
    
    if not choice.isdigit():
        sender.reply("❌ 输入无效")
        return
    
    selected_idx = int(choice) - 1
    if selected_idx < 0 or selected_idx >= len(accounts):
        sender.reply("❌ 序号无效")
        return
    
    account_id = accounts[selected_idx]
    token_data = middleware.bucketGet('G_sxzb_token', account_id)
    remark = "默认账号"
    if token_data and '#' in token_data:
        remark = token_data.split('#', 1)[0].strip()
    
    sender.reply(f"""你选择了账号: {remark}
[1] 授权账号
[2] 更新token
[3] 删除账号
回复q退出""")
    
    op = sender.input(60000, 1, False).strip()
    
    if op == '1':
        _handle_authorize_single(account_id)
    elif op == '2':
        _handle_update_token_single(account_id, remark)
    elif op == '3':
        _handle_delete_account_single(account_id, remark)

def batch_authorize_accounts(target_accounts):
    """批量授权账号并一次性支付"""
    if not target_accounts:
        sender.reply("❌ 没有可授权的账号")
        return
    
    config = get_config()
    account_list = []
    
    # 统计已授权和未授权账号
    authorized_list = []
    unauthorized_list = []
    
    for i, account_id in enumerate(target_accounts, 1):
        token_with_remark = middleware.bucketGet('G_sxzb_token', account_id) or ""
        if '#' in token_with_remark:
            remark = token_with_remark.split('#', 1)[0].strip()
        else:
            remark = "默认账号"
        
        auth_data = middleware.bucketGet('G_sxzb_auth', account_id)
        if auth_data:
            authorized_list.append(f"{i}. {remark} ✅")
            account_list.append(f"{i}. {remark} ✅")
        else:
            unauthorized_list.append(f"{i}. {remark} ❌")
            account_list.append(f"{i}. {remark} ❌")
    
    accounts_str = "\n".join(account_list)
    
    # 根据账号情况显示不同的标题
    if len(authorized_list) > 0 and len(unauthorized_list) > 0:
        title = "批量授权所有账号"
        tip = f"共 {len(target_accounts)} 个账号（已授权{len(authorized_list)}个，未授权{len(unauthorized_list)}个）"
    elif len(authorized_list) > 0:
        title = "批量续费已授权账号"
        tip = f"共 {len(target_accounts)} 个已授权账号"
    else:
        title = "批量授权未授权账号"
        tip = f"共 {len(target_accounts)} 个未授权账号"
    
    sender.reply(f"""====={title}=====
{tip}:
{accounts_str}
------------------
请输入授权月数 (1-12):
==================""")
    
    months_input = sender.input(120000, 1, False).strip()
    if not months_input.isdigit() or int(months_input) < 1 or int(months_input) > 12:
        sender.reply("❌ 月数必须为1-12之间的整数")
        return
    
    months = int(months_input)
    total_price = config['price'] * months * len(target_accounts)
    required_points = config['points_per_month'] * months * len(target_accounts)
    current_points = get_user_points()
    
    pay_menu = f"""=====批量授权支付=====
🎯 授权账号数: {len(target_accounts)}个
🎯 授权时长: {months}个月/账号
💰 总金额: ¥{total_price:.2f}
💎 积分支付: {required_points}积分（当前: {current_points['total']}）
------------------
[1] 微信支付
[2] 积分支付
回复数字选择，回复q取消
=================="""
    
    sender.reply(pay_menu)
    pay_choice = sender.input(120000, 1, False).strip()
    
    if pay_choice.lower() == 'q':
        sender.reply("✅ 已取消授权")
        return
    
    payment_success = False
    if pay_choice == '1' and config['zsm']:
        payment_success = _batch_wechat_payment(target_accounts, months, total_price, config)
    elif pay_choice == '2':
        payment_success = _batch_points_payment(target_accounts, months, required_points)
    else:
        sender.reply("❌ 无效支付方式")
        return
    
    if payment_success:
        success_count = 0
        for account_id in target_accounts:
            try:
                expire_time = (datetime.now() + timedelta(days=months*30)).strftime("%Y-%m-%d")
                auth_info = {
                    'expire_time': expire_time,
                    'payment_type': 'batch',
                    'months': months
                }
                middleware.bucketSet('G_sxzb_auth', account_id, json.dumps(auth_info))
                auto_upload_qinglong(account_id)
                success_count += 1
            except:
                pass
        
        ql_config = get_ql_config()
        ql_note = ""
        if all([ql_config['url'], ql_config['client_id'], ql_config['client_secret']]):
            ql_note = "\n📤 已自动同步到青龙面板"
        
        sender.reply(f"""✅ 批量授权成功！
🎯 共授权 {success_count}/{len(target_accounts)} 个账号
📅 授权时长: {months}个月/账号
📆 到期日期: {(datetime.now() + timedelta(days=months*30)).strftime("%Y-%m-%d")}{ql_note}""")

def _batch_wechat_payment(accounts, months, amount, config):
    """批量微信支付"""
    if not config['zsm']:
        sender.reply("❌ 管理员未配置收款码")
        return False
    
    sender.sendImageByURL(config['zsm'])
    sender.reply(f"""=====微信扫码支付=====
🎯 授权账号数: {len(accounts)}个
🎯 授权时长: {months}个月/账号
💰 总金额: ¥{amount:.2f}
------------------
请扫码支付后发送"完成"或截图
回复q取消支付
==================""")
    
    result = sender.listen(600000, 1, False)
    if result.lower() == 'q':
        sender.reply("✅ 已取消支付")
        return False
    
    sender.reply(f"""✅ 支付确认成功
💰 金额: ¥{amount:.2f}元
==================""")
    return True

def _batch_points_payment(accounts, months, required_points):
    """批量积分支付"""
    user_points = get_user_points(userid)
    
    if user_points['total'] < required_points:
        sender.reply(f"""❌ 积分不足！
需要: {required_points}积分
当前: {user_points['total']}积分""")
        return False
    
    sender.reply(f"""⚠ 确认使用积分批量支付吗？
💎 扣除: {required_points}积分
💰 剩余: {user_points['total'] - required_points}积分
------------------
回复 [Y] 确认支付
回复 [N] 取消""")
    
    confirm = sender.input(60000, 1, False).strip().lower()
    if confirm != 'y':
        sender.reply("✅ 积分支付已取消")
        return False
    
    remaining = required_points
    new_points = user_points.copy()
    
    if new_points['dd_sign_coin'] >= remaining:
        new_points['dd_sign_coin'] -= remaining
    else:
        remaining -= new_points['dd_sign_coin']
        new_points['dd_sign_coin'] = 0
        new_points['dd_sign_points'] -= remaining
    
    new_points['total'] = new_points['dd_sign_coin'] + new_points['dd_sign_points']
    set_user_points(userid, new_points)
    
    sender.reply(f"✅ 积分批量支付成功！扣除 {required_points}积分，剩余: {new_points['total']}")
    return True

def _handle_authorize_single(account_id):
    """处理单个账号授权"""
    config = get_config()
    
    payment_msg = f"""=====账号授权=====
📋 授权费用: {config['price']}元/月
💎 或使用积分: {config['points_per_month']}积分/月
------------------
请选择支付方式:
1. 微信支付({config['price']}元/月)
2. 积分支付({config['points_per_month']}积分/月)
------------------
回复「q」取消授权
=================="""
    
    sender.reply(payment_msg)
    payment_choice = sender.input(60000, 1, False).strip()
    
    if payment_choice.lower() == 'q':
        sender.reply("✅ 已取消授权")
        return
    
    if payment_choice == '1':
        _process_wechat_payment(account_id, config)
    elif payment_choice == '2':
        _process_points_payment(account_id, config)
    else:
        sender.reply("❌ 无效选择")

def _process_wechat_payment(account_id, config):
    """处理微信支付"""
    if not config['zsm']:
        sender.reply("❌ 管理员未配置收款码")
        return
    
    sender.sendImageByURL(config['zsm'])
    sender.reply(f"""=====微信支付授权=====
💰 请支付: {config['price']}元
⏰ 请在3分钟内完成支付

支付完成后发送支付结果截图或者文字"完成"
回复「q」取消支付
==================""")
    
    result = sender.listen(180000, 1, False)
    if result.lower() == 'q':
        sender.reply("✅ 已取消支付")
        return
    
    expire_time = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    auth_info = {
        'expire_time': expire_time,
        'payment_type': 'wechat',
        'amount': config['price']
    }
    
    middleware.bucketSet('G_sxzb_auth', account_id, json.dumps(auth_info))
    
    ql_success, ql_msg = auto_upload_qinglong(account_id)
    ql_status = f"\n📤 青龙同步: {ql_msg}" if ql_success or "配置未完成" not in ql_msg else ""
    
    sender.reply(f"""✅ 授权成功
📅 到期时间: {expire_time}
💰 支付方式: 微信支付
💵 支付金额: {config['price']}元{ql_status}""")

def _process_points_payment(account_id, config):
    """处理积分支付"""
    user_points = get_user_points(userid)
    required_points = config['points_per_month']
    
    if user_points['total'] < required_points:
        sender.reply(f"""❌ 积分不足
💎 需要积分: {required_points}
💰 当前积分: {user_points['total']}
💸 还差: {required_points - user_points['total']}积分""")
        return
    
    remaining = required_points
    new_points = user_points.copy()
    
    if new_points['dd_sign_coin'] >= remaining:
        new_points['dd_sign_coin'] -= remaining
        remaining = 0
    else:
        remaining -= new_points['dd_sign_coin']
        new_points['dd_sign_coin'] = 0
        new_points['dd_sign_points'] -= remaining
    
    new_points['total'] = new_points['dd_sign_coin'] + new_points['dd_sign_points']
    set_user_points(userid, new_points)
    
    expire_time = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    auth_info = {
        'expire_time': expire_time,
        'payment_type': 'points',
        'points': required_points
    }
    
    middleware.bucketSet('G_sxzb_auth', account_id, json.dumps(auth_info))
    
    ql_success, ql_msg = auto_upload_qinglong(account_id)
    ql_status = f"\n📤 青龙同步: {ql_msg}" if ql_success or "配置未完成" not in ql_msg else ""
    
    sender.reply(f"""✅ 授权成功
📅 到期时间: {expire_time}
💎 消耗积分: {required_points}
💰 剩余积分: {new_points['total']}{ql_status}""")

def _handle_update_token_single(account_id, old_remark):
    """处理更新token"""
    old_token = middleware.bucketGet('G_sxzb_token', account_id)
    
    sender.reply(f"""=====更新Token=====
📱 账号: {old_remark}
------------------
请输入新的token:
格式: 备注#token
或直接输入token(保留原备注)
------------------
回复「q」取消更新
==================""")
    
    new_token_input = sender.input(120000, 1, False).strip()
    if new_token_input.lower() == 'q':
        sender.reply("✅ 已取消更新")
        return
    
    if '#' in new_token_input:
        new_remark, new_token = new_token_input.split('#', 1)
        new_remark = new_remark.strip()
        new_token = new_token.strip()
    else:
        new_remark = old_remark
        new_token = new_token_input.strip()
    
    if new_token.lower().startswith("bearer "):
        new_token = new_token[7:].strip()
    
    token_with_remark = f"{new_remark}#{new_token}"
    is_valid, result = validate_token(token_with_remark)
    
    if not is_valid:
        sender.reply(f"❌ Token验证失败: {result.get('error', '未知错误')}")
        return
    
    middleware.bucketSet('G_sxzb_token', account_id, token_with_remark)
    sender.reply(f"""✅ 更新成功
📱 账号: {new_remark}
🔑 Token已更新""")

def _handle_delete_account_single(account_id, remark):
    """处理删除账号"""
    token_data = middleware.bucketGet('G_sxzb_token', account_id)
    
    sender.reply(f"""=====确认删除=====
📱 账号: {remark}
⚠️ 删除后无法恢复
------------------
确认删除请回复「确认」
回复「q」取消删除
==================""")
    
    confirm = sender.input(30000, 1, False).strip()
    if confirm != "确认":
        sender.reply("✅ 已取消删除")
        return
    
    middleware.bucketDel('G_sxzb_token', account_id)
    middleware.bucketDel('G_sxzb_auth', account_id)
    accounts = get_user_accounts()
    if account_id in accounts:
        accounts.remove(account_id)
    middleware.bucketSet('G_sxzb_user', userid, json.dumps(accounts))
    
    sender.reply(f"✅ 删除成功\n📱 账号: {remark}")

def admin_authorize_account():
    """管理员授权账号"""
    sender.reply("""=====管理员授权=====
请输入用户ID:
回复「q」退出
==================""")
    
    user_id = sender.input(60000, 1, False).strip()
    if user_id.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
    accounts = get_user_accounts(user_id)
    if not accounts:
        sender.reply(f"❌ 用户 {user_id} 没有绑定账号")
        return
    
    menu_msg = f"=====用户账号列表=====\n用户ID: {user_id}\n------------------\n"
    for idx, account_id in enumerate(accounts, 1):
        token_data = middleware.bucketGet('G_sxzb_token', account_id)
        if not token_data:
            continue
        
        remark = "默认账号"
        if '#' in token_data:
            remark = token_data.split('#', 1)[0].strip()
        
        auth_data = middleware.bucketGet('G_sxzb_auth', account_id)
        auth_status = "❌ 未授权"
        if auth_data:
            try:
                auth_info = json.loads(auth_data)
                expire_date = auth_info.get('expire_time', '未知')
                auth_status = f"✅ 已授权(至{expire_date})"
            except:
                auth_status = "✅ 已授权"
        
        menu_msg += f"{idx}. {remark} {auth_status}\n"
    
    menu_msg += "------------------\n请输入要授权的账号序号:\n回复「q」退出\n=================="
    sender.reply(menu_msg)
    
    idx_input = sender.input(60000, 1, False).strip()
    if idx_input.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
    try:
        idx = int(idx_input) - 1
        if idx < 0 or idx >= len(accounts):
            sender.reply("❌ 无效序号")
            return
    except:
        sender.reply("❌ 请输入数字")
        return
    
    account_id = accounts[idx]
    
    sender.reply("""请输入授权天数:
示例: 30(表示30天)
回复「q」取消
==================""")
    
    days_input = sender.input(60000, 1, False).strip()
    if days_input.lower() == 'q':
        sender.reply("✅ 已取消")
        return
    
    try:
        days = int(days_input)
        if days <= 0:
            sender.reply("❌ 天数必须大于0")
            return
    except:
        sender.reply("❌ 请输入有效数字")
        return
    
    expire_time = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    auth_info = {
        'expire_time': expire_time,
        'payment_type': 'admin',
        'days': days
    }
    
    middleware.bucketSet('G_sxzb_auth', account_id, json.dumps(auth_info))
    
    ql_success, ql_msg = auto_upload_qinglong(account_id)
    ql_status = f"\n📤 青龙同步: {ql_msg}" if ql_success or "配置未完成" not in ql_msg else ""
    
    sender.reply(f"""✅ 授权成功
👤 用户ID: {user_id}
🆔 账号ID: {account_id}
📅 到期时间: {expire_time}
⏱️ 授权天数: {days}天{ql_status}""")

def sz_clean_accounts():
    """清理未授权和授权过期的森选直播账号"""
    if not sender.isAdmin():
        sender.reply("""
=====权限不足=====
❌ 您没有权限执行此操作
==================""")
        return
        
    # 获取所有用户
    users = middleware.bucketAllKeys(bucket='G_sxzb_user')
    
    if not users:
        sender.reply("""
=====清理结果=====
❌ 未找到任何绑定账号
==================""")
        return
        
    sender.reply(f"""
=====开始清理=====
📊 共找到: {len(users)}个用户
⏳ 清理中请稍候...
==================""")
    
    cleaned_count = 0
    failed_count = 0
    today = datetime.now().date()
    
    for user in users:
        try:
            accountlist = middleware.bucketGet(bucket='G_sxzb_user', key=f'{user}')
            if not accountlist:
                continue
                
            accounts = json.loads(accountlist)
            if not isinstance(accounts, list):
                accounts = [accounts]
                
            valid_accounts = []
            
            for account_id in accounts:
                should_delete = False
                auth_data_str = middleware.bucketGet(bucket='G_sxzb_auth', key=account_id)
                
                if not auth_data_str:
                    # 未授权账号，删除
                    should_delete = True
                else:
                    try:
                        auth_data = json.loads(auth_data_str)
                        expire_date = auth_data.get('expire_time')
                        
                        if expire_date:
                            expire_date_obj = datetime.strptime(expire_date, "%Y-%m-%d").date()
                            if expire_date_obj < today:
                                # 已过期账号，删除
                                should_delete = True
                    except:
                        # 数据异常，删除
                        should_delete = True
                
                if should_delete:
                    try:
                        # 删除token和授权信息
                        middleware.bucketDel(bucket='G_sxzb_token', key=account_id)
                        middleware.bucketDel(bucket='G_sxzb_auth', key=account_id)
                        cleaned_count += 1
                    except:
                        failed_count += 1
                else:
                    # 保留有效账号
                    valid_accounts.append(account_id)
            
            # 更新用户的账号列表
            if valid_accounts:
                middleware.bucketSet(bucket='G_sxzb_user', key=user, value=json.dumps(valid_accounts))
            else:
                # 如果用户没有有效账号了，删除用户记录
                middleware.bucketDel(bucket='G_sxzb_user', key=user)
                
        except Exception as e:
            failed_count += 1
            continue
    
    # 清理完成
    total_processed = cleaned_count + failed_count
    if total_processed > 0:
        efficiency = (cleaned_count / total_processed) * 100
        result_msg = f"""
=====清理完成=====
✅ 成功清理: {cleaned_count}个账号
❌ 清理失败: {failed_count}个账号
📊 清理效率: {efficiency:.1f}%
=================="""
    else:
        result_msg = f"""
=====清理完成=====
✅ 未发现需要清理的账号
所有账号均为有效授权状态
=================="""
    
    sender.reply(result_msg)

def get_random_ua():
    """生成随机UA"""
    versions = ['126.0.0.0', '127.0.0.0', '128.0.0.0', '129.0.0.0', '130.0.0.0', '131.0.0.0', '132.0.0.0']
    wechat_versions = ['7.0.20.1781', '7.0.21.1800', '7.0.22.1850']
    return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(versions)} Safari/537.36 MicroMessenger/{random.choice(wechat_versions)} NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF"

def get_live_room_list():
    """获取直播间列表"""
    url = "https://yh.sentezhenxuan.com/api/mobile/shop-live/room/getLiveRoomList"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "app-sign": "wx1b482e08a5617509",
        "user-agent": get_random_ua()
    }
    params = {
        "source_type": 2314,
        "source_from": 2321,
        "source_lang": "zh_CN",
        "currency_id": 86,
        "site_id": ""
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        data = r.json()
        return data.get("data", []) if data.get("code") == 0 else []
    except:
        return []

def get_all_authorized_users():
    """获取所有已授权用户"""
    all_users = middleware.bucketAllKeys(bucket='G_sxzb_user') or []
    authorized_users = []
    today = datetime.now().date()
    for user in all_users:
        accounts = get_user_accounts(user)
        has_valid_auth = False
        for account_id in accounts:
            auth_data = middleware.bucketGet('G_sxzb_auth', account_id)
            if auth_data:
                try:
                    auth_info = json.loads(auth_data)
                    expire_date = auth_info.get('expire_time', '')
                    if expire_date:
                        expire_date_obj = datetime.strptime(expire_date, "%Y-%m-%d").date()
                        if expire_date_obj >= today:
                            has_valid_auth = True
                            break
                except:
                    pass
        if has_valid_auth:
            authorized_users.append(user)
    return authorized_users

def sz_subscribe():
    """用户订阅/取消订阅开播提醒"""
    current_status = middleware.bucketGet('G_sxzb_subscribe', userid) or 'on'
    
    if current_status == 'on':
        middleware.bucketSet('G_sxzb_subscribe', userid, 'off')
        sender.reply("✅ 已关闭订阅")
    else:
        middleware.bucketSet('G_sxzb_subscribe', userid, 'on')
        sender.reply("""✅ 订阅成功！

🔔 开播后将自动推送通知
⚠️ 请及时抓包更新token

👉 发送「森选直播管理」更新token
👉 再次发送「森选订阅」可关闭""")

def sz_push():
    """手动触发推送（自动模式）"""
    custom_msg = middleware.bucketGet('G_SXZB', 'push_message') or ''
    subscribers = get_subscribers()
    
    if not subscribers:
        sender.reply("❌ 没有用户订阅，无需推送")
        return
    
    # 模式1：配置了自定义文字 → 直接推送
    if custom_msg:
        message = custom_msg
        
        success_count = 0
        push_errors = []
        
        for user_id in subscribers:
            push_success = False
            try:
                middleware.push('wx', '', user_id, '', message)
                push_success = True
            except Exception as wx_err:
                push_errors.append(f"WX-{user_id}: {str(wx_err)[:30]}")
            
            try:
                middleware.push('qq', '', user_id, '', message)
                push_success = True
            except Exception as qq_err:
                push_errors.append(f"QQ-{user_id}: {str(qq_err)[:30]}")
            
            if push_success:
                success_count += 1
        
        report = f"""✅ 自定义文字推送完成
👥 订阅用户: {len(subscribers)}个
📧 推送成功: {success_count}次
📝 推送内容:
{message}"""
        
        if push_errors:
            report += "\n------------------\n⚠️ 推送错误:\n" + "\n".join([f"• {e}" for e in push_errors[:5]])
        
        sender.reply(report)
        
        # 发送报告给管理员
        admin_list = middleware.bucketGet('G_SXZB', 'push_admins') or ''
        if admin_list:
            admins = [a.strip() for a in admin_list.split(',') if a.strip()]
            try:
                middleware.notifyMasters(report, admins)
            except:
                pass
        return
    
    # 模式2：未配置自定义文字 → 检测直播间开播
    clean_old_push_records()
    rooms = get_live_room_list()
    today = datetime.now().strftime('%Y-%m-%d')
    active_rooms = [r for r in rooms if r.get('start_time', '').startswith(today) and r.get('status') == '0' and '测' not in r.get('title', '')]
    
    if not active_rooms:
        sender.reply("❌ 当前没有今天开播的直播间")
        return
    
    success_count = 0
    pushed_rooms = []
    push_errors = []
    
    for room in active_rooms:
        push_key = f"room_{room['id']}_{today}"
        if middleware.bucketGet('G_sxzb_pushed', push_key):
            continue
        
        message = f"""🔴 森选直播开播提醒

📺 直播间: {room.get('title', '未知')}
🕐 开播时间: {room.get('start_time', '未知')}
👤 主播: {room.get('anchor_name', '未知')}

⚠️ Token可能失效，请及时抽包更新！
👉 发送「森选直播管理」更新token"""
        
        room_success = 0
        for user_id in subscribers:
            push_success = False
            try:
                middleware.push('wx', '', user_id, '森选直播开播', message)
                push_success = True
            except Exception as wx_err:
                push_errors.append(f"WX-{user_id}: {str(wx_err)[:30]}")
            
            try:
                middleware.push('qq', '', user_id, '森选直播开播', message)
                push_success = True
            except Exception as qq_err:
                push_errors.append(f"QQ-{user_id}: {str(qq_err)[:30]}")
            
            if push_success:
                room_success += 1
        
        middleware.bucketSet('G_sxzb_pushed', push_key, 'true')
        success_count += room_success
        pushed_rooms.append(room['title'])
    
    room_list = '\n'.join([f"• {r}" for r in pushed_rooms])
    report = f"""✅ 直播间开播推送完成
📺 直播间: {len(pushed_rooms)}个
👥 订阅用户: {len(subscribers)}个
📧 推送次数: {success_count}次
------------------
{room_list}"""
    
    if push_errors:
        report += "\n------------------\n⚠️ 推送错误:\n" + "\n".join([f"• {e}" for e in push_errors[:5]])
    
    sender.reply(report)
    
    # 发送报告给管理员
    admin_list = middleware.bucketGet('G_SXZB', 'push_admins') or ''
    if admin_list:
        admins = [a.strip() for a in admin_list.split(',') if a.strip()]
        try:
            middleware.notifyMasters(report, admins)
        except:
            pass

def clean_old_push_records():
    """清理旧的推送记录（保留今天的）"""
    today = datetime.now().strftime('%Y-%m-%d')
    all_keys = middleware.bucketAllKeys(bucket='G_sxzb_pushed') or []
    for key in all_keys:
        if today not in key:
            middleware.bucketDel(bucket='G_sxzb_pushed', key=key)

def get_subscribers():
    """获取所有订阅用户（所有已授权用户默认订阅）"""
    authorized_users = get_all_authorized_users()
    subscribers = []
    for user_id in authorized_users:
        subscribe_status = middleware.bucketGet('G_sxzb_subscribe', user_id) or 'on'
        if subscribe_status == 'on':
            subscribers.append(user_id)
    return subscribers


# 主入口函数
try:
    usermessage = sender.getMessage()
except AttributeError:
    usermessage = ""

if re.search(r'森选直播登录', usermessage):
    bindaccount()
elif re.search(r'森选直播管理', usermessage):
    sz_manage()
elif re.search(r'森选直播查询', usermessage):
    query_account_status()
elif re.search(r'森选直播教程', usermessage):
    show_tutorial()
elif re.search(r'森选直播授权$', usermessage) and sender.isAdmin():
    admin_authorize_account()
elif re.search(r'森选直播清理', usermessage) and sender.isAdmin():
    sz_clean_accounts()
elif re.search(r'森选订阅', usermessage):
    sz_subscribe()
elif re.search(r'森选推送', usermessage):
    sz_push()
else:
    sender.setContinue()
