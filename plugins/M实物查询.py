# ==========================市场元数据=========================================
# [open_source: false]是否开源
# [title: M实物查询]
# [author: buzhi]
# [icon: ]图标链接地址，支持http和https
# [version: 2.0.6]
# [description: 默认查询指令：M实物<br/>增加对接青龙查询<br/>指定日期查询指令：M实物 xxx（xxx为日期，例如20240101；或时间范围：20250530-20250601）<br/>查询天数指令：M实物天数，例如：M实物5，就是查询近五天<br/>查询关键词物品：M实物+关键词；查询关键字个数例如：M实物+关键字 数字<br/>注意：只适用奥特曼内置容器<br/>删除实物关键词指令：M实物-牛奶<br/><br/>2025-06-01更新：1、增加奥特曼文件夹下多路径查询（详细请看配参）<br/>2、增加免密M实物文本分享链接查询<br/>3、增加多文件合并统计查询<br/>4、指定日期查询支持范围成查询<br/>5、优化文本输出样式【交流群】QQ群：862839828]
# [platform: qq,wx,wb,tg,tb]
# [public:true]
# [price: 3.88]
# [service: Q群862839828]
# [class: 工具类]
# ==========================函数解析元数据======================================
# [priority: 1000 ]
# [admin: true]
# [disable:false]
# [rule: ^M?实物(| [\s\S]+)$] 匹配规则，多个规则时向下依次写多个
# [rule: ^M?实物\d+$]
# [rule: ^M?实物(\+|-)[\s\S]+$]
# ==========================参数配置数据（最下面）===============================
# [param: {"required":true,"key":"buzhi_mEntity.filePathBox","placeholder":"","bool":true,"name":"路径开关","desc":"是否开启奥特曼路径查询模式"}]
# [param: {"required":true,"key":"buzhi_mEntity.pathsBox","placeholder":"","bool":true,"name":"启用多路径","desc":"默认关闭为单路径，开启后M文件夹名称则需要填写完整的路径多个请用,隔开"}]
# [param: {"required":true,"key":"buzhi_mEntity.filePath","placeholder":"","name":"M文件夹名称","desc":"未开启多路径文件夹名称例如：M_main，开启多路径填写完整文件夹路径例如：/autMan/task/scripts/M1/auto/,/autMan/task/scripts/M2/auto/，多个使用,隔开"}]
# [param: {"required":false,"key":"buzhi_mEntity.deviceName","placeholder":"","name":"设备命名","desc":"命名实物设备的名称，多路径请用,隔开命名"}]
# [param: {"spliter":true}]
# [param: {"required":true,"key":"buzhi_mEntity.qlBox","placeholder":"","bool":true,"name":"青龙开关","desc":"是否开启青龙查询模式，需要青龙权限"}]
# [param: {"required":false,"key":"buzhi_mEntity.qlNames","placeholder":"","name":"青龙名称","desc":"奥特曼对接的青龙名称，多个请用,隔开"}]
# [param: {"required":true,"key":"buzhi_mEntity.qlFilePaths","placeholder":"","name":"青龙M实物文件路径","desc":"填写完整文件夹路径，多个青龙就填写多个路径，例如：/M_Scripts/scripts/auto/,/M_Scripts/scripts/auto/，多个使用,隔开"}]
# [param: {"required":false,"key":"buzhi_mEntity.qlDeviceName","placeholder":"","name":"青龙设备命名","desc":"命名青龙实物设备的名称，多个青龙请用,隔开命名，不填写默认青龙名称"}]
# [param: {"spliter":true}]
# [param: {"required":true,"key":"buzhi_mEntity.shareLinkBox","placeholder":"","bool":true,"name":"文本链接开关","desc":"是否开启文本链接查询模式"}]
# [param: {"required":false,"key":"buzhi_mEntity.shareLinks","placeholder":"","name":"文本链接","desc":"多个文本分享链接请用,分割"}]
# [param: {"required":false,"key":"buzhi_mEntity.linkDeviceNames","placeholder":"","name":"链接设备命名","desc":"命名实物设备的名称，多个文本链接请用,隔开命名"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_mEntity.mergeBox","placeholder":"","bool":true,"name":"合并输出","desc":"当有多个查询时，是否开启合并输出"}]
# [param: {"required":false,"key":"buzhi_mEntity.deviceNames","placeholder":"","name":"合并设备命名","desc":"合并输出命名实物设备的名称"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_mEntity.searchDays","placeholder":"2","name":"查询天数","desc":"默认2天，填写数字"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_mEntity.deviceIcon","placeholder":"","name":"设备Icon图","desc":"自定义Icon图，如：💻，不填，默认为不显示"}]
# [param: {"required":false,"key":"buzhi_mEntity.dateIcon","placeholder":"","name":"日期Icon图","desc":"自定义Icon图，如：⏱，不填，默认为不显示"}]
# [param: {"required":false,"key":"buzhi_mEntity.airIcon","placeholder":"","name":"空军Icon图","desc":"自定义Icon图，如：💨，不填，默认为不显示"}]
# [param: {"required":false,"key":"buzhi_mEntity.entityIcon","placeholder":"","name":"中奖Icon图","desc":"自定义Icon图，如：🎁，不填，默认为不显示"}]

