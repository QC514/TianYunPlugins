#[pin:false]
#[public:true]
#[disable:false]
# [rule: ^(签到|系统管理|积分查询|查询积分|充值积分|积分充值|DD_.*|R_.*|卡密:DD_.*|更新配置)$]
# [cron: 0 0 0 * * *]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [author: linzixuan]
# [title: 卡密系统]
# [icon: https://i.miji.bid/2025/06/27/4aff8aa2b4f09d0d3f3bd97379836265.png]
# [class: 工具类]
# [version: 5.7]
# [price: 0]
# [description: 签到获取积分,积分可用于兑换各类服务。命令:签到丨积分查询丨充值积分丨系统管理(管理员)<br>支持卡密充值,收款码充值,支持积分管理,支持服务积分设置<br>更新：适配BOGW和GW框架收款<br>修正管理系统，支持用户自定义化！<br>区分签到积分与充值积分<br>5.1更新：支持对接码支付！<br>5.2更新：支持新版收款码和赞赏码充值，优化数据桶构造，新增指令：'更新配置'，用途：迁移旧数据桶至新数据桶！]
# [param: {"required":true,"key":"dd_sign_config.sign","bool":true,"placeholder":"","name":"签到功能","desc":"勾选可签到，默认关闭，需要先关闭奥特曼自带的签到功能！(用户系统里面)"}]
# [param: {"required":true,"key":"dd_sign_config.signcoin","bool":false,"placeholder":"默认:1-5 填写例:1-5","name":"积分区间","desc":"用户每次签到的积分区间"}]
# [param: {"required":true,"key":"dd_sign_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_sign_config.rate","bool":false,"placeholder":"默认:100 填写例:100","name":"兑换比例","desc":"1元=多少积分"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_switch","bool":true,"placeholder":"","name":"码支付功能","desc":"开启后可使用码支付进行充值"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_gateway","bool":false,"placeholder":"https://pay.xxxxx.com/","name":"码支付网关","desc":"支付网关地址，例如: https://pay.xxxxx.com/"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_pid","bool":false,"placeholder":"1001","name":"商户ID","desc":"支付平台的商户ID"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_key","bool":false,"placeholder":"89unJUB8HZ54Hj7x4nUj56HN4nUzUJ8i","name":"商户密钥","desc":"支付平台的商户密钥"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_type","bool":false,"placeholder":"alipay,wxpay,qqpay","name":"支付方式","desc":"支付方式，多个用英文逗号隔开，不填默认使用收银台模式"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_notify_url","bool":false,"placeholder":"https://your-domain.com/notify","name":"回调地址","desc":"支付成功回调地址，例如: https://your-domain.com/notify"}]


from datetime import datetime
import random
import middleware
import time
import json
import re
import hashlib  # 添加hashlib模块导入
import requests  # 使用requests库替代urllib

# 获取发送者信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
imtype = sender.getImtype()
username = sender.getUserName()

# 存储桶定义
CONFIG_BUCKET = 'dd_sign_config'  # 配置参数桶
SIGN_DATE_BUCKET = 'dd_sign_dates'  # 签到日期桶
POINTS_BUCKET = 'dd_sign_points'  # 用户积分桶
CARD_BUCKET = 'dd_sign_cards'  # 卡密桶
RECHARGE_BUCKET = 'dd_sign_recharge'  # 充值记录桶
PAY_ORDERS_BUCKET = 'dd_sign_orders'  # 支付订单桶

# 签到配置参数
signswitch = middleware.bucketGet(bucket=CONFIG_BUCKET, key='sign') or 'false'
signcoin = middleware.bucketGet(bucket=CONFIG_BUCKET, key='signcoin') or '1-5'

# 添加插件积分配置
PLUGIN_CONFIGS = {}
# 在PLUGIN_CONFIGS后添加支付配置
PAYMENT_CONFIG = {
    'zsm': middleware.bucketGet(CONFIG_BUCKET, 'zsm') or '',  # 赞赏码链接
    'rate': middleware.bucketGet(CONFIG_BUCKET, 'rate') or '100',  # 充值比例,默认1元=100积分
    # 码支付相关配置
    'ma_pay_switch': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_switch') or 'false',  # 码支付开关
    'ma_pay_gateway': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_gateway') or '',  # 支付网关
    'ma_pay_pid': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_pid') or '',  # 商户ID
    'ma_pay_key': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_key') or '',  # 商户密钥
    'ma_pay_type': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_type') or 'alipay,wxpay,qqpay',  # 支付方式，默认全部
    'ma_pay_notify_url': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_notify_url') or '',  # 回调地址
    'use_mapi': middleware.bucketGet(CONFIG_BUCKET, 'use_mapi') or 'true',  # 使用mapi接口，默认开启
    'pid': '',  # 将在后面初始化
    'key': '',  # 将在后面初始化
    'gateway': '',  # 将在后面初始化
}

