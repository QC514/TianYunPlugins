# [pin:true]
# ==========================市场元数据=========================================
# [open_source: false]是否开源
# [title: JD店铺签到]
# [author: buzhi]
# [icon: https://pic.ziyuan.wang/2023/12/10/guest_ff977392d9673.png]图标链接地址，支持http和https
# [version: 3.0.10]
# [description: 【指令】总指令：店铺签到。<br/>指令：爬签到（爬取当天的店铺签到信息，配参开启解析token，建议21:30后跑爬）<br/>指令：tokens：###&###(###为解析的token数据)<br/>指令：店铺签到 含店铺签到的链接信息<br/>指令：店铺清理或dpql（对指定青龙中的token进行检测清理无效和无豆的token）<br/>【要求】①自行填写容器配参<br/>②需要python3环境和依赖：requests、bs4。依赖安装路径（奥特曼web->脚本容器->依赖管理->新增（python3依赖））<br/>【说明】配参开启定时开关后每天23:30自动爬取当天店铺签到信息，并解析入库指定容器拉起“店铺签到”脚本进行运行。请自行给容器中的“店铺签到”任务定时零点签到。默认6dy库“店铺签到”，其他签到请更改配参。<br/>【更新】本次带来重构后的3.0版本，更新特性如下：<br/>1、配参CK位置可填多个，增加爬签到token解析筛选开关。<br/>2、增加单运行签到脚本指令：运行签到或签到运行。<br/>3、增加获取当前容器token指令：tokens。<br/>4、增加自定义UA、H5接口（待测试）<br/>5、新增20token上限功能，不需要的到配参进行关闭<br/>更新：修复token清理中检测失败导致的token被清问题<br/>【教程说明】<a href="https://docs.qq.com/doc/DZGpYYUZIYUZVTUhE">点击查看教程</a><br/>【交流群】QQ群：862839828]
# [platform: qq,wx]
# [public:true]
# [price: 8.8]
# [service: Q群862839828]
# [class: 工具类]
# ==========================函数解析元数据======================================
# [rule: ^(店铺签到|dpqd|店铺清理|dpql|tokens|爬签到|运行签到|签到运行|tokens：[A-F0-9\W]+)$] 匹配规则，多个规则时向下依次写多个
# [rule: ^(店铺签到|dpqd) ([\s\S]+)$]
# [priority: 1000 ]
# [admin: true]
# [disable:false]
# [cron: 30 23 * * *]
# ==========================参数配置数据（最下面）===============================
# [param: {"required":false,"key":"buzhi_JdDpSign.versionBox","placeholder":"","bool":true,"name":"适配开关","desc":"奥特曼2.5.5以下版本，可开启此开关并根据目标容器注释填写<br/>2.5.5及以上版本请关闭此开关，并根据目标容器注释填写<br/>2.5.7及以上版本可填写容器名格式但要开启此开关并给qls权限"}]
# [param: {"required":true,"key":"buzhi_JdDpSign.container","placeholder":"","name":"目标容器","desc":"2.5.5以下版本：请开启上面版本适配开关并填写容器管理=>对接容器 里面容器的名称，多容器用英文逗号隔开，如：容器1,容器2；<br/>2.5.5以上版本：请关闭上面版本适配开关并按照示例填写，单容器：\u005b\u007b\u0022\u006e\u0061\u006d\u0065\u0022\u003a\u0022\u9752\u9f99\u0031\u0022\u002c\u0022\u0068\u006f\u0073\u0074\u0022\u003a\u0022\u0068\u0074\u0074\u0070\u003a\u002f\u002f\u0069\u0070\u003a\u7aef\u53e3\u0022\u002c\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0069\u0064\u0022\u003a\u0022\u0078\u0078\u0078\u0022\u002c\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0073\u0065\u0063\u0072\u0065\u0074\u0022\u003a\u0022\u0078\u0078\u0078\u0022\u007d\u005d<br/>多容器请以英文逗号隔开：\u005b\u007b\u0022\u006e\u0061\u006d\u0065\u0022\u003a\u0022\u9752\u9f99\u0031\u0022\u002c\u0022\u0068\u006f\u0073\u0074\u0022\u003a\u0022\u0068\u0074\u0074\u0070\u003a\u002f\u002f\u0069\u0070\u003a\u7aef\u53e3\u0022\u002c\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0069\u0064\u0022\u003a\u0022\u0078\u0078\u0078\u0022\u002c\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0073\u0065\u0063\u0072\u0065\u0074\u0022\u003a\u0022\u0078\u0078\u0078\u0022\u007d\u002c\u007b\u0022\u006e\u0061\u006d\u0065\u0022\u003a\u0022\u9752\u9f99\u0032\u0022\u002c\u0022\u0068\u006f\u0073\u0074\u0022\u003a\u0022\u0068\u0074\u0074\u0070\u003a\u002f\u002f\u0069\u0070\u003a\u7aef\u53e3\u0022\u002c\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0069\u0064\u0022\u003a\u0022\u0078\u0078\u0078\u0022\u002c\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0073\u0065\u0063\u0072\u0065\u0074\u0022\u003a\u0022\u0078\u0078\u0078\u0022\u007d\u005d"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_JdDpSign.scriptName","placeholder":"6dylan6_jdpro/jd_dpqd_main.js,6dylan6_jdpro/jd_dpqd_sign.js","name":"脚本名","desc":"这里填库名/脚本名，如：6dylan6_jdpro/jd_dpqd_main.js,6dylan6_jdpro/jd_dpqd_sign.js 默认6dy库店铺签到，同一个库多个店铺签到请用“,”分割,按签到顺序填写"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.variable","placeholder":"jd_dpqd_tokens","name":"变量名","desc":"这里填环境变量名，默认6dy库环境变量jd_dpqd_tokens"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.splits","placeholder":"&","name":"token分隔符","desc":"这里填多个token之间的分隔符，请填写,、&、@、|等，默认为,"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.ckIndex","placeholder":"","name":"CK位置","desc":"请填写数字，用于获取JDCK有效CK指定位置用于获取店铺token，多个用英文逗号隔开，默认为1"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.optionSaveBox","placeholder":"","bool":true,"name":"tokens储存位置","desc":"关，则将tokens保存在配置文件；开，则将tokens保存在环境变量中"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.tokenSignBox","placeholder":"","bool":true,"name":"爬签到解析开关","desc":"是否开启解析token，只针对“爬签到”指令，默认不解析"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.tokenSignInfoBox","placeholder":"","bool":true,"name":"爬签token筛选开关","desc":"针对“爬签到”指令，在开启解析token开关后，是否进行token筛选，不会储存和运行青龙签到，默认不开启"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.tokenSignInfoBox2","placeholder":"","bool":true,"name":"tokens 指令筛选开关","desc":"针对“tokens xxx”指令，开启此开关将筛选token，默认不开启"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.dpzmQlBox","placeholder":"","bool":true,"name":"店铺转码运行签到开关","desc":"是否开启店铺签到转码拉起店铺签到脚本，只针对“店铺签到 签到信息”指令，默认不拉起签到"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.delay","placeholder":"3","name":"token解析延迟","desc":"请填写阿拉伯数字如：1，填1则表示解析多个token中间延迟1秒，不填则走默认延迟4秒，请正确填写。"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.tokenDelay","placeholder":"1","name":"token检测延迟","desc":"请填写阿拉伯数字如：1，填1则表示检测多个token中间延迟1秒，不填则走默认延迟1秒，解析失败属于正常。"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_JdDpSign.tokenIfoBox","placeholder":"","bool":true,"name":"Token信息开关","desc":"是否开启店铺信息输出和token筛选功能，默认不开启"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.firstSignBox","placeholder":"","bool":true,"name":"首签筛选开关","desc":"判断当天的店铺token是否为首次签到，非首签不入库，默认不开启"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.off20Box","placeholder":"","bool":true,"name":"关闭token限制","desc":"关闭储存token是否超过20个的判断，超过则不入库"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.tokenRetry","placeholder":"5","name":"token检测次数","desc":"在token检测失败时，token重新检测的最大次数,，默认为5"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.beansNums","placeholder":"","name":"最低豆数量","desc":"填写阿拉伯数字如：10，所填为最低入库标准，与豆份额数为且关系，不填为空则默认豆数量不影响入库"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.beansShare","placeholder":"","name":"最低豆份额数","desc":"填写阿拉伯数字如：100，所填为最低入库标准，与豆数量为且关系，不填为空则默认豆份额数不影响入库"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.maxBeansDays","placeholder":"","name":"最长天数","desc":"填写阿拉伯数字如：10，所填为最大入库标准，与豆数量、份额为且关系，不填为空则不影响入库"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_JdDpSign.notify","placeholder":"","name":"管理员通知类型","desc":"多个用英文逗号隔开。可选qq、qb、wx、wb、tg、tb等。默认全通知"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.shopUrl","placeholder":"","name":"店铺信息地址","desc":"这里可以自定义填写自己的店铺信息地址，默认空就行，不要乱填！！！"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_JdDpSign.customUA","placeholder":"","name":"UA","desc":"UA自定义地址，填写请求地址"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.customH5","placeholder":"","name":"H5","desc":"H5自定义地址，填写请求地址"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_JdDpSign.fakeBox","placeholder":"","bool":true,"name":"定时开关","desc":"是否开启定时开关，默认不开启，开启最好填写管理员通知类型配参"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_JdDpSign.proxyBox","placeholder":"","bool":true,"name":"代理开关","desc":"是否启用代理，开启后下面填写的代理才生效"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.proxy","placeholder":"","name":"代理池地址","desc":"auto-proxy-pool格式：http://ip:端口号，只在提取token和检测token时使用"}]
# [param: {"required":false,"key":"buzhi_JdDpSign.apiProxy","placeholder":"","name":"api代理","desc":"api代理直链，只在提取token和检测token时使用"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_JdDpSign.saveTokenInfo","placeholder":"","bool":true,"name":"","desc":"请不要勾选"}]

