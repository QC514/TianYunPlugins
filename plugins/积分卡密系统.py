#[pin:false]
#[public:true]
#[disable:false]
# [rule: ^(签到|系统管理|积分查询|查询积分|充值积分|积分充值|DD_.*|R_.*|卡密:DD_.*|更新配置)$]
# [cron: 0 0 0 * * *]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [author: rujingxianghai]
# [title: 积分卡密系统]
# [class: 工具类]
# [version: 5.7]
# [price: 0]
# [description: 签到获取积分,积分可用于兑换各类服务。命令:签到丨积分查询丨充值积分丨系统管理(管理员)<br>支持卡密充值,收款码充值,积分管理,服务积分设置<br>5.7更新：码支付统一走vorto_utils，移除支付锁<br>5.6更新：优化码支付二维码生成方式]
# [param: {"required":true,"key":"dd_sign_config.sign","bool":true,"placeholder":"","name":"签到功能","desc":"勾选可签到，默认关闭，需要先关闭奥特曼自带的签到功能！(用户系统里面)"}]
# [param: {"required":true,"key":"dd_sign_config.signcoin","bool":false,"placeholder":"默认:1-5 填写例:1-5","name":"积分区间","desc":"用户每次签到的积分区间"}]
# [param: {"required":true,"key":"dd_sign_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_sign_config.rate","bool":false,"placeholder":"默认:100 填写例:100","name":"兑换比例","desc":"1元=多少积分"}]

from datetime import datetime
import random
import middleware
import time
import json
import re
import requests
import vorto_utils

# Sender info
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
imtype = sender.getImtype()
username = sender.getUserName()

# Bucket definitions
CONFIG_BUCKET = 'dd_sign_config'
SIGN_DATE_BUCKET = 'dd_sign_dates'
POINTS_BUCKET = 'dd_sign_points'
CARD_BUCKET = 'dd_sign_cards'
RECHARGE_BUCKET = 'dd_sign_recharge'
PAY_ORDERS_BUCKET = 'dd_sign_orders'

# Sign config
signswitch = middleware.bucketGet(bucket=CONFIG_BUCKET, key='sign') or 'false'
signcoin = middleware.bucketGet(bucket=CONFIG_BUCKET, key='signcoin') or '1-5'

# Plugin configs (dynamic)
PLUGIN_CONFIGS = {}

# Recharge config (only zsm + rate remain)
RECHARGE_CONFIG = {
    'zsm': middleware.bucketGet(CONFIG_BUCKET, 'zsm') or '',
    'rate': middleware.bucketGet(CONFIG_BUCKET, 'rate') or '100',
}


# ==================== Points Functions ====================

def get_user_points(uid):
    """Get user points"""
    return int(middleware.bucketGet(POINTS_BUCKET, uid) or 0)


def add_user_points(uid, points, channel="", name=""):
    """Add points to user"""
    current = int(middleware.bucketGet(POINTS_BUCKET, uid) or 0)
    middleware.bucketSet(POINTS_BUCKET, uid, str(current + points))
    return get_user_points(uid)


def deduct_user_points(uid, points, channel="", name=""):
    """Deduct points from user"""
    current = int(middleware.bucketGet(POINTS_BUCKET, uid) or 0)
    if current < points:
        return False
    middleware.bucketSet(POINTS_BUCKET, uid, str(current - points))
    return True


# ==================== Sign Function ====================

def sign():
    """Daily sign-in"""
    today = str(datetime.now().date())

    lock_key = f'sign_lock_{userid}'
    if middleware.bucketGet(CONFIG_BUCKET, lock_key):
        sender.reply('操作太频繁，请稍后再试~')
        return

    try:
        middleware.bucketSet(CONFIG_BUCKET, lock_key, '1')

        last_sign = middleware.bucketGet(SIGN_DATE_BUCKET, userid)
        if last_sign == today:
            sender.reply('你好,你今日已经签到过了哦~')
            return

        min_coin, max_coin = map(int, signcoin.split('-'))
        coins = random.randint(min_coin, max_coin)

        current_coins = add_user_points(userid, coins, "签到", username)
        middleware.bucketSet(SIGN_DATE_BUCKET, userid, today)

        msg = f"""•你好,{username}
•签到成功,获得{coins}🌸
•你还有: {current_coins}🌸
•你可通过以下操作获取🌸
① 【签到】发送签到令签到
② 【积分查询】查看可兑换服务"""
        sender.reply(msg)

    except Exception as e:
        sender.reply(f'签到失败:{str(e)}')
    finally:
        middleware.bucketDel(CONFIG_BUCKET, lock_key)


