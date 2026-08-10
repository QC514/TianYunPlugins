# [title: 星妈优选]
# [language: python]
# [class: 工具类]
# [service: 203066880] 售后联系
# [author: rujingxianghai] 作者
# [rule: ^(星妈|xingma)(登录|登陆)$|^登(录|陆)(星妈|xingma)$|^(星妈|xingma)(查询|管理|授权|检测|教程)$|^(查询|管理)(星妈|xingma)$|^星妈一键运行$]
# [cron: 18 12 * * *] cron定时
# [priority: 0] 优先级
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用平台
# [open_source: false] 是否开源
# [icon: https://i.mji.rip/2025/07/11/2350538ac014afbea48b64409bd5931c.png] 图标
# [version: 1.0] 版本号
# [public: true] 是否发布
# [price: 88.88] 上架价格
# [description: 【白名单】星妈优选全自动积分管理插件<br>指令：星妈登录、星妈查询、星妈管理、星妈一键运行、星妈授权、星妈检测、星妈教程]

# [param: {"required":true,"key":"s_xmyx.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"授权价格(元)/月"}]
# [param: {"required":false,"key":"s_xmyx.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一月需要多少积分"}]
# [param: {"required":false,"key":"s_xmyx.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_xmyx.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]

import os
import json
import time
import hashlib
import random
import re
import requests
from datetime import datetime, timedelta
import middleware
import vorto_utils
from vorto_utils import mask_account, check_auth_status, calculate_auth_time

# 初始化
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_xmyx_user', key=userid)

PLUGIN_CONFIG = {'bucket': 's_xmyx', 'coin_key': 'dd_sign_points', 'name': '星妈'}

# 星妈API配置
appid = "xmyx"
appKey = middleware.bucketGet(bucket='s_xmyx', key='appKey') or 'TwUQ01lKS1Km5zlV2f7amsZc5EQYkTbv'


def get_user_content():
    """获取插件配置"""
    Vipmoney = float(middleware.bucketGet('s_xmyx', 'Vipmoney') or '0.88')
    coin = int(middleware.bucketGet('s_xmyx', 'coin') or '0')
    return Vipmoney, coin


# ==================== 核心API类 ====================

