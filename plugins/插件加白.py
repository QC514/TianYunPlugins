#[pin:false]
#[public:true]
#[disable:false]
#[platform: qq,qb,wx,tb,tg,web,wxmp]
#[author: sky2022]
#[title: 插件加白]
#[class: 工具类]
#[version: 1.0.0]
#[price: 0]
#[description: 为用户添加插件白名单权限，指令：插件加白，支持换行分割多个用户名]
#[rule: ^插件加白$]
#[icon: https://i.miji.bid/2025/06/27/ff2b2c997f5bf6e1ec52e97548c159c1.png]

import middleware
import json

def add_whitelist(sender, users, plugin_name):
    """添加白名单"""
    bucket = "autMarketBoughts"
    success_count = 0
    fail_count = 0
    
    for user in users:
        user = user.strip()
        if not user:
            continue
            
        try:
            # 获取现有插件列表
            existing = middleware.bucketGet(bucket, user)
            if existing:
                # 如果已有插件，检查新插件是否已存在
                plugins = existing.split(',')
                if plugin_name not in plugins:
                    # 添加新插件到列表末尾
                    new_value = f"{existing},{plugin_name}"
                else:
                    # 插件已存在，跳过
                    sender.reply(f"用户 {user} 已有插件 {plugin_name} 的白名单")
                    continue
            else:
                # 如果没有现有插件，直接设置
                new_value = plugin_name
                
            # 保存更新后的插件列表
            if middleware.bucketSet(bucket, user, new_value):
                success_count += 1
            else:
                fail_count += 1
                
        except Exception as e:
            fail_count += 1
            sender.reply(f"为用户 {user} 添加白名单时出错: {str(e)}")
            
    return success_count, fail_count

if __name__ == '__main__':
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    
    # 获取用户列表
    sender.reply("""=====插件加白=====
请输入要加白的用户名
(一行一个，输入q退出)
==================""")
    
    user_input = sender.input(120000, 1000, False).strip()
    if user_input.lower() == 'q':
        sender.reply("已退出")
        exit()
        
    users = [u for u in user_input.split('\n') if u.strip()]
    
    if not users:
        sender.reply("未输入任何用户名，已退出")
        exit()
        
    # 获取插件名称
    sender.reply("""=====插件加白=====
请输入要加白的插件名称：
(输入q退出)
==================""")
    plugin_name = sender.input(120000, 1000, False).strip()
    
    if plugin_name.lower() == 'q':
        sender.reply("已退出")
        exit()
    
    if not plugin_name:
        sender.reply("未输入插件名称，已退出")
        exit()
        
    # 执行加白操作
    success_count, fail_count = add_whitelist(sender, users, plugin_name)
    
    # 输出结果
    sender.reply(f"""=====加白结果=====
✅ 成功: {success_count} 个
❌ 失败: {fail_count} 个
------------------
🔸 插件名称: {plugin_name}
🔸 总用户数: {len(users)}
==================""") 