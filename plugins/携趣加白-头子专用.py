#[pin:true]
#[open_source: false]
#[disable:false]
#[title: 携趣加白-头子专用]
#[create_at: 2023-08-05 15:53:10]
#[author: 960342874]
#[version: 1.0.3]
#[price: 2.0]
#[rule: ^携趣头子加白$]
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[admin: true]
#[public:true]
#[class: 工具类]
#[service: <img src="https://pic.fglt.net/common/a8/common_4_verify_icon.gif" border="0" /> <b>官方权威认证</b>  交流群758982908 ]
#[description: 【1】指令：携趣头子加白 (发送指令后会有教程)<br>【2】可以无限设置携趣账号，代理剩余不足时，插件自动匹配其他账号加白IP<br>【3】配合代理池实现代理自由，完美解决代理不够用问题<br>【4】定时任务默认30分钟一次，可自行设置<br>【5】插件默认自动获取ip并加白，若您需要加白指定IP请设置配参 <br>（适用代理池搭建在了不同网络环境的情况） <br>【6】需要python环境 <br>【7更新】ip接口可选，账号余量查询]
#[cron: 0 0/30 * * * ?  ]
#[param: {"required":true,"key":"otto.tzxq","bool":false,"placeholder":"","name":"账号信息","desc":"uid=你的携趣uid,ukey=你的携趣ukey#uid=你的携趣uid,ukey=你的携趣ukey（uid和ukey之间用逗号，多个账号之间用#号)"}]
#[param: {"required":false,"key":"otto.option","bool":false,"placeholder":"","name":"获取ip的接口","desc":"填1或者2，默认1，ip获取不准时可自己调整"}]
#[param: {"required":false,"key":"otto.fixedip","bool":false,"placeholder":"","name":"指定IP","desc":"适用代理池搭建在了不同网络环境的情况"}]
#[icon:	https://www.xiequ.cn/Home/img/logo.png]
import time
import middleware
import requests
import re
import json
def main():
    tzxq = middleware.get("tzxq")
    option = middleware.get("option") or "1"
    fixedip = middleware.get("fixedip")
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userID = sender.getUserID()
    ImType = sender.getImtype()
    plugin_key = "xqtz"
    response = requests.get("https://ztt-1251929976.cos.ap-beijing.myqcloud.com/aut_plugin.txt")
    yunhei = response.json()
    
    if not yunhei or plugin_key not in yunhei:
        sender.reply("未验证已退出！")
        return
    elif yunhei[plugin_key]['state'] == "invalid":
        sender.reply("插件禁用：原因未知！")
        return
    elif userID in yunhei['master_yunhei']['data'] and ImType != 'croncmd':
        sender.reply("你已被云黑-All")
        return
    elif userID in yunhei[plugin_key]['branch_yunhei']['data'] and ImType != 'croncmd':
        sender.reply("你已被云黑----携趣头子加白")
        return


    if fixedip:
        ip_new = fixedip
        sender.reply("您的IP是 " + ip_new)
        delete_multiple_accounts(tzxq)
        check_all_accounts_ip(tzxq)
        result = extract_tzxq_value(tzxq, ip_new)
    else:
        if option == "1":
            url = "https://www.ip.cn/api/index?ip&type=0"
            timeout = 30

            response = requests.get(url, timeout=timeout)

            if response.status_code == 200:
                ip_data = response.json()
                ip_new = ip_data["ip"]
                sender.reply("您的IP是 " + ip_new)
                delete_multiple_accounts(tzxq)
                check_all_accounts_ip(tzxq)
                result = extract_tzxq_value(tzxq, ip_new)
            else:
                print(f"Failed to fetch IP. Status code: {response.status_code}")
        
        elif option == "2":
            url = "http://api.xiequ.cn/VAD/OnlyIp.aspx?yyy=123"
            response = requests.get(url)

            if response.status_code == 200:
                ip_new = response.text
                sender.reply("您的IP是 " + ip_new)
                delete_multiple_accounts(tzxq)
                check_all_accounts_ip(tzxq)
                result = extract_tzxq_value(tzxq, ip_new)
            else:
                print(f"Failed to fetch IP from the external API. Status code: {response.status_code}")