# 同步配置到标准字段
PAYMENT_CONFIG['pid'] = PAYMENT_CONFIG['ma_pay_pid']
PAYMENT_CONFIG['key'] = PAYMENT_CONFIG['ma_pay_key']
PAYMENT_CONFIG['gateway'] = PAYMENT_CONFIG['ma_pay_gateway']

# 支付方式中文名称映射
PAY_TYPE_NAMES = {
    'alipay': '支付宝',
    'wxpay': '微信支付',
    'qqpay': 'QQ钱包',
}

def get_user_points(uid):
    """获取用户积分"""
    return int(middleware.bucketGet(POINTS_BUCKET, uid) or 0)

def add_user_points(uid, points, channel="", name=""):
    """增加用户积分"""
    current = int(middleware.bucketGet(POINTS_BUCKET, uid) or 0)
    middleware.bucketSet(POINTS_BUCKET, uid, str(current + points))
    return get_user_points(uid)

def deduct_user_points(uid, points, channel="", name=""):
    """扣除用户积分"""
    current = int(middleware.bucketGet(POINTS_BUCKET, uid) or 0)
    if current < points:
        return False
    middleware.bucketSet(POINTS_BUCKET, uid, str(current - points))
    return True

def sign():
    """签到功能"""
    today = str(datetime.now().date())
    
    # 使用锁键来控制并发
    lock_key = f'sign_lock_{userid}'
    
    # 检查是否存在锁，防止重复操作
    if middleware.bucketGet(CONFIG_BUCKET, lock_key):
        sender.reply('操作太频繁，请稍后再试~')
        return
        
    try:
        # 设置锁
        middleware.bucketSet(CONFIG_BUCKET, lock_key, '1')
        
        # 检查是否已经签到
        last_sign = middleware.bucketGet(SIGN_DATE_BUCKET, userid)
        if last_sign == today:
            sender.reply('你好,你今日已经签到过了哦~')
            return
            
        # 计算签到奖励
        min_coin, max_coin = map(int, signcoin.split('-'))
        coins = random.randint(min_coin, max_coin)
        
        # 增加积分
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
        # 释放锁
        middleware.bucketDel(CONFIG_BUCKET, lock_key)

def query_points():
    """查询积分"""
    msg = f"""=====积分查询=====
💰 总积分: {get_user_points(userid)}

🎯 可用插件及积分:"""

    # 遍历所有插件配置并显示积分值
    for plugin_id, config in PLUGIN_CONFIGS.items():
        try:
            coin_value = middleware.bucketGet(config['bucket'], config['coin_key'])
            if coin_value and coin_value != '0':  # 只显示有效的积分值
                msg += f"\n• {config['name']}: {coin_value}积分/月"
        except Exception as e:
            print(f"Error getting coin value for {plugin_id}: {str(e)}")  # 用于调试
            continue
            
    msg += """
==================
💡 发送"充值积分"可充值
=================="""
    
    sender.reply(msg)

def use_points(plugin_id, points):
    """使用积分"""
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

def generate_card(amount):
    """生成卡密"""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    card = 'DD_' + ''.join(random.choice(chars) for _ in range(12))
    middleware.bucketSet(CARD_BUCKET, card, str(amount))
    return card

def use_card(card):
    """使用卡密"""
    try:
        # 提取卡密格式
        card_match = re.search(r'(?:卡密:)?(DD_[A-Z0-9]{12})', card)
        if not card_match:
            return False, '卡密格式错误!'
        
        card = card_match.group(1)
        amount = middleware.bucketGet(CARD_BUCKET, card)
        
        # 调试信息
        print(f"卡密: {card}")
        print(f"获取到的金额: {amount}")
        
        if not amount:
            return False, '卡密不存在!'
        if amount == 'False':
            return False, '卡密已被使用!'
            
        try:
            amount = int(amount)
        except ValueError:
            try:
                # 尝试解析JSON格式
                card_info = json.loads(amount)
                return False, f'卡密已被{card_info["user"]}使用\n使用时间:{card_info["time"]}'
            except:
                return False, '卡密数据格式错误!'
            
        if amount <= 0:
            return False, '卡密面额错误!'
            
        current = add_user_points(userid, amount, "卡密充值", username)
        
        # 记录使用信息
        use_info = {
            'user': userid,
            'username': username,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'amount': amount
        }
        middleware.bucketSet(CARD_BUCKET, card, json.dumps(use_info))
        return True, f'充值成功!\n获得积分:{amount}\n当前积分:{current}'
        
    except Exception as e:
        print(f"充值过程出错: {str(e)}")  # 打印详细错误信息
        return False, f'充值失败: {str(e)}'

