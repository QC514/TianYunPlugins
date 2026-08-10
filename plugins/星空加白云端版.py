#[title: 星空加白云端版]
#[language: python]
#[class: 工具类]
#[author: rujingxianghai]
#[service: 203066880] 售后联系方式
#[disable: false] 禁用开关，true表示禁用，false表示可用
#[admin: false] 是否为管理员指令
#[rule: ^星空加白$] 匹配规则，多个规则时向下依次写多个
#[cron: ] cron定时，支持5位域和6位域
#[priority: 0] 优先级，数字越大表示优先级越高
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[open_source: false]是否开源
#[icon: https://y.gtimg.cn/music/photo_new/T053M000002Qqrye0oyZSp.jpg]图标链接地址，请使用48像素的正方形图标，支持http和https
#[version: 1.0.0]版本号
#[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
#[price: 0] 上架价格
#[description: 星空代理加白云端版本，云端整理ip，统一同步至星空。用户独立卡密，免除星空接口泄露风险。] 

import requests
import middleware
import json

# 获取发送者信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

# [param: {"required":true,"key":"s_xkjb.key","bool":false,"placeholder":"必填项","name":"KEY值","desc":"用于标识用户的唯一KEY"}]

def get_public_ip():
    """获取外网IP地址"""
    # 尝试主接口
    try:
        response = requests.get('https://myip.ipip.net/s', timeout=5)
        if response.status_code == 200:
            ip = response.text.strip()
            if ip and ip != "127.0.0.1":
                return ip
    except Exception:
        pass
    
    # 尝试备用接口
    try:
        response = requests.get('http://42.194.132.65:5010/', timeout=5)
        if response.status_code == 200:
            ip = response.text.strip()
            if ip and ip != "127.0.0.1":
                return ip
    except Exception:
        pass
    
    return None

def sync_ip_via_api(api_url, key, ip):
    """通过自建接口同步IP"""
    try:
        data = {
            'key': key,
            'ip': ip
        }
        
        response = requests.post(f"{api_url}/xkdl-sync", json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return {
                'verify': False,
                'is_new': False,
                'message': f'接口请求失败，状态码：{response.status_code}'
            }
    except Exception as e:
        return {
            'verify': False,
            'is_new': False,
            'message': f'请求错误：{str(e)}'
        }

def main():
    """主函数"""
    try:
        # 获取配置参数
        key = middleware.bucketGet('s_xkjb', 'key') or '{}'
        api_url = 'https://xkdl.vorto.cn'

        if not key or key == '{}':
            return "请先设置KEY值"

        # 获取当前IP
        current_ip = get_public_ip()
        if not current_ip:
            return "获取当前IP失败"

        # 调用自建接口同步IP
        result = sync_ip_via_api(api_url, key, current_ip)
        
        if not result['verify']:
            return f"KEY验证失败：{result['message']}"
        
        if result['is_new']:
            return f"IP更新成功！\n新IP：{current_ip}\n状态：{result['message']}"
        else:
            return f"当前IP（{current_ip}）未发生变化，无需更新"

    except Exception as e:
        return f"发生错误：{str(e)}"

if __name__ == "__main__":
    message = sender.getMessage()
    if '星空加白' in message:
        if not sender.isAdmin():
            sender.reply("❌ 您不是管理员，无法进行操作")
            sender.setContinue()
        else:
            sender.reply(main())