import requests
import json
import os
import sys
import middleware
from datetime import datetime, timedelta, date
import re
import time

# 获取发送者ID
senderID = middleware.getSenderID()
# # 创建发送者
sender = middleware.Sender(senderID)
# # 获取用户id
userId = sender.getUserID()
# # 获取渠道
imType = sender.getImtype()
# # 获取触发信息
message = sender.getMessage()
isAdmin = sender.isAdmin()

filePathBox = middleware.bucketGet("buzhi_mEntity", "filePathBox")  # 路径查询开关
pathsBox = middleware.bucketGet("buzhi_mEntity", "pathsBox")  # 多路径
filePath = middleware.bucketGet("buzhi_mEntity", "filePath")  # 文件路径
filePathNum = 0
if filePathBox == "true":
    if not filePath:
        sender.reply("配参还没填写文件路径")
        sys.exit()
    if pathsBox == "true":
        if "/" not in filePath and "," not in filePath:
            sender.reply("当前开启多路径模式，请检查文件路径是否正确或是多个路径")
            sys.exit()
    else:
        filePath = f"/autMan/task/scripts/{filePath}/auto/"
filePath = filePath.split(",")
filePathNum = len(filePath)

deviceName = middleware.bucketGet("buzhi_mEntity", "deviceName")  # 命名
mergeBox = middleware.bucketGet("buzhi_mEntity", "mergeBox")  # 合并输出
deviceNames = middleware.bucketGet("buzhi_mEntity", "deviceNames")  # 合并命名
deviceName = deviceName.split(",")
if pathsBox == "true" and filePathBox == "true":
    if len(deviceName) < filePathNum:
        for i in range(len(deviceName), filePathNum):
            deviceName.append(f"路径查询{i}")

#  文本链接
shareLinkBox = middleware.bucketGet("buzhi_mEntity", "shareLinkBox")
if shareLinkBox == "true":
    shareLinks = middleware.bucketGet("buzhi_mEntity", "shareLinks")
    if not shareLinks:
        sender.reply("配参还没填写文本链接")
        sys.exit()
    else:
        shareLinks = shareLinks.split(",")
    linkDeviceNames = middleware.bucketGet("buzhi_mEntity", "linkDeviceNames")
    linkDeviceNames = linkDeviceNames.split(",")
    if len(linkDeviceNames) < len(shareLinks):
        for i in range(len(linkDeviceNames), len(shareLinks)):
            linkDeviceNames.append(f"文本链接查询{i}")