#   --------------------------------一般不动区--------------------------------
#                     _ooOoo_
#                    o8888888o
#                    88" . "88
#                    (| -_- |)
#                     O\ = /O
#                 ____/`---'\____
#               .   ' \\| |// `.
#                / \\||| : |||// \
#              / _||||| -:- |||||- \
#                | | \\\ - /// | |
#              | \_| ''\---/'' | |
#               \ .-\__ `-` ___/-. /
#            ___`. .' /--.--\ `. . __
#         ."" '< `.___\_<|>_/___.' >'"".
#        | | : `- \`.;`\ _ /`;.`/ - ` : | |
#          \ \ `-. \_ __\ /__ _/ .-` / /
#  ======`-.____`-.___\_____/___.-`____.-'======
#                     `=---='
#
#  .............................................
#           佛祖保佑             永无BUG
#           佛祖镇楼             BUG辟邪
# 佛曰:
#        写字楼里写字间，写字间里程序员；
#        程序人员写程序，又拿程序换酒钱。
#        酒醒只在网上坐，酒醉还来网下眠；
#        酒醉酒醒日复日，网上网下年复年。
#        但愿老死电脑间，不愿鞠躬老板前；
#        奔驰宝马贵者趣，公交自行程序员。
#        别人笑我忒疯癫，我笑自己命太贱；
#        不见满街漂亮妹，哪个归得程序员？
#
#   --------------------------------更新日志区--------------------------------
#  更新日志
# -2024/08/17 16点-
# -2024/11/16 拾起代码进行修改
# -2024/11/23 3.0初版代码完成
# -3.0.0
# --1.重构代码。
# --2.新增token20上限
# --3.新增自定义UA、H54.2
# --4.修复获取token的api接口
# --4.增加获取CK用与获取token
# --5.增加运行签到、签到运行指令
# --6.优化代码结构
# -3.0.5
# -1、修复单脚本运行问题；2、token切换解析逻辑增加延迟；3、修复已知问题
# -3.0.6
# -1、修复配参豆限制未填不入库的问题;2、修复json格式参数外漏问题
# -3.0.7
# -1、修复token清理时，检测失败导致token被清除的问题
#   --------------------------------代码区--------------------------------

import middleware
import os, sys
import datetime
import json
import time
import re
import random

# import concurrent.futures
import copy

#   --------------------------------初始化中间件--------------------------------
# 获取发送者ID
senderID = middleware.getSenderID()
# 创建发送者
sender = middleware.Sender(senderID)
# 获取发送者类型,定时的类型是fake
senderType = sender.getImtype()
# 获取触发信息
mess = sender.getMessage()
#   --------------------------------初始化通知功能和相关依赖--------------------------------
if senderType == "fake":
    mess = "店铺签到"

notify = middleware.bucketGet("buzhi_JdDpSign", "notify")  # 通知类型
if not notify:
    notify = ["qq", "qb", "wx", "tg", "wb"]
else:
    notify = notify.split(",")
print(f"当前通知平台：{notify}")
# 判断是否安装了bs4依赖
try:
    from bs4 import BeautifulSoup
except:
    if senderType == "fake":
        middleware.notifyMasters("正在安装bs4依赖，请稍后...", notify)
    else:
        sender.reply("正在安装bs4依赖，请稍后...")
    middleware.pip_install("bs4")
    try:
        from bs4 import BeautifulSoup
    except:
        if senderType == "fake":
            middleware.notifyMasters("bs4安装失败，请手动安装bs4", notify)
        else:
            sender.reply("bs4安装失败，请手动安装bs4")
        sys.exit()
# 判断是否安装了requests依赖
try:
    import requests
except:
    if senderType == "fake":
        middleware.notifyMasters("正在安装requests依赖，请稍后...", notify)
    else:
        sender.reply("正在安装requests依赖，请稍后...")
    middleware.pip_install("requests")
    try:
        import requests
    except:
        if senderType == "fake":
            middleware.notifyMasters("requests安装失败，请手动安装requests", notify)
        else:
            sender.reply("requests安装失败，请手动安装requests")
        sys.exit()
#   --------------------------------初始化日期、全局变量--------------------------------
today = datetime.date.today()
# 设计几个日期格式，用于爬取店铺信息
date_string = today.strftime("%m月%d日")
date_string2 = today.strftime("%m月%d")
date_string3 = today.strftime("%m.%d")
date_month = datetime.datetime.now().month
date_day = datetime.datetime.now().day
# date_string = "11月 30日"
tokenNums = 0
tokenNewNums = 0
# isRqm == True: 填写的目标容器为容器名称，False:填写目标容器为json格式
isRqm = True
# atmVersion == False: atm为低版本不适配权限授权模式，True: atm为高版本兼容权限授权模式
atmVersion = True
#   --------------------------------根据是否为定时触发，导入配参数据--------------------------------
fakeBox = middleware.bucketGet("buzhi_JdDpSign", "fakeBox")  # 定时开关
if fakeBox == "true" or senderType != "fake":
    # 获取当前插件名称
    pluginName = sender.getPluginName()
    # 奥特曼版本适配开关
    versionBox = middleware.bucketGet("buzhi_JdDpSign", "versionBox")
    # 获取容器名称
    container = middleware.bucketGet("buzhi_JdDpSign", "container")
    if container == "":
        middleware.notifyMasters("【JD店铺签到】目标容器不能为空", notify)
        sys.exit()
    elif "，" in container:
        middleware.notifyMasters("【JD店铺签到】请使用英文逗号分割", notify)
        sys.exit()
    # 获取奥特曼版本号
    autVersion = middleware.version()["sn"]
    # -----------------------------------#
    # 以奥特曼2.5.5版本为界限进行适配
    # -----------------------------------#
    if versionBox == "false" or versionBox == "":
        if "name" in container and "host" in container and "client_id" in container:
            print(container)
            qlNameList = json.loads(container)
            isRqm = False
        else:
            if senderType == "fake":
                middleware.notifyMasters(
                    f"【{pluginName}】提醒您，当前奥特曼版本{autVersion}，当前适配开关关闭，请按照注释目标容器填写正确的JSON格式！",
                    notify,
                )
            else:
                sender.reply(
                    f"【{pluginName}】提醒您，当前奥特曼版本{autVersion}，当前适配开关关闭，请按照注释目标容器填写正确的JSON格式！"
                )
            sys.exit()
    else:
        if autVersion < "2.5.5":
            atmVersion = False
            if "name" in container and "host" in container and "client_id" in container:
                if senderType == "fake":
                    middleware.notifyMasters(
                        f"【{pluginName}】提醒您，当前奥特曼版本{autVersion}，当前适配开关已打开，请按照注释目标容器填写正确的容器名！",
                        notify,
                    )
                else:
                    sender.reply(
                        f"【{pluginName}】提醒您，当前奥特曼版本{autVersion}，当前适配开关已打开，请按照注释目标容器填写正确的容器名！"
                    )
                sys.exit()
            else:
                qlNameList = container.split(",")
                isRqm = True
        elif autVersion >= "2.5.5" and autVersion < "2.5.7":
            atmVersion = False
            if senderType == "fake":
                middleware.notifyMasters(
                    f"【{pluginName}】提醒您，当前奥特曼版本{autVersion}不支持填写容器名称，请按配参注释要求填写JSON格式",
                    notify,
                )
            else:
                sender.reply(
                    f"【{pluginName}】提醒您，当前奥特曼版本{autVersion}不支持填写容器名称，请按配参注释要求填写JSON格式"
                )
            sys.exit()
        elif autVersion >= "2.5.7":
            if "name" in container and "host" in container and "client_id" in container:
                if senderType == "fake":
                    middleware.notifyMasters(
                        f"【{pluginName}】提醒您，当前奥特曼版本{autVersion}，当前适配开关已打开，请按照注释目标容器填写正确的容器名！",
                        notify,
                    )
                else:
                    sender.reply(
                        f"【{pluginName}】提醒您，当前奥特曼版本{autVersion}，当前适配开关已打开，请按照注释目标容器填写正确的容器名！"
                    )
                sys.exit()
            else:
                atmVersion = True
                isRqm = True
                qlNameList = container.split(",")
        else:
            if senderType == "fake":
                middleware.notifyMasters(
                    f"【{pluginName}】提醒您，目标容器填写错误，请按配参注释要求重新填写目标容器配参",
                    notify,
                )
            else:
                sender.reply(
                    f"【{pluginName}】提醒您，目标容器填写错误，请按配参注释要求重新填写目标容器配参"
                )
            sys.exit()
    # -----------------------------------#
    # 导入配参信息，定义全局变量
    # -----------------------------------#
    ckIndex = middleware.bucketGet("buzhi_JdDpSign", "ckIndex")  # 获取指定位置的ck
    if ckIndex == "":
        ckIndex = [1]
    else:
        ckIndex = [int(i) for i in ckIndex.split(",")]
    scriptName = middleware.bucketGet("buzhi_JdDpSign", "scriptName")  # 脚本名
    variable = middleware.bucketGet("buzhi_JdDpSign", "variable")  # 环境变量名
    splits = middleware.bucketGet("buzhi_JdDpSign", "splits")  # 分隔符
    delay = middleware.bucketGet(
        "buzhi_JdDpSign", "delay"
    )  # 解析自定义延迟时间，单位秒
    tokenDelay = middleware.bucketGet(
        "buzhi_JdDpSign", "tokenDelay"
    )  # 检测token信息自定义时间，单位秒
    if not delay:
        delay = 3
    else:
        delay = int(delay)
    if not tokenDelay:
        tokenDelay = 2
    else:
        tokenDelay = int(delay)
    optionSaveBox = middleware.bucketGet(
        "buzhi_JdDpSign", "optionSaveBox"
    )  # token保存位置开关
    shopUrl = middleware.bucketGet("buzhi_JdDpSign", "shopUrl")  # 自定义店铺地址
    # aBox = middleware.bucketGet("buzhi_JdDpSign", "ABox")  # 签到解析开关
    proxyBox = middleware.bucketGet("buzhi_JdDpSign", "proxyBox")  # 代理开关
    auto_proxy = middleware.bucketGet("buzhi_JdDpSign", "proxy")  # 代理池地址
    apiProxy = middleware.bucketGet("buzhi_JdDpSign", "apiProxy")  # api代理
    tokenSignBox = middleware.bucketGet(
        "buzhi_JdDpSign", "tokenSignBox"
    )  # 爬签到指令解析开关
    tokenSignInfoBox = middleware.bucketGet(
        "buzhi_JdDpSign", "tokenSignInfoBox"
    )  # 爬签到指令信息输出开关
    tokenSignInfoBox2 = middleware.bucketGet(
        "buzhi_JdDpSign", "tokenSignInfoBox2"
    )  # tokens xxx token信息输出和筛选开关
    dpzmQlBox = middleware.bucketGet(
        "buzhi_JdDpSign", "dpzmQlBox"
    )  # 店铺签到转码拉起签到开关
    tokenIfoBox = middleware.bucketGet(
        "buzhi_JdDpSign", "tokenIfoBox"
    )  # token信息输出开关和筛选开关
    firstSignBox = middleware.bucketGet(
        "buzhi_JdDpSign", "firstSignBox"
    )  # 首签筛选开关
    off20Box = middleware.bucketGet("buzhi_JdDpSign", "off20Box")  # 20token判断开关
    tokenRetry = middleware.bucketGet(
        "buzhi_JdDpSign", "tokenRetry"
    )  # token检测最大次数
    if not tokenRetry:
        tokenRetry = 5
    else:
        tokenRetry = int(tokenRetry)
    beansNums = middleware.bucketGet("buzhi_JdDpSign", "beansNums")  # 豆子数量
    if not beansNums:
        beansNums = 0
    else:
        beansNums = int(beansNums)
    beansShare = middleware.bucketGet("buzhi_JdDpSign", "beansShare")  # 份额
    if not beansShare:
        beansShare = 0
    else:
        beansShare = int(beansShare)
    maxBeansDays = middleware.bucketGet(
        "buzhi_JdDpSign", "maxBeansDays"
    )  # 最长入库时间
    if not maxBeansDays:
        maxBeansDays = 0
    else:
        maxBeansDays = int(maxBeansDays)

    # 自定义接口
    uaHost = middleware.bucketGet("buzhi_JdDpSign", "customUA")
    if not uaHost:
        uaHost = "http://jiagang.6dot.cn:3006/UA"
    else:
        uaHost = uaHost
    h5Host = middleware.bucketGet("buzhi_JdDpSign", "customH5")
    if not h5Host:
        h5Host = "http://jiagang.6dot.cn:3006/H5ST_V"
    else:
        h5Host = h5Host
    # print(uaHost)
    # print(h5Host)
    # 自用开关
    saveTokenInfo = middleware.bucketGet("buzhi_JdDpSign", "saveTokenInfo")