# ==================== Query & Use Points ====================

def query_points():
    """Query points"""
    msg = f"""=====积分查询=====
💰 总积分: {get_user_points(userid)}

🎯 可用插件及积分:"""

    for plugin_id, config in PLUGIN_CONFIGS.items():
        try:
            coin_value = middleware.bucketGet(config['bucket'], config['coin_key'])
            if coin_value and coin_value != '0':
                msg += f"\n• {config['name']}: {coin_value}积分/月"
        except:
            continue

    msg += """
==================
💡 发送"充值积分"可充值
=================="""
    sender.reply(msg)


def use_points(plugin_id, points):
    """Use points for plugin"""
    if plugin_id not in PLUGIN_CONFIGS:
        return False, "插件不存在"

    current = get_user_points(userid)
    if current < points:
        return False, f"积分不足\n当前积分:{current}\n需要积分:{points}"

    try:
        success = deduct_user_points(userid, points, PLUGIN_CONFIGS[plugin_id]['name'], username)
        if success:
            return True, f"扣除{points}积分成功\n当前积分:{get_user_points(userid)}"
        return False, "扣除积分失败"
    except:
        return False, "扣除积分失败"


# ==================== Card Functions ====================

def generate_card(amount):
    """Generate card"""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    card = 'DD_' + ''.join(random.choice(chars) for _ in range(12))
    middleware.bucketSet(CARD_BUCKET, card, str(amount))
    return card


def use_card(card):
    """Use card"""
    try:
        card_match = re.search(r'(?:卡密:)?(DD_[A-Z0-9]{12})', card)
        if not card_match:
            return False, '卡密格式错误!'

        card = card_match.group(1)
        amount = middleware.bucketGet(CARD_BUCKET, card)

        if not amount:
            return False, '卡密不存在!'
        if amount == 'False':
            return False, '卡密已被使用!'

        try:
            amount = int(amount)
        except ValueError:
            try:
                card_info = json.loads(amount)
                return False, f'卡密已被{card_info["user"]}使用\n使用时间:{card_info["time"]}'
            except:
                return False, '卡密数据格式错误!'

        if amount <= 0:
            return False, '卡密面额错误!'

        current = add_user_points(userid, amount, "卡密充值", username)

        use_info = {
            'user': userid,
            'username': username,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'amount': amount
        }
        middleware.bucketSet(CARD_BUCKET, card, json.dumps(use_info))
        return True, f'充值成功!\n获得积分:{amount}\n当前积分:{current}'

    except Exception as e:
        return False, f'充值失败: {str(e)}'


# ==================== Admin System ====================

