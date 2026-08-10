#[pin:false]
#[public:true]
#[title: 人工通知]
#[service:2661320550] 
#[disable: false] 
#[admin: false] 
#[rule: ^(人工|售后)$|^(回复)\s+([a-zA-Z0-9]{8})\s+(.+)$]  # 更新后的规则，支持管理员回复
#[priority: 0] 优先级，数字越大表示优先级越高
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[version: 1.0.3]版本号
#[author: sky2022]
#[icon: https://i.miji.bid/2025/06/27/ff2b2c997f5bf6e1ec52e97548c159c1.png]
#[price: 0]
#[description: 当用户需要人工帮助时通知管理员，支持管理员回复功能] 
#[param: {"required":true,"key":"dd_rg.notify","bool":false,"placeholder":"qq,wx","name":"管理员通知","desc":"设置接受管理员通知的渠道，如 qq,wx,tg  用英文逗号分割,不设置不推送"}]
#[param: {"required":false,"key":"dd_rg.admin_ids","bool":false,"placeholder":"123456,789012","name":"管理员ID列表","desc":"多个ID用逗号分隔，用于回复功能权限控制"}]

import middleware
import json
import time
import hashlib
import re
from datetime import datetime

def now13() -> int: 
    """获取13位时间戳"""
    return int(time.time() * 1000)

def is_admin(user_id: str) -> bool:
    """检查当前用户是否为管理员"""
    admin_ids = middleware.bucketGet('dd_rg', 'admin_ids') or ''
    if not admin_ids:
        return False
    admin_list = [aid.strip() for aid in admin_ids.split(',') if aid.strip()]
    return user_id in admin_list

def generate_request_id(user_id: str) -> str:
    """生成请求ID"""
    return hashlib.md5(f"{user_id}_{now13()}".encode()).hexdigest()[:8]

def save_user_request(request_id: str, user_id: str, platform: str, question: str, is_image: bool = False):
    """保存用户请求信息"""
    request_info = {
        "user_id": user_id,
        "platform": platform,
        "question": question,
        "is_image": is_image,
        "timestamp": now13(),
        "status": "pending"  # pending, replied
    }
    middleware.bucketSet('user_help_request', request_id, json.dumps(request_info, ensure_ascii=False))

