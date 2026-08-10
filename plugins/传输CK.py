#[title: 传输CK]
#[language: python]
#[class: 工具类]
#[author: zq8884]
#[service: 421148494]
#[disable:false]
#[admin: true]
#[rule: ^传输CK$]
#[priority: 0]
#[cron: 33 0-23 * * *]
#[open_source: false]
#[icon: http://166.108.197.159:3000/configData/icon/0_容器/Cookiecloud_A.png]
#[version: 2.2]
#[public: true]
#[price: 4.9] 上架价格
#[description: 指令：传输CK。功能：传输倒数N个有效的JD_COOKIE到目的容器，自行在定时推送中添加定时"传输CK"，传输会剔除禁用CK，支持传输黑名单（指定pin排除），支持传输指定数量CK。V2.2：更新多容器传输，目标容器CK限额。]

# [param: {"required":true,"key":"zq8884.containA","bool":false,"placeholder":"多个容器英文逗号分割","name":"源容器名字","desc":"对接容器名字"}]
# [param: {"required":false,"key":"zq8884.containB","bool":false,"placeholder":"选填项,AutuMan对接的第二个容器名字","name":"目标容器名字","desc":"对接第二个容器名字"}]
# [param: {"required":true,"key":"zq8884.remark","bool":false,"placeholder":"建议留空","name":"CK 备注","desc":"自定义 CK 备注"}]
# [param: {"required":true,"key":"zq8884.count","bool":false,"placeholder":"英文逗号隔开，如：80,80代表第一个容器传输80个CK，第二个容器传输80个CK。","name":"传输CK数量","desc":"指定要传输的 CK 数量，从源容器倒序开始计算并排除禁用的CK。"}]
# [param: {"required":true,"key":"zq8884.max_ck_count","bool":false,"placeholder":"目标容器最大CK数量","name":"目标容器容量","desc":"目标容器最大CK数量，超过则跳过操作，不填则不限制。"}]
# [param: {"required":false,"key":"zq8884.exclude","bool":false,"placeholder":"选填项，排除 CK 的 pt_pin 值","name":"排除的 CK","desc":"指定排除的 CK pin值，多个用 & 连接"}]


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
传输CK插件 - 多容器Cookie同步工具（支持目标容器容量限制）
功能：支持从多个源容器传输有效JD_COOKIE到目标容器
特性：
1. 目标容器为空时正常传输
2. count留空时传输所有有效CK
3. 支持目标容器CK数量限制
4. 读取源容器原有备注信息
5. 根据配置决定是否覆盖备注
版本：1.7.1
作者：zq8884
服务ID：421148494
最后修改：2025-07-29
"""

import json
import requests
import middleware
import re

def seekql(container_name):
    """
    根据容器名称查找容器连接信息
    
    Args:
        container_name (str): 容器名称
        
    Returns:
        tuple: (QLurl, qltoken) 或 None
    """
    keys = sender.bucketAllKeys(bucket='qls')
    if not keys:
        return None
    
    for key in keys:
        value = sender.bucketGet(bucket="qls", key=key)
        if value:
            try:
                container_info = json.loads(value)
                if container_info.get("name") == container_name:
                    QLurl = container_info['host']
                    ClientID = container_info['client_id']
                    ClientSecret = container_info['client_secret']
                    qltoken = QLtoken(QLurl, ClientID, ClientSecret)
                    return QLurl, qltoken
            except json.JSONDecodeError:
                continue
    return None

def QLtoken(QLurl, ClientID, ClientSecret):
    """
    获取青龙面板API令牌
    
    Args:
        QLurl (str): 面板URL
        ClientID (str): 客户端ID
        ClientSecret (str): 客户端密钥
        
    Returns:
        str: 访问令牌或 None
    """
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and "token" in response.text:
            qlrequests = json.loads(response.content)
            return qlrequests['data']['token']
        return None
    except requests.exceptions.RequestException:
        return None

def allenvs(qltoken, QLurl):
    """
    获取容器所有环境变量
    
    Args:
        qltoken (str): API令牌
        QLurl (str): 面板URL
        
    Returns:
        list: 环境变量列表或 None（获取失败时返回None）
    """
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": "Bearer " + qltoken,
        "accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response_data = response.json()
        return response_data['data'] if response_data['code'] == 200 else None
    except requests.exceptions.RequestException:
        return None

def transfer_ck():
    """主函数：执行多容器CK传输流程（支持备注保留/覆盖和目标容器容量限制）"""
    # === 参数解析 ===
    containers = middleware.bucketGet(bucket="zq8884", key="containA") or ""
    counts = middleware.bucketGet(bucket="zq8884", key="count") or ""
    exclude_pins_str = middleware.bucketGet(bucket="zq8884", key="exclude") or ""
    config_remark = middleware.bucketGet(bucket="zq8884", key="remark") or ""  # 用户配置的备注
    max_ck_count_str = middleware.bucketGet(bucket="zq8884", key="max_ck_count") or ""  # 目标容器最大CK数量
    
    container_list = [c.strip() for c in containers.split(',') if c.strip()]
    exclude_pins = [p.strip() for p in exclude_pins_str.split('&') if p.strip()]
    
    # 解析目标容器最大CK数量
    max_ck_count = None
    if max_ck_count_str:
        try:
            max_ck_count = int(max_ck_count_str)
        except ValueError:
            sender.reply(f"❌ 目标容器CK限制数量配置错误: '{max_ck_count_str}' 不是有效的整数")
            return
    
    # === 解析count参数：留空表示传输所有CK ===
    count_list = []
    if counts:
        for c in counts.split(','):
            c_stripped = c.strip()
            if c_stripped:  # 非空值转换为整数
                try:
                    count_list.append(int(c_stripped))
                except ValueError:
                    sender.reply(f"❌ 传输数量配置错误: '{c}' 不是有效的整数")
                    return
    else:
        # count参数留空时，为每个容器设置None表示传输所有
        count_list = [None] * len(container_list)
    
    # === 参数验证 ===
    if not container_list:
        sender.reply("❌ 未配置源容器")
        return
    if len(container_list) != len(count_list):
        sender.reply("❌ 源容器与传输数量配置不匹配")
        return
    
    # === 目标容器连接 ===
    containerB_name = middleware.bucketGet(bucket="zq8884", key="containB") or ""
    if not containerB_name:
        sender.reply("❌ 未配置目标容器")
        return
    
    resultB = seekql(containerB_name)
    if not resultB:
        sender.reply(f"❌ 目标容器连接失败: {containerB_name}")
        return
    QLurlB, qltokenB = resultB
    
    # === 检查目标容器当前CK数量 ===
    current_ck_count = 0
    if max_ck_count is not None:
        envsB = allenvs(qltokenB, QLurlB)
        
        # 关键修改：区分"获取失败"和"目标容器为空"
        if envsB is None:  # 获取失败（网络错误等）
            sender.reply(f"❌ 获取目标容器环境变量失败: {containerB_name}")
            return
        elif envsB == []:  # 目标容器为空（正常状态）
            current_ck_count = 0
        else:  # 成功获取环境变量
            # 统计目标容器当前启用的JD_COOKIE数量
            for env in envsB:
                if env['name'] == "JD_COOKIE" and env['status'] == 0:
                    current_ck_count += 1
        
        # 如果目标容器CK数量已达上限，则跳过传输
        if current_ck_count >= max_ck_count:
            sender.reply(f"⛔ 目标容器 {containerB_name} 当前已有 {current_ck_count} 个CK，已达到设置的最大数量 {max_ck_count}，跳过传输。")
            return
    
    # === 多源容器CK收集 ===
    all_cookies = []  # 存储格式: [{'value': cookie, 'source_remark': 源备注}, ...]
    container_reports = []
    total_found = 0
    
    for i, container_name in enumerate(container_list):
        count = count_list[i]
        resultA = seekql(container_name)
        
        if not resultA:
            container_reports.append(f"🚫 {container_name}: 连接失败")
            continue
        
        QLurlA, qltokenA = resultA
        envsA = allenvs(qltokenA, QLurlA)
        
        if envsA is None:  # 获取失败
            container_reports.append(f"🚫 {container_name}: 获取环境变量失败")
            continue
        elif envsA == []:  # 源容器为空
            container_reports.append(f"⚠️ {container_name}: 没有有效CK")
            continue
        
        # 筛选有效CK（同时记录源备注）
        valid_cookies = [
            {
                'value': env['value'],
                'source_remark': env.get('remarks', '')  # 获取源容器中的备注
            }
            for env in envsA 
            if env['name'] == "JD_COOKIE" 
            and env['status'] == 0 
            and get_pt_pin(env['value']) not in exclude_pins
        ]
        
        # === count为None时传输所有有效CK ===
        if count is None:
            cookies_to_transfer = valid_cookies
            count_display = "所有"
        else:
            # 取倒数count个CK
            cookies_to_transfer = valid_cookies[-count:]
            count_display = str(count)
        
        found_count = len(cookies_to_transfer)
        total_found += found_count
        
        all_cookies.extend(cookies_to_transfer)
        container_reports.append(
            f"✅ {container_name}: 传输 {found_count}/{count_display} 个CK"
        )
    
    # === CK传输到目标容器 ===
    added_count = 0
    updated_count = 0
    remark_override_count = 0  # 统计备注被覆盖的数量
    skipped_count = 0  # 统计因目标容器容量限制而跳过的CK数量
    
    for cookie_info in all_cookies:
        # 检查目标容器当前CK数量是否已达上限
        if max_ck_count is not None and current_ck_count + added_count >= max_ck_count:
            skipped_count += 1
            continue  # 跳过当前CK传输
        
        cookie_value = cookie_info['value']
        source_remark = cookie_info['source_remark']
        
        # 确定最终备注：如果用户配置了备注则覆盖，否则使用源备注
        final_remark = config_remark if config_remark else source_remark
        if config_remark and config_remark != source_remark:
            remark_override_count += 1
        
        pt_pin = get_pt_pin(cookie_value)
        if not pt_pin:
            continue
            
        # 检查目标容器是否存在相同pt_pin
        existing_env = find_cookie_by_pin(QLurlB, qltokenB, pt_pin)
        
        if existing_env:
            # 检查值或备注是否有变化
            value_changed = existing_env['value'] != cookie_value
            remark_changed = existing_env.get('remarks', '') != final_remark
            
            if value_changed or remark_changed:
                if QLupdate(
                    QLurl=QLurlB,
                    qltoken=qltokenB,
                    env_id=existing_env['id'],
                    new_value=cookie_value,
                    remark=final_remark
                ):
                    updated_count += 1
        else:
            # 添加新CK
            if QLadd(
                QLurl=QLurlB,
                qltoken=qltokenB,
                cookie_value=cookie_value,
                remark=final_remark
            ):
                added_count += 1
    
    # === 生成传输报告 ===
    report_lines = [
        "===== 🚀 CK传输完成 =====",
        f"📦 源容器: {len(container_list)}个",
        f"🎯 目标容器: {containerB_name}"
    ]
    
    # 添加目标容器容量信息
    if max_ck_count is not None:
        report_lines.append(f"📏 目标容器容量: {current_ck_count}/{max_ck_count} (当前/最大)")
    
    report_lines.extend([
        "\n".join(container_reports),
        "----------------------------",
        f"📊 传输统计:",
        f"✅ 新增CK: {added_count}",
        f"🔄 更新CK: {updated_count}"
    ])
    
    # 添加跳过的CK数量
    if skipped_count > 0:
        report_lines.append(f"⏭️ 跳过CK: {skipped_count} (目标容器已满)")
    
    report_lines.extend([
        f"📥 总数: {added_count + updated_count}/{total_found}",
        f"📝 备注处理: {'使用配置覆盖' if config_remark else '保留源备注'} ({remark_override_count}个备注被覆盖)"
    ])
    
    sender.reply("\n".join(report_lines))

def find_cookie_by_pin(QLurl, qltoken, pt_pin):
    """
    在容器中根据pt_pin查找Cookie环境变量
    
    Args:
        QLurl (str): 面板URL
        qltoken (str): API令牌
        pt_pin (str): 要查找的pt_pin值
        
    Returns:
        dict: 环境变量信息或 None
    """
    envs = allenvs(qltoken, QLurl)
    if envs is None or envs == []:
        return None
        
    for env in envs:
        if env['name'] == "JD_COOKIE":
            env_pt_pin = get_pt_pin(env['value'])
            if env_pt_pin == pt_pin:
                return env
    return None

def QLadd(QLurl, qltoken, cookie_value, remark=""):
    """
    添加新的环境变量
    
    Args:
        QLurl (str): 面板URL
        qltoken (str): API令牌
        cookie_value (str): Cookie值
        remark (str): 备注信息
        
    Returns:
        bool: 是否添加成功
    """
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": f"Bearer {qltoken}",
        "Content-Type": "application/json"
    }
    payload = [{
        "name": "JD_COOKIE",
        "value": cookie_value,
        "remarks": remark
    }]
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def QLupdate(QLurl, qltoken, env_id, new_value, remark=""):
    """
    更新现有环境变量（值和备注）
    
    Args:
        QLurl (str): 面板URL
        qltoken (str): API令牌
        env_id (int): 环境变量ID
        new_value (str): 新的Cookie值
        remark (str): 新的备注信息
        
    Returns:
        bool: 是否更新成功
    """
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": f"Bearer {qltoken}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "JD_COOKIE",
        "value": new_value,
        "remarks": remark,  # 更新备注信息
        "id": env_id
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload, timeout=15)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_pt_pin(cookie):
    """
    从Cookie字符串中提取pt_pin值
    
    Args:
        cookie (str): Cookie字符串
        
    Returns:
        str: pt_pin值或 None
    """
    match = re.search(r"pt_pin=([^;]+);", cookie)
    return match.group(1) if match else None

# === 主程序入口 ===
if __name__ == "__main__":
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    transfer_ck()