def system():
    """System management"""
    if not sender.isAdmin():
        sender.reply('您没有权限!')
        return

    msg = """========系统管理========
1、生成卡密
2、查看卡密
3、删除卡密
4、积分管理
5、充值管理
6、支付配置
7、服务积分设置
8、添加插件积分配置
======================
回复序号,退出【q】！"""

    sender.reply(msg)
    choice = sender.input(120000, 1, False)

    if choice == 'q':
        sender.reply('已退出')
        return

    if choice == '1':
        msg = """请选择生成方式:
1、单张生成
2、批量生成
=============
回复序号,退出【q】！"""
        sender.reply(msg)
        subchoice = sender.input(120000, 1, False)

        if subchoice == 'q':
            return

        if subchoice == '1':
            sender.reply('请输入卡密面额(积分):')
            amount = sender.input(120000, 1, False)
            try:
                amount = int(amount)
                if amount <= 0:
                    sender.reply('面额必须大于0')
                    return
                card = generate_card(amount)
                sender.reply(f'生成成功!\n卡密:{card}\n面额:{amount}积分')
            except:
                sender.reply('面额必须是数字!')

        elif subchoice == '2':
            sender.reply('请输入卡密面额(积分):')
            amount = sender.input(120000, 1, False)
            try:
                amount = int(amount)
                if amount <= 0:
                    sender.reply('面额必须大于0')
                    return

                sender.reply('请输入生成数量:')
                count = sender.input(120000, 1, False)
                try:
                    count = int(count)
                    if count <= 0 or count > 100:
                        sender.reply('数量必须在1-100之间')
                        return

                    cards = []
                    for _ in range(count):
                        card = generate_card(amount)
                        cards.append(card)

                    msg = f'批量生成成功!\n面额:{amount}积分\n数量:{count}张\n\n卡密列表:\n'
                    msg += '\n'.join(cards)
                    sender.reply(msg)
                except:
                    sender.reply('数量必须是数字!')
            except:
                sender.reply('面额必须是数字!')
        else:
            sender.reply('输入错误!')

    elif choice == '2':
        cards = middleware.bucketAllKeys(CARD_BUCKET)
        if not cards:
            sender.reply('暂无卡密!')
            return

        msg = '========卡密列表========\n'
        for card in cards:
            if not card.startswith('DD_'):
                continue
            card_data = middleware.bucketGet(CARD_BUCKET, card)
            try:
                use_info = json.loads(card_data)
                if isinstance(use_info, dict):
                    msg += f'卡密:{card}\n状态:已被{use_info["user"]}使用\n使用时间:{use_info["time"]}\n面额:{use_info["amount"]}积分\n\n'
                else:
                    msg += f'卡密:{card}\n面额:{card_data}积分\n状态:未使用\n\n'
            except:
                if card_data != 'False':
                    msg += f'卡密:{card}\n面额:{card_data}积分\n状态:未使用\n\n'
        msg += '======================'
        sender.reply(msg)

    elif choice == '3':
        sender.reply('请输入要删除的卡密:')
        card = sender.input(120000, 1, False)
        if middleware.bucketDel(CARD_BUCKET, card):
            sender.reply('删除成功!')
        else:
            sender.reply('卡密不存在!')

    elif choice == '4':
        msg = """========积分管理========
1、查询用户积分
2、修改用户积分
3、批量充值积分
======================
回复序号,退出【q】！"""
        sender.reply(msg)
        subchoice = sender.input(120000, 1, False)

        if subchoice == '1':
            query_points()

        elif subchoice == '2':
            sender.reply('请输入用户ID:')
            user_id = sender.input(120000, 1, False)
            sender.reply('请输入积分数量(负数表示扣除):')
            amount = sender.input(120000, 1, False)
            try:
                amount = int(amount)
                current = get_user_points(user_id)
                if amount < 0 and abs(amount) > current:
                    sender.reply('积分不足!')
                    return
                add_user_points(user_id, amount)
                sender.reply(f'修改成功!当前积分:{get_user_points(user_id)}')
            except:
                sender.reply('输入错误!')

        elif subchoice == '3':
            sender.reply('请输入充值金额:')
            amount = sender.input(120000, 1, False)
            try:
                amount = int(amount)
                if amount <= 0:
                    sender.reply('金额必须大于0')
                    return

                sender.reply('请输入用户ID列表(用逗号分隔):')
                users = sender.input(120000, 1, False).split(',')
                success = 0
                for user_id in users:
                    user_id = user_id.strip()
                    if user_id:
                        add_user_points(user_id, amount)
                        success += 1
                sender.reply(f'批量充值完成!\n成功:{success}\n失败:{len(users)-success}')
            except:
                sender.reply('输入错误!')

    elif choice == '5':
        handle_recharge()

    elif choice == '6':
        msg = f"""========支付配置========
当前配置:
收款码: {'已配置' if RECHARGE_CONFIG['zsm'] else '未配置'}
兑换比例: 1元={RECHARGE_CONFIG['rate']}积分
码支付: 请在Vorto初始化中配置

1、设置收款码
2、设置兑换比例
======================
回复序号,退出【q】！"""
        sender.reply(msg)
        subchoice = sender.input(120000, 1, False)

        if subchoice == '1':
            sender.reply('请发送赞赏码图片链接:')
            zsm = sender.input(120000, 1, False)
            middleware.bucketSet('dd_sign_config', 'zsm', zsm)
            RECHARGE_CONFIG['zsm'] = zsm
            sender.reply('设置成功!')

        elif subchoice == '2':
            sender.reply('请输入兑换比例(1元=?积分):')
            rate = sender.input(120000, 1, False)
            try:
                rate = int(rate)
                if rate <= 0:
                    sender.reply('比例必须大于0')
                    return
                middleware.bucketSet('dd_sign_config', 'rate', str(rate))
                RECHARGE_CONFIG['rate'] = str(rate)
                sender.reply('设置成功!')
            except:
                sender.reply('输入错误!')

    elif choice == '7':
        msg = """========服务积分设置========
当前支持的服务:"""

        service_list = []
        for idx, (service_id, config) in enumerate(PLUGIN_CONFIGS.items(), 1):
            service_list.append((str(idx), service_id, config['name']))
            msg += f"\n{idx}、{config['name']}"

        msg += """
======================
操作选项:
a、新增服务
d、删除服务
或输入序号修改积分
退出请输入【q】"""
        sender.reply(msg)

        service_map = {str(idx): service_id for idx, service_id, _ in service_list}

        subchoice = sender.input(120000, 1, False)
        if subchoice == 'q':
            return

        if subchoice == 'a':
            sender.reply("""请按以下格式输入服务信息:
服务ID,存储桶名,积分键名,显示名称
示例: myplugin,dd_myplugin,coin,我的插件""")

            service_info = sender.input(120000, 1, False)
            try:
                service_id, bucket, coin_key, name = [x.strip() for x in service_info.split(',')]

                if service_id in PLUGIN_CONFIGS:
                    sender.reply(f'服务ID [{service_id}] 已存在!')
                    return

                new_config = {
                    'bucket': bucket,
                    'coin_key': coin_key,
                    'name': name
                }

                custom_plugins = json.loads(middleware.bucketGet('dd_sign_config', 'custom_plugins') or '{}')
                custom_plugins[service_id] = new_config
                middleware.bucketSet('dd_sign_config', 'custom_plugins', json.dumps(custom_plugins))

                PLUGIN_CONFIGS[service_id] = new_config
                sender.reply(f'成功添加服务: {name}')

            except ValueError:
                sender.reply('输入格式错误!')
                return

        elif subchoice == 'd':
            sender.reply('请输入要删除的服务序号:')
            del_idx = sender.input(120000, 1, False)

            if del_idx not in service_map:
                sender.reply('序号无效!')
                return

            service_id = service_map[del_idx]
            service_name = PLUGIN_CONFIGS[service_id]['name']

            custom_plugins = json.loads(middleware.bucketGet('dd_sign_config', 'custom_plugins') or '{}')
            if service_id in custom_plugins:
                del custom_plugins[service_id]
                middleware.bucketSet('dd_sign_config', 'custom_plugins', json.dumps(custom_plugins))
                del PLUGIN_CONFIGS[service_id]
                sender.reply(f'成功删除服务: {service_name}')
            else:
                sender.reply('该服务为系统内置,无法删除!')

        elif subchoice in service_map:
            service = service_map[subchoice]
            config = PLUGIN_CONFIGS[service]

            current = middleware.bucketGet(config['bucket'], config['coin_key']) or '未设置'
            sender.reply(f'当前{config["name"]}需要积分: {current}\n请输入新的积分数量:')

            new_coins = sender.input(120000, 1, False)
            try:
                new_coins = int(new_coins)
                if new_coins <= 0:
                    sender.reply('积分必须大于0')
                    return
                middleware.bucketSet(config['bucket'], config['coin_key'], str(new_coins))
                sender.reply(f'设置成功!\n{config["name"]}现在需要{new_coins}积分')
            except:
                sender.reply('输入错误!')
        else:
            sender.reply('输入错误!')

    elif choice == '8':
        msg = """========添加插件积分配置========
请按照以下格式输入插件配置信息:
插件备注,插件数据桶名,积分数据桶名,对外显示的名称

示例: kuwo,dd_kuwo,coin,酷我音乐
======================
回复配置信息,退出【q】！"""
        sender.reply(msg)

        config_input = sender.input(120000, 1, False)
        if config_input == 'q':
            sender.reply('已退出')
            return

        try:
            parts = [x.strip() for x in config_input.split(',')]
            if len(parts) != 4:
                sender.reply('配置格式错误!\n请按照: 插件ID,存储桶名,积分键名,显示名称')
                return

            plugin_id, bucket, coin_key, name = parts

            if not all([plugin_id, bucket, coin_key, name]):
                sender.reply('所有字段都不能为空!')
                return

            if plugin_id in PLUGIN_CONFIGS:
                sender.reply(f'插件ID [{plugin_id}] 已存在!')
                return

            new_config = {
                'bucket': bucket,
                'coin_key': coin_key,
                'name': name
            }

            try:
                custom_plugins = json.loads(middleware.bucketGet('dd_sign_config', 'custom_plugins') or '{}')
            except json.JSONDecodeError:
                custom_plugins = {}

            custom_plugins[plugin_id] = new_config

            try:
                middleware.bucketSet('dd_sign_config', 'custom_plugins', json.dumps(custom_plugins))
                PLUGIN_CONFIGS[plugin_id] = new_config

                msg = f"""添加成功!
插件ID: {plugin_id}
存储桶: {bucket}
积分键名: {coin_key}
显示名称: {name}

提示: 新配置已生效,可以通过"积分查询"查看"""
                sender.reply(msg)

            except Exception as e:
                sender.reply(f'保存配置失败: {str(e)}')

        except Exception as e:
            sender.reply(f'添加失败: {str(e)}\n请检查输入格式是否正确')
    else:
        sender.reply('输入错误!')