class XingMaYouXuanAuto:
    def __init__(self, access_token):
        self.token = access_token
        self.headers = {
            "Host": "www.feihevip.com",
            "token": access_token,
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48(0x1800302b) NetType/4G Language/zh_CN",
            "Referer": "https://servicewechat.com/wx4205ec55b793245e/215/page-frame.html",
            "fhAppid": appid,
            "source": "1",
        }

    def get_signature(self):
        fh_nonce_str = self._gen_nonce(16)
        fh_timestamp = str(int(str(int(time.time() * 1000))[:10]))
        data = "{}"
        sign_string = f"fhAppid{appid}fhNonceStr{fh_nonce_str}fhTimestamp{fh_timestamp}{data}{appKey}"
        return {
            "fhNonceStr": fh_nonce_str,
            "fhTimestamp": fh_timestamp,
            "fhSign": hashlib.md5(sign_string.encode("utf-8")).hexdigest().upper(),
        }

    def get_signature2(self):
        fh_nonce_str = self._gen_nonce(16)
        fh_timestamp = str(int(str(int(time.time() * 1000))[:10]))
        sign_string = f"fhAppidxmhfhNonceStr{fh_nonce_str}fhTimestamp{fh_timestamp}98d9fe9b613a479dbcb111ca261e3ce1"
        return {
            "fhNonceStr": fh_nonce_str,
            "fhTimestamp": fh_timestamp,
            "fhSign": hashlib.md5(sign_string.encode("utf-8")).hexdigest().upper(),
        }

    def _gen_nonce(self, length):
        char_pool = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        return ''.join(random.choice(char_pool) for _ in range(length))

    def get_user_info(self):
        try:
            signature = self.get_signature()
            res = requests.post(
                url="https://www.feihevip.com/api/starMember/getMemberInfo",
                headers={**self.headers, **signature},
                json={},
                timeout=(5, 30),
            ).json()
            if res.get("code") == "200" and res.get("data"):
                return res["data"]
            else:
                print(f"⛔️ 查询用户信息失败! {res.get('msg')}")
        except Exception as e:
            print(f"⛔️ 查询用户信息失败! {e}")
        return None

    def signin(self):
        try:
            for attempt in range(1, 4):
                try:
                    signature = self.get_signature()
                    _header = {**self.headers, **signature}
                    res = requests.post(
                        url="https://www.feihevip.com/api/member/signin/sign",
                        headers=_header,
                        json={},
                        timeout=(5, 30),
                    ).json()
                    if res.get("code") == "200":
                        try:
                            info_res = requests.get(
                                url="https://www.feihevip.com/api/member/signin/getSignInfo?signType=1",
                                headers=_header,
                                json={},
                                timeout=(5, 30),
                            ).json()
                            sign_pop = info_res.get("data", {}).get("signPop")
                            point = sign_pop[0]["signPoint"] if sign_pop else 0
                            print(f"✅ 签到获得积分: {point}分")
                        except Exception as e:
                            print(f"⚠️ 获取签到积分信息失败: {str(e)}")
                        return True
                    else:
                        if attempt < 3:
                            time.sleep(2)
                            continue
                        return False
                except Exception as e:
                    if attempt < 3:
                        time.sleep(2)
                        continue
                    raise e
            return False
        except Exception as e:
            print(f"⛔️ 签到失败! {e}")
            return False

    def get_task_list(self):
        try:
            for attempt in range(1, 4):
                try:
                    signature = self.get_signature()
                    res = requests.get(
                        url="https://www.feihevip.com/api/member/signin/getTaskList",
                        headers={**self.headers, **signature},
                        json={},
                        timeout=(5, 30),
                    ).json()
                    if res.get("code") == "200" and len(res.get("data", [])) > 0:
                        return res["data"]
                    else:
                        if attempt < 3:
                            time.sleep(2)
                            continue
                except Exception as e:
                    if attempt < 3:
                        time.sleep(2)
                        continue
                    raise e
            return []
        except Exception as e:
            print(f"⛔️ 获取任务失败! {e}")
            return []

    def tofinish(self, task_name, task_type):
        try:
            for attempt in range(1, 3):
                try:
                    signature = self.get_signature()
                    res = requests.get(
                        url=f"https://www.feihevip.com/api/member/signin/tofinish?taskType={task_type}",
                        headers={**self.headers, **signature},
                        json={},
                        timeout=(5, 30),
                    ).json()
                    if res.get("code") == "200":
                        print(f"🚀 开始执行任务: {task_name}")
                        return True
                    else:
                        if attempt < 2:
                            time.sleep(2)
                            continue
                        return False
                except Exception as e:
                    if attempt < 2:
                        time.sleep(2)
                        continue
                    raise e
            return False
        except Exception as e:
            print(f"⛔️ 执行任务{task_name}失败! {e}")
            return False

    def complete_task(self, task_name, task_type):
        try:
            for attempt in range(1, 4):
                try:
                    signature = self.get_signature()
                    res = requests.get(
                        url=f"https://www.feihevip.com/api/member/signin/completeTask?taskType={task_type}",
                        headers={**self.headers, **signature},
                        json={},
                        timeout=(5, 30),
                    ).json()
                    if res.get("code") == "200":
                        if res.get("data"):
                            point = res["data"].get("awardSendPoints", 0)
                            print(f"✅ 完成任务: {task_name}, 获取积分: {point}分")
                        else:
                            print(f"✅ 任务: {task_name} 已完成")
                        return True
                    else:
                        if attempt < 3:
                            time.sleep(2)
                            continue
                        return False
                except Exception as e:
                    if attempt < 3:
                        time.sleep(2)
                        continue
                    raise e
            return False
        except Exception as e:
            print(f"⛔️ 完成任务{task_name}失败! {e}")
            return False

    def refresh_token(self):
        try:
            signature = self.get_signature2()
            response = requests.get(
                "https://mom.feihe.com/program/token/refreshToken",
                headers={
                    "Host": "mom.feihe.com",
                    "token": self.token,
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48(0x1800302b) NetType/4G Language/zh_CN",
                    "Referer": "https://servicewechat.com/wx4205ec55b793245e/215/page-frame.html",
                    "fhAppid": "xmh",
                    "source": "1",
                    **signature,
                },
                timeout=(5, 30),
            ).json()
            new_token = response.get("data")
            if new_token:
                self.token = new_token
                self.headers["token"] = new_token
                return new_token
            return None
        except Exception as e:
            print(f"⛔️ 刷新 Token 失败: {e}")
            return None