def system():
    """系统管理"""
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
9、释放常规支付锁
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
赞赏码: {'已配置' if PAYMENT_CONFIG['zsm'] else '未配置'}
兑换比例: 1元={PAYMENT_CONFIG['rate']}积分
MAPI接口: {'已启用' if PAYMENT_CONFIG['use_mapi'] == 'true' else '已禁用'}
码支付商户ID: {PAYMENT_CONFIG['ma_pay_pid'] or '未设置'}
码支付网关: {PAYMENT_CONFIG['ma_pay_gateway'] or '未设置'}
码支付回调地址: {PAYMENT_CONFIG['ma_pay_notify_url'] or '未设置'}

1、设置赞赏码
2、设置兑换比例
3、切换MAPI接口
4、设置码支付商户ID
5、设置码支付密钥
6、设置码支付网关
7、设置码支付回调地址
======================
回复序号,退出【q】！"""
        sender.reply(msg)
        subchoice = sender.input(120000, 1, False)

        if subchoice == '1':
            sender.reply('请发送赞赏码图片链接:')
            zsm = sender.input(120000, 1, False)
            middleware.bucketSet('dd_sign_config', 'zsm', zsm)
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
                sender.reply('设置成功!')
            except:
                sender.reply('输入错误!')

        elif subchoice == '3':
            current = PAYMENT_CONFIG['use_mapi']
            new_value = 'false' if current == 'true' else 'true'
            middleware.bucketSet('dd_sign_config', 'use_mapi', new_value)
            sender.reply(f'MAPI接口已{"启用" if new_value == "true" else "禁用"}!')
            # 更新运行时配置
            PAYMENT_CONFIG['use_mapi'] = new_value

        elif subchoice == '4':
            sender.reply('请输入码支付商户ID:')
            pid = sender.input(120000, 1, False)
            middleware.bucketSet('dd_sign_config', 'ma_pay_pid', pid)
            PAYMENT_CONFIG['ma_pay_pid'] = pid
            PAYMENT_CONFIG['pid'] = pid
            sender.reply('设置成功!')

        elif subchoice == '5':
            sender.reply('请输入码支付密钥:')
            key = sender.input(120000, 1, False)
            middleware.bucketSet('dd_sign_config', 'ma_pay_key', key)
            PAYMENT_CONFIG['ma_pay_key'] = key
            PAYMENT_CONFIG['key'] = key
            sender.reply('设置成功!')

        elif subchoice == '6':
            sender.reply('请输入码支付网关地址(例如: https://pay.domain.com):')
            gateway = sender.input(120000, 1, False)
            middleware.bucketSet('dd_sign_config', 'ma_pay_gateway', gateway)
            PAYMENT_CONFIG['ma_pay_gateway'] = gateway
            PAYMENT_CONFIG['gateway'] = gateway
            sender.reply('设置成功!')

        elif subchoice == '7':
            sender.reply('请输入码支付回调地址(例如: https://your-domain.com/notify):')
            notify_url = sender.input(120000, 1, False)
            if notify_url:
                middleware.bucketSet('dd_sign_config', 'ma_pay_notify_url', notify_url)
                PAYMENT_CONFIG['ma_pay_notify_url'] = notify_url
                sender.reply('设置成功!')
            else:
                sender.reply('回调地址不能为空!')
    elif choice == '7':
        msg = """========服务积分设置========
当前支持的服务:"""

        # 从配置中动态生成服务列表
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
        
        # 构建service_map
        service_map = {str(idx): service_id for idx, service_id, _ in service_list}
        
        subchoice = sender.input(120000, 1, False)
        if subchoice == 'q':
            return
            
        if subchoice == 'a':
            # 新增服务
            sender.reply("""请按以下格式输入服务信息:
服务ID,存储桶名,积分键名,显示名称
示例: myplugin,dd_myplugin,coin,我的插件""")
            
            service_info = sender.input(120000, 1, False)
            try:
                service_id, bucket, coin_key, name = [x.strip() for x in service_info.split(',')]
                
                # 验证服务ID是否已存在
                if service_id in PLUGIN_CONFIGS:
                    sender.reply(f'服务ID [{service_id}] 已存在!')
                    return
                    
                # 添加新服务配置
                new_config = {
                    'bucket': bucket,
                    'coin_key': coin_key,
                    'name': name
                }
                
                # 保存到自定义配置
                custom_plugins = json.loads(middleware.bucketGet('dd_sign_config', 'custom_plugins') or '{}')
                custom_plugins[service_id] = new_config
                middleware.bucketSet('dd_sign_config', 'custom_plugins', json.dumps(custom_plugins))
                
                # 更新运行时配置
                PLUGIN_CONFIGS[service_id] = new_config
                
                sender.reply(f'成功添加服务: {name}')
                
            except ValueError:
                sender.reply('输入格式错误!')
                return
                
        elif subchoice == 'd':
            # 删除服务
            sender.reply('请输入要删除的服务序号:')
            del_idx = sender.input(120000, 1, False)
            
            if del_idx not in service_map:
                sender.reply('序号无效!')
                return
                
            service_id = service_map[del_idx]
            service_name = PLUGIN_CONFIGS[service_id]['name']
            
            # 从配置中删除
            custom_plugins = json.loads(middleware.bucketGet('dd_sign_config', 'custom_plugins') or '{}')
            if service_id in custom_plugins:
                del custom_plugins[service_id]
                middleware.bucketSet('dd_sign_config', 'custom_plugins', json.dumps(custom_plugins))
                
                # 更新运行时配置
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
            # 验证输入格式
            parts = [x.strip() for x in config_input.split(',')]
            if len(parts) != 4:
                sender.reply('配置格式错误!\n请按照: 插件ID,存储桶名,积分键名,显示名称')
                return
            
            plugin_id, bucket, coin_key, name = parts
            
            # 验证必填项
            if not all([plugin_id, bucket, coin_key, name]):
                sender.reply('所有字段都不能为空!')
                return
            
            # 验证插件ID是否已存在
            if plugin_id in PLUGIN_CONFIGS:
                sender.reply(f'插件ID [{plugin_id}] 已存在!')
                return
            
            # 构建新的插件配置
            new_config = {
                'bucket': bucket,
                'coin_key': coin_key,
                'name': name
            }
            
            # 读取现有的自定义配置
            try:
                custom_plugins = json.loads(middleware.bucketGet('dd_sign_config', 'custom_plugins') or '{}')
            except json.JSONDecodeError:
                custom_plugins = {}
            
            # 添加新配置
            custom_plugins[plugin_id] = new_config
            
            # 保存更新后的配置
            try:
                middleware.bucketSet('dd_sign_config', 'custom_plugins', json.dumps(custom_plugins))
                
                # 更新运行时配置
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
    elif choice == '9':
        # 释放常规支付锁（码支付不使用支付锁）
        pay_lock_key = 'recharge_lock'
        if middleware.bucketDel('dd_sign_config', pay_lock_key):
            sender.reply('常规支付锁已释放!')
        else:
            sender.reply('当前没有常规支付锁!')
    else:
        sender.reply('输入错误!')

def send_payment_message(amount):
    """发送收款消息"""
    # 先尝试BORW格式
    msg_borw = {
        "type": "pay",
        "data": {
            "price": amount,
            "title": "积分充值",
            "payType": "wechat"
        }
    }
    sender.reply(json.dumps(msg_borw))
    
    # 再发送GW格式
    msg_gw = {
        "type": "wxpay",
        "data": {
            "amount": amount,
            "desc": "积分充值"
        }
    }
    sender.reply(json.dumps(msg_gw))
    
    # 最后发送普通收款码
    sender.reply(f"请扫码赞赏,完成后发送赞赏金额:")
    sender.reply(PAYMENT_CONFIG['zsm'])

def recharge():
    """充值积分 - 常规支付（使用支付锁）"""
    if not PAYMENT_CONFIG['zsm']:
        sender.reply('未配置赞赏码,请联系管理员!')
        return

    # 常规支付使用支付锁，防止多用户同时支付冲突
    pay_lock_key = 'recharge_lock'
    lock_info = middleware.bucketGet(CONFIG_BUCKET, pay_lock_key)
    if lock_info:
        try:
            lock_data = json.loads(lock_info)
            # 检查锁是否过期(2分钟)
            if time.time() - lock_data['time'] < 120:  # 改为120秒
                sender.reply('当前有其他用户正在支付中，请稍后再试!')
                return
        except:
            pass
    
    # 设置支付锁
    lock_data = {
        'user': userid,
        'time': int(time.time())
    }
    middleware.bucketSet(CONFIG_BUCKET, pay_lock_key, json.dumps(lock_data))
        
    try:
        rate = int(PAYMENT_CONFIG['rate'])
    except:
        rate = 100
        
    current = get_user_points(userid)
    msg = f"""========充值积分========