qinglong = {}  # 青龙信息
qlBox = middleware.bucketGet("buzhi_mEntity", "qlBox")
if qlBox == "true":
    qlNames = middleware.bucketGet("buzhi_mEntity", "qlNames")
    if qlNames:
        qlNames = qlNames.split(",")
    else:
        sender.reply("开启青龙查询，未填写奥特曼对接的青龙名称")
        exit(0)
    qlFilePaths = middleware.bucketGet("buzhi_mEntity", "qlFilePaths")
    qlFilePaths = qlFilePaths.split(",")
    if len(qlFilePaths) != len(qlNames):
        sender.reply("青龙文件路径个数和填写对接的青龙个数不一致")
        exit(0)
    qlDeviceName = middleware.bucketGet("buzhi_mEntity", "qlDeviceName")
    if qlDeviceName:
        qlDeviceName = qlDeviceName.split(",")
        if len(qlDeviceName) < len(qlNames):
            for i in range(len(qlDeviceName), len(qlNames)):
                qlDeviceName.append(qlNames[i])
    else:
        qlDeviceName = qlNames
        

searchDays = middleware.bucketGet("buzhi_mEntity", "searchDays")  # 默认查询天数

deviceIcon = middleware.bucketGet("buzhi_mEntity", "deviceIcon")
dateIcon = middleware.bucketGet("buzhi_mEntity", "dateIcon")
airIcon = middleware.bucketGet("buzhi_mEntity", "airIcon")
entityIcon = middleware.bucketGet("buzhi_mEntity", "entityIcon")

if not searchDays:
    searchDays = 2
else:
    try:
        searchDays = int(searchDays)
    except:
        sender.reply("默认查询天数填写数字！")
        sys.exit()

dateList = []  # 日期列表
today = date.today()
todayStr = today.strftime("%Y-%m-%d")
yesterdayStr = (today - timedelta(days=1)).strftime("%Y-%m-%d")


def updataDateList(days):
    dateList.append(today.strftime("%Y-%m-%d"))
    for i in range(1, days):
        dateList.append((today - timedelta(days=i)).strftime("%Y-%m-%d"))


entitys = {}  # 实物数据


def initializeEntitys():
    for date in dateList:
        entitys[date] = {}  # 初始化数据


entityTexts = []  # 实物文本
keywordSwList = []  # 关键字实物列表
search_num = ""  # 实物搜索个数


class Qinglong:
    def __init__(self, ql_ipport, client_id, client_secret):
        self.ql_ipport = ql_ipport
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.get_token()

    def get_token(self):
        """
        连接青龙获取token
        """
        url = f"{self.ql_ipport}/open/auth/token?client_id={self.client_id}&client_secret={self.client_secret}"
        response = requests.get(url)
        if response.status_code == 200:
            token = response.json().get("data", {}).get("token")
            # print(token)
            return token
        else:
            return False

    def api_ql(self, api, apd, method, body="", way="open"):
        """
        其他接口
        """
        url = f"{self.ql_ipport}/{way}/{api}{apd}"
        # print(url)
        # print("token:", self.token)
        # print("body:", body)
        # print(method)

        headers = {
            # "Content-Type": "application/x-www-form-urlencoded",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": "Bearer " + self.token,
        }

        response = requests.request(method, url, headers=headers, data=body)
        # print(response.url)
        return response.json()

    def get_script(self, file, path):
        """
        获取脚本内容
        """
        return self.api_ql(
            "scripts",
            f"/detail?file={file}&path={path}&t={str(round(time.time() * 1000))}",
            "get",
            "",
        )

    def save_script(self, fileName, path, data):
        """
        保存脚本内容
        """
        body = {"content": data, "filename": fileName, "path": path}
        return self.api_ql(
            "",
            f"/scripts?t={str(round(time.time() * 1000))}",
            "put",
            json.dumps(body),
        )


def getAutQL():
    """
    获取青龙信息
    """
    try:
        qls = []
        qlsId = sender.bucketAllKeys("qls")
        for qlid in qlsId:
            ql = json.loads(sender.bucketGet("qls", qlid))
            qls.append(ql)
        for ql in qls:
            if ql["name"] in qlNames:
                qinglong[ql["name"]] = ql
        ql_list = qinglong.keys()
        for ql in qlNames:
            if ql not in ql_list:
                sender.reply(f"{ql}：未在奥特曼对接的青龙中找到对应的信息")
    except:
        sender.reply(f"青龙名称填写错误或未给qinglong权限")