else:
    print("定时已关闭")


class Ql:
    """
    青龙配置
    """

    def __init__(self, ql_ipport, client_id, client_secret):
        self.ql_ipport = ql_ipport
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.get_token()

    def get_token(self):
        """
        连接青龙获取token
        """
        try:
            url = f"{self.ql_ipport}/open/auth/token?client_id={self.client_id}&client_secret={self.client_secret}"
            response = requests.get(url)
            token = response.json().get("data", {}).get("token")

            return token
        except:
            middleware.notifyMasters("【JD店铺签到】获取青龙token失败", notify)

    def api_ql(self, api, apd, method, body="", way="open"):
        """
        其他接口
        """
        url = f"{self.ql_ipport}/{way}/{api}{apd}"

        headers = {
            # "Content-Type": "application/x-www-form-urlencoded",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": "Bearer " + self.token,
        }

        response = requests.request(method, url, headers=headers, data=body)
        return response.json()

    def get_system(self, method):
        """
        获取系统版本
        """
        url = f"{self.ql_ipport}/api/system"
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
        }

        response = requests.request(method, url, headers=headers)
        return response.json()

    def get_kcrons(self, keyword):
        """
        关键词获取crons
        """
        # keyword = quote(keyword)
        return self.api_ql(
            "crons", f"?searchValue={keyword}&t={str(round(time.time() * 1000))}", "get"
        )

    def get_crons(self):
        """
        获取所有定时任务
        """
        return self.api_ql(
            "crons", f"?searchValue=&t={str(round(time.time() * 1000))}", "get"
        )

    def run_crons(self, cron_ids):
        """
        运行定时任务
        接收cro_ids 为列表，里面的id整数
        """
        body = list(map(str, cron_ids))
        return self.api_ql(
            "crons", f"/run?t={str(round(time.time() * 1000))}", "put", json.dumps(body)
        )

    def get_configs(self):
        """
        获取配置文件
        """
        if self.get_system("get")["data"]["version"] < "2.17":
            return self.api_ql(
                "configs", f"/config.sh?t={str(round(time.time() * 1000))}", "get"
            )
        else:
            return self.api_ql(
                "configs",
                f"/detail?path=config.sh&t={str(round(time.time() * 1000))}",
                "get",
            )

    def save_configs(self, data):
        """
        保存配置
        """
        return self.api_ql(
            "configs",
            f"/save?t={str(round(time.time() * 1000))}",
            "post",
            json.dumps(data),
        )

    def get_envs(self):
        """
        获取所有环境变量
        """
        return self.api_ql("envs", "", "get", "")

    def add_envs(self, data):
        """
        添加环境变量
        code = 500 # 重复添加
        payload = [{"name": "wxMsg", "value": "1", "remarks": "cs"}, {"name": "wxMsg", "value": "2", "remarks": "cs"}]
        """
        return self.api_ql("envs", "", "post", json.dumps(data))

    def updata_envs(self, data):
        """
        更新环境变量数据
        字典格式（单个数据）
        {"name": "ceshi", "value": "3", "remarks": "cs", "id": 30}
        """
        return self.api_ql("envs", "", "put", json.dumps(data))