当前积分: {current}🌸
兑换比例: 1元 = {rate}积分
======================"""
    
    sender.reply(msg)
    
    # 直接发送收款码
    sender.replyImage(PAYMENT_CONFIG['zsm'])
    
    # 等待支付结果
    ddzf = sender.waitPay("q", 100 * 1000)
    
    try:
        if not ddzf or str(ddzf) == 'q':
            sender.reply('已取消支付')
            return
            
        # 尝试解析支付结果
        try:
            if isinstance(ddzf, str):
                ddzf = json.loads(ddzf)
        except json.JSONDecodeError:
            sender.reply('支付结果解析失败，如果您已完成支付，请联系管理员')
            return
            
        # 支持多种收款消息格式
        try:
            # 新格式1: 微信赞赏
            if ddzf.get('Type') == '微信赞赏':
                paid_amount = float(ddzf.get('Money', 0))
                pay_time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                payer_name = ddzf.get('FromName', '')
            # 新格式2: 微信收款
            elif ddzf.get('Type') == '微信收款':
                paid_amount = float(ddzf.get('Money', 0))
                pay_time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                payer_name = ddzf.get('FromName', '')
            # 旧格式1: BORW格式
            elif ddzf.get('Money'):
                paid_amount = float(ddzf.get('Money', 0))
                pay_time = ddzf.get('Time', '').replace('T', ' ').split('.')[0]
                payer_name = ddzf.get('FromName', '')
            # 旧格式2: GW格式
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
        
        # 生成订单号
        recharge_id = f"R_{int(time.time())}_{userid}"
        
        # 更新用户积分
        add_user_points(userid, points)
        
        # 记录充值订单
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
        sender.reply(f"处理支付结果时出错，如果您已完成支付，请联系管理员")
        print(f"支付处理错误: {str(e)}")  # 记录详细错误信息到日志
    finally:
        # 释放支付锁
        middleware.bucketDel(CONFIG_BUCKET, pay_lock_key)

def check_recharge(recharge_id):
    """查询充值状态"""
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
    """处理充值申请"""
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
        # 获取待审核订单
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
                
            # 更新订单状态
            data['status'] = 'success'
            middleware.bucketSet('dd_sign_recharge', recharge_id, json.dumps(data))
            
            sender.reply('审核通过!')
            
            # 通知用户
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

            # 更新订单状态
            data['status'] = 'failed'
            middleware.bucketSet('dd_sign_recharge', recharge_id, json.dumps(data))
            
            sender.reply('已取消订单!')
            
            # 通知用户
            middleware.push('wx', '', data['user'], '',
                f"""充值已取消!
订单号: {recharge_id}
充值金额: {data['amount']}元""")
                
        except:
            sender.reply('操作失败!')
    else:
        sender.reply('输入错误!')

# 在初始化时加载自定义插件配置
try:
    custom_plugins = json.loads(middleware.bucketGet('dd_sign_config', 'custom_plugins') or '{}')
    PLUGIN_CONFIGS.update(custom_plugins)
except:
    pass



# 添加MD5计算函数
def calculate_md5(text):
    """计算字符串的MD5值"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# 添加HTTP请求函数
def http_request(url, data=None, method='GET'):
    """发送HTTP请求
    
    Args:
        url: 请求地址
        data: POST请求数据，字典格式
        method: 请求方法，GET或POST
        
    Returns:
        响应内容，字符串格式
    """
    try:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        if method == 'POST' and data:
            response = requests.post(url, data=data, headers=headers, timeout=10)
        else:
            response = requests.get(url, timeout=10)
            
        return response.text
    except Exception as e:
        print(f"HTTP请求错误: {str(e)}")
        return None

# 从响应中提取重定向URL
def extract_redirect_url(html_content):
    """从HTML内容中提取location.href的值"""
    if not html_content:
        return None
        
    # 使用正则表达式匹配location.href = "URL"格式
    match = re.search(r'location\.href\s*=\s*[\'"]([^\'"]+)[\'"]', html_content)
    if match:
        return match.group(1)
    return None


# 添加生成二维码函数
def generate_qrcode(url):
    """生成二维码图片

    Args:
        url: 要生成二维码的URL

    Returns:
        str: 二维码API的URL
    """
    try:
        # 使用 qrtool.cn 的API生成二维码，使用safe参数确保正确编码
        from urllib.parse import quote
        encoded_url = quote(url, safe='')
        api_url = f"https://api.qrtool.cn/?text={encoded_url}"
        return api_url
    except Exception as e:
        # 如果导入失败，使用requests的quote方法
        try:
            encoded_url = requests.utils.quote(url, safe='')
            api_url = f"https://api.qrtool.cn/?text={encoded_url}"
            return api_url
        except Exception as e2:
            print(f"生成二维码失败: {str(e2)}")
            return None

