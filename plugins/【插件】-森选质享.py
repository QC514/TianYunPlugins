# [rule: ^(森选|sz)(登录|登陆|查询|管理|授权|教程|清理|上传|一键运行)$]
# [disable:false]
# [platform: qq,wx]
# [cron: 15 22 * * *]
# [public: true]
# [title: 【插件】-森选质享]
# [author: huawei]
# [service: 1603960061] 售后联系方式
# [open_source: false]
# [class: 工具类]
# [version: 1.7.1]
# [price: 4.88]
# [admin: false]
# [icon: http://113.45.39.135:8080/admin/images/gallery/1750458890545208841.jpg]

# [description: vx小程序【银辉助手】插件自带任务<br>适配呆呆积分支付<br><br>指令：<br>森选登录：绑定账号(支持批量,每行备注#token)<br>森选管理：账号管理/授权/批量删除<br>森选查询：查询积分与状态<br>森选上传：批量同步到青龙(管理员)<br>森选清理：清理过期账号(管理员)<br>森选教程：使用指南<br>]

# 插件参数配置
# [param: {"required":false,"key":"G_szyx_config.zsm","name":"收款码","placeholder":"http://example.com/pay.jpg"}]
# [param: {"required":false,"key":"G_szyx_config.price","name":"月费价格","placeholder":"0.88"}]
# [param: {"required":false,"key":"G_szyx_config.points_per_month","name":"积分/月","placeholder":"100","value":"100","desc":"一个账号每月所需积分数量"}]
# [param: {"required":false,"key":"G_szyx_config.ql_config","name":"青龙容器","placeholder":"http://ip:5700丨ClientID丨ClientSecret","desc":"用丨分割三个参数"}]
# [param: {"required":false,"key":"G_szyx_config.ql_envname","name":"青龙变量名","placeholder":"G_SZYX","value":"G_SZYX","desc":"提交到青龙的变量名"}]

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
from typing import List, Dict, Any, Tuple, Optional

# 获取发送者信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()