# ==================== 任务执行 ====================

def run_task(task_list, client, account_id):
    """执行任务列表中的所有任务"""
    if not task_list or not isinstance(task_list, list):
        return
    for task in task_list:
        try:
            if not task.get("taskName") or not task.get("taskType"):
                continue
            if re.search(r"购买任意商品", task.get("taskName", "")):
                continue
            client.tofinish(task["taskName"], task["taskType"])
            wait_time = random.randint(2, 5)
            time.sleep(wait_time)
            client.complete_task(task["taskName"], task["taskType"])
            time.sleep(1)
            task_interval = random.randint(3, 6)
            time.sleep(task_interval)
        except Exception as e:
            print(f"执行任务失败: {str(e)}, 任务: {task.get('taskName', '未知')}")
            continue


def save_refreshed_token(client, account):
    """刷新并保存token"""
    try:
        new_token = client.refresh_token()
        if new_token:
            middleware.bucketSet('s_xmyx_token', account, new_token)
    except:
        pass


# ==================== 登录 ====================

def bind_account():
    """绑定账号"""
    sender.reply(
        "=====星妈优选登录=====\n"
        "请输入您的access_token\n"
        "支持批量登录(换行分隔)\n"
        "------------------\n"
        "回复\"q\"退出\n"
        "=================="
    )
    input_text = sender.input(120000, 1, False)
    if not input_text:
        sender.reply("⏰ 操作超时")
        return
    if input_text.strip().lower() == 'q':
        sender.reply("✅ 已取消")
        return

    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    tokens = list(dict.fromkeys(lines))

    if not tokens:
        sender.reply("❌ 未检测到有效的token")
        return

    success_list = []
    fail_list = []

    for token in tokens:
        try:
            client = XingMaYouXuanAuto(token)
            user_info = client.get_user_info()
            if user_info:
                user = user_info.get("baseInfo") or {}
                mobile = user.get("mobile") or user.get("fullName") or user.get("openId")
                if mobile:
                    accounts = eval(middleware.bucketGet('s_xmyx_user', userid) or '[]')
                    if mobile not in accounts:
                        accounts.append(mobile)
                        middleware.bucketSet('s_xmyx_user', userid, str(accounts))
                    middleware.bucketSet('s_xmyx_token', mobile, token)
                    success_list.append(f"✅ {mask_account(mobile)} 登录成功")
                else:
                    fail_list.append(f"❌ {token[:6]}... 无法获取手机号")
            else:
                fail_list.append(f"❌ {token[:6]}... token无效或过期")
            if len(tokens) > 1:
                time.sleep(0.5)
        except Exception as e:
            fail_list.append(f"❌ {token[:6]}... 验证失败: {str(e)[:20]}")

    result = "=====登录完成=====\n"
    result += f"✅ 成功: {len(success_list)}个\n"
    result += f"❌ 失败: {len(fail_list)}个\n"
    if success_list:
        result += '\n'.join(success_list) + '\n'
    if fail_list:
        result += '\n'.join(fail_list) + '\n'
    result += "=================="
    sender.reply(result)