# 码支付API类
class MaPay_Api:
    def __init__(self, config):
        """初始化码支付API类

        Args:
            config (dict): 配置信息，包含以下字段:
                - gateway: 支付网关地址，例如 https://mpay.vorto.cn
                - pid: 商户ID
                - key: 商户密钥
                - pay_type: 支付方式，多个用逗号分隔
        """
        self.config = config
        self.pay_type_names = {
            'alipay': '支付宝',
            'wxpay': '微信支付',
            'qqpay': 'QQ钱包',
        }

    def calculate_md5(self, text):
        """计算字符串的MD5值"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
        
    def sort_dict_by_key(self, data):
        """对字典按照键名排序"""
        return dict(sorted(data.items(), key=lambda x: x[0]))

    def create_payment(self, amount, out_trade_no, name, user_id, pay_type=None, sitename=""):
        """创建支付订单 (mapi接口)

        Args:
            amount: 支付金额
            out_trade_no: 商户订单号
            name: 商品名称
            user_id: 用户ID (会传递到param参数)
            pay_type: 支付方式，如果为None则使用配置中的默认支付方式
            sitename: 网站名称 (可选)

        Returns:
            (success, pay_data, msg): 是否成功、支付数据、消息
        """
        try:
            # 获取支付方式
            if pay_type is None:
                pay_types = [p.strip() for p in self.config['pay_type'].split(',') if p.strip()]
                if not pay_types:
                    pay_types = ["alipay", "wxpay", "qqpay"]
                pay_type = pay_types[0]  # 默认使用第一个支付方式

            # 构造支付参数
            params = {
                'pid': self.config['pid'],
                'type': pay_type,
                'out_trade_no': out_trade_no,
                'name': name,
                'money': str(amount),
                'sitename': sitename,
                'param': user_id
            }

            # 添加回调地址
            if self.config.get('ma_pay_notify_url'):
                params['notify_url'] = self.config['ma_pay_notify_url']

            # 移除空值
            params = {k: v for k, v in params.items() if v}

            # 按照ASCII码排序参数
            sorted_params = self.sort_dict_by_key(params)

            # 拼接成key=value&key=value格式
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])

            # 添加密钥进行MD5签名
            sign = self.calculate_md5(sign_str + self.config['key']).lower()

            # 添加签名到参数
            params['sign'] = sign
            params['sign_type'] = 'MD5'

            # 构建mapi接口URL
            mapi_url = self.config['gateway']
            if mapi_url.endswith('/'):
                mapi_url = mapi_url[:-1]
            mapi_url = f"{mapi_url}/mapi.php"

            # 发送POST请求
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(mapi_url, data=params, headers=headers, timeout=10)

            if response.status_code != 200:
                return False, None, f"创建支付订单失败，HTTP状态码: {response.status_code}"

            # 解析响应
            try:
                result = response.json()
                #sender.reply(f"创建支付订单响应: {result}")
            except:
                return False, None, "创建支付订单失败，返回数据格式错误"

            # 判断返回结果
            code = result.get('code', 0)
            msg = result.get('msg', '未知状态')

            if code == 1:  # 码支付API返回的成功状态码是1
                # 支付成功，返回支付数据
                return True, result, msg
            else:
                return False, None, msg

        except Exception as e:
            return False, None, f"创建订单失败: {str(e)}"

    def query_order(self, out_trade_no=None, trade_no=None):
        """查询订单状态

        Args:
            out_trade_no: 商户订单号
            trade_no: 系统订单号（二选一传入即可）

        Returns:
            (success, data, msg): 是否成功、订单数据、消息
        """
        try:
            # 构建查询接口URL - 根据文档格式
            query_url = self.config['gateway']
            if query_url.endswith('/'):
                query_url = query_url[:-1]

            # 根据文档，查询接口路径应该是 /xpay/epay/api.php
            if '/xpay/epay/api.php' not in query_url:
                query_url = f"{query_url}/xpay/epay/api.php"

            # 构建请求参数 - 根据文档格式
            params = {
                "act": "order",
                "pid": self.config['pid'],
                "key": self.config['key']
            }

            # 添加订单号参数（二选一）
            if trade_no:
                params["trade_no"] = trade_no
            elif out_trade_no:
                params["out_trade_no"] = out_trade_no
            else:
                return False, None, "必须提供商户订单号或系统订单号"

            # 打印调试信息
            print(f"查询订单URL: {query_url}")
            print(f"查询参数: {params}")

            # 发送GET请求
            response = requests.get(query_url, params=params, timeout=10)

            print(f"响应状态码: {response.status_code}")
            #sender.reply(f"响应内容: {response.text[:500]}")  # 只打印前500字符

            if response.status_code != 200:
                return False, None, f"查询订单失败，HTTP状态码: {response.status_code}"

            # 解析响应
            try:
                result = response.json()
            except:
                # 如果JSON解析失败，尝试解析文本响应
                try:
                    result = response.text
                    return False, None, f"查询订单失败，返回数据格式错误: {result}"
                except:
                    return False, None, "查询订单失败，返回数据格式错误"

            # 判断返回结果 - 根据文档，成功状态码是1
            code = result.get('code', 0)
            msg = result.get('msg', '未知状态')

            if code == 1:  # 根据文档，成功状态码是1
                # 查询成功，返回订单数据
                # 检查订单状态，根据文档status字段：1为支付成功，0为未支付
                order_status = result.get('status')
                if order_status == 1:  # 1表示支付成功
                    return True, result, "支付成功"
                else:
                    return True, result, "订单未支付"
            else:
                return False, None, msg

        except Exception as e:
            return False, None, f"查询订单异常: {str(e)}"



# 通过查询订单状态检测支付状态的函数（替代回调接口）
def poll_mapi_payment_status(out_trade_no, max_tries=30):
    """通过查询订单状态检测支付状态 - 不依赖回调接口，主动查询订单状态

    Args:
        out_trade_no: 商户订单号
        max_tries: 最大尝试次数（每次等待5秒）

    Returns:
        (is_paid, msg, data): 是否支付成功、消息和数据
    """
    # 创建MaPay_Api实例用于查询订单
    ma_pay_api = MaPay_Api(PAYMENT_CONFIG)

    for i in range(max_tries):
        try:
            # 查询订单状态 - 使用商户订单号
            success, data, msg = ma_pay_api.query_order(out_trade_no=out_trade_no)
            #sender.reply(f"查询订单状态: {success}, {data}, {msg}")

            # 如果查询成功且订单已支付
            if success and isinstance(data, dict) and data.get('status') == 1:
                return True, "支付成功", data

            # 等待用户输入或超时
            result = sender.listen(5000)  # 等待5秒
            if result == 'q':
                return False, "用户取消查询", None

        except Exception as e:
            # 查询出错，继续尝试
            print(f"查询订单状态出错: {str(e)}")

    return False, "查询超时，订单可能尚未支付", None

# 修改码支付功能，使用mapi接口和查询订单状态
def ma_pay_recharge():
    """码支付充值功能 - 不使用支付锁，支持多用户同时支付"""
    # 检查配置是否完整
    if not (PAYMENT_CONFIG['ma_pay_gateway'] and PAYMENT_CONFIG['ma_pay_pid'] and PAYMENT_CONFIG['ma_pay_key']):
        sender.reply('码支付配置不完整，请联系管理员!')
        return False

    # 确保新旧字段同步
    PAYMENT_CONFIG['pid'] = PAYMENT_CONFIG['ma_pay_pid']
    PAYMENT_CONFIG['key'] = PAYMENT_CONFIG['ma_pay_key']
    PAYMENT_CONFIG['gateway'] = PAYMENT_CONFIG['ma_pay_gateway']

    # 码支付不使用支付锁，支持多用户同时支付
    
    try:
        # 获取兑换比例
        try:
            rate = int(PAYMENT_CONFIG['rate'])
        except:
            rate = 100
            
        # 询问充值金额
        sender.reply(f"""