class SenxuanClient:
    """森选质享客户端"""

    def __init__(self, token_with_remark):
        # 分割Token和备注
        if "#" in token_with_remark:
            self.remark, self.raw_token = token_with_remark.split("#", 1)
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

        # 使用新的域名 (yb.yuanhukj.com)
        self.base_url = "https://yb.yuanhukj.com/api/mobile"
        self.session = requests.Session()

        # 设置请求头
        self.headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "content-type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Referer": "https://servicewechat.com/wx243e6a357085251f/4/page-frame.html",
            "authorization": self.token,
            "app-sign": "wx243e6a357085251f",
            "Host": "yb.yuanhukj.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541411) XWEB/16965",
            "xweb_xhr": "1",
        }
        self.session.headers.update(self.headers)

    def get_user_info(self):
        """获取用户信息"""
        try:
            url = f"{self.base_url}/account/user/overview?source_type=2314&source_from=2321&source_lang=zh_CN&currency_id=86&site_id="
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                return data.get("data")
        except Exception as e:
            print(f"获取用户信息失败: {e}")
        return None

    def get_user_info_new(self):
        """获取用户详细信息"""
        url = f"{self.base_url}/account/user/overview_my"
        params = {
            "source_type": 2314,
            "source_from": 2321,
            "source_lang": "zh_CN",
            "currency_id": 86,
            "site_id": "",
            "isOrder": 1,
        }
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                user_data = data.get("data")
                return user_data
            return None
        except Exception as e:
            return None

    def get_video_detail(self, vid: int) -> Optional[Dict[str, Any]]:
        """获取单个视频详情"""
        url = f"{self.base_url}/video/getOneVideo?source_type=2314&source_from=2321&source_lang=zh_CN&currency_id=86&site_id=&vid={vid}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("code") == 0 and data.get("data"):
                return data.get("data")
            return None
        except Exception as e:
            return None

    def add_user_view_num(self, vid: int) -> Dict[str, Any]:
        """记录用户观看视频"""
        url = f"{self.base_url}/video/addUserViewNum?source_type=2314&source_from=2321&source_lang=zh_CN&currency_id=86&site_id=&vid={vid}&playMode=0"
        body = {"baseVersion": "3.12.1", "playMode": 0}
        try:
            print(f"  正在记录观看，视频ID: {vid}")
            headers = {"Content-Type": "application/json"}
            response = self.session.post(url, json=body, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            print(f"  记录观看结果: {result.get('msg')}")
            return result
        except Exception as e:
            print(f"  记录观看请求异常: {e}")
            return {"status": 500, "msg": str(e)}

    def video_job(self, vid: int, wait_time: int) -> Dict[str, Any]:
        """提交视频观看完成"""
        url = f"{self.base_url}/video/addVideoJob"

        start_time = int(time.time() * 1000)
        end_time = start_time + (wait_time * 1000) + 1000

        body = {
            "source_type": 2314,
            "source_from": 2321,
            "source_lang": "zh_CN",
            "currency_id": "86",
            "site_id": "",
            "vid": vid,
            "startTime": start_time,
            "endTime": end_time,
            "baseVersion": "3.12.1",
            "playMode": 0,
        }

        try:
            print(f"  开始播放 {wait_time}秒...")
            for i in range(wait_time, 0, -10):
                print(f"  剩余 {i} 秒...")
                time.sleep(min(10, i))
            print(f"  播放完成，提交中...")

            headers = {"Content-Type": "application/json"}
            response = self.session.post(url, json=body, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            print(f"  提交结果: {result.get('msg')}")
            return result
        except Exception as e:
            print(f"  提交观看失败: {e}")
            return {"status": 500, "msg": str(e)}

    def add_video_job(self, vid: int, wait_time: int) -> Dict[str, Any]:
        """提交视频任务完成（同video_job）"""
        return self.video_job(vid, wait_time)

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
        """获取所有视频ID"""
        try:
            print("正在请求视频列表...")
            url = f"{self.base_url}/video/list?source_type=2314&source_from=2321&source_lang=zh_CN&currency_id=86&site_id=&page=1&limit=10&status=1&source=0&isXn=1"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # 新接口返回 code == 0
            if data.get("code") == 0 and data.get("data"):
                items = data.get("data", {}).get("items", [])
                if isinstance(items, list) and len(items) > 0:
                    video_ids = [video.get("id") for video in items if video.get("id")]
                    print(f"成功获取 {len(video_ids)} 个视频")
                    return video_ids

            print(f"获取视频列表失败: {data.get('msg')}")
            return []

        except Exception as e:
            print(f"请求视频列表异常: {e}")
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
            "playMode": 0,
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
        """提现 - 新接口（使用手机端请求头）"""
        url = f"{self.base_url}/pay/pay-payment-channel/addUserWithdraw"

        params = {
            "source_type": 2314,
            "source_from": 2321,
            "source_lang": "zh_CN",
            "currency_id": 86,
            "site_id": "",
        }

        # 使用手机端请求头
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "app-sign": "wx4dff990a8fa3a1e7",
            "authorization": self.token,
            "charset": "utf-8",
            "referer": "https://servicewechat.com/wx4dff990a8fa3a1e7/3/page-frame.html",
            "user-agent": "Mozilla/5.0 (Linux; Android 14; Redmi K20 Pro Build/UKQ1.240624.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/138.0.7204.180 Mobile Safari/537.36 XWEB/1380283 MMWEBSDK/20250904 MMWEBID/8960 MicroMessenger/8.0.65.2960(0x28004137) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
            "accept-encoding": "gzip, deflate, br",
        }

        try:
            print("正在提交提现申请...")
            response = self.session.post(url, data=params, headers=headers, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("code") == 0:
                data = result.get("data", {})
                process_result = data.get("processResult")
                if process_result == "success":
                    print(f"✅ 提现成功")
                    return {"success": True, "msg": "提现成功", "data": data}
                else:
                    reason = data.get("reason", "未知原因")
                    print(f"❌ 提现失败: {reason}")
                    return {"success": False, "msg": f"提现失败: {reason}"}
            else:
                msg = result.get("msg", "未知错误")
                print(f"❌ 提现失败: {msg}")
                return {"success": False, "msg": msg}
        except Exception as e:
            print(f"❌ 提现请求异常: {e}")
            return {"success": False, "msg": str(e)}

    def get_consume_record(self, page: int = 1, rows: int = 20) -> Dict[str, Any]:
        """获取奖励记录（新接口 - /api/mobile/pay/index/consumeRecord）"""
        try:
            url = f"{self.base_url}/pay/index/consumeRecord"
            params = {
                "source_type": 2314,
                "source_from": 2321,
                "source_lang": "zh_CN",
                "currency_id": 86,
                "site_id": "",
                "change_type": 0,
                "page": page,
                "rows": rows,
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == 0 and data.get("data"):
                consume_data = data.get("data", {})
                items = consume_data.get("items", [])
                income = consume_data.get("income", 0)

                return {
                    "success": True,
                    "records": items,
                    "count": len(items),
                    "income": income,
                    "total": consume_data.get("total", 0),
                }
        except Exception as e:
            print(f"获取奖励记录失败: {e}")

        return {"success": False, "msg": "获取奖励记录失败"}

    def get_commission_info(self):
        """获取佣金信息"""
        try:
            url = f"{self.base_url}/account/commission?page=1&limit=5"
            response = self.session.get(url, timeout=10)
            if response.status_code == 404:
                return {"success": False, "msg": "佣金接口不可用"}
            response.raise_for_status()
            data = response.json()

            if data.get("code") == 0 and data.get("data"):
                commission_data = data.get("data", {})
                commission_list = commission_data.get(
                    "records", []
                ) or commission_data.get("list", [])
                return {
                    "success": True,
                    "records": commission_list,
                    "count": len(commission_list),
                }
        except Exception as e:
            print(f"获取佣金信息失败: {e}")

        return {"success": False, "msg": "获取佣金信息失败"}

    def run_daily_task(self) -> Dict[str, Any]:
        """运行每日任务"""
        results = {
            "video_count": 0,
            "success_videos": 0,
            "answer_videos": 0,
            "withdraw": None,
            "balance": 0,
            "commission": None,
        }

        try:
            # 1. 获取用户详细信息
            user_info = self.get_user_info_new()
            if user_info:
                results["balance"] = float(
                    user_info.get("user_money", 0) or user_info.get("now_money", 0)
                )
                results["video_count"] = user_info.get("video_answer_not", 0)
                print(
                    f"账户余额: ¥{results['balance']}, 还需答题: {results['video_count']}个\n"
                )

            # 2. 一次性获取所有视频
            video_ids = self.get_video_ids()

            if not video_ids:
                print("没有获取到视频")
            else:
                print(f"\n获取到 {len(video_ids)} 个视频，开始处理...\n")

                # 3. 逐个处理视频
                for idx, vid in enumerate(video_ids, 1):
                    print(f"[{idx}/{len(video_ids)}] 处理视频 {vid}")

                    # 获取视频详情（获取wait_time和奖励金额）
                    video_detail = self.get_video_detail(vid)
                    wait_time = 10  # 默认等待时间
                    reward_amount = 0  # 奖励金额

                    if video_detail:
                        wait_time = int(video_detail.get("wait_time", 10))
                        reward_amount = float(video_detail.get("je", 0))
                        print(f"视频等待时间: {wait_time}秒")

                    # 1. 记录观看开始
                    view_result = self.add_user_view_num(vid)
                    if view_result.get("status") == 500:
                        print(f"[x] 记录观看失败\n")
                        continue

                    # 2. 等待并提交观看完成
                    job_result = self.add_video_job(vid, wait_time)
                    if job_result.get("code") == 0:
                        results["success_videos"] += 1
                        print(f"[✓] 任务完成")
                    else:
                        print(f"[x] 任务提交失败\n")
                        continue

                    # 3. 获取奖励（答题自动提交）
                    reward_result = self.reward_user_small_change()
                    if reward_result.get("code") == 0:
                        results["answer_videos"] += 1
                        print(f"[✓] 奖励获取成功")
                    else:
                        print(f"[i] 本视频无奖励或不需要答题")

                    print()
                    time.sleep(1)

            # 4. 提现（已关闭）
            # withdraw_result = self.withdraw()
            # results["withdraw"] = withdraw_result

            # 5. 获取佣金信息
            commission_info = self.get_commission_info()
            if commission_info.get("success"):
                results["commission"] = commission_info

            # 6. 更新账户信息
            user_info = self.get_user_info_new()
            if user_info:
                results["balance"] = float(
                    user_info.get("user_money", 0) or user_info.get("now_money", 0)
                )

        except Exception as e:
            print(f"运行任务出错: {e}")
            import traceback

            traceback.print_exc()

        return results

    def get_withdraw_records(self):
        """获取提现记录"""
        try:
            print("正在获取提现记录...")
            url = f"{self.base_url}/account/withdraw/records?page=1&limit=15"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == 0 and data.get("data"):
                withdraw_data = data.get("data", {})
                withdraw_list = withdraw_data.get("records", []) or withdraw_data.get(
                    "list", []
                )
                return {
                    "success": True,
                    "records": withdraw_list,
                    "count": len(withdraw_list),
                }
        except Exception as e:
            print(f"获取提现记录失败: {e}")

        return {"success": False, "msg": "获取提现记录失败"}


# 通用函数
def get_config():
    """获取插件配置"""
    try:
        price_str = middleware.bucketGet(bucket="G_szyx_config", key="price") or "0.88"
        price = float(price_str) if price_str.replace(".", "", 1).isdigit() else 0.88
        zsm = middleware.bucketGet(bucket="G_szyx_config", key="zsm") or ""
        points_per_month_str = (
            middleware.bucketGet(bucket="G_szyx_config", key="points_per_month")
            or "100"
        )
        points_per_month = (
            int(points_per_month_str) if points_per_month_str.isdigit() else 100
        )
        ql_config = middleware.bucketGet(bucket="G_szyx_config", key="ql_config") or ""
        ql_envname = (
            middleware.bucketGet(bucket="G_szyx_config", key="ql_envname") or "S_SZYX"
        )
        return {
            "price": price,
            "zsm": zsm,
            "points_per_month": points_per_month,
            "ql_config": ql_config,
            "ql_envname": ql_envname,
        }
    except Exception as e:
        sender.reply(f"❌ 配置获取失败: {str(e)}")
        return {
            "price": 0.88,
            "zsm": "",
            "points_per_month": 100,
            "ql_config": "",
            "ql_envname": "S_SZYX",
        }


def get_ql_token(url: str, cid: str, sec: str) -> str:
    """获取青龙Token"""
    try:
        resp = requests.get(
            f"{url}/open/auth/token",
            params={"client_id": cid, "client_secret": sec},
            timeout=10,
        )
        data = resp.json()
        if data.get("code") == 200:
            return data["data"]["token"]
    except:
        pass
    return ""


def push_to_ql(account_id: str, expire: str, ql_config: str, envname: str) -> bool:
    """推送单个账号到青龙"""
    try:
        parts = ql_config.split("丨")
        if len(parts) != 3:
            return False
        url, cid, sec = parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return False
    token = get_ql_token(url, cid, sec)
    if not token:
        return False
    token_with_remark = middleware.bucketGet("G_szyx_token", account_id)
    if not token_with_remark:
        return False
    if "#" in token_with_remark:
        remark, raw_token = token_with_remark.split("#", 1)
        remark, raw_token = remark.strip(), raw_token.strip()
    else:
        raw_token, remark = token_with_remark.strip(), "默认账号"
    value = f"{remark}#{raw_token}"
    remarks = f"森选:{remark}|账号:{account_id}|到期:{expire}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        resp = requests.get(
            f"{url}/open/envs",
            headers=headers,
            params={"searchValue": envname},
            timeout=10,
        )
        envs = resp.json().get("data", [])
        existing = next(
            (
                e
                for e in envs
                if e.get("name") == envname and account_id in e.get("remarks", "")
            ),
            None,
        )
        if existing:
            env_id = existing.get("_id") or existing.get("id")
            requests.put(
                f"{url}/open/envs",
                headers=headers,
                json={
                    "id": env_id,
                    "name": envname,
                    "value": value,
                    "remarks": remarks,
                },
                timeout=10,
            )
        else:
            requests.post(
                f"{url}/open/envs",
                headers=headers,
                json=[{"name": envname, "value": value, "remarks": remarks}],
                timeout=10,
            )
        return True
    except:
        return False


def delete_from_ql(account_id: str, ql_config: str, envname: str) -> bool:
    """从青龙删除账号"""
    try:
        parts = ql_config.split("丨")
        if len(parts) != 3:
            return False
        url, cid, sec = parts[0].strip(), parts[1].strip(), parts[2].strip()
    except:
        return False
    token = get_ql_token(url, cid, sec)
    if not token:
        return False
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        resp = requests.get(
            f"{url}/open/envs",
            headers=headers,
            params={"searchValue": envname},
            timeout=10,
        )
        envs = resp.json().get("data", [])
        existing = next(
            (
                e
                for e in envs
                if e.get("name") == envname and account_id in e.get("remarks", "")
            ),
            None,
        )
        if existing:
            env_id = existing.get("_id") or existing.get("id")
            requests.delete(
                f"{url}/open/envs", headers=headers, json=[env_id], timeout=10
            )
        return True
    except:
        return False


def get_user_accounts(user_id=None):
    """获取用户账号列表"""
    if user_id is None:
        user_id = userid

    uservalue = middleware.bucketGet("G_szyx_user", user_id) or "[]"
    user_accounts = []

    if uservalue:
        try:
            accounts_list = json.loads(uservalue)
            if isinstance(accounts_list, list):
                user_accounts = accounts_list
            else:
                user_accounts = [str(accounts_list)]
        except json.JSONDecodeError:
            # 不使用eval，直接返回空列表（安全处理）
            user_accounts = []

    return [str(acc) for acc in user_accounts]


def get_user_points(user_id=None):
    """获取用户积分 - 适配呆呆积分数据结构"""
    if not user_id:
        user_id = sender.getUserID()

    # 优先尝试直接获取用户积分
    points = middleware.bucketGet("dd_sign_coin", user_id) or "0"
    user_points = middleware.bucketGet("dd_sign_points", user_id) or "0"

    result_points = {
        "dd_sign_coin": int(points),
        "dd_sign_points": int(user_points),
        "total": int(points) + int(user_points),
    }

    # 如果没找到，尝试带'sign_'前缀的key
    if points == "0":
        sign_key = f"sign_{user_id}"
        sign_points = middleware.bucketGet("dd_sign_coin", sign_key)
        if sign_points:
            result_points["dd_sign_coin"] = int(sign_points)
            result_points["total"] = int(sign_points) + int(user_points)

    return result_points


def set_user_points(user_id, points):
    """设置用户积分 - 适配呆呆积分数据结构"""
    # 尝试更新主积分值
    middleware.bucketSet("dd_sign_coin", user_id, str(points["dd_sign_coin"]))
    middleware.bucketSet("dd_sign_points", user_id, str(points["dd_sign_points"]))

    # 尝试更新带'sign_'前缀的积分值
    sign_key = f"sign_{user_id}"
    middleware.bucketSet("dd_sign_coin", sign_key, str(points["dd_sign_coin"]))
    return True


def verify_commission_api_rs256(token: str) -> Dict[str, Any]:
    """验证RS256 Token（新小程序）"""
    try:
        import base64

        # 解析Token
        parts = token.split(".")
        if len(parts) != 3:
            return {"success": False, "msg": "Token格式错误"}

        # 解码Payload
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding

        decoded = base64.urlsafe_b64decode(payload)
        data = json.loads(decoded)

        # 检查过期时间
        exp = data.get("exp")
        if exp:
            from datetime import datetime

            exp_time = datetime.fromtimestamp(exp)
            if datetime.now() > exp_time:
                return {"success": False, "msg": "Token已过期"}

        # 提取用户ID
        user_id = data.get("id") or data.get("user_id")

        return {"success": True, "user_id": user_id, "data": data}
    except Exception as e:
        return {"success": False, "msg": str(e)}


def verify_commission_api(token: str) -> Dict[str, Any]:
    """使用佣金接口验证token有效性"""
    # 优先尝试RS256验证（新小程序）
    rs256_result = verify_commission_api_rs256(token)
    if rs256_result["success"]:
        return rs256_result

    # 使用新接口 (yb.yuanhukj.com)
    try:
        url = "https://yb.yuanhukj.com/api/mobile/account/commission?page=1&limit=5"
        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "content-type": "application/json",
            "Connection": "keep-alive",
            "Referer": "https://servicewechat.com/wx243e6a357085251f/4/page-frame.html",
            "authorization": token,
            "app-sign": "wx243e6a357085251f",
            "Host": "yb.yuanhukj.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541411) XWEB/16965",
            "Cb-lang": "zh-CN",
            "xweb_xhr": "1",
            "Accept": "*/*",
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("code") == 0 and data.get("data"):
            user_id = None
            commission_data = data.get("data", {})
            user_transactions = commission_data.get(
                "records", []
            ) or commission_data.get("list", [])
            if user_transactions and len(user_transactions) > 0:
                user_id = user_transactions[0].get("uid") or user_transactions[0].get(
                    "user_id"
                )

            return {"success": True, "user_id": user_id, "data": data}
        else:
            return {"success": False, "msg": data.get("msg", "未知错误"), "data": data}
    except Exception as e:
        return {"success": False, "msg": str(e), "error": e}


def validate_token(token_with_remark):
    """验证Token有效性并返回账号信息"""
    try:
        # 处理带备注的token
        if "#" in token_with_remark:
            remark, raw_token = token_with_remark.split("#", 1)
            remark = remark.strip()
            token = raw_token.strip()
        else:
            token = token_with_remark.strip()
            remark = "默认账号"

        # 简单验证Token格式
        if len(token) < 10:  # 合理的最小长度
            return False, {"error": "Token格式错误，长度不足"}

        # 确保token有Bearer前缀
        if token.lower().startswith("bearer "):
            full_token = token
        else:
            full_token = f"Bearer {token}"

        # 直接使用佣金API验证(最可靠的方法)
        commission_result = verify_commission_api(full_token)
        if commission_result["success"]:
            account_id = commission_result.get("user_id")
            # 如果通过佣金API能获取到用户ID，就使用它
            if account_id:
                return True, {"account_id": str(account_id), "nickname": remark}
            # 如果佣金API成功但没有获取到用户ID，也返回成功，使用时间戳生成ID
            timestamp = int(time.time() * 1000)
            account_id = f"szyx_{hashlib.md5(str(timestamp).encode()).hexdigest()[:10]}"
            return True, {"account_id": str(account_id), "nickname": remark}

        # 佣金API验证失败
        return False, {
            "error": f"佣金API验证失败: {commission_result.get('msg', '未知错误')}"
        }

    except Exception as e:
        return False, {"error": f"验证失败: {str(e)}"}


def bindaccount():
    """森选登录绑定(支持单个或批量)"""
    sender.reply(
        "=====森选登录=====\n单个：粘贴Token\n批量：换行分割，每行 备注#token\n\n💡 回复q退出"
    )

    ck_input = sender.input(300000, 1, False).strip()
    if ck_input.lower() == "q":
        return

    lines = [l.strip() for l in ck_input.split("\n") if l.strip()]

    # 批量模式：多行输入
    if len(lines) > 1:
        sender.reply(f"🔄 检测到 {len(lines)} 条数据，开始批量验证...")
        success_cnt, fail_cnt = 0, 0
        accounts = get_user_accounts()

        for i, line in enumerate(lines, 1):
            if "#" in line:
                remark, token = line.split("#", 1)
                remark, token = remark.strip(), token.strip()
            else:
                token, remark = line.strip(), f"账号{i}"

            if token.lower().startswith("bearer "):
                token = token[7:].strip()
            token = token.strip("\"'").strip()

            if len(token) < 20:
                fail_cnt += 1
                continue

            is_valid, result = validate_token(f"{remark}#{token}")
            if not is_valid:
                fail_cnt += 1
                continue

            account_id = result.get("account_id", f"szyx_{i}")
            middleware.bucketSet("G_szyx_token", str(account_id), f"{remark}#{token}")
            if account_id not in accounts:
                accounts.append(account_id)
            success_cnt += 1

        middleware.bucketSet("G_szyx_user", userid, json.dumps(accounts))
        sender.reply(
            f"✅ 批量绑定完成\n成功: {success_cnt}个\n失败: {fail_cnt}个\n\n下一步: 发『森选管理』授权\n⚠️ 每天请用手机端手动提现，电脑端无法到账"
        )
        return

    # 单个模式
    access_token = ck_input.strip()
    if access_token.lower().startswith("bearer "):
        access_token = access_token[7:].strip()
    access_token = access_token.strip("\"'").strip()

    if len(access_token) < 20:
        sender.reply("❌ Token过短")
        return

    is_valid, result = validate_token(f"验证中#{access_token}")
    if not is_valid:
        sender.reply(f"❌ Token验证失败: {result.get('error', '无效Token')}")
        return

    sender.reply("✅ Token有效\n请输入备注(如：张三)\n回复q取消")
    remark_input = sender.input(120000, 1, False).strip()
    if not remark_input or remark_input.lower() == "q":
        sender.reply("❌ 已取消")
        return

    remark = remark_input.strip()
    account_id = result.get("account_id", "unknown")
    middleware.bucketSet("G_szyx_token", str(account_id), f"{remark}#{access_token}")
    accounts = get_user_accounts()
    if account_id not in accounts:
        accounts.append(account_id)
    middleware.bucketSet("G_szyx_user", userid, json.dumps(accounts))

    sender.reply(
        f"✅ 绑定成功\n备注: {remark}\nID: {account_id}\n下一步: 发『森选管理』授权\n⚠️ 每天请用手机端手动提现，电脑端无法到账"
    )


def authorize_account(account_id):
    """授权账号并处理支付"""
    config = get_config()

    # 获取账号信息
    token_with_remark = middleware.bucketGet("G_szyx_token", account_id)
    if not token_with_remark:
        sender.reply("❌ 账号令牌无效，无法获取账号信息")
        return

    # 从token中提取备注
    if "#" in token_with_remark:
        remark, token = token_with_remark.split("#", 1)
    else:
        token = token_with_remark
        remark = "默认账号"

    # 创建客户端实例
    client = SenxuanClient(token_with_remark)

    # 尝试获取用户信息
    user_info = client.get_user_info()
    nickname = user_info.get("nickname", "森选用户") if user_info else "森选用户"

    # 获取当前用户积分
    current_points = get_user_points()

    # 显示授权信息
    display_name = f"{nickname} ({remark})" if remark else nickname
    sender.reply(
        f"您正在授权账号: {account_id}\n👤 账号: {display_name}\n📊 当前积分: {current_points['total']}\n\n请输入授权月数 (1-12):"
    )

    months = sender.input(120000, 1, False)

    if not months.isdigit() or int(months) < 1 or int(months) > 12:
        sender.reply("❌ 月数必须为1-12之间的整数")
        return

    months = int(months)
    total_price = config["price"] * months
    required_points = config["points_per_month"] * months

    pay_menu = f"""
=====森选质享授权支付=====
🎯 授权时长: {months}个月
💰 金额: ¥{total_price:.2f}
📊 积分支付: {required_points}积分（当前积分: {current_points["total"]}）
------------------
[1] 微信支付
[2] 积分支付
回复数字选择支付方式，回复q取消
=================="""
    sender.reply(pay_menu)
    pay_choice = sender.input(120000, 1, False)

    if pay_choice == "1" and config["zsm"]:
        # 微信支付流程
        payment_success = wechat_payment_flow(
            account_id, months, total_price, config, display_name
        )
    elif pay_choice == "2":
        # 积分支付流程
        payment_success = point_payment_flow(account_id, months, required_points)
    elif pay_choice.lower() == "q":
        sender.reply("✅ 已取消授权")
        return
    else:
        sender.reply("❌ 无效支付方式")
        return

    if payment_success:
        # 获取授权结果（包含到期日期和续费类型）
        auth_result = complete_authorization(account_id, months, display_name)

        # 显示包含具体到期日期的成功信息
        sender.reply(
            f"✅ {auth_result['renew_type']}成功！森选质享已加入定时任务\n"
            f"📅 到期日期: {auth_result['expire_date']}（{months}个月）"
        )


def wechat_payment_flow(account_id, months, amount, config, nickname):
    """微信支付处理"""
    sender.reply(f"""
=====微信扫码支付=====
🎯 授权时长: {months}个月
💰 金额: ¥{amount:.2f}
------------------
请扫描下方二维码支付
回复q取消支付
==================""")
    sender.replyImage(config["zsm"])

    payment_result = sender.waitPay(timeout=600000, exitcode="q")

    if payment_result == "q":
        sender.reply("✅ 支付已取消")
        return False

    Money, Time, From = parse_payment_result(payment_result)

    if Money is None:
        sender.reply("❌ 无法解析支付结果")
        return False

    if float(Money) >= float(amount):
        sender.reply(f"""
✅ 支付成功 ✅
💰 金额: ¥{Money}元
⏰ 时间: {Time}
{f"👤 付款人: {From}" if From else ""}
==================""")
        return True
    else:
        sender.reply(f"""
❌ 支付金额不足 ❌
应付: ¥{amount:.2f}元 
实付: ¥{Money}元
==================""")
        return False


def point_payment_flow(account_id, months, required_points):
    """积分支付处理"""
    # 获取积分余额
    user_points = get_user_points()
    sign_coin = user_points["dd_sign_coin"]
    sign_points = user_points["dd_sign_points"]

    # 检查积分是否足够
    if user_points["total"] < required_points:
        sender.reply(f"""
❌ 积分不足！
需要: {required_points}积分
当前: {user_points["total"]}积分
请「联系管理员」充值积分
        """)
        return False

    # 确认支付
    sender.reply(f"""
⚠ 确认使用积分支付吗？
📊 扣除: {required_points}积分
📈 剩余: {user_points["total"] - required_points}积分
------------------
回复 [Y] 确认支付
回复 [N] 取消
    """)

    confirm = sender.input(60000, 1, False).lower()
    if confirm != "y":
        sender.reply("✅ 积分支付已取消")
        return False

    # 优先扣除签到积分
    if sign_coin >= required_points:
        sign_coin -= required_points
    else:
        # 签到积分不足，先扣完签到积分，剩余扣用户积分
        remaining = required_points - sign_coin
        sign_coin = 0
        sign_points -= remaining

    result_points = {
        "dd_sign_coin": sign_coin,
        "dd_sign_points": sign_points,
    }

    # 扣除积分
    new_points = sign_points + sign_coin
    set_user_points(userid, result_points)

    # 记录交易流水
    transaction_data = {
        "userid": userid,
        "account_id": account_id,
        "months": months,
        "points": required_points,
        "balance": new_points,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "森选质享授权",
    }
    middleware.bucketSet(
        "dd_sign_transactions", f"tx_{int(time.time())}", json.dumps(transaction_data)
    )

    sender.reply(f"✅ 积分支付成功！扣除 {required_points}积分，剩余积分: {new_points}")
    return True


def parse_payment_result(raw_data):
    """解析微信支付结果"""
    Money, Time, From = None, "", ""

    try:
        if isinstance(raw_data, dict):
            # 处理字典格式
            if raw_data.get("type") in ["微信赞赏", "微信收款"]:
                Money = float(raw_data.get("money", 0))
                Time = raw_data.get("time", "")
                From = raw_data.get("from_name", "")
            else:
                Money = float(raw_data.get("Money", 0))
                Time = raw_data.get("Time", "")

        else:
            # 处理JSON字符串或文本格式
            try:
                data = json.loads(raw_data)
                if data.get("type") in ["微信赞赏", "微信收款"]:
                    Money = float(data.get("money", 0))
                    Time = data.get("time", "")
                    From = data.get("from_name", "")
            except:
                # 处理包含"二维码赞赏到账"的文本格式
                if "二维码赞赏到账" in raw_data:
                    try:
                        amount_str = raw_data.split("收款金额￥")[1].split("\n")[0]
                        time_str = raw_data.split("到账时间")[1].split("\n")[0].strip()
                        Money = float(amount_str)
                        Time = time_str
                    except:
                        pass

    except Exception as e:
        sender.reply(f"❌ 解析支付结果失败: {str(e)}")

    return Money, Time, From


def complete_authorization(account_id, months, display_name):
    """记录授权时间并存储到数据桶"""
    # 1. 尝试获取现有授权信息
    existing_auth = middleware.bucketGet("G_szyx_auth", account_id)

    # 2. 初始化时间变量
    new_expire_time = None
    renew_msg = "新授权"  # 默认为新授权

    # 3. 检查是否已有授权信息
    if existing_auth:
        try:
            auth_info = json.loads(existing_auth)
            # 尝试解析时间格式
            try:
                expire_time = datetime.strptime(auth_info["expire_time"], "%Y-%m-%d")
            except:
                # 如果格式错误，尝试解析为时间戳
                try:
                    expire_time = datetime.fromtimestamp(
                        float(auth_info["expire_time"])
                    )
                except:
                    # 所有解析失败则使用当前时间
                    expire_time = datetime.now()

            # 检查是否已经过期
            if expire_time.date() >= datetime.now().date():
                # 未过期，在原有基础上续费
                new_expire_time = expire_time + timedelta(days=months * 30)
                renew_msg = "续费"
            else:
                # 已过期，从当前时间开始计算
                new_expire_time = datetime.now() + timedelta(days=months * 30)
                renew_msg = "新授权"
        except Exception as e:
            print(f"[WARN] 解析现有授权信息失败: {str(e)}")

    # 4. 如果没有设置新时间，使用当前时间
    if not new_expire_time:
        new_expire_time = datetime.now() + timedelta(days=months * 30)
        renew_msg = "新授权"

    # 5. 格式化到期日期（年-月-日）
    expire_date = new_expire_time.date().strftime("%Y-%m-%d")

    # 6. 存储授权信息
    auth_data = {
        "userid": userid,
        "display_name": display_name,
        "account_id": account_id,
        "expire_time": expire_date,
        "authorized_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "authorized_months": months,
        "is_renewal": ("续费" if renew_msg == "续费" else "新授权"),
    }

    middleware.bucketSet(
        bucket="G_szyx_auth", key=account_id, value=json.dumps(auth_data)
    )

    # 自动同步到青龙
    cfg = get_config()
    if cfg.get("ql_config"):
        try:
            push_to_ql(account_id, expire_date, cfg["ql_config"], cfg["ql_envname"])
        except:
            pass

    # 返回带有续费类型和日期的信息
    return {"expire_date": expire_date, "renew_type": renew_msg}


def delete_account(account_id):
    """删除账号"""
    accounts = get_user_accounts()

    sender.reply(f"""
=====删除账号确认=====
确认删除账号 {account_id} 吗？
请回复 [Y] 确认
回复 [N] 取消
==================""")
    user_confirm = sender.input(120000, 1, False).strip().lower()

    if user_confirm != "y":
        sender.reply("✅ 已取消删除操作")
        return

    try:
        middleware.bucketDel(bucket="G_szyx_token", key=account_id)
        middleware.bucketDel(bucket="G_szyx_auth", key=account_id)

        if account_id in accounts:
            accounts.remove(account_id)
            if accounts:
                middleware.bucketSet(
                    bucket="G_szyx_user", key=userid, value=json.dumps(accounts)
                )
            else:
                middleware.bucketDel(bucket="G_szyx_user", key=userid)

        sender.reply("✅ 账号删除成功")

    except Exception as e:
        sender.reply(f"❌ 删除失败: {str(e)}")


def batch_delete_accounts(accounts):
    """批量删除账号"""
    if not accounts:
        sender.reply("❌ 没有账号可删除")
        return

    account_list = []
    for i, acc_id in enumerate(accounts, 1):
        token_data = middleware.bucketGet("G_szyx_token", acc_id) or ""
        remark = token_data.split("#")[0].strip() if "#" in token_data else "默认账号"
        account_list.append(f"[{i}] {remark}")

    list_str = "\n".join(account_list)
    sender.reply(
        f"=====批量删除=====\n{list_str}\n\n输入要删除的序号(多个用逗号分隔)\n如: 1,2,3 或 全部\n💡 回复q退出"
    )

    choice = sender.input(60000, 1, False).strip()
    if not choice or choice.lower() == "q":
        sender.reply("✅ 已取消")
        return

    to_delete = []
    if choice == "全部":
        to_delete = accounts[:]
    else:
        try:
            indices = [
                int(x.strip()) - 1 for x in choice.split(",") if x.strip().isdigit()
            ]
            to_delete = [accounts[i] for i in indices if 0 <= i < len(accounts)]
        except:
            sender.reply("❌ 输入格式错误")
            return

    if not to_delete:
        sender.reply("❌ 未选择有效账号")
        return

    sender.reply(f"⚠️ 确认删除 {len(to_delete)} 个账号？\n回复 Y 确认 / N 取消")
    confirm = sender.input(60000, 1, False).strip().lower()
    if confirm != "y":
        sender.reply("✅ 已取消")
        return

    success_cnt, fail_cnt = 0, 0
    remaining = [a for a in accounts if a not in to_delete]

    for acc_id in to_delete:
        try:
            middleware.bucketDel("G_szyx_token", acc_id)
            middleware.bucketDel("G_szyx_auth", acc_id)
            success_cnt += 1
        except:
            fail_cnt += 1

    if remaining:
        middleware.bucketSet("G_szyx_user", userid, json.dumps(remaining))
    else:
        middleware.bucketDel("G_szyx_user", userid)

    sender.reply(f"✅ 批量删除完成\n成功: {success_cnt}个\n失败: {fail_cnt}个")


def batch_authorize_accounts(unauthorized_accounts):
    """批量授权未授权账号并一次性支付"""
    if not unauthorized_accounts:
        sender.reply("❌ 没有未授权的账号")
        return

    config = get_config()

    # 显示账号列表
    account_list = []
    for i, account_id in enumerate(unauthorized_accounts, 1):
        # 获取token和备注
        token_with_remark = middleware.bucketGet("G_szyx_token", account_id) or ""
        if "#" in token_with_remark:
            remark, token = token_with_remark.split("#", 1)
            remark = remark.strip()
        else:
            token = token_with_remark
            remark = "默认账号"

        account_list.append(f"{i}. {remark}")

    accounts_str = "\n".join(account_list)

    sender.reply(f"""
=====批量授权未授权账号=====
发现 {len(unauthorized_accounts)} 个未授权账号:
{accounts_str}
------------------
请输入授权月数 (1-12):
===================""")

    months = sender.input(120000, 1, False)
    if not months.isdigit() or int(months) < 1 or int(months) > 12:
        sender.reply("❌ 月数必须为1-12之间的整数")
        return

    months = int(months)
    total_price = config["price"] * months * len(unauthorized_accounts)
    required_points = config["points_per_month"] * months * len(unauthorized_accounts)

    # 获取当前用户积分
    current_points = get_user_points()

    pay_menu = f"""
=====批量授权支付=====
🎯 授权账号数: {len(unauthorized_accounts)}个
🎯 授权时长: {months}个月/账号
💰 总金额: ¥{total_price:.2f}
📊 积分支付: {required_points}积分（当前积分: {current_points["total"]}）
------------------
[1] 微信支付
[2] 积分支付
回复数字选择支付方式，回复q取消
=================="""
    sender.reply(pay_menu)
    pay_choice = sender.input(120000, 1, False)

    if pay_choice == "1" and config["zsm"]:
        # 微信支付流程
        payment_success = batch_wechat_payment(
            unauthorized_accounts, months, total_price, config
        )
    elif pay_choice == "2":
        # 积分支付流程
        payment_success = batch_point_payment(
            unauthorized_accounts, months, required_points
        )
    elif pay_choice.lower() == "q":
        sender.reply("✅ 已取消授权")
        return
    else:
        sender.reply("❌ 无效支付方式")
        return

    if payment_success:
        # 为每个账号设置授权
        success_count = 0
        for account_id in unauthorized_accounts:
            try:
                token_with_remark = (
                    middleware.bucketGet("G_szyx_token", account_id) or ""
                )
                if "#" in token_with_remark:
                    remark, token = token_with_remark.split("#", 1)
                    remark = remark.strip()
                else:
                    token = token_with_remark
                    remark = "默认账号"

                display_name = f"{remark}"

                # 设置授权
                auth_result = complete_authorization(account_id, months, display_name)
                success_count += 1

            except Exception as e:
                sender.reply(f"⚠️ 账号 {account_id} 授权失败: {str(e)}")

        # 显示成功信息
        sender.reply(
            f"✅ 批量授权成功！\n"
            f"🎯 共授权 {success_count}/{len(unauthorized_accounts)} 个账号\n"
            f"📅 授权时长: {months}个月/账号\n"
            f"📆 到期日期: {(datetime.now() + timedelta(days=months * 30)).strftime('%Y-%m-%d')}"
        )


def batch_wechat_payment(accounts, months, amount, config):
    """批量微信支付处理"""
    sender.reply(f"""
=====微信扫码支付=====
🎯 授权账号数: {len(accounts)}个
🎯 授权时长: {months}个月/账号
💰 总金额: ¥{amount:.2f}
------------------
请扫描下方二维码支付
回复q取消支付
==================""")
    sender.replyImage(config["zsm"])

    payment_result = sender.waitPay(timeout=600000, exitcode="q")

    if payment_result == "q":
        sender.reply("✅ 支付已取消")
        return False

    Money, Time, From = parse_payment_result(payment_result)

    if Money is None:
        sender.reply("❌ 无法解析支付结果")
        return False

    if float(Money) >= float(amount):
        sender.reply(f"""
✅ 支付成功 ✅
💰 金额: ¥{Money}元
⏰ 时间: {Time}
{f"👤 付款人: {From}" if From else ""}
==================""")
        return True
    else:
        sender.reply(f"""
❌ 支付金额不足 ❌
应付: ¥{amount:.2f}元 
实付: ¥{Money}元
==================""")
        return False


def batch_point_payment(accounts, months, required_points):
    """批量积分支付处理"""
    # 获取积分余额
    user_points = get_user_points()
    sign_coin = user_points["dd_sign_coin"]
    sign_points = user_points["dd_sign_points"]

    # 检查积分是否足够
    if user_points["total"] < required_points:
        sender.reply(f"""
❌ 积分不足！
需要: {required_points}积分
当前: {user_points["total"]}积分
请「联系管理员」充值积分
        """)
        return False

    # 确认支付
    sender.reply(f"""
⚠ 确认使用积分批量支付吗？
📊 扣除: {required_points}积分
📈 剩余: {user_points["total"] - required_points}积分
------------------
回复 [Y] 确认支付
回复 [N] 取消
    """)

    confirm = sender.input(60000, 1, False).lower()
    if confirm != "y":
        sender.reply("✅ 积分支付已取消")
        return False

    # 优先扣除签到积分
    if sign_coin >= required_points:
        sign_coin -= required_points
    else:
        # 签到积分不足，先扣完签到积分，剩余扣用户积分
        remaining = required_points - sign_coin
        sign_coin = 0
        sign_points -= remaining

    result_points = {
        "dd_sign_coin": sign_coin,
        "dd_sign_points": sign_points,
    }

    # 扣除积分
    new_points = sign_points + sign_coin
    set_user_points(userid, result_points)

    # 记录交易流水
    transaction_data = {
        "userid": userid,
        "accounts": len(accounts),
        "months": months,
        "points": required_points,
        "balance": new_points,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "森选质享批量授权",
    }
    middleware.bucketSet(
        "dd_sign_transactions", f"tx_{int(time.time())}", json.dumps(transaction_data)
    )

    sender.reply(
        f"✅ 积分批量支付成功！扣除 {required_points}积分，剩余积分: {new_points}"
    )
    return True


def run_single_account_task(account_id):
    """运行单个账号的任务"""
    # 获取账号的token
    token_with_remark = middleware.bucketGet("G_szyx_token", account_id)
    if not token_with_remark:
        sender.reply("❌ 账号Token缺失，无法运行任务")
        return

    # 获取备注
    if "#" in token_with_remark:
        remark, token = token_with_remark.split("#", 1)
        remark = remark.strip()
    else:
        token = token_with_remark.strip()
        remark = "默认账号"

    display_name = remark

    sender.reply(f"⏳ 任务执行中\n账号: {display_name}")

    try:
        # 创建客户端并运行任务
        client = SenxuanClient(token_with_remark)
        result = client.run_daily_task()

        # 处理结果
        success_videos = result.get("success_videos", 0)
        total_videos = result.get("video_count", 0)

        # 任务完成后重新获取用户信息以获得正确的余额
        user_info = client.get_user_info_new()
        balance = "未知"
        if user_info:
            balance_value = float(user_info.get("user_money", 0))
            balance = f"¥{balance_value:.2f}"

        # 构建结果消息
        result_msg = f"森选任务结果\n账号: {display_name}\n视频: {success_videos}个\n余额: {balance}"

        sender.reply(result_msg)

    except Exception as e:
        err_msg = str(e)
        if len(err_msg) > 100:
            err_msg = err_msg[:97] + "..."
        sender.reply(f"❌ 任务运行失败: {err_msg}")


def sz_manage():
    """账号管理"""
    accounts = get_user_accounts()

    if not accounts:
        sender.reply("❌ 您尚未绑定任何账号，请先绑定")
        return

    # 统计授权状态
    authorized_count = 0
    unauthorized_accounts = []
    for account_id in accounts:
        auth_data = middleware.bucketGet("G_szyx_auth", key=account_id)
        if auth_data:
            authorized_count += 1
        else:
            unauthorized_accounts.append(account_id)

    # 构建账号列表
    account_list = []
    for i, account_id in enumerate(accounts, 1):
        # 获取token和备注
        token_with_remark = middleware.bucketGet("G_szyx_token", account_id) or ""
        if "#" in token_with_remark:
            remark, token = token_with_remark.split("#", 1)
            remark = remark.strip()
        else:
            token = token_with_remark
            remark = "默认账号"

        # 获取授权状态
        auth_data = middleware.bucketGet("G_szyx_auth", key=account_id)
        status = "✅" if auth_data else "❌"
        status_text = "已授权" if auth_data else "未授权"

        # 显示账号信息和授权状态
        account_list.append(f"[{i}] {remark} {status}{status_text}")

    # 添加多账号选项
    if accounts:
        account_list.append("\n[0] 所有账号授权（支付）")
        account_list.append("[8888] 批量删除账号")
    if unauthorized_accounts:
        account_list.append("[9999] 没有授权的账号授权（合并支付）")

    account_list_str = "\n".join(account_list)

    # 显示用户积分
    user_points = get_user_points()

    sender.reply(f"""
=====森选质享账号管理=====
🔢 绑定账号: {len(accounts)}个
✅ 已授权: {authorized_count}个
❌ 未授权: {len(accounts) - authorized_count}个
📊 当前积分: {user_points["total"]}
-------------------------
{account_list_str}
------------------
回复序号选择操作（q退出）
===================""")

    choice = sender.input(60000, 1, False)
    if choice.lower() == "q":
        sender.reply("已退出管理")
        return

    if choice == "0":
        # 所有账号授权
        sender.reply("您选择了所有账号授权")
        for account_id in accounts:
            authorize_account(account_id)
        return
    elif choice == "8888":
        # 批量删除账号
        batch_delete_accounts(accounts)
        return
    elif choice == "9999":
        # 没有授权的账号批量授权(合并支付)
        sender.reply("您选择了没有授权的账号授权（合并支付）")
        batch_authorize_accounts(unauthorized_accounts)
        return
    elif not choice.isdigit():
        sender.reply("❌ 输入无效")
        return

    selected_idx = int(choice) - 1
    if selected_idx < 0 or selected_idx >= len(accounts):
        sender.reply("❌ 序号无效")
        return

    selected_account = accounts[selected_idx]

    # 获取选中账号的备注
    token_with_remark = middleware.bucketGet("G_szyx_token", selected_account) or ""
    if "#" in token_with_remark:
        remark, token = token_with_remark.split("#", 1)
        remark = remark.strip()
    else:
        remark = "默认账号"

    sender.reply(
        f"你选择了账号: {remark}\n[1] 授权账号\n[2] 任务运行\n[3] 更新账号\n[4] 删除账号"
    )
    op = sender.input(60000, 1, False)

    if op == "1":
        authorize_account(selected_account)
    elif op == "2":
        run_single_account_task(selected_account)
    elif op == "3":
        update_account_token(selected_account, remark)
    elif op == "4":
        delete_account(selected_account)


def update_account_token(account_id, old_remark):
    """更新账号的token"""
    sender.reply(f"请输入新的token (格式：备注#token 或直接输入token):")
    new_token_input = sender.input(120000, 1, False)

    if not new_token_input or new_token_input.lower() == "q":
        sender.reply("❌ 已取消更新")
        return

    # 处理新token
    if "#" in new_token_input:
        # 用户输入了带备注的格式
        remark, access_token = new_token_input.split("#", 1)
        remark = remark.strip()
    else:
        # 用户只输入了token，保留原备注
        access_token = new_token_input.strip()
        remark = old_remark

    # 完整的token_with_remark
    token_with_remark = f"{remark}#{access_token}"

    # 验证新token有效性
    is_valid, result = validate_token(token_with_remark)

    if is_valid:
        # 更新token
        middleware.bucketSet(
            bucket="G_szyx_token", key=account_id, value=token_with_remark
        )
        sender.reply(f"✅ Token更新成功！账号备注: {remark}")

        # 显示验证结果
        if isinstance(result, dict) and result.get("nickname"):
            sender.reply(f"✅ 验证成功: {result.get('nickname', '未知用户')}")
    else:
        sender.reply(f"❌ Token验证失败: {result}\n请重新获取有效的Token")


def sz_auto_run():
    """一键运行所有已授权账号任务"""
    # 1. 获取所有授权账号
    authorized_accounts = []
    all_accounts = []  # 所有账号，包括已过期的
    auth_keys = middleware.bucketAllKeys(bucket="G_szyx_auth") or []

    # 记录过期账号
    expired_accounts = []
    expiring_soon_accounts = []  # 即将过期的账号（3天内）

    # 2. 检查授权是否有效
    today = datetime.now().date()
    for account_id in auth_keys:
        auth_data_str = middleware.bucketGet("G_szyx_auth", key=account_id)
        if not auth_data_str:
            continue

        all_accounts.append(account_id)
        try:
            auth_data = json.loads(auth_data_str)
            expire_date = auth_data.get("expire_time")

            # 检查授权是否过期
            if expire_date:
                try:
                    expire_date_obj = datetime.strptime(expire_date, "%Y-%m-%d").date()
                    days_diff = (expire_date_obj - today).days

                    if days_diff < 0:  # 已过期
                        # 记录过期账号信息
                        expired_accounts.append(
                            {
                                "account_id": account_id,
                                "auth_data": auth_data,
                                "days_expired": abs(days_diff),
                            }
                        )
                    elif days_diff <= 3:  # 3天内即将过期
                        expiring_soon_accounts.append(
                            {
                                "account_id": account_id,
                                "auth_data": auth_data,
                                "days_remaining": days_diff,
                            }
                        )
                        authorized_accounts.append(account_id)  # 仍然可以运行任务
                    else:
                        # 只有不过期的才运行
                        authorized_accounts.append(account_id)
                except:
                    pass  # 忽略无效日期格式的账号
        except:
            pass  # 忽略格式错误的授权信息

    if not authorized_accounts and not expired_accounts:
        sender.reply("❌ 没有已授权的账号")
        return

    # 直接使用超简洁模式
    is_simple_mode = True

    # 3. 运行所有授权账号
    run_results = []
    skip_results = []  # 用于记录跳过的账号
    failed_accounts = []  # 用于记录失败的账号
    success_accounts = []  # 用于记录成功的账号
    ck_invalid_accounts = []  # 用于记录CK失效的账号
    total_success_videos = 0

    if authorized_accounts:
        sender.reply(f"⛳ 开始处理 {len(authorized_accounts)} 个授权账号，请稍候...")

        for account_id in authorized_accounts:
            # 运行已授权的单个账号任务
            token_with_remark = middleware.bucketGet("G_szyx_token", account_id)
            if not token_with_remark:
                skip_results.append(account_id)
                continue

            # 获取备注
            if "#" in token_with_remark:
                remark, raw_token = token_with_remark.split("#", 1)
                remark = remark.strip()
            else:
                raw_token = token_with_remark.strip()
                remark = "默认账号"

            display_name = remark

            # 运行任务
            try:
                client = SenxuanClient(token_with_remark)
                result = client.run_daily_task()

                # 记录任务结果
                success_videos = result.get("success_videos", 0)
                answer_videos = result.get("answer_videos", 0)
                total_success_videos += success_videos

                # 任务完成后重新获取用户信息以获得正确的余额
                user_info = client.get_user_info_new()
                balance = "未知"
                if user_info:
                    balance_value = float(user_info.get("user_money", 0))
                    balance = f"¥{balance_value:.2f}"

                # 构建结果消息
                videos_msg = f"✅{success_videos}个视频"
                balance_msg = f" | 余额{balance}"

                # 记录成功账号
                success_accounts.append(display_name)

                # 如果不是简洁模式，记录详细结果
                if not is_simple_mode:
                    # 记录结果 - 每个账号单独一行，更简洁的格式
                    run_results.append(
                        f"👤 {display_name}:\n   {videos_msg}{balance_msg}"
                    )
            except Exception as e:
                err_msg = str(e)
                if len(err_msg) > 50:
                    err_msg = err_msg[:47] + "..."

                # 记录失败账号
                failed_accounts.append(display_name)

                # 检测是否是CK失效（常见错误）
                is_ck_invalid = any(
                    keyword in err_msg
                    for keyword in [
                        "token",
                        "authorization",
                        "auth",
                        "invalid",
                        "expired",
                        "unauthorized",
                        "401",
                        "403",
                        "验证",
                        "失效",
                        "过期",
                    ]
                )

                # 如果是CK失效，发送通知
                if is_ck_invalid:
                    ck_invalid_accounts.append(display_name)
                    try:
                        # 获取用户ID
                        auth_data_str = middleware.bucketGet(
                            "G_szyx_auth", key=account_id
                        )
                        if auth_data_str:
                            auth_data = json.loads(auth_data_str)
                            user_id = auth_data.get("userid")
                            if user_id:
                                # 构建通知
                                push_msg = f"森选CK失效提醒\n账号: {remark}\n原因: {err_msg}\n请到『森选管理』更新CK"

                                # 推送到多个平台
                                try:
                                    middleware.push(
                                        "wx",
                                        "",
                                        user_id,
                                        "森选质享CK失效通知",
                                        push_msg,
                                    )
                                except:
                                    pass
                                try:
                                    middleware.push(
                                        "qq",
                                        "",
                                        user_id,
                                        "森选质享CK失效通知",
                                        push_msg,
                                    )
                                except:
                                    pass
                    except Exception as push_err:
                        print(f"发送CK失效通知失败: {push_err}")

                # 如果不是简洁模式，记录详细失败信息
                if not is_simple_mode:
                    run_results.append(
                        f"👤 {display_name}:\n   ❌ 运行失败 ({err_msg})"
                    )

        # 构建报告
        if is_simple_mode:
            # 超简洁模式 - 只显示总数统计
            result_msg = "森选一键运行汇总"
            result_msg += (
                f"\n成功: {len(success_accounts)} 失败: {len(failed_accounts)}"
            )
            if ck_invalid_accounts:
                result_msg += f"\nCK失效: {len(ck_invalid_accounts)}"
            if skip_results:
                result_msg += f"\n跳过: {len(skip_results)}"
            result_msg += f"\n完成视频: {total_success_videos}"
            if failed_accounts:
                sample = "、".join(failed_accounts[:5])
                suffix = "..." if len(failed_accounts) > 5 else ""
                result_msg += f"\n失败账号: {sample}{suffix}"
        else:
            # 详细模式 - 显示每个账号的信息
            result_msg = "🚀 森选质享任务运行报告 📊\n====================\n"
            result_msg += "\n".join(run_results)

            # 格式化总结信息
            summary = f"\n\n🎬 本次完成: {total_success_videos}个视频"

            # 添加跳过的账号信息
            if skip_results:
                summary += f"\n⚠ 跳过账号: {len(skip_results)}个 (Token缺失)"

            result_msg += summary + "\n==================="

        sender.reply(result_msg)

    # 4. 处理过期账号和即将过期账号的通知
    if expired_accounts or expiring_soon_accounts:
        # 延迟一下，避免消息过快发送
        time.sleep(1)

        # 发送过期账号通知
        if expired_accounts:
            expired_msg = "⚠️ 以下账号已过期，无法执行任务:\n"
            for acc in expired_accounts:
                account_id = acc["account_id"]
                days_expired = acc["days_expired"]
                auth_data = acc["auth_data"]

                # 获取账号备注
                token_with_remark = (
                    middleware.bucketGet("G_szyx_token", account_id) or ""
                )
                if "#" in token_with_remark:
                    remark, _ = token_with_remark.split("#", 1)
                    remark = remark.strip()
                else:
                    remark = "默认账号"

                expired_msg += f"👤 {remark}: 已过期{days_expired}天\n"

                # 向用户发送过期通知
                try:
                    user_id = auth_data.get("userid")
                    if user_id:
                        # 构建过期通知
                        push_msg = f"森选账号过期\n账号: {remark}\n已过期: {days_expired}天\n如需续费请联系管理员"

                        # 推送到多个平台
                        try:
                            middleware.push(
                                "wx", "", user_id, "森选质享账号过期通知", push_msg
                            )
                        except:
                            pass
                        try:
                            middleware.push(
                                "qq", "", user_id, "森选质享账号过期通知", push_msg
                            )
                        except:
                            pass
                except Exception as e:
                    print(f"发送过期通知失败: {e}")

            sender.reply(expired_msg)

        # 发送即将过期账号通知
        if expiring_soon_accounts:
            expiring_msg = "⏰ 以下账号即将过期，请及时续费:\n"
            for acc in expiring_soon_accounts:
                account_id = acc["account_id"]
                days_remaining = acc["days_remaining"]
                auth_data = acc["auth_data"]

                # 获取账号备注
                token_with_remark = (
                    middleware.bucketGet("G_szyx_token", account_id) or ""
                )
                if "#" in token_with_remark:
                    remark, _ = token_with_remark.split("#", 1)
                    remark = remark.strip()
                else:
                    remark = "默认账号"

                expiring_msg += f"👤 {remark}: 还剩{days_remaining}天过期\n"

                # 向用户发送即将过期通知
                try:
                    user_id = auth_data.get("userid")
                    if user_id:
                        # 构建即将过期通知
                        push_msg = f"森选账号即将到期\n账号: {remark}\n剩余: {days_remaining}天\n请及时续费"

                        # 推送到多个平台
                        try:
                            middleware.push(
                                "wx", "", user_id, "森选质享账号即将过期", push_msg
                            )
                        except:
                            pass
                        try:
                            middleware.push(
                                "qq", "", user_id, "森选质享账号即将过期", push_msg
                            )
                        except:
                            pass
                except Exception as e:
                    print(f"发送即将过期通知失败: {e}")

            sender.reply(expiring_msg)


def admin_authorize_account():
    """管理员授权功能"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有管理员权限！")
        return

    # 第一步：选择操作类型
    sender.reply(
        "=====管理员授权操作=====\n"
        "[1] 一键授权所有用户\n"
        "[2] 单独授权用户\n"
        "回复数字选择操作\n"
        "===================="
    )
    choice = sender.input(60000, 1, False)

    if choice == "1":
        # 一键授权所有用户
        users = middleware.bucketAllKeys(bucket="G_szyx_user")
        if not users:
            sender.reply("❌ 未找到任何绑定用户")
            return

        sender.reply("请输入授权月数 (1-12):")
        months = sender.input(120000, 1, False)
        if not months.isdigit() or int(months) < 1 or int(months) > 12:
            sender.reply("❌ 月数必须为1-12之间的整数")
            return
        months = int(months)

        success_count = 0
        for user in users:
            accounts = get_user_accounts(user)
            for account_id in accounts:
                try:
                    # 获取token和备注
                    token_with_remark = (
                        middleware.bucketGet("G_szyx_token", account_id) or ""
                    )
                    if "#" in token_with_remark:
                        remark, token = token_with_remark.split("#", 1)
                        remark = remark.strip()
                    else:
                        token = token_with_remark
                        remark = "默认账号"

                    # 设置授权时间
                    expire_time = datetime.now() + timedelta(days=months * 30)

                    # 存储授权信息
                    auth_data = {
                        "userid": user,
                        "remark": remark,
                        "account_id": account_id,
                        "expire_time": str(expire_time.date()),
                        "authorized_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "authorized_months": months,
                        "authorized_by": "admin",
                    }

                    middleware.bucketSet(
                        bucket="G_szyx_auth",
                        key=account_id,
                        value=json.dumps(auth_data),
                    )
                    success_count += 1

                except Exception as e:
                    sender.reply(f"❌ 授权用户 {user} 失败: {str(e)}")

        sender.reply(f"✅ 一键授权完成！成功授权 {success_count} 个账号")

    elif choice == "2":
        # 单独授权用户
        sender.reply("请输入需要授权的用户ID:")
        target_userid = sender.input(120000, 1, False)
        if not target_userid:
            sender.reply("❌ 用户ID无效")
            return

        accounts = get_user_accounts(target_userid)
        if not accounts:
            sender.reply(f"❌ 用户 {target_userid} 未绑定任何森选账号")
            return

        # 显示该用户的所有账号
        account_lines = []
        for i, account_id in enumerate(accounts, 1):
            token_with_remark = middleware.bucketGet("G_szyx_token", account_id) or ""
            if "#" in token_with_remark:
                remark, token = token_with_remark.split("#", 1)
                remark = remark.strip()
            else:
                token = token_with_remark
                remark = "默认账号"

            account_lines.append(f"[{i}] {remark}")

        account_list = "\n".join(account_lines)

        sender.reply(
            "=====用户账号列表=====\n"
            f"用户ID: {target_userid}\n"
            f"账号列表:\n{account_list}\n"
            "------------------\n"
            "回复 [0] 授权全部账号\n"
            "回复序号授权单个账号\n"
            "===================="
        )

        account_choice = sender.input(120000, 1, False)
        if account_choice == "0":
            # 授权全部账号
            sender.reply("请输入授权月数 (1-12):")
            months = sender.input(120000, 1, False)
            if not months.isdigit() or int(months) < 1 or int(months) > 12:
                sender.reply("❌ 月数必须为1-12之间的整数")
                return
            months = int(months)

            success_count = 0
            for account_id in accounts:
                try:
                    token_with_remark = (
                        middleware.bucketGet("G_szyx_token", account_id) or ""
                    )
                    if "#" in token_with_remark:
                        remark, token = token_with_remark.split("#", 1)
                        remark = remark.strip()
                    else:
                        token = token_with_remark
                        remark = "默认账号"

                    expire_time = datetime.now() + timedelta(days=months * 30)

                    auth_data = {
                        "userid": target_userid,
                        "remark": remark,
                        "account_id": account_id,
                        "expire_time": str(expire_time.date()),
                        "authorized_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "authorized_months": months,
                        "authorized_by": "admin",
                    }

                    middleware.bucketSet(
                        bucket="G_szyx_auth",
                        key=account_id,
                        value=json.dumps(auth_data),
                    )
                    success_count += 1

                except Exception as e:
                    sender.reply(f"❌ 授权账号失败: {str(e)}")

            sender.reply(f"✅ 成功授权该用户所有账号（{success_count}个）")

        elif account_choice.isdigit():
            # 授权单个账号
            selected_idx = int(account_choice) - 1
            if selected_idx < 0 or selected_idx >= len(accounts):
                sender.reply("❌ 序号无效")
                return

            account_id = accounts[selected_idx]
            token_with_remark = middleware.bucketGet("G_szyx_token", account_id) or ""
            if "#" in token_with_remark:
                remark, token = token_with_remark.split("#", 1)
                remark = remark.strip()
            else:
                token = token_with_remark
                remark = "默认账号"

            sender.reply(f"您选择了账号: {remark}\n请输入授权月数 (1-12):")
            months = sender.input(120000, 1, False)
            if not months.isdigit() or int(months) < 1 or int(months) > 12:
                sender.reply("❌ 月数必须为1-12之间的整数")
                return
            months = int(months)

            expire_time = datetime.now() + timedelta(days=months * 30)

            auth_data = {
                "userid": target_userid,
                "remark": remark,
                "account_id": account_id,
                "expire_time": str(expire_time.date()),
                "authorized_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "authorized_months": months,
                "authorized_by": "admin",
            }

            middleware.bucketSet(
                bucket="G_szyx_auth", key=account_id, value=json.dumps(auth_data)
            )
            sender.reply(f"✅ 授权成功！账号 {remark} 已授权 {months}个月")

        else:
            sender.reply("❌ 无效选择")
    else:
        sender.reply("❌ 无效选择")


def query_account_status():
    """查询账号状态"""
    accounts = get_user_accounts()

    if not accounts:
        sender.reply("❌ 您尚未绑定任何账号，请先绑定")
        return

    for idx, account_id in enumerate(accounts, 1):
        # 获取账号的access token
        token_with_remark = middleware.bucketGet("G_szyx_token", account_id)
        if not token_with_remark:
            sender.reply(f"账号 {idx}: ❌ Token缺失")
            continue

        # 获取备注
        if "#" in token_with_remark:
            remark, token = token_with_remark.split("#", 1)
            remark = remark.strip()
            token = token.strip()
        else:
            token = token_with_remark.strip()
            remark = "默认账号"

        display_name = remark

        result_msg = f"森选查询\n账号: {display_name}\n"

        # 检查授权状态
        auth_data = middleware.bucketGet("G_szyx_auth", key=account_id)
        expire_date = "未知"

        if auth_data:
            try:
                auth_info = json.loads(auth_data)
                expire_date = auth_info.get("expire_time", "未知")
                result_msg += f"授权: 已授权\n到期: {expire_date}\n"

                # 检查是否即将到期（小于4天）
                if expire_date != "未知":
                    try:
                        expire_date_obj = datetime.strptime(
                            expire_date, "%Y-%m-%d"
                        ).date()
                        today = datetime.now().date()
                        days_left = (expire_date_obj - today).days

                        if days_left < 0:
                            # 已过期
                            result_msg += "提醒: 授权已过期(将清理)\n"
                        elif days_left < 4:
                            # 即将到期（小于4天）
                            result_msg += f"提醒: 即将到期({days_left}天)\n"
                    except:
                        pass
            except:
                result_msg += "授权: 已授权\n到期: 未知\n"
        else:
            result_msg += "授权: 未授权\n"

        # 获取账号积分等信息
        try:
            # 创建客户端实例
            client = SenxuanClient(token_with_remark)

            # 优先使用新接口获取奖励记录
            consume_info = client.get_consume_record(page=1, rows=20)

            if (
                consume_info
                and consume_info.get("success")
                and consume_info.get("records")
            ):
                # 使用新接口的奖励记录
                records = consume_info.get("records") or []

                # 分离奖励记录和提现记录
                reward_records = [
                    r for r in records if "提现" not in r.get("record_title", "")
                ]
                withdraw_records = [
                    r for r in records if "提现" in r.get("record_title", "")
                ]
                reward_income = sum(
                    float(r.get("record_money", 0)) for r in reward_records
                )

                # 显示奖励统计
                result_msg += f"今日奖励: ¥{reward_income:.2f}\n奖励记录: {len(reward_records)}条\n"

                # 显示最近的奖励记录
                if reward_records:
                    result_msg += "最近奖励:\n"
                    for i, record in enumerate(reward_records[:3]):
                        record_title = record.get("record_title", "未知")
                        record_money = record.get("record_money", 0)
                        record_time = record.get("record_time", "未知")
                        result_msg += f"- ¥{record_money} {record_title} {str(record_time)[:10]}\n"

                # 显示提现记录
                if withdraw_records:
                    withdraw_total = sum(
                        float(r.get("record_money", 0)) for r in withdraw_records
                    )
                    result_msg += f"提现: {len(withdraw_records)}笔  合计: ¥{withdraw_total:.2f}\n"
                    for i, record in enumerate(withdraw_records[:3]):
                        record_money = record.get("record_money", 0)
                        record_time = record.get("record_time", "未知")
                        result_msg += f"- ¥{record_money} {str(record_time)[:10]}\n"
                else:
                    result_msg += "提现: 暂无\n"
            else:
                # 尝试使用原来的佣金接口作为备用
                commission_info = client.get_commission_info()
                if (
                    commission_info
                    and commission_info.get("success")
                    and commission_info.get("records")
                ):
                    records = commission_info.get("records") or []

                    # 筛选提现记录
                    withdraw_records = [
                        r for r in records if r.get("type") == "user_tx"
                    ]

                    # 计算总提现金额
                    total_amount = 0
                    for record in withdraw_records:
                        try:
                            amount = float(record.get("number", "0"))
                            total_amount += amount
                        except:
                            pass

                    # 显示提现统计
                    result_msg += (
                        f"提现: {len(withdraw_records)}笔  合计: ¥{total_amount:.2f}\n"
                    )

                    # 显示最近的提现记录
                    if withdraw_records:
                        result_msg += "最近提现:\n"

                        # 最多显示5条记录
                        for i, record in enumerate(withdraw_records[:5]):
                            amount = record.get("number", "0")
                            add_time = record.get("add_time", "未知")
                            # 保持原始时间格式
                            result_msg += f"现金{amount}元-{add_time}\n"
                else:
                    # 尝试通过佣金接口验证并获取信息
                    if token:
                        bearer_token = (
                            f"Bearer {token}"
                            if not token.lower().startswith("bearer ")
                            else token
                        )
                        commission_result = verify_commission_api(bearer_token)
                        if commission_result.get("success"):
                            data = commission_result.get("data", {})
                            if data and data.get("list"):
                                records = data["list"]

                                # 筛选提现记录
                                withdraw_records = [
                                    r for r in records if r.get("type") == "user_tx"
                                ]

                                # 计算总提现金额
                                total_amount = 0
                                for record in withdraw_records:
                                    try:
                                        amount = float(record.get("number", "0"))
                                        total_amount += amount
                                    except:
                                        pass

                                # 显示提现统计
                                result_msg += f"提现: {len(withdraw_records)}笔  合计: ¥{total_amount:.2f}\n"

                                # 显示最近的提现记录
                                if withdraw_records:
                                    result_msg += "最近提现:\n"

                                    # 最多显示5条记录
                                    for i, record in enumerate(withdraw_records[:5]):
                                        amount = record.get("number", "0")
                                        add_time = record.get("add_time", "未知")
                                        # 保持原始时间格式
                                        result_msg += f"现金{amount}元-{add_time}\n"
                        else:
                            result_msg += "状态: CK可能失效(去森选管理更新)\n"

        except Exception as e:
            result_msg += f"❌ 查询失败: {str(e)[:50]}\n"

        sender.reply(result_msg.strip())


def show_tutorial():
    """显示使用教程"""
    tutorial = """森选质享教程
📱 入口: #小程序://银辉云选/mpcwyYtMQegcNjc

🔑 抓包获取Token
域名: yb.yuanhukj.com
字段: authorization (去掉Bearer)
格式: 备注#token

📋 指令说明
森选登录 - 绑定账号
森选管理 - 授权/更新Token
森选查询 - 查积分余额
森选运行 - 执行任务(管理员)
森选青龙 - 导出青龙配置

💡 Token失效→森选管理→更新账号"""
    sender.reply(tutorial)


def sz_export_qinglong():
    """导出已授权账号到青龙格式"""
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 您尚未绑定任何账号")
        return

    today = datetime.now().date()
    valid_tokens = []
    expired_count = 0
    unauthorized_count = 0

    for account_id in accounts:
        token_with_remark = middleware.bucketGet("G_szyx_token", account_id)
        if not token_with_remark:
            continue

        if "#" in token_with_remark:
            remark, token = token_with_remark.split("#", 1)
            remark, token = remark.strip(), token.strip()
        else:
            token, remark = token_with_remark.strip(), "默认账号"

        auth_data_str = middleware.bucketGet("G_szyx_auth", account_id)
        if not auth_data_str:
            unauthorized_count += 1
            continue

        try:
            auth_data = json.loads(auth_data_str)
            expire_date = auth_data.get("expire_time")
            if expire_date:
                expire_date_obj = datetime.strptime(expire_date, "%Y-%m-%d").date()
                if expire_date_obj < today:
                    expired_count += 1
                    continue
        except:
            unauthorized_count += 1
            continue

        valid_tokens.append(f"{remark}#{token}")

    if not valid_tokens:
        msg = "❌ 没有有效的已授权账号可导出"
        if expired_count:
            msg += f"\n⏰ 已过期: {expired_count}个"
        if unauthorized_count:
            msg += f"\n🔒 未授权: {unauthorized_count}个"
        sender.reply(msg)
        return

    env_value = "\n".join(valid_tokens)
    result_msg = f"""森选青龙配置
环境变量名: S_SZYX
格式: 备注#token
有效账号: {len(valid_tokens)}个"""
    if expired_count:
        result_msg += f"\n已过期: {expired_count}个(已跳过)"
    if unauthorized_count:
        result_msg += f"\n未授权: {unauthorized_count}个(已跳过)"
    result_msg += f"\n\n复制以下内容到青龙:\n{env_value}"

    sender.reply(result_msg)


def sz_upload_qinglong():
    """管理员批量上传所有账号到青龙"""
    if not sender.isAdmin():
        sender.reply("❌ 仅管理员可用")
        return
    cfg = get_config()
    if not cfg["ql_config"]:
        sender.reply("❌ 未配置青龙面板\n请在插件参数中配置【青龙容器】")
        return
    parts = cfg["ql_config"].split("丨")
    if len(parts) != 3:
        sender.reply(
            "❌ 青龙配置格式错误\n格式: http://ip:5700丨ClientID丨ClientSecret"
        )
        return
    host, cid, sec = parts[0].strip(), parts[1].strip(), parts[2].strip()
    ql_token = get_ql_token(host, cid, sec)
    if not ql_token:
        sender.reply("❌ 获取青龙Token失败，请检查配置")
        return
    sender.reply("🔄 正在获取青龙变量...")
    headers = {
        "Authorization": f"Bearer {ql_token}",
        "Content-Type": "application/json",
    }
    envname = cfg["ql_envname"]
    try:
        envs_r = requests.get(
            f"{host}/open/envs",
            headers=headers,
            params={"searchValue": envname},
            timeout=10,
        )
        ql_envs = [
            env for env in envs_r.json().get("data", []) if env.get("name") == envname
        ]
    except Exception as e:
        sender.reply(f"❌ 获取变量失败: {e}")
        return
    ql_accounts = {}
    for env in ql_envs:
        remarks = env.get("remarks", "")
        env_id = env.get("_id") or env.get("id")
        if "账号:" in remarks:
            acc_id = remarks.split("账号:")[1].split("|")[0].strip()
            if acc_id and env_id:
                ql_accounts[acc_id] = env_id
    sender.reply(f"📊 青龙变量: {len(ql_envs)}个\n🔍 识别账号: {len(ql_accounts)}个")
    try:
        users = middleware.bucketAllKeys(bucket="G_szyx_user") or []
    except:
        users = []
    update_cnt, add_cnt, skip_cnt, fail_cnt = 0, 0, 0, 0
    today = datetime.now().date()
    for uid in users:
        accounts = get_user_accounts(uid)
        for account_id in accounts:
            auth_data_str = middleware.bucketGet("G_szyx_auth", account_id)
            if not auth_data_str:
                skip_cnt += 1
                continue
            try:
                auth_data = json.loads(auth_data_str)
                expire = auth_data.get("expire_time", "")
                if expire and datetime.strptime(expire, "%Y-%m-%d").date() < today:
                    skip_cnt += 1
                    continue
            except:
                skip_cnt += 1
                continue
            token_with_remark = middleware.bucketGet("G_szyx_token", account_id)
            if not token_with_remark:
                skip_cnt += 1
                continue
            if "#" in token_with_remark:
                remark, raw_token = token_with_remark.split("#", 1)
                remark, raw_token = remark.strip(), raw_token.strip()
            else:
                raw_token, remark = token_with_remark.strip(), "默认账号"
            value = f"{remark}#{raw_token}"
            remarks = f"森选:{remark}|账号:{account_id}|用户:{uid}|到期:{expire}"
            if account_id in ql_accounts:
                try:
                    r = requests.put(
                        f"{host}/open/envs",
                        headers=headers,
                        json={
                            "id": ql_accounts[account_id],
                            "name": envname,
                            "value": value,
                            "remarks": remarks,
                        },
                        timeout=10,
                    )
                    if r.status_code == 200 and r.json().get("code") == 200:
                        update_cnt += 1
                    else:
                        fail_cnt += 1
                except:
                    fail_cnt += 1
            else:
                try:
                    r = requests.post(
                        f"{host}/open/envs",
                        headers=headers,
                        json=[{"name": envname, "value": value, "remarks": remarks}],
                        timeout=10,
                    )
                    if r.status_code == 200 and r.json().get("code") == 200:
                        add_cnt += 1
                    else:
                        fail_cnt += 1
                except:
                    fail_cnt += 1
    sender.reply(
        f"✅ 同步完成\n📊 青龙原有: {len(ql_envs)}\n🔄 更新: {update_cnt}\n➕ 新增: {add_cnt}\n⏭️ 跳过: {skip_cnt}\n❌ 失败: {fail_cnt}"
    )


def sz_clean_accounts():
    """清理未授权和授权过期的森选账号"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作")
        return

    users = middleware.bucketAllKeys(bucket="G_szyx_user")
    if not users:
        sender.reply("❌ 未找到任何绑定账号")
        return

    sender.reply(f"""
=====开始清理=====
📊 共找到: {len(users)}个用户
清理中请稍候...
==================""")

    cleaned_count = 0
    failed_count = 0
    today = datetime.now().date()

    for user in users:
        try:
            accountlist = middleware.bucketGet(bucket="G_szyx_user", key=f"{user}")
            if not accountlist:
                continue

            accounts = json.loads(accountlist)
            if not isinstance(accounts, list):
                accounts = [accounts]

            valid_accounts = []

            for account_id in accounts:
                should_delete = False
                auth_data_str = middleware.bucketGet(
                    bucket="G_szyx_auth", key=account_id
                )

                if not auth_data_str:
                    # 未授权账号，删除
                    should_delete = True
                else:
                    try:
                        auth_data = json.loads(auth_data_str)
                        expire_date = auth_data.get("expire_time")

                        if expire_date:
                            expire_date_obj = datetime.strptime(
                                expire_date, "%Y-%m-%d"
                            ).date()
                            if expire_date_obj < today:
                                # 已过期账号，删除
                                should_delete = True
                    except:
                        # 数据异常，删除
                        should_delete = True

                if should_delete:
                    try:
                        # 删除token和授权信息
                        middleware.bucketDel(bucket="G_szyx_token", key=account_id)
                        middleware.bucketDel(bucket="G_szyx_auth", key=account_id)
                        cleaned_count += 1
                    except:
                        failed_count += 1
                else:
                    # 保留有效账号
                    valid_accounts.append(account_id)

            # 更新用户的账号列表
            if valid_accounts:
                middleware.bucketSet(
                    bucket="G_szyx_user", key=user, value=json.dumps(valid_accounts)
                )
            else:
                # 如果用户没有有效账号了，删除用户记录
                middleware.bucketDel(bucket="G_szyx_user", key=user)

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


# 主入口函数
try:
    usermessage = sender.getMessage()
except AttributeError:
    usermessage = ""

if re.search(r"(森选|sz)登(录|陆)", usermessage):
    bindaccount()
elif re.search(r"(森选|sz)管理", usermessage):
    sz_manage()
elif re.search(r"(森选|sz)查询", usermessage):
    query_account_status()
elif re.search(r"(森选|sz)一键运行", usermessage) and sender.isAdmin():
    sz_auto_run()
elif re.search(r"(森选|sz)教程", usermessage):
    show_tutorial()
elif re.search(r"(森选|sz)授权$", usermessage) and sender.isAdmin():
    admin_authorize_account()
elif re.search(r"(森选|sz)清理", usermessage) and sender.isAdmin():
    sz_clean_accounts()
elif re.search(r"(森选|sz)上传", usermessage) and sender.isAdmin():
    sz_upload_qinglong()
else:
    sender.setContinue()