# ==================== Recharge Functions ====================

def recharge():
    """QR code recharge (waitPay)"""
    if not RECHARGE_CONFIG['zsm']:
        sender.reply('未配置赞赏码,请联系管理员!')
        return

    try:
        rate = int(RECHARGE_CONFIG['rate'])
    except:
        rate = 100

    current = get_user_points(userid)
    msg = f"""========充值积分========
当前积分: {current}🌸
兑换比例: 1元 = {rate}积分
======================"""

    sender.reply(msg)
    sender.replyImage(RECHARGE_CONFIG['zsm'])

    ddzf = sender.waitPay("q", 100 * 1000)

    try:
        if not ddzf or str(ddzf) == 'q':
            sender.reply('已取消支付')
            return

        try:
            if isinstance(ddzf, str):
                ddzf = json.loads(ddzf)
        except json.JSONDecodeError:
            sender.reply('支付结果解析失败，如果您已完成支付，请联系管理员')
            return

        try:
            if ddzf.get('Type') in ('微信赞赏', '微信收款'):
                paid_amount = float(ddzf.get('Money', 0))
                pay_time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                payer_name = ddzf.get('FromName', '')
            elif ddzf.get('Money'):
                paid_amount = float(ddzf.get('Money', 0))
                pay_time = ddzf.get('Time', '').replace('T', ' ').split('.')[0]
                payer_name = ddzf.get('FromName', '')
            elif ddzf.get('money'):
                paid_amount = float(ddzf.get('money', 0))
                pay_time = ddzf.get('time', '').replace('T', ' ').split('.')[0]
                payer_name = ddzf.get('fromName', '')
            else:
                sender.reply('不支持的支付消息格式')
                return

            if not pay_time:
                pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if paid_amount <= 0:
                sender.reply('支付金额无效')
                return

        except (ValueError, TypeError) as e:
            sender.reply(f"支付金额格式错误: {str(e)}")
            return

        points = int(paid_amount * rate)
        recharge_id = f"R_{int(time.time())}_{userid}"

        add_user_points(userid, points)

        middleware.bucketSet(RECHARGE_BUCKET, recharge_id, json.dumps({
            'user': userid,
            'amount': paid_amount,
            'points': points,
            'paid_amount': paid_amount,
            'time': int(time.time()),
            'pay_time': pay_time,
            'payer_name': payer_name,
            'status': 'success'
        }))

        msg = f"""=====充值成功=====
订单号: {recharge_id}
充值金额: {paid_amount}元
获得积分: {points}
当前积分: {get_user_points(userid)}
支付时间: {pay_time}"""
        if payer_name:
            msg += f"\n支付用户: {payer_name}"
        sender.reply(msg)

    except Exception as e:
        sender.reply("处理支付结果时出错，如果您已完成支付，请联系管理员")