积分比例：1元 = {rate}积分
请输入要充值的金额(元)，输入q退出:""")
        amount_str = sender.input(120000, 1, False)
        
        # 退出充值
        if amount_str.lower() == 'q':
            sender.reply('已取消充值')
            return True
            
        # 验证金额
        try:
            amount = float(amount_str)
            if amount <= 0:
                sender.reply('充值金额必须大于0')
                return True
        except ValueError:
            sender.reply('请输入有效的金额')
            return True
            
        # 保留两位小数
        amount = round(amount, 2)
        
        # 生成商户订单号
        out_trade_no = f"MP{int(time.time())}{userid}"
        
        # 解析支付方式
        pay_types_str = PAYMENT_CONFIG['ma_pay_type'].strip()
        if not pay_types_str:
            pay_types_str = "alipay,wxpay,qqpay"  # 默认支付方式
            
        pay_types = [p.strip() for p in pay_types_str.split(',') if p.strip()]
        
        # 选择支付方式
        selected_type = ""
        if len(pay_types) == 1:
            # 只有一种支付方式
            selected_type = pay_types[0]
            
            # 获取当前积分信息
            current_points = get_user_points(userid)
            # 计算将获得的积分
            will_get_points = int(amount * rate)
            # 计算充值后总积分
            total_after = current_points + will_get_points
            
            # 显示充值信息
            sender.reply(f"""===== 充值信息 =====
当前积分: {current_points}
充值金额: {amount}元
充值后总积分: {total_after}""")
        else:
            # 多种支付方式，让用户选择
            pay_options_text = "\n".join([f"{i+1}. {PAY_TYPE_NAMES.get(t, t)}" for i, t in enumerate(pay_types)])
            
            # 获取当前积分信息
            current_points = get_user_points(userid)
            # 计算将获得的积分
            will_get_points = int(amount * rate)
            # 计算充值后总积分
            total_after = current_points + will_get_points
            
            sender.reply(f"""===== 充值信息 =====