def getLinkSW(keyword=""):
    """
    链接文本实物处理
    """
    print("处理链接实物")
    for index, link in enumerate(shareLinks):
        response = requests.get(link)
        if response.status_code == 200:
            lines = response.text.split("\n")
            try:
                if not keyword:
                    txtProcess(lines, linkDeviceNames[index])
                else:
                    searchKeywordSW(lines, keyword, linkDeviceNames[index])
            except Exception as e:
                sender.reply(f"获取第{index+1}个链接中的实物遇到问题，{e}")
        else:
            sender.reply(f"请检查链接第{index+1}个链接是否正确！")


def autPathSW(keyword=""):
    """
    奥特曼docker多路径处理
    """
    print("处理奥特曼实物")
    # 开启多路径查询
    for index, path in enumerate(filePath):
        try:
            os.chdir(path)
            print("当前路径2：", os.getcwd())
            with open("gifts.csv", "r", encoding="utf-8") as file:
                lines = file.readlines()
                try:
                    if not keyword:
                        txtProcess(lines, deviceName[index])
                    else:
                        searchKeywordSW(lines, keyword, deviceName[index])
                except Exception as e:
                    sender.reply(f"获取第{index+1}个路径文件中的实物遇到问题，{e}")
        except Exception as e:
            sender.reply(f"请检查文件夹路径{index+1}是否正确！！！{e}")


def qlPathSW(keyword=""):
    """
    获取青龙实物
    """
    print("处理青龙实物")
    # 开启多青龙查询
    for ql_name, ql_data in qinglong.items():
        time.sleep(1)
        # try:
        ql_link = Qinglong(ql_data["host"], ql_data["client_id"], ql_data["client_secret"])
        index = qlNames.index(ql_name)
        file_content = ql_link.get_script("gifts.csv", qlFilePaths[index])
        if file_content.get("code", 0) == 200:
            lines = file_content.get("data", "").split("\n")
            try:
                if not keyword:
                    txtProcess(lines, qlDeviceName[index])
                else:
                    searchKeywordSW(lines, keyword, qlDeviceName[index])
            except Exception as e:
                sender.reply(f"获取【{ql_name}】青龙中的实物遇到问题，{e}")
        else:
            sender.reply(f"【{ql_name}】青龙请求获取实物信息失败")
        # except Exception as e:
        #     sender.reply(f"【{ql_name}】读取实物信息失败！{e}")


def txtProcess(lines, deviceName):
    """
    文本处理
    @ lines 文本行
    @ type 1:autPathSW 2:shareLinkSW
    """
    counts = {}
    today_num = 0
    yesterday_num = 0
    date_num = 0
    for date in dateList:
        counts[date] = {}
    entity_text = f"{deviceIcon}设备：{deviceName}"
    for line in lines:
        if not line:
            continue
        # 使用逗号分割每一行数据
        parts = line.split(",")
        # 提取日期部分
        date_str = parts[0][:10]
        # 提取第二个逗号后的物品名（即索引为2的部分）
        item_name = parts[1].strip()
        if date_str in dateList:
            isExist = counts.get(date_str, 0)
            isExists = entitys.get(date_str, 0)
            if isExist:
                if isExist.get(item_name, 0):
                    isExist[item_name] += 1
                    counts[date_str] = isExist
                else:
                    isExist[item_name] = 1
                    counts[date_str] = isExist
            else:
                counts[date_str] = {item_name: 1}
            if isExists:
                if isExists.get(item_name, 0):
                    isExists[item_name] += 1
                    entitys[date_str] = isExists
                else:
                    isExists[item_name] = 1
                    entitys[date_str] = isExists
            else:
                entitys[date_str] = {item_name: 1}
            # print(f"{item_name}:{isExists.get(item_name, 0)}")
    # 合并所有物品名和数量
    for date, value in counts.items():
        entity_text += f"\n{'-' * 12}\n{dateIcon}时间：{date}"
        if len(value.keys()):
            # if isinstance(value, dict) and value:
            for name, num in value.items():
                entity_text += f"\n{entityIcon}{name} ({num})"
                today_num += num if date == todayStr else 0
                yesterday_num += num if date == yesterdayStr else 0
                date_num += num
        else:
            entity_text += f"\n{airIcon}" if airIcon else "\n空"
    if todayStr in dateList:
        entity_text += f"\n今日收获{today_num}个实物"
    if len(dateList) > 1:
        if yesterdayStr in dateList:
            if todayStr in dateList:
                entity_text += f"，昨日收获{yesterday_num}个，{len(dateList)}天共收获{date_num}个实物"
            else:
                entity_text += f"\n昨日收获{yesterday_num}个，{len(dateList)}天共收获{date_num}个实物"
        else:
            entity_text += f"{len(dateList)}天共收获{date_num}个实物"
    else:
        if todayStr in dateList:
            entity_text += f"，{len(dateList)}天共收获{date_num}个实物"
        else:
            entity_text += f"\n{len(dateList)}天共收获{date_num}个实物"
    entityTexts.append(entity_text)


