# ==========================市场元数据=========================================
# [title: ip变化通知]
# [open_source: false]是否开源
# [icon: https://www.freeimg.cn/i/2023/12/24/6587d4a2a807d.jpg]图标链接地址，支持http和https
# [version: 0.1.8]版本号
# [author: sn_jmh]
# [class: 工具类]从工具类、查询类、娱乐类、餐饮类、影音类、生活类、图片类、游戏类等中选择，也可自定义
# [platform: qq,qb,wx,wb,tg,tb,mq]适用的平台 qq/qb/wx/tb/tg/wxmp/web之间选择，中间用英文逗号隔开
# [public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [price: 0.00] 上架价格
# [service: QQ:313154383]写上售后联系方式，方便用户联系咨询
# [description: 【触发规则】ip<br>【插件描述】检测ip有变化通知管理员，可以自己配参填写ip接口。自己控制定时。交流群：593755244<br>【更新内容】更换接口，新增地址信息。]
# ==========================功能元数据======================================
# [rule: ^ip$] 匹配规则，多个规则时向下依次写多个
# [cron: 2 2 29 2 *] cron定时，支持5位域和6位域
# [admin: true] 是否为管理员指令
# [disable:false] 禁用开关，true表示禁用，false表示可用
# [priority: 10] 优先级，数字越大表示优先级越高
# ==========================配参数据（最下面）===============================
# [param: {"required":false,"key":"sn_jmh.http_ip","placeholder":"http://httpbin.org/ip","name":"显示IP的网址","desc":"自定义网址"}]

import middleware
import requests
import re

imTypes = ['qq', 'qb', 'wx', 'wb', 'tg', 'tb', 'mq']
IP = middleware.bucketGet("sn_jmh", "IP")
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
content = sender.getMessage()
http_ip = middleware.bucketGet("sn_jmh", "http_ip")

def httpbin():
    if http_ip == "":
        print("使用默认请求网址.")
        try:
            url = "http://myip.ipip.net"
            response = requests.get(url)
            text = response.text

            try:
                ip = re.search(r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", text).group()
            except AttributeError:
                ip = "IP地址未找到"
            return ip

        except requests.RequestException as e:
            print(f"请求ip失败，{e}")
            middleware.notifyMasters(f'通知\nip变化通知发生错误{e}.', imTypes)
    else:
        print("使用自定义请求网址.")
        try:
            payload = {}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Connection': 'keep-alive'
            }
            response = requests.request("GET", http_ip, headers=headers, data=payload)
            text = response.text
            try:
                ip = re.search(r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", text).group()
            except AttributeError:
                ip = "IP地址未找到"
            return ip

        except requests.RequestException as e:
            print(f"使用自定义借口失败，{e}")
            middleware.notifyMasters(f'通知\nip变化通知发生错误{e}.', imTypes)
# 获取地址
def get_ip_location(ip):
    try:
        # IP 查询 API 的 URL，返回值为中文
        api_url = 'http://ip-api.com/json/{}?lang=zh-CN'

        response = requests.get(api_url.format(ip))
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                # 构建并返回 IP 地址的地理位置信息
                location_info = '{} {} {} {}'.format(
                    # data['query'],
                    data['country'],
                    data['regionName'],
                    data['city'],
                    data['zip']
                )
                return location_info
            else:
                print(f"查询失败: {data['message']}")
                return False
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        middleware.notifyMasters(f'通知\nip变化通知获取地址错误{e}.', imTypes)
        print(f"发生未知错误: {e}")
        return False

def main():
    ip = httpbin()
    if "ip" in content:
        if ip == IP:
            print("ip没有变化.")
            sender.reply(f'通知\nip没有变化\n现ip：{ip}')
        else:
            print(f"ip变化为，{ip}")
            location = get_ip_location(ip)
            if location:
                sender.reply(f'通知\n{location}\n新ip：{ip}\n原ip：{IP}')
                middleware.bucketSet("sn_jmh", "IP", ip)
            else:
                sender.reply(f'通知\n新ip：{ip}\n原ip：{IP}')
                middleware.bucketSet("sn_jmh", "IP", ip)
    else:
        if ip == IP:
            print("ip没有变化不通知.")
        else:
            print(f"ip变化为，{ip}")
            location = get_ip_location(ip)
            if location:
                middleware.notifyMasters(f'通知\n{location}\n新ip：{ip}\n原ip：{IP}')
                middleware.bucketSet("sn_jmh", "IP", ip)
            else:
                middleware.notifyMasters(f'通知\n新ip：{ip}\n原ip：{IP}')
                middleware.bucketSet("sn_jmh", "IP", ip)

if __name__ == '__main__':
    main()