当前积分: {current_points}
充值积分: {will_get_points}
充值后总积分: {total_after}
=======================
请选择支付方式:
{pay_options_text}

请回复对应序号(1-{len(pay_types)})，或输入q取消:""")
            
            choice = sender.input(120000, 1, False)
            
            if choice.lower() == 'q':
                sender.reply('已取消充值')
                return True
                
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(pay_types):
                    selected_type = pay_types[choice_idx]
                else:
                    sender.reply('选择无效，已取消充值')
                    return True
            except ValueError:
                sender.reply('输入无效，已取消充值')
                return True
        
        # 打印配置信息以便调试
        config_debug = f"""当前配置信息：
gateway: {PAYMENT_CONFIG['gateway']}
pid: {PAYMENT_CONFIG['pid']}
key: {PAYMENT_CONFIG['key'][:4]}****
pay_type: {selected_type}
使用查询订单状态判断支付结果（不依赖回调）
"""
        print(config_debug)
        
        # 使用MAPI接口
        ma_pay_api = MaPay_Api(PAYMENT_CONFIG)
        
        # 创建支付订单
        try:
            success, result, msg = ma_pay_api.create_payment(
                amount=amount,
                out_trade_no=out_trade_no,
                name=f"{senderID}-积分充值-{str(amount)}",
                user_id=userid,
                pay_type=selected_type
            )
        except Exception as e:
            sender.reply(f'创建订单时出错: {str(e)}')
            return True
        
        if not success:
            # 检查是否是没有可用支付账号的错误，如果是则回退到默认收款码
            if "没有找到可用支付账号" in msg or "没有找到可用的" in msg:
                sender.reply(f'码支付暂不可用({msg})，切换到默认收款方式')
                return False  # 返回False触发回退到recharge()
            else:
                sender.reply(f'创建订单失败: {msg}')
                return True
            
        # 提取支付链接 - 只需要获取payurl
        payurl = result.get('payurl', '')

        if not payurl:
            sender.reply('获取支付链接失败')
            return True

        # 发送支付链接
        selected_type_name = PAY_TYPE_NAMES.get(selected_type, selected_type)

        # 直接使用原始支付链接生成二维码
        qrcode_api_url = generate_qrcode(payurl)
        if qrcode_api_url:
            # 尝试使用CQ码格式将图片嵌入到消息中
            if selected_type == "qqpay":
                pay_msg = f'请使用【{selected_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\nQQ支付打开图片若是黑屏，长按屏幕进行"识别二维码"即可！\n[CQ:image,file={qrcode_api_url}]'
            else:
                pay_msg = f'请使用【{selected_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\n[CQ:image,file={qrcode_api_url}]'
            sender.reply(pay_msg)
        else:
            # 如果二维码生成失败，直接发送原始支付链接
            sender.reply(f"二维码生成失败，请使用【{selected_type_name}】打开链接：\n{payurl}")
        
        # 轮询支付结果
        is_paid, msg, data = poll_mapi_payment_status(out_trade_no)
        
        if is_paid:
            # 支付成功，更新订单状态和用户积分
            points = int(amount * rate)
            add_user_points(userid, points, "码支付充值", username)
            
            # 记录充值订单
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
            
            # 发送成功消息
            success_msg = f"""=====充值成功=====
订单号: {out_trade_no}
充值金额: {amount}元
获得积分: {points}
当前积分: {get_user_points(userid)}
================"""
            sender.reply(success_msg)
        else:
            # 支付失败或超时
            sender.reply(f"支付未完成: {msg}")
        
        return True
        
    except Exception as e:
        sender.reply(f'创建订单失败: {str(e)}')
        return True
    # 码支付不使用支付锁，无需释放

# 主逻辑
message = sender.getMessage()

if message == '签到' and signswitch == 'true':
    sign()
    
elif message == '系统管理':
    system()
    
elif message == '积分查询' or message == '查询积分':
    query_points()
    
elif 'DD_' in message:  # 卡密充值
    success, msg = use_card(message)
    sender.reply(msg)

elif imtype == 'fake':
    # 清理状态
    for key in middleware.bucketAllKeys('dd_state'):
        middleware.bucketDel('dd_state', key)

elif message == '充值积分' or message == '积分充值':
    # 判断是否使用码支付
    if PAYMENT_CONFIG.get('ma_pay_switch', 'false').lower() == 'true':
        # 使用码支付
        if not ma_pay_recharge():
            recharge()
    else:
        recharge()
    
elif message.startswith('R_'):  # 查询充值
    msg = check_recharge(message)
    sender.reply(msg)
else:
    sender.setContinue()