def searchSW(date_list: list = ""):
    """
    查询实物
    """
    global dateList
    if date_list:
        dateList = date_list
        initializeEntitys()
    # 路径文件查询
    if filePathBox == "true":
        autPathSW()
    #  链接查询
    if shareLinkBox == "true":
        getLinkSW()
    # 青龙查询
    if qlBox == "true":
        getAutQL()
        qlPathSW()
    if filePathBox == "true" or shareLinkBox == "true" or qlBox == "true":
        if mergeBox == "true":
            today_num = 0
            yesterday_num = 0
            date_num = 0
            entity_text = f"{deviceIcon}设备：{deviceNames}"
            # 合并所有物品名和数量
            for date, value in entitys.items():
                entity_text += f"\n{'-' * 12}\n{dateIcon}时间：{date}"
                if len(value.keys()):
                    for name, num in value.items():
                        entity_text += f"\n{entityIcon}{name} ({num})"
                        today_num += num if date == todayStr else 0
                        yesterday_num += num if date == yesterdayStr else 0
                        date_num += num
                else:
                    entity_text += f"\n{airIcon}" if airIcon else "\n空"
            if todayStr in dateList:
                entity_text += f"\n今日收获{today_num}个实物"
            if len(dateList) > 1:
                if yesterdayStr in dateList:
                    if todayStr in dateList:
                        entity_text += f"，昨日收获{yesterday_num}个，{len(dateList)}天共收获{date_num}个实物"
                    else:
                        entity_text += f"\n昨日收获{yesterday_num}个，{len(dateList)}天共收获{date_num}个实物"
                else:
                    entity_text += f"{len(dateList)}天共收获{date_num}个实物"
            else:
                if todayStr in dateList:
                    entity_text += f"，{len(dateList)}天共收获{date_num}个实物"
                else:
                    entity_text += f"\n{len(dateList)}天共收获{date_num}个实物"
            sender.reply(entity_text)
        else:
            for text in entityTexts:
                sender.reply(text)
    else:
        sender.reply("当前未开启查询方式！")


def searchKeywordSW(lines, keyword, deviceName=""):
    """
    查询关键词实物信息
    """
    data_list = []
    entity_text = f"{deviceIcon}设备：{deviceName}"
    for line in lines:
        if not line:
            continue
        # 使用逗号分割每一行数据
        parts = line.split(",")
        # 提取日期部分
        date_str = parts[0][:10]
        # 提取第二个逗号后的物品名（即索引为2的部分）
        data_pin = parts[2]
        data_phone = parts[3]
        data_address = parts[4]
        data_shop = parts[6]
        data_link = parts[7]
        item_name = parts[1].strip()
        if keyword in item_name:
            keyword_sw_dic = {
                "时间": date_str,
                "账号": data_pin,
                "商品": item_name,
                "店铺": data_shop,
                "手机号": data_phone,
                "地址": data_address,
                "链接": data_link,
                "设备": deviceName,
            }
            data_list.append(keyword_sw_dic)
            keywordSwList.append(keyword_sw_dic)

    # 合并所有物品名和数量
    if len(data_list):
        for index, data in enumerate(data_list):
            # if index != len(data_list) -1:
            if mergeBox == "false":
                if index == search_num:
                    break
            entity_text += f"\n{'-' * 12}\n🧭时间：{data['时间']}\n🆔账号：{data['账号']}\n🎁商品：{data['商品']}\n🏪店铺：{data['店铺']}\n📱手机号：{data['手机号']}\n🌎️地址：{data['地址']}\n🚀链接：{data['链接']}"
    else:
        entity_text += f"\n{airIcon}" if airIcon else "\n未查到指定关键词的中奖信息"
    entity_text += f"\n共查到{len(data_list)}条含有关键词【{keyword}】的实物信息"
    entityTexts.append(entity_text)