#   --------------------------------定义店铺签到类--------------------------------
class JdDpSign:
    """
    店铺签到
    """

    def __init__(self):
        # 青龙数据处理
        self.qlName = ""
        # 青龙配置
        self.ql = ""
        # 青龙类
        self.Ql = ""
        # super().__init__(
        #     self.ql["host"], self.ql["client_id"], self.ql["client_secret"]
        # )
        # ck列表
        self.jdCks = []
        self.jdCk = ""
        # 定时脚本id
        self.cornId = ""
        # 定时任务脚本名
        self.cornName = ""
        # 定时任务检查次数
        self.checkNum = 12
        # 环境变量id
        self.envId = ""
        # 旧token，字符串类型
        self.oldTokens = ""
        # aut旧token
        self.autOldTokens = ""
        # 新token，字符串类型
        self.newTokens = ""
        # 筛选后的新token，字符串类型
        self.newSiftTokens = ""
        self.shopId = "shopId"
        self.retry = 0
        self.tkRetry = 0
        self.ncH5 = ""
        self.ncUa = ""
        self.h5Ver = ""
        # token检测文本输出
        self.tokenText = ""
        # token检测信息
        self.tokenInfo = []

    def main(self):
        """
        主程序
        """
        global saveTokenInfo
        if mess == "dpql" or mess == "店铺清理" or mess == "tokens":
            for qlName in qlNameList:
                self.tokenInfo = []
                self.get_Ql(qlName)
                if mess == "tokens":
                    self.resultOutput(f"开始获取【{self.qlName}】容器中的token")
                else:
                    self.resultOutput(f"开始检测【{self.qlName}】容器中的token")
                # 环境变量
                print(f"开始获取{self.qlName}容器中的旧token")
                if optionSaveBox == "true":
                    envResult = self.get_envTokens()
                    if envResult["code"] != 0 and envResult["code"] != 2:
                        sys.exit()
                else:
                    configResult = self.get_configTokens()
                    if configResult["code"] != 0 and configResult["code"] != 2:
                        sys.exit()
                if not self.oldTokens:
                    self.resultOutput(f"【{self.qlName}】无token")
                else:
                    if mess == "tokens":
                        self.resultOutput(
                            f"【{self.qlName}】容器\ntokens：{self.oldTokens}"
                        )
                        continue
                    tokenTextDict = {}
                    print(f"{self.qlName}容器开始进行token检测")
                    self.newSiftTokens = ""  # 切换容器清空筛选后的token
                    for index, token in enumerate(self.oldTokens.split(splits)):
                        tokenText, result = self.getTokenMessage(token)
                        if result == 0:
                            if index != len(self.oldTokens) - 1:
                                self.newSiftTokens += f"{token}{splits}"
                                # self.tokenText += f"{tokenText}\n" + "-" * 15 + "\n"
                                tokenTextDict[token] = tokenText
                            else:
                                self.newSiftTokens += f"{token}"
                                # self.tokenText += f"{tokenText}\n"
                                tokenTextDict[token] = tokenText
                        else:
                            tokenTextDict[token] = tokenText
                    self.tokenText = ("\n" + "-" * 15 + "\n").join(
                        tokenTextDict.values()
                    )
                    self.newSiftTokens = self.remove_old(self.newSiftTokens, "")
                    if optionSaveBox == "true":
                        saveResult = self.save_envs(self.newSiftTokens)
                    else:
                        saveResult = self.save_config(self.newSiftTokens)
                    if saveResult["code"] == 0:
                        self.resultOutput(
                            f"【{self.qlName}】容器中token检测如下：\n{self.tokenText}\n\n清理结果：\ntokens：{self.newSiftTokens}"
                        )
            if saveTokenInfo == "true":
                if mess == "tokens":
                    self.autOldTokens = middleware.bucketGet("buzhi.JdDp","tokens")
                    if self.autOldTokens:
                        self.resultOutput(f"aut桶\ntokens：{self.autOldTokens}")
                    else:
                        self.resultOutput("aut桶中无token")
                    sys.exit()
                self.tokenInfo = []
                tokenTextDict = {}
                print(f"开始检测aut桶中保存的token")
                self.newSiftTokens = ""  # 切换容器清空筛选后的token
                self.oldTokens = middleware.bucketGet("buzhi.JdDp","tokens")
                if self.oldTokens:
                    for index, token in enumerate(self.oldTokens.split(splits)):
                        tokenText, result = self.getTokenMessage(token)
                        if result == 0:
                            if index != len(self.oldTokens) - 1:
                                self.newSiftTokens += f"{token}{splits}"
                                tokenTextDict[token] = tokenText
                            else:
                                self.newSiftTokens += f"{token}"
                                tokenTextDict[token] = tokenText
                        else:
                            tokenTextDict[token] = tokenText
                    self.tokenText = ("\n" + "-" * 15 + "\n").join(
                        tokenTextDict.values()
                    )
                    self.newSiftTokens = self.remove_old(self.newSiftTokens, "")
                    middleware.bucketSet(
                        "buzhi.JdDp","tokens", self.newSiftTokens
                    )
                    self.resultOutput(
                        f"aut桶中token检测如下：\n{self.tokenText}\n\n清理结果：\ntokens：{self.newSiftTokens}"
                    )
                    print("开始更新token信息")
                    middleware.bucketSet("buzhi.JdDp","tokenInfo", json.dumps(self.tokenInfo))
                else:
                    self.resultOutput("aut桶中无token")
            sys.exit()
        elif mess == ("运行签到" or "签到运行"):
            for qlName in qlNameList:
                self.get_Ql(qlName)
                self.resultOutput(f"开始执行【{self.qlName}】容器中的签到脚本")
                self.save_run_scripts("", "")
                self.resultOutput(f"【{self.qlName}】容器签到执行完毕")
            sys.exit()
        elif mess == "店铺签到" or mess == "dpqd" or mess == "爬签到":
            self.get_Ql(qlNameList[0])
            if not self.jdCks:
                self.get_cks()
                self.jdCk = self.jdCks[0]
            dpData = self.dp_data()  # 爬店铺信息
            print(dpData)
            self.resultOutput(dpData)
            if dpData == "今天店铺签到信息暂未更新":
                sys.exit()
            if (mess == "爬签到" and tokenSignBox == "true") or mess != "爬签到":
                self.jx_token(dpData)
            else:
                sys.exit()
        elif "店铺签到 " in mess or "dpqd " in mess:
            self.get_Ql(qlNameList[0])
            if not self.jdCks:
                self.get_cks()
                # print(self.jdCks)
                self.jdCk = self.jdCks[0]
            self.jx_token(mess)
        elif "tokens：" in mess:
            self.newTokens = mess.split("tokens：")[-1].strip()
        if not self.newTokens:
            self.resultOutput("token获取失败，退出程序")
            sys.exit()
        else:
            # 获取aut桶中保存的token
            if saveTokenInfo == "true":
                print("开始获取aut桶中token")
                self.autOldTokens = middleware.bucketGet("buzhi.JdDp","tokens")
                if not self.autOldTokens:
                    self.autOldTokens = ""
            if (
                (tokenSignInfoBox == "true" and mess == "爬签到")
                or (tokenSignInfoBox2 == "true" and "tokens：" in mess)
                or (tokenIfoBox == "true" and mess != "爬签到")
            ):
                print("开启进行token筛选")
                newTokenList = self.newTokens.split(splits)
                tokenTextDict = {}
                for index, token in enumerate(newTokenList):
                    tokenText, result = self.getTokenMessage(token)
                    if result == 0:
                        if index != len(newTokenList) - 1:
                            self.newSiftTokens += f"{token}{splits}"
                            # self.tokenText += f"{tokenText}\n" + "-" * 15 + "\n"
                            tokenTextDict[token] = tokenText
                        else:
                            self.newSiftTokens += f"{token}"
                            # self.tokenText += f"{tokenText}\n"
                            tokenTextDict[token] = tokenText
                    else:
                        tokenTextDict[token] = tokenText
                self.tokenText = ("\n" + "-" * 15 + "\n").join(tokenTextDict.values())
                if not self.newSiftTokens:
                    self.resultOutput(f"全部不符合条件，退出程序\n{self.tokenText}")
                    sys.exit()
                else:
                    if mess == "爬签到":
                        self.newSiftTokens = self.remove_old(self.newSiftTokens, "")
                        self.resultOutput(f"tokens：{self.newSiftTokens}")
                        self.resultOutput(f"解析结果：\n{self.tokenText}")
                        # aut桶处理
                        self.autTokenProcess(tokenTextDict)
                    else:
                        self.newSiftTokens = self.remove_old(self.newSiftTokens, "")
                        if "tokens：" not in mess:
                            self.resultOutput(f"tokens：{self.newSiftTokens}")
                        for qlName in qlNameList:
                            self.get_Ql(qlName)
                            print(
                                f"{self.qlName}青龙版本：",
                                self.Ql.get_system("get")["data"]["version"],
                            )
                            # 环境变量
                            if optionSaveBox == "true":
                                envResult = self.get_envTokens()
                                if envResult["code"] != 0 and envResult["code"] != 2:
                                    continue
                            else:
                                configResult = self.get_configTokens()
                                if (
                                    configResult["code"] != 0
                                    and configResult["code"] != 2
                                ):
                                    continue
                            tokenResult, limitToken = self.limitToken(
                                self.newSiftTokens
                            )
                            if tokenResult:
                                tokenTextDict2 = copy.deepcopy(tokenTextDict)
                                if limitToken:
                                    limitTokenList = limitToken.split(splits)
                                    [
                                        tokenTextDict2.get(i)
                                        + "\n超过20token限制，不入库"
                                        for i in limitTokenList
                                    ]
                                self.tokenText = ("\n" + "-" * 15 + "\n").join(
                                    tokenTextDict2.values()
                                )
                                mainResult = self.save_run_scripts(
                                    tokenResult, limitToken
                                )
                                if mainResult:
                                    self.resultOutput(
                                        f"【{self.qlName}】容器结果：\n{self.tokenText}"
                                    )
                        # aut桶处理
                        self.autTokenProcess(tokenTextDict)
            else:
                self.newSiftTokens = self.remove_old(self.newSiftTokens, "")
                if "tokens：" not in mess:
                    self.resultOutput(f"tokens：{self.newTokens}")
                if mess != "爬签到":
                    for qlName in qlNameList:
                        self.get_Ql(qlName)
                        print(
                            f"{self.qlName}青龙版本：",
                            self.Ql.get_system("get")["data"]["version"],
                        )
                        # 环境变量
                        if optionSaveBox == "true":
                            envResult = self.get_envTokens()
                            if envResult["code"] != 0 and envResult["code"] != 2:
                                continue
                        else:
                            configResult = self.get_configTokens()
                            if configResult["code"] != 0 and configResult["code"] != 2:
                                continue
                        tokenResult, limitToken = self.limitToken(self.newTokens)
                        if tokenResult:
                            self.save_run_scripts(tokenResult, limitToken)
                    # aut桶处理
                    self.autTokenProcess({})
    #   --------------------------------店铺解析方法定义--------------------------------
    def resultOutput(self, data):
        """
        输出结果
        """
        if senderType == "fake":
            middleware.notifyMasters(data, notify)
        else:
            sender.reply(data)

    def timestamp(self):
        """
        获取当前时间戳
        """
        return int(time.time() * 1000)

    def fromtimestamp(self, timestamp):
        """
        时间戳转换
        """
        return datetime.datetime.fromtimestamp(timestamp / 1000.0)

    def remove_old(self, tokenOld: str, token: str):
        """
        去除token中的重复splits
        去除失效token，即无豆token
        tokenOld去除含token的部分
        """
        token = token.split(splits)
        # pattern = r''+ f'(\{splits})' + '+'
        pattern = r"" + f"\{splits}" + "+"
        tokenOld = re.sub(pattern, splits, tokenOld)  # 多个splits替换成一个
        # sender.reply(f'1212：{tokenOld}')
        tokens = tokenOld.strip(splits)  # 去除首尾的splits
        # sender.reply(f'处理后tokens：{tokens}')
        if len(token) != 0:
            oldList = tokens.split(splits)
            tokens = [x for x in oldList if x not in token]
            tokens = splits.join(tokens)
        return tokens

    def shortToLong(self, url):
        """
        JD短链接还原
        """
        reg2 = re.compile(r"hrl=\'(.+?)\';")
        body = self.apiRequest(url).text
        if body:
            # 提取访问内容中链接
            hrl = reg2.search(body)
            if hrl and len(hrl.groups()) >= 1:
                # 获取目标链接
                shopurl_response = requests.get(hrl.group(1))
                shopurl = shopurl_response.url

                if shopurl:
                    return shopurl
                else:
                    return False
        return False

    def apiRequest(
        self, url, data={}, headers={}, proxies=None, way="0", method="POST"
    ):
        """
        2024.4.27 23:41更新：1、去除代理重试部分；2、优化请求方式，减少不必要的变量
        通用请求：代理池、api直链、本地
        """
        if proxyBox == "true" and auto_proxy and way == "1":
            print("代理池请求")
            try:
                response = requests.get(
                    url=url,
                    params=data,
                    headers=headers,
                    proxies={
                        "http": auto_proxy,
                        "https": auto_proxy,
                    },
                    timeout=30,
                )
            except:
                if apiProxy:
                    print("代理池请求失败，开始执行api代理")
                    proxy = requests.get(url=apiProxy).text
                    try:
                        response = requests.get(
                            url=url,
                            params=data,
                            headers=headers,
                            proxies={"http": proxy, "https": proxy},
                            timeout=30,
                        )
                    except:
                        print("api代理请求失败，开始执行本地请求")
                        response = requests.get(
                            url=url, headers=headers, params=data, timeout=30
                        )
        elif proxyBox == "true" and apiProxy and way == "1":
            print("使用api代理")
            proxy = requests.get(url=apiProxy).text
            try:
                response = requests.get(
                    url=url,
                    params=data,
                    headers=headers,
                    proxies={"http": proxy, "https": proxy},
                    timeout=30,
                )
            except:
                print("api代理请求失败，开始执行本地请求")
                response = requests.get(
                    url=url, headers=headers, params=data, timeout=30
                )
        else:
            response = requests.get(url=url, headers=headers, params=data, timeout=30)
        return response

    def xin_ua(self):
        """
        获取nc_ua和h5_ver
        """
        self.ncUa = ""
        self.h5Ver = ""
        try:
            response = requests.post(
                url=uaHost,
                json={},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            print(response.text)
            if response.json()["code"] == 200 or response.json()["retcode"] == 0:
                body = response.json()
                self.ncUa = body.get("data", "")
                self.h5Ver = self.ncUa.split(";")[2]
                return True
            else:
                return False
        except Exception as e:
            print("获取UA部分出现错误：", e)
            return False

    def xin_h5(self, token):
        """
        h5请求获取h5st
        """
        self.ncH5 = ""
        uaResult = self.xin_ua()
        # 减少服务器压力
        time.sleep(0.5)
        if uaResult:
            h5Body = {
                "appId": "4da33",
                "fn": "interact_center_shopSign_getActivityInfo",
                "body": {"token": token, "venderId": ""},
                "apid": "interCenter_shopSign",
                "ver": self.h5Ver,
                "cl": "ios",
                "code": 1,
                "user": "jd_qqjUmaZKovPZ",
                "ua": self.ncUa,
            }
            # print("h5请求body：", h5_body)
            try:
                response = requests.post(
                    url=h5Host,
                    json=h5Body,
                    headers={"Content-Type": "application/json"},
                    timeout=30,
                )
                print(f"h5:{response.text}")
                if response.json()["code"] == 200:
                    body = response.json()
                    self.ncH5 = body["data"]
                    return True
                else:
                    return False

            except Exception as e:
                print("获取h5出现错误：", e)
                return False
        else:
            print("ua获取失败！")
            return False

    def h5ApiToken(self, token):
        """
        h5请求获取token信息
        """
        h5Result = self.xin_h5(token)
        token = self.getEidToken("https://u.jd.com/brtU6Lo")
        if h5Result:
            try:
                response = self.apiRequest(
                    url=f"https://api.m.jd.com/api?loginType=2&{self.ncH5}&x-api-eid-token={token}",
                    headers={
                        "Referer": "http://h5.m.jd.com",
                        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                        "User-Agent": self.ncUa,
                        "Content-Type": "application/json",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Host": "api.m.jd.com",
                        "Connection": "keep-alive",
                        "X-Requested-With": "com.jingdong.app.mall",
                        "Cookie": self.jdCk
                    },
                    way="1",
                ).json()
                print(f"token检测code：", response["code"])
                if response["code"] == 200:
                    # token正常
                    self.tkRetry = 0
                    return response
                elif response["code"] == 402:
                    # token失效
                    self.tkRetry = 0
                    return False
                else:
                    return "false"
            except Exception as e:
                print(f"{token}检测失败，{e}")
                return "false"
        else:
            print("获取h5失败！")
            return "false"
            
    def getEidToken(self, referer):
        url = "http://jiagang.6dot.cn:3006/jddToken"
        
        payload = f'url={referer}'
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)
        if response.status_code == 200:
            response = response.json()
            if response.get("code") == 200:
                token = response.get("data").get("token")
                # print(token)
                return token
            return False
        return False

    #   --------------------------------定义token筛选方法--------------------------------
    def getTokenMessage(self, token):
        """
        获取token信息组合成文本输出
        1、根据配参开关进行判断是否首签功能
        2、根据配参数据进行token筛选
        返回数据text、status
        text token文本信息文本
        status token状态：-2、-1、0、1、2、3、4、5、6、7
            -2：token检测失败
            -1：token失效
            0：符合条件
            1：token不符合首签
            2：豆份额数据不符合
            3：豆数量不符合
            4：红包数量不符合
            5：签到天数不符合
            6：超过token最长签到天数
            7：不符合数量和份额
        """
        text = f"{token}："  # token信息文本
        status = False  # 是否有豆标志
        status1 = False  # 开启份额数筛选标志
        status2 = False  # 开启豆数量筛选标志
        # status3 = False  # 开启红包大小筛选标志
        status4 = False  # 开启最长签到天数筛选标志
        status5 = False  # 开启20token超限检测标志
        discountStatus = False
        numberStatus = False
        daysStatus = True
        num = 0  # 有豆计数，大于0表示符合条件，小于0表示不符合条件
        if beansShare:
            status1 = True
        if beansNums:
            status2 = True
        # if redPacketNums:
        #     status3 = True
        if maxBeansDays:
            status4 = True
        if off20Box:
            status5 = True
        tokenMessage = self.h5ApiToken(token)
        if tokenMessage == False:
            text += "\n失效"
            return text, -1
        if tokenMessage == "false":
            for _ in range(tokenRetry):
                print(f"{token}检测失败，开始第{_ +1}次重试")
                tokenMessage = self.h5ApiToken(token)
                if tokenMessage == False:
                    text += "\n失效"
                    return text, -1
                if tokenMessage != "false":
                    break
                time.sleep(2)
            if tokenMessage == "false":
                text += "\ntoken检测失败"
                if mess == "店铺清理" or mess == "dpql":
                    return text, 0
                else:
                    return text, -2
        if tokenMessage:
            # print(tokenMessage)
            try:
                startTime = self.fromtimestamp(tokenMessage["data"]["startTime"])
            except:
                startTime = None
            if mess != "店铺清理" or mess != "dpql":
                # 排除token检测外进行首签判断
                if (
                    mess != "店铺清理"
                    and mess != "dpql"
                    and startTime != None
                    and firstSignBox == "true"
                ):
                    # 判断首签
                    if (self.timestamp() - 86400000) < tokenMessage["data"][
                        "startTime"
                    ]:
                        text += f"\n首签：是"
                    else:
                        text += f"\n首签：否\n非首签，token不入库"
                        return text, 1
            try:
                endTime = self.fromtimestamp(tokenMessage["data"]["endTime"])
            except:
                endTime = None
            text += f"\n开始时间：{startTime}\n结束时间：{endTime}"
            try:
                activityName = tokenMessage["data"]["activityName"]
            except:
                activityName = None
            # text += f'\n活动名称：{activityName}'
            try:
                venderId = tokenMessage["data"]["venderId"]
            except:
                venderId = None
            try:
                activityId = tokenMessage["data"]["id"]
            except:
                activityId = None
            try:
                continuePrizeRuleList = tokenMessage["data"]["continuePrizeRuleList"]
            except:
                continuePrizeRuleList = False
            if continuePrizeRuleList != False:
                beansList = []  # 豆列表
                # redPacketList = []  # 红包列表
                for RuleList in continuePrizeRuleList:
                    for prize in RuleList["prizeList"]:
                        days = RuleList["days"]  # 天数
                        discount = prize["discount"]  # 豆/红包数量
                        number = prize["number"]  # 豆或红包份额数
                        if prize["type"] == 4:
                            text += f"\n{days}天{discount}豆{number}份--"
                            if prize["status"] == 5:
                                text += "无豆"
                            elif prize["status"] == 2:
                                text += "有豆"
                                beansList.append(
                                    [
                                        int(discount),
                                        int(number),
                                        int(days),
                                        tokenMessage["data"]["startTime"],
                                    ]
                                )

                if mess == "店铺清理" or mess == "dpql":
                    if len(beansList) > 0:
                        # 豆存在，看豆
                        for discountList in beansList:
                            days = discountList[2]
                            startTime = discountList[3]
                            if discountList == beansList[-1] and self.timestamp() > (
                                startTime + days * 86400000
                            ):
                                # 当前时间超过最长豆的时间
                                text += "\n超过最长签到时间，移除token"
                                return text, 6
                        self.tokenInfo.append({
                            token:{
                                "venderId":venderId,
                                "activityId": activityId
                            }
                        })
                        return text, 0
                    else:
                        text += "\n无豆，移除token"
                        return text, None

                elif mess != "店铺清理" and mess != "dpql":
                    if len(beansList) > 0:
                        # 看豆
                        status = True
                        print("进入1")
                        for discountList in beansList:
                            discount = discountList[0]  # 豆子数量
                            number = discountList[1]  # 豆子份额
                            days = discountList[2]  # 天数
                            if status1 and not status2:
                                # 份额数开，豆数量关
                                discountStatus = True
                                if status4 and days > maxBeansDays:
                                    # 开启最长天数，但超过最长天数
                                    daysStatus = False
                                elif number >= beansShare:
                                    numberStatus = True
                                    num += 1
                            elif not status1 and status2:
                                # 份额数关，豆数量开
                                numberStatus = True
                                if status4 and days > maxBeansDays:
                                    # 开启最长天数，但超过最长天数
                                    daysStatus = False
                                elif discount >= beansNums:
                                    discountStatus = True
                                    num += 1
                            elif status1 and status2:
                                if status4:  #  天数开
                                    if days < maxBeansDays:
                                        if (
                                            number >= beansShare
                                            and discount >= beansNums
                                        ):
                                            discountStatus = True
                                            numberStatus = True
                                            num += 1
                                        elif (
                                            number < beansShare
                                            and discount >= beansNums
                                        ):
                                            discountStatus = True
                                        elif (
                                            number >= beansShare
                                            and discount < beansNums
                                        ):
                                            numberStatus = True
                                    else:
                                        daysStatus = False
                                else:
                                    if number >= beansShare and discount >= beansNums:
                                        discountStatus = True
                                        numberStatus = True
                                        num += 1
                                    elif number < beansShare and discount >= beansNums:
                                        discountStatus = True
                                    elif number >= beansShare and discount < beansNums:
                                        numberStatus = True
                            elif not status1 and not status2 and not status4:
                                print("进入2")
                                status = True
                                daysStatus = True
                    else:
                        text += "\n无豆，token不入库"
                        return text, None
            else:
                text += "\ntoken检测信息获取失败"
                return text, -2
        # else:
        #     text += "\ntoken检测信息获取失败"
        #     return text, -2
        if status:
            if daysStatus:
                # 开启份额未开启数量
                if status1 and not status2:
                    if numberStatus:
                        self.tokenInfo.append({
                            token:{
                                "venderId":venderId,
                                "activityId": activityId
                            }
                        })
                        return text, 0
                    else:
                        text += f"\n豆份额少于{beansShare}份，token不入库"
                        return text, 2
                elif not status1 and status2:
                    # 开启数量未开启份额
                    if discountStatus:
                        self.tokenInfo.append({
                            token:{
                                "venderId":venderId,
                                "activityId": activityId
                            }
                        })
                        return text, 0
                    else:
                        text += f"\n豆数量少于{beansNums}豆，token不入库"
                        return text, 3
                elif status1 and status2:
                    # 开启份额和数量
                    if numberStatus and discountStatus:
                        self.tokenInfo.append({
                            token:{
                                "venderId":venderId,
                                "activityId": activityId
                            }
                        })
                        return text, 0
                    elif not numberStatus:
                        text += f"\n豆份额少于{beansShare}份，token不入库"
                        return text, 2
                    elif not discountStatus:
                        text += f"\n豆数量少于{beansNums}豆，token不入库"
                        return text, 3
                    else:
                        text += f"\n豆数量少于{beansNums}豆且豆份额少于{beansShare}份，token不入库"
                        return text, 7
                else:
                    self.tokenInfo.append({
                        token:{
                            "venderId":venderId,
                            "activityId": activityId
                        }
                    })
                    return text, 0
            else:
                text += f"\n最大签到天数大于{maxBeansDays}天，token不入库"
                return text, 5
        else:
            text += "\n无豆，token不入库"
            return text, None

    def dp_data(self):
        """
        爬取https://shimo.im/docs/zdkyBe8EEyfl4gA6/read中的每日京东店铺签到
        https://shimo.im/docs/9jYgTY3vJvPYtqWD
        https://taou.cn/2tjsw
        """
        if shopUrl == "":
            url = "https://shimo.im/docs/KrkEl4QRzXT8OYqJ/read"
        else:
            url = shopUrl
        response = self.apiRequest(url)
        response.encoding = "utf-8"
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        ps = soup.find_all("p")
        dp_list = []
        today_dp = ""
        for p in ps:
            if "新增" in p.get_text():
                index = ps.index(p)
                dp_list.append((index))
        if (
            date_string in ps[dp_list[0]].get_text()
            or date_string2 in ps[dp_list[0]].get_text()
            or date_string3 in ps[dp_list[0]].get_text()
            or (
                f"{date_month}月" in ps[dp_list[0]].get_text()
                and f"{date_day}日" in ps[dp_list[0]].get_text()
            )
        ):
            for i in range(dp_list[0], dp_list[1]):
                if ps[i].get_text() == "":
                    continue
                today_dp += ps[i].get_text() + "\n"
        else:
            today_dp = "今天店铺签到信息暂未更新"
        return today_dp

    def get_shopId(self, dpxx: str):
        """解析店铺信息获取店铺id"""
        shopIdList = []
        pattern = r"(https://u.jd.com/\w+)"
        matches = re.findall(pattern, dpxx)
        self.resultOutput(f"获取到{len(matches)}个短链接")
        for match in matches:
            req = self.shortToLong(match)
            if req == False:
                url = "http://rpi.zhelee.cn:9999"
                headers = {"User-Agent": self.UA}
                params = {"url": match}
                req = self.apiRequest(
                    url, headers=headers, data=params, timeout=60
                ).json()
            if "shopId" in req:
                self.shopId = "shopId"
            elif "venderId" in req:
                self.shopId = "venderId"
            try:
                Id = req.split(f"{self.shopId}=")[1].split("&")[0]
                print(f"{match}店铺ID：{Id}")
                shopIdList.append(Id)
            except:
                print("获取店铺ID失败，跳过")
        return shopIdList

    def get_token(self, shopId):
        """
        根据店铺id获取token
        """
        # url = "https://api.m.jd.com/client.action"
        # data = {"venderId": shopId, "source": "m-shop"}
        # url = f"https://api.m.jd.com/client.action?functionId=whx_getShopHomeActivityInfo&client=wh5&uuid=60326374769122806&appid=shop_m_jd_com&clientVersion=11.0.0&body={json.dumps(data)}"
        # headers = {
        #     "User-Agent": self.UA(),
        #     # "User-Agent": "jdltapp;iPhone;3.7.0;14.4;eb5a9e7e596e262b4ffb3b6b5c830984c8a5c0d5;network/wifi;ADID/5603541B-30C1-4B5C-A782-20D0B569D810;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,2;addressid/1041002757;hasOCPay/0;appBuild/101;supportBestPay/0;pv/34.6;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/5;ads/;psn/eb5a9e7e596e262b4ffb3b6b5c830984c8a5c0d5|44;jdv/0|androidapp|t_335139774|appshare|CopyURL|1612612940307|1612612944;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        #     "Accept": "*/*",
        #     "Host": "api.m.jd.com",
        #     "Connection": "keep-alive",
        #     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        #     "Accept-Language": "zh-CN,zh;q=0.9,th-CN;q=0.8,th;q=0.7,vi-CN;q=0.6,vi;q=0.5,en-US;q=0.4,en;q=0.3",
        #     "Charset": "UTF-8",
        #     "Accept-Encoding": "gzip,deflat",
        #     "Origin": "https://shop.m.jd.com",
        #     "Referer": "https://shop.m.jd.com/",
        #     "Cookie": self.jdCk,
        # }
        token = self.getEidToken("https://shop.m.jd.com/")
        if token:
            data = {"venderId": shopId, "source": "m-shop"}
            url = f"https://api.m.jd.com/client.action?functionId=whx_getShopHomeActivityInfo&client=wh5&uuid=60326374769122806&appid=shop_m_jd_com&clientVersion=11.0.0&body={json.dumps(data)}&x-api-eid-token={token}"
            payload = {}
            proxies={
                "http": 'http://119.3.156.10:1098',
                "https": 'http://119.3.156.10:1098',
            }
            headers = {
                "Accept": "*/*",
                "Host": "api.m.jd.com",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept-Language": "zh-CN,zh;q=0.9,th-CN;q=0.8,th;q=0.7,vi-CN;q=0.6,vi;q=0.5,en-US;q=0.4,en;q=0.3",
                "Charset": "UTF-8",
                "Accept-Encoding": "gzip,deflat",
                "Origin": "https://shop.m.jd.com",
                "Referer": "https://shop.m.jd.com/",
                "User-Agent": self.UA(),
                # "User-Agent": "jdltapp;iPhone;3.7.0;14.4;eb5a9e7e596e262b4ffb3b6b5c830984c8a5c0d5;network/wifi;ADID/5603541B-30C1-4B5C-A782-20D0B569D810;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,2;addressid/1041002757;hasOCPay/0;appBuild/101;supportBestPay/0;pv/34.6;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/5;ads/;psn/eb5a9e7e596e262b4ffb3b6b5c830984c8a5c0d5|44;jdv/0|androidapp|t_335139774|appshare|CopyURL|1612612940307|1612612944;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
                "Cookie": self.jdCk
            }
            req = self.apiRequest(url, data={}, headers=headers, way="1")
            print("code：", req.status_code)
            if req.status_code == 404:
                return False
            if req.text:
                req = req.json()
                try:
                    if req["code"] == "0":
                        if "token=" in req["result"]["signStatus"]["isvUrl"]:
                            token = req["result"]["signStatus"]["isvUrl"].split("token=")[
                                -1
                            ]
                            print(f"获取{shopId}：{token}")
                            return token
                except:
                    print(f"店铺{shopId}token获取失败")
                    return None
            else:
                print(f"店铺{shopId}token获取失败：{req.status_code}")
                return False
    
    def jx_token(self, dpxx):
        """
        将店铺信息进行token提取
        """
        print("开始获取店铺id")
        shopIdList = self.get_shopId(dpxx)
        if not shopIdList:
            self.resultOutput("获取店铺id失败，退出程序")
            sys.exit()
        else:
            # 获取token
            self.resultOutput("token解析中，请稍后...")
            for index, shopId in enumerate(shopIdList):
                for ckindex, jdCk in enumerate(self.jdCks):
                    dpToken = self.get_token(shopId)
                    if dpToken:
                        if index != len(shopIdList) - 1:
                            self.newTokens += f"{dpToken}{splits}"
                        else:
                            self.newTokens += f"{dpToken}"
                        break
                    elif dpToken == False:
                        if ckindex != len(self.jdCks) - 1:
                            print("切换CK进行获取token")
                            self.jdCk = self.jdCks[ckindex + 1]
                            time.sleep(1)
            self.newTokens = self.newTokens.strip(splits)

    def autTokenProcess(self, tokenTextDict):
        """
        aut桶token处理
        """
        if saveTokenInfo == "true":
            self.oldTokens = self.autOldTokens
            self.qlName = "aut桶"
            tokenResult, limitToken = self.limitToken(
                self.newSiftTokens
            )
            if tokenResult and tokenTextDict:
                tokenTextDict2 = copy.deepcopy(tokenTextDict)
                if limitToken:
                    limitTokenList = limitToken.split(splits)
                    [
                        tokenTextDict2.get(i)
                        + "\n超过20token限制，不入库"
                        for i in limitTokenList
                    ]
                self.tokenText = ("\n" + "-" * 15 + "\n").join(
                    tokenTextDict2.values()
                )
                self.resultOutput(
                    f"【{self.qlName}】容器结果：\n{self.tokenText}"
                )
            print("aut桶开始储存token")
            middleware.bucketSet(
                "buzhi.JdDp","tokens", tokenResult
            )
            print("aut桶开始token信息处理")
            newTokenInfo = []
            limitTokenList = limitToken.split(splits)
            for tokenInfo in self.tokenInfo:
                if tokenInfo.keys() not in limitTokenList:
                    newTokenInfo.append(tokenInfo)
            middleware.bucketSet(
                "buzhi.JdDp","tokenInfo", json.dumps(newTokenInfo)
            )
            print("aut桶数据处理完成")


    #   --------------------------------青龙方法定义--------------------------------

    def get_Ql(self, qlName):
        """
        获取青龙方法self.Ql
        """
        if isRqm:
            self.qlName = qlName
        else:
            self.qlName = qlName["name"]
        self.ql = self.get_qls()
        self.Ql = Ql(
            self.ql["host"],
            self.ql["client_id"],
            self.ql["client_secret"],
        )

    def get_qls(self):
        """
        获取指定青龙信息
        """
        print(f"当前容器名：{self.qlName}")
        try:
            if versionBox == "true":
                if not atmVersion:
                    qls = json.loads(middleware.bucketGet("qinglong", "QLS"))
                elif atmVersion:
                    # qls = json.loads(sender.bucketGet("qinglong", "QLS"))
                    qls = []
                    qlsId = sender.bucketAllKeys("qls")
                    for Id in qlsId:
                        ql = json.loads(sender.bucketGet("qls", Id))
                        qls.append(ql)
            else:
                qls = qlNameList
            for ql in qls:
                if ql["name"] == self.qlName:
                    # print(f"{self.qlName}:{ql}")
                    return ql
                elif ql == qls[-1] and ql["name"] != self.qlName:
                    self.notifyMasters(
                        f"【JD店铺签到】目标容器【{self.qlName}】不存在，请检查配参填写是否正确",
                        notify,
                    )
        except:
            self.notifyMasters(
                "【JD店铺签到】目标容器填写错误或未给qinglong权限", notify
            )

    def remove_dup(self, token: str):
        """
        去除token中的重复部分
        使用列表去除重复数据并保持顺序不变
        """
        uniqueData = []
        seen = set()

        for item in token.split(splits):
            if item and item not in seen:
                seen.add(item)
                uniqueData.append(item)

        result = splits.join(uniqueData)
        print("去重成功")
        return result

    def get_cks(self):
        """
        获取指定位置的CK
        """
        try:
            envs = self.Ql.get_envs()
        except:
            middleware.notifyMasters(
                f"链接容器【{self.qlName}】获取环境变量失败，请检查配置是否正确或网络是否正常",
                notify,
            )
            print("获取环境变量失败")
            sys.exit()
        else:
            i = 1
            if envs["code"] == 200:
                for env in envs["data"]:
                    if env["name"] == "JD_COOKIE" and env["status"] == 0:
                        # print(env["value"],i)
                        if i in ckIndex:
                            self.jdCks.append(env["value"])
                            ckIndex.remove(i)
                            if not ckIndex:
                                break
                        i += 1
                if not self.jdCks:
                    middleware.notifyMasters(
                        f"获取容器【{self.qlNmae}】有效CK指定位置失败", notify
                    )
                    sys.exit()
            else:
                print("获取环境变量失败")
                middleware.notifyMasters(f"【{self.qlName}】获取环境变量失败", notify)
                sys.exit()

    def save_run_scripts(self, tokenResult, limitToken):
        """
        保存新token运行脚本并保存总token
        """
        print(f"运行脚本：{tokenResult}")
        print(f"旧token：{self.oldTokens}")
        if tokenResult:
            newSaveTokens = ""
            if self.oldTokens:
                # newSaveTokens = self.remove_old(tokenResult, self.oldTokens)
                newSaveTokens = self.remove_old(self.newSiftTokens, limitToken)
            else:
                newSaveTokens = tokenResult
            print(f"需要运行的新token:{newSaveTokens}")
            if optionSaveBox == "true":
                saveResult = self.save_envs(newSaveTokens)
            else:
                saveResult = self.save_config(newSaveTokens)
            if saveResult["code"] != 0:
                return False
        commandList = scriptName.split(",")
        runNum = 0
        for command in commandList:
            getResult = self.get_cronId(command)
            if getResult["code"] != 0:
                break
            self.resultOutput(f"开始运行【{self.qlName}】容器中【{self.cornName}】脚本")
            runResult = self.run_cronId(self.cornId, self.cornName)
            if runResult["code"] != 0:
                break
            time.sleep(10)
            # 监测运行是否完成
            self.get_cronId(command)
            print(f"【{self.qlName}】容器中{command}脚本运行完成")
            runNum += 1
        if runNum == len(commandList):
            if tokenResult:
                print("脚本运行完成，开始保存数据")
                # 环境变量
                if optionSaveBox == "true":
                    saveResult = self.save_envs(tokenResult)
                else:
                    saveResult = self.save_config(tokenResult)
                if saveResult["code"] != 0:
                    print("token 保存失败")
                    return False
                self.resultOutput(
                    f"【JD店铺签到】容器【{self.qlName}】中的脚本运行完成\n新增{len(newSaveTokens.split(splits))}个token\ntokens：{newSaveTokens}\n现有token:{len(tokenResult.split(splits))}个[每天限签20个]"
                )
                return True
        print("脚本运行不完全，请检查日志")
        return False

    def get_envTokens(self):
        """
        获取环境变量旧tokens和id
        """
        try:
            envs = self.Ql.get_envs()
        except:
            middleware.notifyMasters(
                f"【JD店铺签到】链接容器【{self.qlName}】获取环境变量失败，请检查配置是否正确或网络是否正常",
                notify,
            )
            print("获取环境变量失败")
            return {"code": -1, "message": "链接容器失败"}
        else:
            if envs["code"] == 200:
                for env in envs["data"]:
                    if env["name"] == variable:
                        try:
                            if "id" in env:
                                self.envId = env["id"]
                                self.oldTokens = env["value"]
                                return {"code": 0, "message": "success"}
                            elif "_id" in env:
                                self.envId = env["_id"]
                                self.oldTokens = env["value"]
                                return {"code": 0, "message": "success"}
                        except:
                            self.resultOutput(f"【{self.qlName}】未适配")
                            return {
                                "code": 1,
                                "message": "该青龙版本未适配获取环境变量接口",
                            }
                self.envId = ""
                self.oldTokens = ""
                return {"code": 2, "message": f"不存在环境变量{variable}"}
            else:
                print("获取环境变量失败")
                self.resultOutput(f"【{self.qlName}】获取环境变量失败")
                return {
                    "code": -1,
                    "message": "获取环境变量失败，请检查获取环境变量接口是否正常",
                }

    def save_envs(self, value):
        """
        保存环境变量
        """
        if self.envId:
            payload = {
                "name": variable,
                "value": value,
                "remarks": "店铺签到tokens",
                "id": self.envId,
            }
            resl = self.Ql.updata_envs(payload)
            if resl["code"] == 200:
                print(f"{variable}环境变量更新成功")
                return {"code": 0, "message": "success"}
            else:
                print(f"{variable}环境变量更改失败")
                self.resultOutput(f"【{self.qlName}】更新{variable}环境变量失败")
                return {
                    "code": 1,
                    "message": "请检查该青龙版本保存环境变量接口是否正常",
                }
        else:
            payload = [{"name": variable, "value": value, "remarks": "店铺签到Tokens"}]
            self.Ql.add_envs(payload)
            print(f"{variable}环境变量添加成功，值：{value}")
            return {"code": 0, "message": "success"}

    def get_configTokens(self):
        """
        获取配置文件旧tokens
        """
        try:
            getConfigs = self.Ql.get_configs()
            print(f"配置文件：{getConfigs}")
        except:
            middleware.notifyMasters(
                f"【JD店铺签到】链接容器【{self.qlName}】获取配置文件失败，请检查配置是否正确或网络是否正常",
                notify,
            )
            return {"code": -1, "message": "链接容器失败"}
        if getConfigs["code"] != 200:
            middleware.notifyMasters(
                f"【JD店铺签到】链接容器【{self.qlName}】配置文件失败，请检查配置是否正确或网络是否正常",
                notify,
            )
            return {"code": 1, "message": "请检查该青龙版本获取配置文件接口是否正常"}
        else:
            if f"export {variable}=" in getConfigs["data"]:
                # 以换行符分割字符串，获取每一行的内容
                lines = getConfigs["data"].split("\n")
                # 遍历每一行，找到包含指定键的行，并提取值
                for line in lines:
                    if line.startswith(f"export {variable}="):
                        # 提取值部分，并去除引号
                        oldTokens = line.split("=")[1].strip().strip('"')
                        self.oldTokens = self.remove_dup(oldTokens)
                        print("旧tokens：", self.oldTokens)
                        break
                return {"code": 0, "message": "配置文件旧tokens获取成功"}
            else:
                self.oldTokens = ""
                return {"code": 2, "message": f"不存在环境变量{variable}"}

    def save_config(self, value: str):
        """
        修改配置文件
        """
        # 去重处理
        value = self.remove_dup(value)
        try:
            getConfigs = self.Ql.get_configs()
            print(f"配置文件：{getConfigs}")
        except:
            middleware.notifyMasters(
                f"【JD店铺签到】链接容器【{self.qlName}】获取配置文件失败，请检查配置是否正确或网络是否正常",
                notify,
            )
            return {"code": -1, "message": "链接容器失败"}
        if getConfigs["code"] != 200:
            middleware.notifyMasters(
                f"【JD店铺签到】链接容器【{self.qlName}】配置文件失败，请检查配置是否正确或网络是否正常",
                notify,
            )
            return {"code": 1, "message": "请检查该青龙版本获取配置文件接口是否正常"}
        else:
            # 存在时
            if f"export {variable}=" in getConfigs["data"]:
                print(f"配置文件存在{variable}")
                # 以换行符分割字符串，获取每一行的内容
                lines = getConfigs["data"].split("\n")
                # 遍历每一行，找到以指定键开头的行，并替换值
                for i in range(len(lines)):
                    if lines[i].startswith(f"export {variable}="):
                        # 替换为新的值
                        lines[i] = f'export {variable}="{value}"'
                        print(f"新token：{value}")
                        break
                newConfig = "\n".join(lines)
                data = {"content": newConfig, "name": "config.sh"}
                save_configs = self.Ql.save_configs(data)
                if save_configs["code"] == 200:
                    print("配置文件保存成功")
                    return {"code": 0, "message": "success"}
                else:
                    print("配置文件保存失败")
                    self.resultOutput(f"【{self.qlName}】tokens保存失败")
                    return {
                        "code": 1,
                        "message": "请检查该青龙版本获取配置文件接口是否正常",
                    }
            else:
                print(f"配置文件不存在{variable}")
                newLine = f'export {variable}="{value}"'
                lines = getConfigs["data"].split("\n")
                lines.append(newLine)
                newConfig = "\n".join(lines)
                data = {"content": newConfig, "name": "config.sh"}
                saveConfig = self.Ql.save_configs(data)
                if saveConfig["code"] == 200:
                    print("配置文件保存成功")
                    return {"code": 0, "message": "success"}
                else:
                    print("配置文件保存失败")
                    self.resultOutput(f"【{self.qlName}】tokens保存失败")
                    return {
                        "code": 1,
                        "message": "请检查该青龙版本获取配置文件接口是否正常",
                    }

    def get_cronId(self, command):
        """
        获取青龙店铺签到指定id、name，并检测是否运行
        返回脚本id、name
        """
        try:
            # 获取指定crons
            _cronsData = self.Ql.get_kcrons(command)
        except:
            middleware.notifyMasters(
                f"【JD店铺签到】链接容器【{self.qlName}】获取定时任务失败，请检查配置是否正确或网络是否正常",
                notify,
            )
            return {"code": -1, "message": "链接容器失败"}
        if _cronsData["code"] != 200:
            # if _cronsData["code"] == 401:
            # return {"code": -1, "message": "请检查该青龙版本获取定时任务接口是否正常"}
            middleware.notifyMasters(
                f"【JD店铺签到】链接容器【{self.qlName}】定时任务失败，请检查配置是否正确或网络是否正常",
                notify,
            )
            return {"code": 1, "message": "请检查该青龙版本获取定时任务接口是否正常"}
        else:
            crons = _cronsData["data"]
            if "data" in crons:
                if len(crons["data"]) == 0:
                    print("未找到【店铺签到】脚本")
                    self.resultOutput(f"未找到【{self.qlName}】容器中【店铺签到】脚本")
                    return {
                        "code": 2,
                        "message": f"【{self.qlName}】容器中未找到{command}脚本",
                    }
                for cron in crons["data"]:
                    if command in cron["command"]:
                        if "id" in cron:
                            self.cornId = cron["id"]
                            self.cornName = cron["name"]
                        elif "_id" in cron:
                            self.cornId = cron["_id"]
                            self.cornName = cron["name"]
                        else:
                            self.resultOutput(
                                f"获取【{self.qlName}】容器中【店铺签到】脚本id失败"
                            )
                            return {
                                "code": 1,
                                "message": "请检查该青龙版本获取定时任务接口是否正常",
                            }
                        status = cron["status"]
                        if status == 1:
                            # print("空闲中")
                            self.checkNum = 12
                            return {"code": 0, "message": "success"}
                        elif status == 0:
                            # 等待运行结束
                            time.sleep(10)
                            if self.checkNum > 0:
                                self.checkNum -= 1
                                return self.get_cronId(command)
                            else:
                                self.checkNum = 12
                                return {"code": 0, "message": "success"}
            else:
                if len(crons) == 0:
                    print(f"未找到{command}脚本")
                    self.resultOutput(f"未找到【{self.qlName}】容器中“店铺签到”脚本")
                    return {
                        "code": 2,
                        "message": f"【{self.qlName}】容器中未找到{command}脚本",
                    }
                for cron in crons:
                    if command in cron["command"]:
                        if "id" in cron:
                            self.cornId = cron["id"]
                            self.cornName = cron["name"]
                        elif "_id" in cron:
                            self.cornId = cron["_id"]
                            self.cornName = cron["name"]
                        else:
                            self.resultOutput(
                                f"获取【{self.qlName}】容器中【店铺签到】脚本id失败"
                            )
                            return {
                                "code": 1,
                                "message": "请检查该青龙版本获取定时任务接口是否正常",
                            }
                        status = cron["status"]
                        if status == 1:
                            print("空闲中")
                            self.checkNum = 12
                            return {"code": 0, "message": "success"}
                        elif status == 0:
                            # 等待运行结束
                            time.sleep(10)
                            if self.checkNum > 0:
                                self.checkNum -= 1
                                return self.get_cronId(command)
                            else:
                                self.checkNum = 12
                                return {"code": 0, "message": "success"}

    def run_cronId(self, id, name):
        """
        运行指定id任务
        """
        try:
            idResult = self.Ql.run_crons([id])
            print("脚本运行情况", idResult)
        except:
            middleware.notifyMasters(
                f"【JD店铺签到】链接容器【{self.qlName}】运行【{name}】脚本失败，请检查配置是否正确或网络是否正常",
                notify,
            )
            return {"code": -1, "message": "脚本运行失败"}
        if idResult["code"] == 200:
            print("脚本运行成功")
            return {"code": 0, "message": "success"}
        elif idResult["code"] != 200:
            print("脚本运行失败")
            self.resultOutput(f"【{self.qlName}】容器中【{name}】脚本运行失败")
            return {"code": 1, "message": "请检查该青龙版本运行定时任务接口是否正常"}

    def limitToken(self, token: str):
        """
        将现有的旧token添加新token，并限制token数量不大于20
        """
        if self.oldTokens:
            oldTokenList = self.oldTokens.split(splits)
        else:
            oldTokenList = []
        # 去除token中重复部分
        token = self.remove_old(token, self.oldTokens)
        newTokenList = token.split(splits)
        oldLen = len(oldTokenList)
        newLen = len(newTokenList)
        if off20Box != "true":
            print("开始进行20token上限限制")
            if oldLen >= 20:
                self.resultOutput(
                    f"{pluginName}】提醒您，【{self.qlName}】容器旧token数量已超过20个，请自行删除或执行店铺清理指令进行清理，无法添加新token"
                )
                return False, False
            else:
                if oldLen + newLen > 20:
                    oldTokenList.extend(newTokenList[: 20 - oldLen])
                    return f"{splits}".join(oldTokenList), f"{splits}".join(
                        newTokenList[20 - oldLen :]
                    )
                else:
                    oldTokenList.extend(newTokenList)
                    return f"{splits}".join(oldTokenList), ""
        else:
            oldTokenList.extend(newTokenList)
            return f"{splits}".join(oldTokenList), ""

    def UA(self):
        USER_AGENTS = [
            "jdltapp;iPad;3.7.0;14.4;network/wifi;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "jdltapp;android;3.7.0;10;2346663656561603-4353564623932316;network/wifi;model/ONEPLUS A5010;addressid/0;aid/2dfceea045ed292a;oaid/;osVer/29;appBuild/1436;psn/BS6Y9SAiw0IpJ4ro7rjSOkCRZTgR3z2K|10;psq/5;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/10.5;jdv/;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/oppo;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ONEPLUS A5010 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
            "jdltapp;iPhone;3.7.0;14.1;59d6ae6e8387bd09fe046d5b8918ead51614e80a;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone12,1;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/;pv/1.26;apprpd/;ref/JDLTSubMainPageViewController;psq/0;ads/;psn/59d6ae6e8387bd09fe046d5b8918ead51614e80a|3;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.1;Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "jdltapp;iPhone;3.7.0;13.5;22d679c006bf9c087abf362cf1d2e0020ebb8798;network/wifi;ADID/10857A57-DDF8-4A0D-A548-7B8F43AC77EE;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone12,1;addressid/2378947694;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/15.7;apprpd/Allowance_Registered;ref/JDLTTaskCenterViewController;psq/6;ads/;psn/22d679c006bf9c087abf362cf1d2e0020ebb8798|22;jdv/0|kong|t_1000170135|tuiguang|notset|1614153044558|1614153044;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "jdltapp;android;3.7.0;10;2616935633265383-5333463636261326;network/UNKNOWN;model/M2007J3SC;addressid/1840745247;aid/ba9e3b5853dccb1b;oaid/371d8af7dd71e8d5;osVer/29;appBuild/1436;psn/t7JmxZUXGkimd4f9Jdul2jEeuYLwxPrm|8;psq/6;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/5.6;jdv/;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/xiaomi;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 10; M2007J3SC Build/QKQ1.200419.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045135 Mobile Safari/537.36",
            "jdltapp;iPhone;3.7.0;14.3;d7beab54ae7758fa896c193b49470204fbb8fce9;network/4g;ADID/97AD46C9-6D49-4642-BF6F-689256673906;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "jdltapp;android;3.7.0;9;D246836333735-3264353430393;network/4g;model/MIX 2;addressid/138678023;aid/bf8bcf1214b3832a;oaid/308540d1f1feb2f5;osVer/28;appBuild/1436;psn/Z/rGqfWBY/h5gcGFnVIsRw==|16;psq/3;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 9;osv/9;pv/13.7;jdv/;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/xiaomi;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 9; MIX 2 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045135 Mobile Safari/537.36",
            "jdltapp;iPhone;3.7.0;14.4;eb5a9e7e596e262b4ffb3b6b5c830984c8a5c0d5;network/wifi;ADID/5603541B-30C1-4B5C-A782-20D0B569D810;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,2;addressid/1041002757;hasOCPay/0;appBuild/101;supportBestPay/0;pv/34.6;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/5;ads/;psn/eb5a9e7e596e262b4ffb3b6b5c830984c8a5c0d5|44;jdv/0|androidapp|t_335139774|appshare|CopyURL|1612612940307|1612612944;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "jdltapp;iPhone;3.7.0;14.3;21631ed983b3e854a3154b0336413825ad0d6783;network/3g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,4;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.47;apprpd/;ref/JDLTSubMainPageViewController;psq/8;ads/;psn/21631ed983b3e854a3154b0336413825ad0d6783|9;jdv/0|direct|-|none|-|1614150725100|1614225882;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "jdltapp;iPhone;3.7.0;13.5;500a795cb2abae60b877ee4a1930557a800bef1c;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone8,1;addressid/669949466;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/9.11;apprpd/;ref/JDLTSubMainPageViewController;psq/10;ads/;psn/500a795cb2abae60b877ee4a1930557a800bef1c|11;jdv/;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "jdltapp;iPad;3.7.0;14.4;f5e7b7980fb50efc9c294ac38653c1584846c3db;network/wifi;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPad6,3;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/231.11;pap/JA2020_3112531|3.7.0|IOS 14.4;apprpd/;psn/f5e7b7980fb50efc9c294ac38653c1584846c3db|305;usc/kong;jdv/0|kong|t_1000170135|tuiguang|notset|1613606450668|1613606450;umd/tuiguang;psq/2;ucp/t_1000170135;app_device/IOS;utr/notset;ref/JDLTRedPacketViewController;adk/;ads/;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "jdltapp;iPhone;3.7.0;14.4;19fef5419f88076c43f5317eabe20121d52c6a61;network/wifi;ADID/00000000-0000-0000-0000-000000000000;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,8;addressid/3430850943;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/10.4;apprpd/;ref/JDLTSubMainPageViewController;psq/3;ads/;psn/19fef5419f88076c43f5317eabe20121d52c6a61|16;jdv/0|kong|t_1001327829_|jingfen|f51febe09dd64b20b06bc6ef4c1ad790#/|1614096460311|1614096511;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "jdltapp;iPhone;3.7.0;12.2;f995bc883282f7c7ea9d7f32da3f658127aa36c7;network/4g;ADID/9F40F4CA-EA7C-4F2E-8E09-97A66901D83E;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,4;addressid/525064695;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/11.11;apprpd/;ref/JDLTSubMainPageViewController;psq/2;ads/;psn/f995bc883282f7c7ea9d7f32da3f658127aa36c7|22;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 12.2;Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "jdltapp;android;3.7.0;10;5366566313931326-6633931643233693;network/wifi;model/Mi9 Pro 5G;addressid/0;aid/5fe6191bf39a42c9;oaid/e3a9473ef6699f75;osVer/29;appBuild/1436;psn/b3rJlGi AwLqa9AqX7Vp0jv4T7XPMa0o|5;psq/4;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/5.4;jdv/;ref/HomeFragment;partner/xiaomi;apprpd/Home_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; Mi9 Pro 5G Build/QKQ1.190825.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045135 Mobile Safari/537.36",
            "jdltapp;iPhone;3.7.0;14.4;4e6b46913a2e18dd06d6d69843ee4cdd8e033bc1;network/3g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,2;addressid/666624049;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/54.11;apprpd/MessageCenter_MessageMerge;ref/MessageCenterController;psq/10;ads/;psn/4e6b46913a2e18dd06d6d69843ee4cdd8e033bc1|101;jdv/0|kong|t_2010804675_|jingfen|810dab1ba2c04b8588c5aa5a0d44c4bd|1614183499;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "jdltapp;iPhone;3.7.0;14.2;c71b599e9a0bcbd8d1ad924d85b5715530efad06;network/wifi;ADID/751C6E92-FD10-4323-B37C-187FD0CF0551;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,8;addressid/4053561885;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/263.8;apprpd/;ref/JDLTSubMainPageViewController;psq/2;ads/;psn/c71b599e9a0bcbd8d1ad924d85b5715530efad06|481;jdv/0|kong|t_1001610202_|jingfen|3911bea7ee2f4fcf8d11fdf663192bbe|1614157052210|1614157056;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.2;Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "jdltapp;iPhone;3.7.0;14.4;2d306ee3cacd2c02560627a5113817ebea20a2c9;network/4g;ADID/A346F099-3182-4889-9A62-2B3C28AB861E;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,3;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/;pv/1.35;apprpd/Allowance_Registered;ref/JDLTTaskCenterViewController;psq/0;ads/;psn/2d306ee3cacd2c02560627a5113817ebea20a2c9|2;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        ]
        return USER_AGENTS[random.randint(0, len(USER_AGENTS) - 1)]


if __name__ == "__main__":
    if (
        (senderType == "fake" and fakeBox == "true") or senderType != "fake"
    ) and qlNameList:
        if scriptName == "":
            scriptName = "6dylan6_jdpro/jd_dpqd_main.js,6dylan6_jdpro/jd_dpqd_sign.js"
        print(f"当前脚本名：{scriptName}")
        if variable == "":
            variable = "jd_dpqd_tokens"
        print(f"当前变量名：{variable}")
        if splits == "":
            splits = "&"
        print(f"当前分隔符：{splits}")
        if senderType == "fake" and fakeBox == "true":
            middleware.notifyMasters("定时执行JD店铺签到", notify)
            JdDpSign().main()
        else:
            JdDpSign().main()