# ==================== 查询 ====================

def query_accounts():
    """查询账号"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n💡 发送 星妈登录 绑定\n==================")
        return

    accounts = eval(uservalue)
    today = str(datetime.now().date())
    info_lines = []

    for i, account in enumerate(accounts, 1):
        token = middleware.bucketGet('s_xmyx_token', account)
        auth_time = middleware.bucketGet('s_xmyx_auth', account)

        if not auth_time:
            auth_status = '未授权'
        elif auth_time < today:
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'

        score_text = ""
        if token:
            try:
                client = XingMaYouXuanAuto(token)
                save_refreshed_token(client, account)
                user_info = client.get_user_info()
                if user_info:
                    member_points = user_info.get("memberPoints") or {}
                    score = member_points.get("scoreBalance", 0)
                    score_text = f"\n💰 积分: {score}"
            except:
                pass

        info_lines.append(
            f"=====账号信息[{i}/{len(accounts)}]=====\n"
            f"📱 账号: {mask_account(account)}\n"
            f"🔐 状态: {auth_status}{score_text}\n"
            f"=================="
        )

    sender.reply('\n'.join(info_lines))


# ==================== 管理 ====================

def manage_account():
    """管理账号"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n==================")
        return

    accounts = eval(uservalue)
    sender.reply(
        "=====账号管理=====\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "[3] 执行任务\n"
        "------------------\n"
        "回复数字选择\n"
        "回复\"q\"退出\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    if choice == '1':
        _authorize_flow(accounts)
    elif choice == '2':
        _delete_flow(accounts)
    elif choice == '3':
        xm_auto_run()
    else:
        sender.reply("❌ 无效选择")


def _show_account_list(accounts):
    """显示账号选择列表，返回格式化字符串"""
    today = str(datetime.now().date())
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, account in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_xmyx_auth', account)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < today:
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{mask_account(account)}({auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    return account_list


def _select_accounts(accounts):
    """账号选择交互，返回选中的账号列表"""
    sender.reply(_show_account_list(accounts))
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return None

    if choice == '0':
        return accounts.copy()

    selected = []
    for idx in choice.split(','):
        idx = idx.strip()
        if idx.isdigit() and 0 < int(idx) <= len(accounts):
            selected.append(accounts[int(idx) - 1])

    if not selected:
        sender.reply("❌ 未选择有效账号")
        return None

    return selected


def _authorize_flow(accounts):
    """授权流程"""
    selected = _select_accounts(accounts)
    if not selected:
        return

    Vipmoney, coin = get_user_content()

    sender.reply(
        f"=====设置授权时长=====\n"
        f"📦 已选: {len(selected)}个账号\n"
        f"请输入授权月数(如:1)\n"
        f"回复\"q\"退出\n"
        f"=================="
    )
    months_input = sender.input(120000, 1, False)
    if not months_input or months_input.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    try:
        months = int(months_input)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return
    except ValueError:
        sender.reply("❌ 请输入有效数字")
        return

    total_money = len(selected) * months * Vipmoney

    # 构建可用支付方式
    pay_config = vorto_utils.get_pay_config()
    available = []

    if pay_config['qr_pay_switch']:
        available.append(("扫码支付", "qrcode"))
    if pay_config['ma_pay_switch']:
        pay_types = pay_config['pay_types']
        if pay_types:
            for pay_key, pay_name in pay_types.items():
                available.append((f"{pay_name}(码支付)", f"mapay_{pay_key}"))

    if coin > 0:
        available.append(("积分兑换", "coin"))

    if not available and total_money > 0:
        sender.reply("❌ 未配置支付方式，请联系管理员在Vorto初始化中开启")
        return

    # 免费直接授权
    if total_money <= 0:
        _batch_authorize(selected, months)
        return

    # 显示支付方式
    pay_menu = f"=====选择支付方式=====\n📦 账号数: {len(selected)}个\n📅 时长: {months}月\n💰 总金额: ¥{total_money:.2f}\n"
    if coin > 0:
        total_coin = len(selected) * months * coin
        pay_menu += f"📊 积分价格: {total_coin}积分\n"
    pay_menu += "------------------\n"
    for i, (name, _) in enumerate(available, 1):
        pay_menu += f"[{i}] {name}\n"
    pay_menu += "回复数字选择\n=================="
    sender.reply(pay_menu)

    pay_choice = sender.input(120000, 1, False)
    if not pay_choice or pay_choice.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    try:
        pay_idx = int(pay_choice) - 1
        if pay_idx < 0 or pay_idx >= len(available):
            sender.reply("❌ 无效选择")
            return
    except ValueError:
        sender.reply("❌ 请输入有效数字")
        return

    pay_name, pay_type = available[pay_idx]

    # 处理支付
    if pay_type == "qrcode":
        if not _process_qrcode_payment(f"星妈授权-{len(selected)}个账号", months, total_money):
            return
    elif pay_type == "coin":
        total_coin = len(selected) * months * coin
        if not _process_coin_payment(total_coin):
            return
    elif pay_type.startswith("mapay_"):
        actual_type = pay_type.replace("mapay_", "")
        if not _process_mapay_payment(f"星妈授权-{len(selected)}个账号", months, total_money, actual_type):
            return

    _batch_authorize(selected, months)


def _batch_authorize(selected, months):
    """批量授权（不含支付，仅设置授权时间）"""
    success_list = []
    fail_list = []

    for account in selected:
        try:
            new_expire = calculate_auth_time('s_xmyx_auth', account, months=months)
            middleware.bucketSet('s_xmyx_auth', account, new_expire)
            success_list.append(f"{mask_account(account)} → {new_expire}")
        except Exception as e:
            fail_list.append(f"{mask_account(account)} {str(e)}")

    result = "=====授权完成=====\n"
    result += f"✅ 成功: {len(success_list)}个\n"
    if success_list:
        result += '\n'.join(success_list) + '\n'
    if fail_list:
        result += f"❌ 失败: {len(fail_list)}个\n"
        result += '\n'.join(fail_list) + '\n'
    result += "=================="
    sender.reply(result)


def _delete_flow(accounts):
    """删除账号流程"""
    selected = _select_accounts(accounts)
    if not selected:
        return

    sender.reply(
        f"=====删除确认=====\n"
        f"确认删除 {len(selected)} 个账号？\n"
        f"回复 Y 确认\n"
        f"=================="
    )
    confirm = sender.input(120000, 1, False)
    if not confirm or confirm.strip().upper() != 'Y':
        sender.reply("✅ 已取消")
        return

    current_accounts = eval(middleware.bucketGet('s_xmyx_user', userid) or '[]')
    success_list = []
    for account in selected:
        try:
            middleware.bucketDel('s_xmyx_token', account)
            middleware.bucketDel('s_xmyx_auth', account)
            if account in current_accounts:
                current_accounts.remove(account)
            success_list.append(mask_account(account))
        except Exception as e:
            print(f"删除账号异常: {str(e)}")

    if current_accounts:
        middleware.bucketSet('s_xmyx_user', userid, str(current_accounts))
    else:
        middleware.bucketDel('s_xmyx_user', userid)

    sender.reply(
        f"=====删除完成=====\n"
        f"✅ 已删除 {len(success_list)} 个账号\n"
        f"=================="
    )


# ==================== 支付 ====================

def _process_qrcode_payment(project, months, money):
    """收款码支付"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    zsm = pay_config['zsm']
    if not zsm:
        sender.reply('❌ 未配置收款码，请联系管理员')
        return False

    sender.reply(
        f"======扫码支付======\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {money}元\n"
        f"=================="
    )
    sender.replyImage(zsm)

    ddzf = sender.waitPay("q", 300000)
    if str(ddzf) == 'q':
        sender.reply('✅ 已取消')
        return False

    try:
        if isinstance(ddzf, str):
            ddzf = json.loads(ddzf)
        if float(ddzf.get('Money') or ddzf.get('money', 0)) >= float(money):
            return True
        sender.reply("❌ 支付金额不足")
        return False
    except:
        sender.reply("❌ 支付验证失败")
        return False


def _process_coin_payment(required_points):
    """积分支付"""
    user_points = int(middleware.bucketGet('dd_sign_points', userid) or '0')

    if user_points < required_points:
        sender.reply(
            f"=====积分不足=====\n"
            f"❌ 当前: {user_points}\n"
            f"💰 需要: {required_points}\n"
            f"=================="
        )
        return False

    middleware.bucketSet('dd_sign_points', userid, str(user_points - required_points))
    sender.reply(
        f"=====积分扣除成功=====\n"
        f"✅ 扣除: {required_points}\n"
        f"💰 剩余: {user_points - required_points}\n"
        f"=================="
    )
    return True


def _process_mapay_payment(project, months, money, pay_type='alipay'):
    """码支付处理"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    if not pay_config['ma_pay_switch']:
        sender.reply("❌ 码支付功能未开启")
        return False

    try:
        out_trade_no = f"XMYX{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        pay_type_name = pay_config['pay_types'].get(pay_type, '支付宝')

        sender.reply(
            f"=====码支付信息=====\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: {money}元\n"
            f"💳 方式: {pay_type_name}\n"
            f"=================="
        )

        mapay = vorto_utils.MaPayClient()
        order = mapay.create_order(float(money), pay_type, out_trade_no, f"{project}-{money}", userid)

        if order.get('error'):
            sender.reply(f"❌ 创建订单失败: {order.get('error')}")
            return False

        pay_url = order.get('pay_url')
        qr_url = vorto_utils.generate_qrcode_url(pay_url)
        sender.replyImage(qr_url)
        sender.reply(f'💳 请使用【{pay_type_name}】扫码支付\n⏰ 5分钟内完成支付\n输入"q"可取消')

        start_time = time.time()
        timeout = 300

        while time.time() - start_time < timeout:
            user_input = sender.input(5000, 1, False)
            if user_input and user_input.lower() == 'q':
                sender.reply("✅ 已取消支付")
                return False
            if mapay.is_paid(out_trade_no):
                sender.reply("✅ 支付成功！")
                return True

        sender.reply("❌ 支付超时")
        return False
    except Exception as e:
        sender.reply(f"❌ 支付异常: {str(e)}")
        return False


# ==================== 一键运行 ====================

def xm_auto_run():
    """一键运行所有授权账号的任务"""
    authorized_accounts = []
    auth_keys = middleware.bucketAllKeys(bucket='s_xmyx_auth') or []
    today = str(datetime.now().date())

    for account_id in auth_keys:
        auth_time = middleware.bucketGet('s_xmyx_auth', account_id)
        if auth_time and auth_time >= today:
            authorized_accounts.append(account_id)

    if not authorized_accounts:
        sender.reply("❌ 没有已授权的账号")
        return

    run_results = []
    skip_results = []
    total_earned = 0

    for account_id in authorized_accounts:
        access_token = middleware.bucketGet('s_xmyx_token', account_id)
        if not access_token:
            skip_results.append(account_id)
            continue

        client = XingMaYouXuanAuto(access_token)

        # 记录执行前积分
        user_info_before = client.get_user_info() or {}
        member_points_before = user_info_before.get("memberPoints") or {}
        score_before = member_points_before.get("scoreBalance", 0)

        # 签到
        sign_success = client.signin()
        sign_result = "✅" if sign_success else "❌"

        # 执行任务
        task_list = client.get_task_list() or []
        task_count = len(task_list)
        if task_count > 0:
            run_task(task_list, client, account_id)
            task_result = f"✅完成{task_count}任务"
        else:
            task_result = "⏩无任务"

        # 刷新并保存token
        save_refreshed_token(client, account_id)
        time.sleep(1)

        # 记录执行后积分
        user_info_after = client.get_user_info() or {}
        member_points_after = user_info_after.get("memberPoints") or {}
        score_after = member_points_after.get("scoreBalance", 0)
        earned_this_run = max(0, score_after - score_before)
        total_earned += earned_this_run

        run_results.append(f"📱 {mask_account(account_id)}: {sign_result}签到 | {task_result}")

    result_msg = (
        f"🚀 星妈任务汇总 📊\n"
        f"====================\n"
        f"✅ 成功账号: {len(run_results)}个\n"
        f"❌ 失败账号: {len(skip_results)}个\n"
        f"💰 积分收益: {total_earned}\n"
        f"===================="
    )
    return result_msg


# ==================== 教程 ====================

def show_tutorial():
    """显示教程"""
    sender.reply(
        '=====星妈教程=====\n'
        '用户指令:\n'
        '1. 星妈登录 - 绑定账号\n'
        '2. 星妈查询 - 查看积分和状态\n'
        '3. 星妈管理 - 授权、删除、执行任务\n'
        '4. 星妈一键运行 - 批量执行签到和任务\n'
        '5. 星妈教程 - 查看说明\n'
        '------------------\n'
        '管理员指令:\n'
        '1. 星妈授权 - 批量授权\n'
        '2. 星妈检测 - 检测过期并清理\n'
        '------------------\n'
        '绑定输入:\n'
        '输入access_token\n'
        '支持换行批量绑定\n'
        '=================='
    )


# ==================== 管理员功能 ====================

def ks_auth():
    """管理员授权"""
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return

    sender.reply(
        "=====管理员授权=====\n"
        "[1] 授权所有用户\n"
        "[2] 按用户授权\n"
        "------------------\n"
        "回复数字选择操作\n"
        "回复\"q\"退出"
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出管理员授权")
        return

    if choice == '1':
        vorto_utils.admin_auth_all_accounts(
            sender, 's_xmyx_user', 's_xmyx_auth', 's_xmyx_token'
        )
    elif choice == '2':
        vorto_utils.admin_auth_by_user(
            sender, 's_xmyx_user', 's_xmyx_auth', 's_xmyx_token'
        )
    else:
        sender.reply("❌ 无效的选择")


# ==================== 主入口 ====================

def main():
    """主入口"""
    msg = sender.getMessage()

    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '查询' in msg and ('星妈' in msg or 'xingma' in msg.lower()):
        query_accounts()
    elif '管理' in msg and ('星妈' in msg or 'xingma' in msg.lower()):
        manage_account()
    elif '教程' in msg and ('星妈' in msg or 'xingma' in msg.lower()):
        show_tutorial()
    elif '星妈授权' in msg:
        ks_auth()
    elif '星妈检测' in msg:
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        result = check_auth_status(
            's_xmyx', 's_xmyx_user', 's_xmyx_auth', 's_xmyx_token',
            '星妈'
        )
        sender.reply(result)
    elif '星妈一键运行' in msg:
        result = xm_auto_run()
        if result:
            sender.reply(result)
    # 定时任务
    elif sender.getImtype() == 'fake':
        try:
            # 自动执行任务
            result = xm_auto_run()
            if result:
                middleware.notifyMasters(result)
            # 检测授权状态
            check_result = check_auth_status(
                's_xmyx', 's_xmyx_user', 's_xmyx_auth', 's_xmyx_token',
                '星妈'
            )
            middleware.notifyMasters(check_result)
        except:
            pass
    else:
        sender.setContinue()

if __name__ == "__main__":
    main()