def extract_tzxq_value(tzxq_string, ip):
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    
    if "uid" in tzxq_string:
        pattern = r'uid=([^,]+),ukey=([^#]+)'
        matches = re.findall(pattern, tzxq_string)
        
        if matches:
            for match in matches:
                uid, ukey = match
                print(f"携趣uid: {uid}, 携趣ukey: {ukey}")
                response = requests.get(f"http://op.xiequ.cn/ApiUser.aspx?act=suitdt&uid={uid}&ukey={ukey}")
                
                try:
                    data = response.json()
                except ValueError as e:
                    continue
                
                if data["success"] == "true":
                    for item in data["data"]:
                        if int(item["num"]) - int(item["use"]) > 0:
                            add_ip_response = requests.post(f"http://op.xiequ.cn/IpWhiteList.aspx?uid={uid}&ukey={ukey}&act=add&ip={ip}")
                            if "success" in add_ip_response.text:
                                sender.reply(f"携趣加白成功！{add_ip_response.text}\n当前加白智能匹配账号uid为：{uid}\n剩余ip：{int(item['num']) - int(item['use'])}")
                            else:
                                sender.reply(f"携趣加白失败！{add_ip_response.text}")
                            return
                else:
                    sender.reply("请求失败，请检查携趣信息！")
            sender.reply("未找到大于0的套餐")
        else:
            sender.reply("携趣账号设置错误，请检查！")
    else:
        sender.reply("未设置携趣信息，请先设置配参")

def delete_multiple_accounts(tzxq_string):
    if "uid" in tzxq_string:
        pattern = r'uid=([^,]+),ukey=([^#]+)'
        matches = re.findall(pattern, tzxq_string)
        
        if matches:
            for match in matches:
                uid, ukey = match
                print(f"携趣uid: {uid}, 携趣ukey: {ukey}")
                
                response = requests.get(f"http://op.xiequ.cn/IpWhiteList.aspx?uid={uid}&ukey={ukey}&act=del&ip=all")
                
                if "success" in response.text:
                    print(f"成功删除账号 {uid} 的IP白名单信息")
                else:
                    print(f"删除账号 {uid} 的IP白名单信息失败")
        else:
            print("未匹配到uid和ukey")
    else:
        print("未设置携趣信息，请先设置")

def check_all_accounts_ip(tzxq_string):
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    if "uid" in tzxq_string:
        pattern = r'uid=([^,]+),ukey=([^#]+)'
        matches = re.findall(pattern, tzxq_string)
        
        if matches:
            for match in matches:
                uid, ukey = match
                print(f"携趣uid: {uid}, 携趣ukey: {ukey}")
                response = requests.get(f"http://op.xiequ.cn/ApiUser.aspx?act=suitdt&uid={uid}&ukey={ukey}")
                
                try:
                    data = response.json()
                except ValueError as e:
                    sender.reply(f"查询失败,账号uid为 {uid} 的IP可能已用完")
                    continue
                
                if data["success"] == "true":
                    for item in data["data"]:
                        if item["type"] == "免费套餐":
                            remaining_ip = int(item["num"]) - int(item["use"])
                            if remaining_ip > 0:
                                print(f"账号uid为 {uid} 的剩余IP数量为: {remaining_ip}")
                                sender.reply(f"账号uid为 {uid} 的剩余IP数量为: {remaining_ip}")
                            else:
                                print(f"账号uid为 {uid} 的IP已用完")
                                sender.reply(f"账号uid为 {uid} 的IP已用完")
                else:
                    print("请求失败，请检查携趣信息！")
        else:
            print("未找到匹配的uid和ukey")
    else:
        print("未设置携趣信息，请先设置")
def check_senderID_in_json(url, senderID):
    print(f"aaaaaaaaaaaaaaaaaaaaaaaaaaaa {senderID} in JSON data from URL: {url}")
    
    response = requests.get(url)
    
    if response.status_code == 200:
        print("bbbbbbbbbbbbbbbbbbbbbbbb")
        
        json_data = response.json()
        
        if 'account' in json_data:
            account_list = json_data['account'].split(',')
            print(f"cccccccccccccccccccccccccccc: {account_list}")
            
            if senderID in account_list:
                print(f"dddddddddddddddddddddddddddddd {senderID} found in account list")
                return True
            else:
                print(f"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeSenderID {senderID} not found in account list")
                return False
    else:
        print("hhhhhhhhhhhhhhhhhhhhhhhhhFailed to fetch data from the URL")
        return False
if __name__ == '__main__':
    main()