def check_recharge(recharge_id):
    """Check recharge status"""
    data = middleware.bucketGet('dd_sign_recharge', recharge_id)
    if not data:
        return '订单不存在'

    try:
        data = json.loads(data)
        status = {
            'pending': '待审核',
            'success': '已完成',
            'failed': '已取消'
        }.get(data['status'], '未知')

        msg = f"""充值详情:
订单号: {recharge_id}
充值金额: {data['amount']}元
可得积分: {data['points']}
状态: {status}"""
        return msg
    except:
        return '查询失败'


def handle_recharge():
    """Admin recharge management"""
    if not sender.isAdmin():
        sender.reply('您没有权限!')
        return

    msg = """========充值管理========
1、查看待审核
2、审核通过
3、取消订单
======================
回复序号,退出【q】！"""

    sender.reply(msg)
    choice = sender.input(120000, 1, False)

    if choice == 'q':
        sender.reply('已退出')
        return

    if choice == '1':
        pending = []
        for key in middleware.bucketAllKeys('dd_sign_recharge'):
            try:
                data = json.loads(middleware.bucketGet('dd_sign_recharge', key))
                if data['status'] == 'pending':
                    pending.append((key, data))
            except:
                continue

        if not pending:
            sender.reply('暂无待审核订单!')
            return

        msg = '========待审核========\n'
        for recharge_id, data in pending:
            msg += f"""订单号: {recharge_id}
用户: {data['user']}
金额: {data['amount']}元
积分: {data['points']}\n"""
        sender.reply(msg)

    elif choice == '2':
        sender.reply('请输入订单号:')
        recharge_id = sender.input(120000, 1, False)

        try:
            data = json.loads(middleware.bucketGet('dd_sign_recharge', recharge_id))
            if data['status'] != 'pending':
                sender.reply('订单状态错误!')
                return

            data['status'] = 'success'
            middleware.bucketSet('dd_sign_recharge', recharge_id, json.dumps(data))
            sender.reply('审核通过!')

            middleware.push('wx', '', data['user'], '',
                f"""充值成功!
订单号: {recharge_id}
充值金额: {data['amount']}元
获得积分: {data['points']}
当前积分: {get_user_points(data['user'])}""")

        except:
            sender.reply('操作失败!')

    elif choice == '3':
        sender.reply('请输入订单号:')
        recharge_id = sender.input(120000, 1, False)

        try:
            data = json.loads(middleware.bucketGet('dd_sign_recharge', recharge_id))
            if data['status'] != 'pending':
                sender.reply('订单状态错误!')
                return

            data['status'] = 'failed'
            middleware.bucketSet('dd_sign_recharge', recharge_id, json.dumps(data))
            sender.reply('已取消订单!')

            middleware.push('wx', '', data['user'], '',
                f"""充值已取消!
订单号: {recharge_id}
充值金额: {data['amount']}元""")

        except:
            sender.reply('操作失败!')
    else:
        sender.reply('输入错误!')