def searchSWInfo(keyword):
    """
    查询关键词实物信息
    """
    # 路径文件查询
    if filePathBox == "true":
        autPathSW(keyword)
    #  链接查询
    if shareLinkBox == "true":
        getLinkSW(keyword)
    # 青龙查询
    if qlBox == "true":
        getAutQL()
        qlPathSW(keyword)
    if filePathBox == "true" or shareLinkBox == "true" or qlBox == "true":
        if mergeBox == "true":
            entity_text = f"{deviceIcon}设备：{deviceNames}"
            if len(keywordSwList):
                for index, keywordInfo in enumerate(keywordSwList):
                    if index == search_num:
                        break
                    entity_text += f"\n{'-' * 12}\n🧭时间：{keywordInfo['时间']}\n🆔账号：{keywordInfo['账号']}\n🎁商品：{keywordInfo['商品']}\n🏪店铺：{keywordInfo['店铺']}\n📱手机号：{keywordInfo['手机号']}\n🌎️地址：{keywordInfo['地址']}\n🚀链接：{keywordInfo['链接']}"
            else:
                entity_text += f"\n{airIcon}" if airIcon else "\n未查到"
            entity_text += (
                f"\n共查到{len(keywordSwList)}条含有关键词【{keyword}】的实物信息"
            )
            sender.reply(entity_text)
        else:
            for text in entityTexts:
                sender.reply(text)
    else:
        sender.reply("当前未开启查询方式！")


def delKeyWorod(keyword):
    """
    删除关键字实物
    """
    # 开启多路径查询
    # 路径文件查询
    if filePathBox == "true" or qlBox == "true":
        if filePathBox == "true":
            for index, path in enumerate(filePath):
                del_num = 0
                try:
                    os.chdir(path)
                    print("当前路径M：", os.getcwd())
                    temp_file_path = os.getcwd() + "/保留.tmp"
                    print(f"开始删除含有【{keyword}】关键词的实物信息")
                    # lines = ""
                    try:
                        # 打开原始文件和临时文件
                        with open("gifts.csv", "r", encoding="utf-8") as read_file, open(
                            temp_file_path, "w", encoding="utf-8"
                        ) as write_file:
                            lines = read_file.readlines()
                            for line in lines:
                                if not line:
                                    continue
                                if keyword not in line:
                                    write_file.write(line)
                                else:
                                    del_num += 1

                        # 使用os.rename()重命名临时文件为原文件
                        os.replace(
                            temp_file_path, "gifts.csv"
                        )  # 使用os.replace确保原子操作
                        sender.reply(
                            f"{deviceIcon}设备：{deviceName[index]}\n{'-' * 12}\n删除{del_num}条含有【{keyword}】关键词的实物信息"
                        )
                    except Exception as e:
                        print(f"发生错误: {e}")
                        sender.reply(
                            f"{deviceIcon}设备：{deviceName[index]}\n{'-' * 12}\n删除关键词出现错误！"
                        )
                        # 在发生错误时删除临时文件（如果存在）
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)
                except Exception as e:
                    sender.reply(f"请检查文件夹路径{index+1}是否正确！！！{e}")
        if qlBox == "true":
            getAutQL()
            for ql_name, ql_data in qinglong.items():
                try:
                    ql_link = Qinglong(ql_data["host"], ql_data["client_id"], ql_data["client_secret"])
                    index = qlNames.index(ql_name)
                    file_content = ql_link.get_script("gifts.csv", qlFilePaths[index])
                    time.sleep(1)
                    lines = file_content.get("data", "").split("\n")
                    del_num = 0
                    print(f"开始删除青龙【{ql_name}】实物含有【{keyword}】关键词的实物信息")
                    new_lines = ""
                    try:
                        for index2, line in enumerate(lines):
                            if not line or keyword not in line:
                                if index2 != len(lines) - 1:
                                    new_lines += f"\n{line}"
                                else:
                                    new_lines += line
                            else:
                                del_num += 1
                        # 修改文件
                        try:
                            save_response = ql_link.save_script("gifts.csv", qlFilePaths[index], new_lines)
                            if save_response.get("code", 0) == 200:
                                sender.reply(
                                    f"{deviceIcon}设备：{qlDeviceName[index]}\n{'-' * 12}\n删除{del_num}条含有【{keyword}】关键词的实物信息"
                                )
                            else:
                                sender.reply(
                                    f"{deviceIcon}设备：{qlDeviceName[index]}\n{'-' * 12}\n删除【{keyword}】关键词实物失败，青龙文件修改失败"
                                )
                        except Exception as e:
                            print(f"修改文件时发生错误: {e}")
                            sender.reply(
                                f"{deviceIcon}设备：{qlDeviceName[index]}\n{'-' * 12}\n删除【{keyword}】修改文件时发生错误！"
                            )
    
                    except Exception as e:
                        print(f"发生错误: {e}")
                        sender.reply(
                            f"{deviceIcon}设备：{qlDeviceName[index]}\n{'-' * 12}\n删除【{keyword}】修改文件时发生错误！"
                        )
                except Exception as e:
                    sender.reply(f"【{ql_name}】读取实物信息失败！{e}")
    else:
        sender.reply("当前未开启奥特曼路径查询或青龙查询配参，无法使用关键词删除！")


