# [title: 涩涩]
# [language: python]
# [class: 娱乐类]
# [cron: ] cron定时，支持5位域和6位域
# [priority: 0] 优先级，数字越大表示优先级越高
# [platform: qq,qb,wx,tb,tg,web,wxmp,tgbot] 适用的平台
# [open_source: false]是否开源
# [public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [author: Jray_P]
# [icon: http://jray.fun:5080/admin/images/gallery/1732760275082925068.gif ]图标链接地址，请使用48像素的正方形图标，支持http和https
# [price: 0] 上架价格
# [service: 无售后，请勿叨扰原作者] 售后联系方式
# [disable:true] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [version: 1.0.8]版本号
# [rule: 我要乃子] 匹配规则，多个规则时向下依次写多个
# [rule: 我要美女] 匹配规则，多个规则时向下依次写多个
# [rule: 我要黑丝] 匹配规则，多个规则时向下依次写多个
# [rule: 我要白丝] 匹配规则，多个规则时向下依次写多个
# [rule: 我要头像] 匹配规则，多个规则时向下依次写多个
# [rule: 我要壁纸] 匹配规则，多个规则时向下依次写多个
# [description: 更新日志：增加公开处刑功能(大佬的插件，纯搬运。)命令：我要乃子，我要美女，我要黑丝，我要白丝，我要头像，我要壁纸]


# [param: {"required":true,"key":"Jray_config.ss_pushconfig","bool":true,"placeholder":"","name":"是否启用姿势推送","desc":"控制是否启用姿势图片推送功能，true 表示启用，false 表示关闭，必填"}]
# [param: {"required":true,"key":"Jray_config.ss_pushimtype","bool":false,"placeholder":"","name":"消息类型","desc":"推送消息的类型，如微信（wx）、QQ（qq）等，必填"}]
# [param: {"required":false,"key":"Jray_config.ss_pushgroupcode","bool":false,"placeholder":"","name":"推送群组代码","desc":"推送目标的群组代码，可选，群组代码和用户 ID 至少存在一个"}]
# [param: {"required":false,"key":"Jray_config.ss_pushuserid","bool":false,"placeholder":"","name":"推送用户 ID","desc":"推送目标的用户 ID，可选，群组代码和用户 ID 至少存在一个"}]
# [param: {"required":false,"key":"Jray_config.ss_pushtitle","bool":false,"placeholder":"","name":"推送标题","desc":"推送消息的标题，可选"}]
# [param: {"required":true,"key":"Jray_config.ss_pushcontent","bool":false,"placeholder":"","name":"推送内容","desc":"推送消息的内容，必填"}]


import requests
import middleware
from middleware import bucketGet, push


def get_img(ss_type, key):
    """
    根据类型和 API 密钥请求图片链接。
    """
    url = f"https://jkapi.com/api/{ss_type}?apiKey={key}"
    try:
        # 发送请求并获取跳转后的图片链接
        response = requests.get(url, timeout=10, allow_redirects=True)
        response.raise_for_status()  # 如果状态码不是 200，将抛出 HTTPError

        # 返回最终跳转到的图片链接
        return response.url

    except requests.exceptions.RequestException as e:
        # 捕获网络错误
        print(f"网络请求错误：{e}")
    
    # 如果发生错误，返回一个占位图片链接或提示
    return "https://example.com/error_image.jpg"


def process_command(content, send_type, sender):
    """
    根据输入的内容和发送类型处理对应命令。
    """
    # 命令与 API 类型及密钥的映射表
    commands = {
        "我要乃子": ("yo_cup", "9d02cd6e10c51f16ccc27cc164ac4b6d", "帅哥骚等，正在帮你找大的~~", "乃子"),
        "我要美女": ("meinv_img", "5139167a391a2f282283bc8eb28fe6ab", "帅哥骚等，正在帮你找美的~~", "美女"),
        "我要黑丝": ("heisi_img", "9f2132d1e1ace9d304afe3c4e999e0ad", "帅哥骚等，正在帮你找媚的~~", "黑丝"),
        "我要白丝": ("baisi_img", "efa4842cc08a1265d7fe54f5dd4f1f32", "帅哥骚等，正在帮你找嫩的~~", "白丝"),
        "我要头像": ("avatar_woman", None, "帅哥骚等，正在帮你找飒的~~", "头像"),
        "我要壁纸": ("bing_img", None, "帅哥骚等，正在帮你找骚的~~", "壁纸"),
    }

    # 根据用户输入匹配命令
    for command, (api_type, api_key, reply_message, feature_name) in commands.items():
        if command in content:
            # 回复用户消息
            sender.reply(reply_message)
            image_url = ""

            # 根据是否有 API 密钥获取图片
            if api_key:  # 如果需要 API 密钥
                image_url = get_img(api_type, api_key)
            else:  # 如果不需要 API 密钥，直接返回固定 URL
                image_url = f"https://jkapi.com/api/{api_type}"

            # 回复用户图片
            sender.replyImage(image_url)

            # 检查推送配置
            push_config = bucketGet("Jray_config", "ss_pushconfig")
            if push_config and push_config.lower() == "true":
                # 读取推送相关参数
                push_params = {
                    "imType": bucketGet("Jray_config", "ss_pushimtype"),
                    "groupCode": bucketGet("Jray_config", "ss_pushgroupcode"),
                    "userID": bucketGet("Jray_config", "ss_pushuserid"),
                    "title": bucketGet("Jray_config", "ss_pushtitle"),
                    "content": bucketGet("Jray_config", "ss_pushcontent"),
                }

                # 校验推送配置的必填字段
                if not push_params["imType"] or not push_params["content"]:
                    return  # 必填字段缺失，直接退出

                if not push_params["groupCode"] and not push_params["userID"]:
                    return  # 群组代码和用户 ID 都不存在，直接退出

                # 动态生成推送内容，附加功能名称后两个字符
                try:
                    username = sender.getUserName()  # 从 sender 获取用户名
                    dynamic_content = f"{username} {push_params['content']} {feature_name}"

                    # 调用推送方法
                    push(
                        push_params["imType"],
                        push_params["groupCode"] if push_params["groupCode"] else "",
                        push_params["userID"] if push_params["userID"] else "",
                        push_params["title"] if push_params["title"] else "",
                        dynamic_content  # 推送内容
                    )
                except Exception as e:
                    print(f"推送失败，错误原因：{str(e)}")  # 静默处理推送失败

            return

    # 未匹配到任何命令
    sender.reply("抱歉，我不知道你想要什么~ 试试发送“我要乃子”或者“我要美女”吧！")


if __name__ == '__main__':
    # 初始化用户信息
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    user_message = sender.getMessage()

    # 处理用户命令
    process_command(user_message, send_type="reply", sender=sender)