def handle_user_request():
    """处理用户求助请求"""
    # 获取发送者信息
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    user = sender.getUserID()
    
    # 获取用户的来源渠道并标准化
    raw_platform = sender.getImtype()
    platform_map = {
        'qq': 'QQ',
        'wx': '微信',
        'tg': 'Telegram',
        'wb': '微博',
        'tb': '淘宝'
    }
    platform = platform_map.get(raw_platform, raw_platform.upper())
    
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 获取管理员通知配置
    notify = middleware.bucketGet('dd_rg', 'notify')
    
    if not notify:
        sender.reply("抱歉，暂时无法通知管理员，请稍后再试。")
        return
    
    # 检查是否有未处理的请求（防止重复提交）
    all_requests = middleware.bucketAll('user_help_request')
    if all_requests:
        for request_id, request_data in all_requests.items():
            try:
                request_info = json.loads(request_data)
                if (request_info.get("user_id") == user and 
                    request_info.get("status") == "pending"):
                    # 检查请求是否在30分钟内
                    if now13() - request_info.get("timestamp", 0) < 1800000:  # 30分钟
                        sender.reply(f"您已有待处理的求助请求（请求ID: {request_id}），请耐心等待管理员回复。\n如需补充信息，请直接回复此消息。")
                        return
                    else:
                        # 清理过期请求
                        middleware.bucketDel('user_help_request', request_id)
            except Exception:
                continue
    
    # 提示用户输入问题
    sender.reply("请描述您遇到的问题，我们会尽快为您解答:\n(可以发送文字或图片)")
    
    # 等待用户输入，超时时间设置为60秒
    user_input = sender.input(60000, 0, False)
    
    if not user_input:
        sender.reply("您没有输入问题，如需帮助请重新发送「人工」")
        return
    
    # 处理用户输入 - 检测多种图片格式
    is_image = ("[CQ:image" in user_input or 
                "[pic=" in user_input or 
                "image" in user_input.lower() or
                any(ext in user_input.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']))
    supplementary_input = ""
    
    # 询问是否需要补充信息
    if is_image:
        # 用户发送了图片，询问是否需要补充文字说明
        sender.reply("📸 已收到您的图片，是否需要补充文字说明？\n💡 请直接输入说明文字，或回复'不需要'跳过\n⏰ 30秒内有效")
        supplement = sender.input(30000, 0, False)
        if supplement and supplement.strip() and supplement.strip().lower() not in ["不需要", "不用", "跳过", "no"]:
            supplementary_input = supplement
            sender.reply("✅ 已添加文字说明")
    else:
        # 用户发送了文字，询问是否需要补充图片
        sender.reply("📝 已收到您的问题描述，是否需要补充相关图片？\n💡 请直接发送图片，或回复'不需要'跳过\n⏰ 30秒内有效")
        supplement = sender.input(30000, 0, False)
        if supplement and supplement.strip() and supplement.strip().lower() not in ["不需要", "不用", "跳过", "no"]:
            # 检测多种图片格式
            supplement_has_image = ("[CQ:image" in supplement or 
                                  "[pic=" in supplement or 
                                  "image" in supplement.lower() or
                                  any(ext in supplement.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']))
            if supplement_has_image:
                supplementary_input = supplement
                sender.reply("✅ 已添加补充图片")
            else:
                sender.reply("⚠️ 未检测到图片，将作为额外文字说明处理")
                supplementary_input = supplement
    
    # 合并主要内容和补充内容
    final_input = user_input
    has_supplement = False
    if supplementary_input:
        if is_image:
            final_input += "\n\n📝 补充文字说明:\n" + supplementary_input
        else:
            final_input += "\n\n📷 补充图片/信息:\n" + supplementary_input
        has_supplement = True
    
    # 检查最终内容是否包含图片 - 支持多种格式
    final_has_image = ("[CQ:image" in final_input or 
                      "[pic=" in final_input or 
                      "image" in final_input.lower() or
                      any(ext in final_input.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']))
    
    # 生成请求ID
    request_id = generate_request_id(user)
    
    # 保存用户请求信息
    save_user_request(request_id, user, platform, final_input, final_has_image)
    
    # 构造通知消息
    content_type = ""
    if is_image and has_supplement:
        content_type = "📷+📝 图片+文字说明"
    elif is_image:
        content_type = "📷 仅图片"
    elif final_has_image:
        content_type = "📝+📷 文字+图片说明"
    else:
        content_type = "📝 仅文字"
    
    msg = f"""🔔 ===用户求助请求===
⏰ 请求时间: {current_time}
👤 用户ID: {user}
🌐 来源平台: {platform}
📋 请求ID: {request_id}
📊 内容类型: {content_type}
📝 问题详情:
{final_input}

💬 回复格式：回复 {request_id} XXXXX
"""
    
    # 发送通知给管理员
    tsqd = notify.split(',')
    middleware.notifyMasters(msg, tsqd)
    
    
    # 回复用户
    submit_msg = f"""✅ 已成功提交求助请求
📋 请求ID：{request_id}
📊 内容类型：{content_type}
⏳ 管理员已收到通知，请耐心等待回复！"""
    sender.reply(submit_msg)

def handle_admin_reply():
    """处理管理员回复"""
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    admin_id = sender.getUserID()
    
    # 检查管理员权限
    if not is_admin(admin_id):
        sender.reply("🚫 您没有管理员权限")
        return
    
    msg = sender.getMessage()
    
    # 解析回复指令：回复 request_id 回复内容
    match = re.match(r'^回复\s+([a-zA-Z0-9]{8})\s+(.+)$', msg, re.DOTALL)
    if not match:
        # 显示待处理的求助请求
        all_requests = middleware.bucketAll('user_help_request')
        if not all_requests:
            sender.reply("📭 当前没有待处理的求助请求")
            return
        
        pending_requests = []
        for request_id, request_data in all_requests.items():
            try:
                request_info = json.loads(request_data)
                if request_info.get("status") == "pending":
                    request_time = time.strftime('%m-%d %H:%M', 
                                               time.localtime(request_info.get("timestamp", 0) / 1000))
                    question = request_info.get('question', '')
                    if len(question) > 30:
                        question = question[:30] + "..."
                    pending_requests.append(f"📋 {request_id} | 👤 {request_info.get('user_id')} | 🌐 {request_info.get('platform')} | ⏰ {request_time}\n📝 {question}")
            except Exception:
                continue
        
        if not pending_requests:
            sender.reply("📭 当前没有待处理的求助请求")
            return
        
        requests_list = '\n\n'.join(pending_requests)
        sender.reply(f"""🔔 ===待处理求助请求===

{requests_list}

💬 回复格式：
回复 请求ID XXXXX
""")
        return
    
    request_id = match.group(1)
    reply_content = match.group(2).strip()
    
    if not reply_content:
        sender.reply("❌ 回复内容不能为空")
        return
    
    # 查找用户请求
    request_data = middleware.bucketGet('user_help_request', request_id)
    if not request_data:
        sender.reply(f"❌ 找不到求助请求：{request_id}")
        return
    
    try:
        request_info = json.loads(request_data)
    except Exception:
        sender.reply(f"❌ 求助请求数据格式错误：{request_id}")
        return
    
    if request_info.get("status") != "pending":
        sender.reply(f"⚠️ 该求助请求已被处理：{request_id}")
        return
    
    # 更新请求状态
    request_info["status"] = "replied"
    request_info["admin_id"] = admin_id
    request_info["reply_content"] = reply_content
    request_info["reply_time"] = now13()
    
    middleware.bucketSet('user_help_request', request_id, json.dumps(request_info, ensure_ascii=False))
    
    # 通知用户管理员回复
    notification_msg = f"""💬 ===管理员回复===
📋 请求ID：{request_id}
👨‍💼 管理员回复：\n
{reply_content}

如需进一步沟通，请私聊联系管理员！"""
    
    # 使用 middleware.push 发送到各个平台
    reply_success = False
    user_id = request_info["user_id"]
    user_platform = request_info.get("platform", "").lower()
    successful_platform = ""
    error_messages = []
    
    # 根据用户原来的平台优先发送消息
    platforms_to_try = []
    if user_platform == "微信":
        platforms_to_try = ['wx', 'qq', 'tg', 'wb']
    elif user_platform == "qq":
        platforms_to_try = ['qq', 'wx', 'tg', 'wb']
    elif user_platform == "telegram":
        platforms_to_try = ['tg', 'qq', 'wx', 'wb']
    else:
        # 默认尝试所有平台
        platforms_to_try = ['qq', 'wx', 'tg', 'wb', 'tb']
    
    # 尝试发送到各个平台
    for platform in platforms_to_try:
        try:
            middleware.push(platform, '', user_id, '', notification_msg)
            reply_success = True
            successful_platform = platform
            break  # 成功发送到一个平台就停止
        except Exception as e:
            error_messages.append(f"{platform}: {str(e)}")
            continue
    
    # 反馈给管理员
    if reply_success:
        sender.reply(f"""✅ ===回复发送成功===
📋 请求ID：{request_id}
👤 用户ID：{request_info['user_id']}
🌐 用户平台：{request_info['platform']}
📝 原问题：{request_info['question'][:50]}{'...' if len(request_info['question']) > 50 else ''}
💬 您的回复：{reply_content}""")
    else:
        error_detail = '\n'.join(error_messages) if error_messages else '未知错误'
        sender.reply(f"""⚠️ ===回复记录已保存，但用户通知发送失败===
📋 请求ID：{request_id}
👤 用户ID：{request_info['user_id']}
🌐 用户平台：{request_info['platform']}
💬 您的回复：{reply_content}
❌ 错误详情：
{error_detail}

请您手动联系用户或通过其他方式通知用户。""")

def main():
    # 获取发送者信息
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    msg = sender.getMessage()
    
    # 判断是用户求助还是管理员回复
    if re.match(r'^回复\s+([a-zA-Z0-9]{8})', msg):
        handle_admin_reply()
    elif msg in ['人工', '售后']:
        handle_user_request()
    else:
        sender.setContinue()

if __name__ == "__main__":
    main() 