def get_date_range(start_date, end_date, date_format="%Y-%m-%d"):
    """
    获取两个日期之间的所有日期列表

    参数:
    start_date -- 开始日期，格式为YYYYMMDD的字符串
    end_date -- 结束日期，格式为YYYYMMDD的字符串
    date_format -- 返回日期的格式，默认为"%Y-%m-%d"

    返回:
    日期字符串列表，格式为指定的date_format
    """
    # 将字符串转换为datetime对象
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")

    # 初始化日期列表
    date_list = []

    # 生成日期范围
    current_date = start
    while current_date <= end:
        date_list.append(current_date.strftime(date_format))
        current_date += timedelta(days=1)

    return date_list


if __name__ == "__main__":
    if "实物 " in message:
        try:
            date_str = message.split(" ")[1]
            if len(date_str):
                date_list = date_str.split("-")
                if len(date_list) > 1 and int(date_list[0]) and int(date_list[1]):
                    searchSW(get_date_range(date_list[0], date_list[1]))
                elif len(date_list) == 1 and int(date_list[0]):
                    searchSW(
                        [datetime.strptime(date_list[0], "%Y%m%d").strftime("%Y-%m-%d")]
                    )
            else:
                sender.reply("未指定日期！")
        except:
            sender.reply("指定日期格式错误！")
    elif "实物+" in message:
        mess = re.sub(r"^M?实物\+", "", message)
        if mess:
            mess_lsit = mess.split(" ")
            if len(mess_lsit) > 1:
                if mess_lsit[1].isdigit():
                    search_num = int(mess_lsit[1])
                    if search_num > 0:
                        searchSWInfo(mess_lsit[0])
                    else:
                        sender.reply("查询关键字条数不为小于1")
                else:
                    sender.reply("查询关键字个数非正整数字！")
            else:
                searchSWInfo(mess_lsit[0])
        else:
            sender.reply("指定查询关键词不能为空!")
    elif "实物-" in message:
        mess = re.sub(r"^M?实物-", "", message)
        if mess:
            delKeyWorod(mess)
        else:
            sender.reply("指定删除关键词不能为空!")
    elif len(re.compile(r"^M?实物\d+$").findall(message)):
        searchDays = int(re.findall(r"\d+$", message)[0])
        updataDateList(searchDays)
        initializeEntitys()
        searchSW()
    else:
        updataDateList(searchDays)
        initializeEntitys()
        searchSW()
