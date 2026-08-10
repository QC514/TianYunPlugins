# ==========================市场元数据=========================================
# [title: 青龙改定时]
# [open_source: false]是否开源
# [icon: ]图标链接地址，支持http和https
# [version: 0.0.7]版本号
# [author: sn_jmh]
# [class: 工具类]从工具类、查询类、娱乐类、餐饮类、影音类、生活类、图片类、游戏类等中选择，也可自定义
# [platform: qq,qb,wx,wb,tg,tb,mq]适用的平台 qq/qb/wx/tb/tg/wxmp/web之间选择，中间用英文逗号隔开
# [public:true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [price: 1.00] 上架价格
# [service: QQ:313154383]写上售后联系方式，方便用户联系咨询
# [description: 【触发规则】自己设置<br>【插件描述】改青龙中脚本的定时。推荐转赚红包，例如2 0 * * *运行后为3 0 * * *增加的时间可以自己设置。交流群：593755244<br>【更新内容】支持autMan2.5.5版本，修复青龙低版本报错的问题]
# ==========================功能元数据======================================
# [rule: ^改$] 匹配规则，多个规则时向下依次写多个
# [cron: 0 16 * * *] cron定时，支持5位域和6位域
# [admin: true] 是否为管理员指令
# [disable: false] 禁用开关，true表示禁用，false表示可用
# [priority: 10] 优先级，数字越大表示优先级越高
# [param: {"required":false,"key":"sn_jmh.add_js","placeholder":"jd_zzhb.js","name":"脚本名字","desc":"多个用英文逗号分割，6dylan6_jdpro/jd_zzhb.js。"}]
# [param: {"required":false,"key":"sn_jmh.add_time","placeholder":"1","name":"时间增加几","desc":"填写数字。默认是1。"}]
# [param: {"required":false,"key":"sn_jmh.ds_Container","placeholder":"青龙1,青龙2。","name":"指定容器","desc":"绑定的容器名用英文逗号分割。"}]
# [param: {"required":false,"key":"sn_jmh.version","bool":true,"placeholder":"检测","name":"青龙版本","desc":"默认高版本,勾选为低版本。"}]
# [param: {"required":false,"key":"sn_jmh.SN_QLS","placeholder":"","name":"青龙地址和秘钥","desc":"\u005b\u007b\u0022\u006e\u0061\u006d\u0065\u0022\u003a\u0022\u9752\u9f99\u0031\u0022\u002c\u0022\u0068\u006f\u0073\u0074\u0022\u003a\u0022\u0068\u0074\u0074\u0070\u003a\u002f\u002f\u0031\u0039\u0032\u002e\u0031\u0036\u0038\u002e\u0038\u002e\u0031\u003a\u0035\u0037\u0030\u0030\u0022\u002c\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0069\u0064\u0022\u003a\u0022\u0078\u0078\u0078\u0022\u002c\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0073\u0065\u0063\u0072\u0065\u0074\u0022\u003a\u0022\u0078\u0078\u0078\u0022\u007d\u005d。json格式,autMan2.5.5版本以后的必须填写。"}]

import json
import re
import sys
import time
import middleware
import requests

token = None
host = None
groupCode = ""
add_js = middleware.bucketGet("sn_jmh", "add_js")

add_js_list = add_js.split(',')
add_time = middleware.bucketGet("sn_jmh", "add_time")
if add_time == "":
    add_time = 1

QLS = middleware.bucketGet("sn_jmh", "SN_QLS")

ql_Container = middleware.bucketGet("sn_jmh", "ds_Container")
version = middleware.bucketGet("sn_jmh", "version")
bucket = ['pinQQ', 'pinQB', 'pinWX', 'pinWB', 'pinTG', 'pinMQ']
imType = ['qq', 'qb', 'wx', 'wb', 'tg', 'tb', 'mq']

def printf(msg):
    print(msg)
    sys.stdout.flush()

# 选择容器
def run_matching_names(data, ql):
    ql_list = ql.replace("'", "").split(",")
    matching_items = []

    for item in data:
        if item["name"] in ql_list:
            matching_items.append(item)  # 将匹配项添加到列表中

    if len(matching_items) > 0:
        print(f"指定:[{len(matching_items)}]个容器")
        return matching_items
    else:
        middleware.notifyMasters(f"通知\n填写指定容器错误，将运行全部容器。", imType)
        return False
# 获取青龙token
def get_token(host, client_id, client_secret):
    try:
        url = f"{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}"
        response = requests.get(url)
        response.raise_for_status()
        token = response.json()["data"]["token"]
        return token
    except requests.exceptions.RequestException as e:
        printf(f"获取令牌失败:{e}")
        return None

def Get_Status(host, token , search):
    try:
        url = f"{host}/open/crons?searchValue={search}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_json = json.loads(response.text)
        data_value = response_json.get("data", None)
        return data_value

    except requests.exceptions.RequestException as e:
        printf(f"获取状态失败: {e}")
        return False

def set_cron_schedule(host, token, task_id, task_name, command, schedule, labels):
    try:
        url = f"{host}/open/crons"
        payload = {
            "id": task_id,
            "name": task_name,
            "command": command,
            "schedule": schedule,
            "labels": labels
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print("设置任务调度时间失败:", e)

def change_time(status_list):
    try:
        if version == "true":
            status = status_list[0]
            task_id = status['id']
            task_name = status['name']
            command = status['command']
            schedule = status['schedule']
            labels = status['labels']
        else:
            task_id = status_list['data'][0]['id']
            task_name = status_list['data'][0]['name']
            command = status_list['data'][0]['command']
            schedule = status_list['data'][0]['schedule']
            labels = status_list['data'][0]['labels']
        # print(task_id, task_name, command, schedule, labels)
        schedule_parts = schedule.split(" ")
        if len(schedule_parts) >= 5:
            new_minute = int(schedule_parts[0]) + int(add_time)
            print(new_minute)
            if int(new_minute) >= 60:
                middleware.notifyMasters(f"通知\n[{task_name}]\n第一个时间大于或等于60,请到青龙重新设置", imType)
                printf("第一个时间大于或等于60,请到青龙重新设置")
            else:
                # 在第一个时间分量等于59时执行操作
                printf("第一个时间正常.")
                new_schedule = f"{new_minute} {' '.join(schedule_parts[1:])}"
                set_cron_schedule(host, token, task_id, task_name, command, new_schedule, labels)
                middleware.notifyMasters(f"通知\n[{task_name}]\n原时间:{schedule}\n现时间:{new_schedule}", imType)
                printf("设置时间成功")
        else:
            print("定时获取错误")

    except Exception as e:
        print(f"发生错误: {e}")


# 主程序
def run():
    global host
    global token
    try:
        if QLS:
            data = json.loads(QLS)
            if ql_Container != "":
                data = run_matching_names(data, ql_Container)
            for item in data:
                host = item['host']
                # printf(host)
                printf(f"运行【{item['name']}】容器")
                token = get_token(item["host"], item["client_id"], item["client_secret"])
                for js in add_js_list:
                    status = Get_Status(item["host"], token, js)
                    printf(f"js:{js}")
                    printf(f"data_dict:{status}")
                    change_time(status)
        else:
            print("您没有绑定青龙容器。")
    except Exception as e:
        print(f"主程序发生异常: {e}")

if __name__ == '__main__':
    if QLS:
        run()
        print("已设置青龙地址")
    else:
        print("没有设置青龙地址")
        middleware.notifyMasters(f"通知\n未设置青龙地址结束。", imType)