# ==================== MaPay Recharge (via vorto_utils) ====================

def ma_pay_recharge():
    """MaPay recharge using vorto_utils.MaPayClient"""
    pay_config = vorto_utils.get_pay_config()
    if not pay_config['ma_pay_switch']:
        return False

    pay_types = pay_config['pay_types']
    if not pay_types:
        sender.reply("❌ 未配置码支付方式，请联系管理员在Vorto初始化中填写")
        return False

    try:
        rate = int(RECHARGE_CONFIG['rate'])
    except:
        rate = 100

    sender.reply(f"积分比例：1元 = {rate}积分\n请输入要充值的金额(元)，输入q退出:")
    amount_str = sender.input(120000, 1, False)

    if not amount_str or amount_str.lower() == 'q':
        sender.reply('已取消充值')
        return True

    try:
        amount = round(float(amount_str), 2)
        if amount <= 0:
            sender.reply('充值金额必须大于0')
            return True
    except ValueError:
        sender.reply('请输入有效的金额')
        return True

    current_points = get_user_points(userid)
    will_get_points = int(amount * rate)

    # Select payment type
    type_list = list(pay_types.items())
    if len(type_list) == 1:
        selected_key, selected_name = type_list[0]
        sender.reply(
            f"=====充值信息=====\n"
            f"当前积分: {current_points}\n"
            f"充值金额: {amount}元\n"
            f"充值积分: {will_get_points}\n"
            f"=================="
        )
    else:
        options = "\n".join([f"[{i+1}] {name}" for i, (_, name) in enumerate(type_list)])
        sender.reply(
            f"=====充值信息=====\n"
            f"当前积分: {current_points}\n"
            f"充值积分: {will_get_points}\n"
            f"==================\n"
            f"选择支付方式:\n{options}\n"
            f"回复数字选择，输入q取消"
        )
        choice = sender.input(120000, 1, False)
        if not choice or choice.lower() == 'q':
            sender.reply('已取消充值')
            return True
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(type_list):
                selected_key, selected_name = type_list[idx]
            else:
                sender.reply('选择无效')
                return True
        except ValueError:
            sender.reply('输入无效')
            return True

    out_trade_no = f"MP{int(time.time())}{userid}"

    try:
        mapay = vorto_utils.MaPayClient()
        order = mapay.create_order(amount, selected_key, out_trade_no, f"{senderID}-积分充值-{amount}", userid)

        if order.get('error'):
            sender.reply(f"❌ 创建订单失败: {order.get('error')}")
            return True

        pay_url = order.get('pay_url')
        qr_url = vorto_utils.generate_qrcode_url(pay_url)

        sender.reply(f'请使用【{selected_name}】扫描下方二维码完成支付:')
        sender.replyImage(qr_url)
        sender.reply('⏰ 5分钟内完成支付\n输入"q"可取消')

        start_time = time.time()
        timeout = 300

        while time.time() - start_time < timeout:
            user_input = sender.input(5000, 1, False)
            if user_input and user_input.lower() == 'q':
                sender.reply("✅ 已取消支付")
                return True
            if mapay.is_paid(out_trade_no):
                points = int(amount * rate)
                add_user_points(userid, points, "码支付充值", username)

                recharge_id = f"MP_{int(time.time())}_{userid}"
                middleware.bucketSet('dd_sign_recharge', recharge_id, json.dumps({
                    'user': userid,
                    'amount': amount,
                    'points': points,
                    'paid_amount': amount,
                    'time': int(time.time()),
                    'pay_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'status': 'success'
                }))

                sender.reply(
                    f"=====充值成功=====\n"
                    f"订单号: {out_trade_no}\n"
                    f"充值金额: {amount}元\n"
                    f"获得积分: {points}\n"
                    f"当前积分: {get_user_points(userid)}\n"
                    f"=================="
                )
                return True

        sender.reply("❌ 支付超时")
        return True

    except Exception as e:
        sender.reply(f"❌ 支付异常: {str(e)}")
        return True


# ==================== Init Custom Plugins ====================

try:
    custom_plugins = json.loads(middleware.bucketGet('dd_sign_config', 'custom_plugins') or '{}')
    PLUGIN_CONFIGS.update(custom_plugins)
except:
    pass


# ==================== Main Logic ====================

message = sender.getMessage()

if message == '签到' and signswitch == 'true':
    sign()

elif message == '系统管理':
    system()

elif message in ('积分查询', '查询积分'):
    query_points()

elif 'DD_' in message:
    success, msg = use_card(message)
    sender.reply(msg)

elif imtype == 'fake':
    for key in middleware.bucketAllKeys('dd_state'):
        middleware.bucketDel('dd_state', key)

elif message in ('充值积分', '积分充值'):
    pay_config = vorto_utils.get_pay_config()
    if pay_config['ma_pay_switch']:
        if not ma_pay_recharge():
            recharge()
    else:
        recharge()

elif message.startswith('R_'):
    msg = check_recharge(message)
    sender.reply(msg)
else:
    sender.setContinue()
