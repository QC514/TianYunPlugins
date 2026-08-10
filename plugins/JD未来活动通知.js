//[disable:false]
//[author: qingge]
//[price: 2]
//[open_source: false]
//[title: JD未来活动通知]
//[router: /send_private_msg]
//[method: post]
//[public: true] 
//[method: get]
//[version: 1.3.3]
//[priority: 9999999999]
//[service: qq]
//[priority: 1]
//[description: 适合于autMan1.1.5以上，对接脚本容器推送的日志，脚本容器运行结果可直接推送到autMan，，脚本容器配置文件里加入以下参数：<br/>export GOBOT_URL="http://autMan地址:端口/send_private_msg"<br/>export GOBOT_TOKEN=""<br/>export GOBOT_QQ="自己qq号"<br/>export go_cqhttp_url="autMan的IP地址:autMan端口"<br/>export go_cqhttp_qq="自己qq号"<br/>export go_cqhttp_method="send_private_msg"，注：此插件生效需重启autMan，主要针对M库的日志进行分析，当遇到还未开始或还未结束仍有豆的活动，会将活动变量存储到定时指令里，在活动开始时运行变量，当活动结束时会从定时中删除相应变量。<br/>支持实物指定渠道以及京豆群组或个人多渠道推送<br/>支持京豆多奥特曼API推送,需要配合:信息推送,插件<br/>只能用于M本<br/>支持日志黑名单过滤<br/>插件默认禁用<br/>4.24修复推送内置管理员<br/>5.17 支持京豆中奖数据分段式发送,每条信息最多35条<br/>6-4 适配M本的直播间中豆数据<br/>6-8 增加中奖京豆用户数量]
// [param: {"required":false,"key":"who_tz.xbhmd","placeholder":"false","name":"日志黑名单","desc":"多个使用小写,号分开,则不会推送"}]
// [param: {"required":false,"key":"who_tz.xb_tzmf","placeholder":"","name":"京豆中奖通知值","desc":"京豆大于等于?才进行通知，默认0"}]
// [param: {"required":false,"key":"who_tz.xb_atm","placeholder":"","name":"API推送","desc":"填写奥特曼地址:http://192.168.0.111:8080"}]
// [param: {"spliter":true}]
// [param: {"required":false,"key":"who_tz.xb_tcrz","bool":true,"placeholder":"false","name":"调试日志","desc":"默认不输出日志,打开则输出日志"}]
// [param: {"required":false,"key":"who_tz.xb_tsrz","bool":true,"placeholder":"false","name":"推送日志","desc":"默认不输出推送渠道,需要配置下方推送：日志渠道"}]
// [param: {"required":false,"key":"who_tz.xb_tzqzqd","placeholder":"","name":"日志推送(群组)","desc":"多个使用小写,号分开,例如：wx:123456,qq:123456"}]
// [param: {"required":false,"key":"who_tz.xb_tzgrqd","placeholder":"","name":"日志推送(个人)","desc":"多个使用小写,号分开,例如：wx:123456,qq:123456"}]
// [param: {"required":false,"key":"who_tz.xb_tcjy","bool":true,"placeholder":"false","name":"日志简约推送","desc":"默认不开启,打开则简约推送日志"}]
// [param: {"spliter":true}]
// [param: {"required":false,"key":"who_tz.xb_tzqzjd","placeholder":"","name":"京豆推送(群组)","desc":"多个使用小写,号分开,例如：wx:123456,qq:123456"}]
// [param: {"required":false,"key":"who_tz.xb_tzgrjd","placeholder":"","name":"京豆推送(个人)","desc":"多个使用小写,号分开,例如：wx:123456,qq:123456"}]
// [param: {"required":false,"key":"who_tz.xb_tzgrsw","placeholder":"","name":"实物推送(个人)","desc":"多个使用小写,号分开,例如：wx:123456,qq:123456"}]
// [param: {"spliter":true}]
// [param: {"required":false,"key":"who_tz.xb_dsgrjd","placeholder":"","name":"定时推送(个人)","desc":"不配置不通知,多个使用小写,号分开,例如：wx:123456,qq:123456"}]
var xb_tcrz = bucketGet("who_tz", "xb_tcrz")
var xb_atm = bucketGet("who_tz", "xb_atm")//奥特曼接口
var xb_tsrz = bucketGet("who_tz", "xb_tsrz")//是否开启推送
var xb_tzqd = bucketGet("who_tz", "xb_tzqzqd")//日志群组推送
var xb_tzgrqd = bucketGet("who_tz", "xb_tzgrqd")//日志个人推送

var xb_tcjy = bucketGet("who_tz", "xb_tcjy")//日志简约化
var xb_tzgrjd = bucketGet("who_tz", "xb_tzgrjd")//日志京豆个人推送.
var xb_tzqzjd = bucketGet("who_tz", "xb_tzqzjd")//日志京豆群组推送.
var xb_tzgrsw = bucketGet("who_tz", "xb_tzgrsw")//日志实物群组推送
var xb_tzmf = bucketGet("who_tz", "xb_tzmf")//京豆通知门阀
var xb_dsgrjd = bucketGet("who_tz", "xb_dsgrjd")//自动定时通知
var doudou_tj = "", jd_dou = 0, dd = ""
function mian() {
    var xb_name = ""
    //Debug("路由流程")
    var router = getRouter()
    //Debug("路由：" + router)
    var method = getMethod()
    //Debug("方法：" + method)
    var params = getRouterParams()
    //Debug("参数：" + JSON.stringify(params))
    var data = getRouterData()
    //Debug("内容：" + data)
    var obj = JSON.parse(data)
    var hqdd = obj.message
    if (xb_tcrz == "true") {
        Debug(hqdd)
    }

    //日志推送


    //检查日志内容是否有已经结束，删除定时指令
    if ((/垃圾活动/.test(hqdd) || /活动已经?结束/.test(hqdd)) || /export/.test(hqdd)) {
        if (/M直播抽豆/.test(hqdd)) {

        } else {
            var exptPattern = /export \S+=\"\S+\"/
            var expt = exptPattern.exec(hqdd).toString()
            //检查变量是否重复
            var hasThisCron = false
            var cs = cron.get()
            for (i = 0; i < cs.length; i++) {
                if (cs[i].cmd == expt) {
                    cron.delete(cs[i].id)
                    break
                }
            }
        }
    }
    if (xb_tsrz == "true") {
        if (hmd(data)) {
            return
        } else {
            if (xb_tzqd == "") {//群组

            } else {
                if (xb_tcjy == "true") {
                    if (/店铺信息/.test(hqdd)) {
                        var swdd = hqdd.split("店铺信息");
                        var targetInfo = swdd[1].trim();  // 获取#百丽官方旗舰店后面的内容并去除多余空格
                    } else if (/店铺信息/.test(hqdd)) {
                        var swdd = hqdd.split("活动未开始");
                        var targetInfo = swdd[1].trim();  // 获取#百丽官方旗舰店后面的内容并去除多余空格
                    } else if (/乌托邦/.test(hqdd)) {
                        var swdd = hqdd.split("乌托邦");
                        var targetInfo = swdd[1].trim();  // 获取#百丽官方旗舰店后面的内容并去除多余空格
                    } else if (/M积分兑换/.test(hqdd)) {
                        var swdd = hqdd.split("M积分兑换");
                        var targetInfo = swdd[1].trim();  // 获取#百丽官方旗舰店后面的内容并去除多余空格
                    } else if (/本通知/.test(hqdd)) {
                        var swdd = hqdd
                    } else {
                        var swdd = hqdd.split("#");
                    }



                    if (/触发拉黑/.test(hqdd) || /火爆/.test(hqdd) || /】/.test(hqdd) || /活动未开始/.test(hqdd)) {
                        let swdd = hqdd.split("活动名称");
                        if (swdd[1] == "") {
                            var jianyue = hqdd
                        } else {
                            var jianyue = swdd
                        }

                    } else {
                        var jianyue = targetInfo
                    }
                } else {
                    var jianyue = hqdd
                }
                if (jianyue == "" || jianyue == undefined) {

                } else {
                    let tz_zd = xb_tzqd.split(",")
                    for (i = 0; i < tz_zd.length; i++) {
                        let qd_zd = tz_zd[i].split(":")
                        push({
                            imType: qd_zd[0],
                            userID: "",
                            title: "",
                            groupCode: qd_zd[1],
                            content: `${jianyue}\n---------------\运行结果通知`,
                        });

                    }
                }
            }
            if (xb_tzgrqd == "") {//个人

            } else {
                if (xb_tcjy == "true") {
                    if (/店铺信息/.test(hqdd)) {
                        var swdd = hqdd.split("店铺信息");
                        var targetInfo = swdd[1].trim();  // 获取#百丽官方旗舰店后面的内容并去除多余空格
                    } else if (/店铺信息/.test(hqdd)) {
                        var swdd = hqdd.split("活动未开始");
                        var targetInfo = swdd[1].trim();  // 获取#百丽官方旗舰店后面的内容并去除多余空格
                    } else if (/乌托邦/.test(hqdd)) {
                        var swdd = hqdd.split("乌托邦");
                        var targetInfo = swdd[1].trim();  // 获取#百丽官方旗舰店后面的内容并去除多余空格
                    } else if (/M积分兑换/.test(hqdd)) {
                        var swdd = hqdd.split("M积分兑换");
                        var targetInfo = swdd[1].trim();  // 获取#百丽官方旗舰店后面的内容并去除多余空格
                    } else if (/本通知/.test(hqdd)) {
                        var swdd = hqdd
                    } else {
                        var swdd = hqdd.split("#");
                    }




                    if (/触发拉黑/.test(hqdd) || /火爆/.test(hqdd) || /】/.test(hqdd) || /活动未开始/.test(hqdd)) {
                        let swdd = hqdd.split("活动名称");
                        if (swdd[1] == "") {
                            var jianyue = hqdd
                        } else {
                            var jianyue = swdd[1]
                        }
                    } else {
                        var jianyue = targetInfo
                    }

                } else {
                    var jianyue = hqdd
                }
                if (jianyue == "" || jianyue == undefined) {

                } else {
                    let tz_zd = xb_tzgrqd.split(",")
                    for (i = 0; i < tz_zd.length; i++) {
                        let qd_zd = tz_zd[i].split(":")
                        push({
                            imType: qd_zd[0],
                            userID: qd_zd[1],
                            title: "",
                            groupCode: "",
                            content: `${jianyue}\n--------------\n运行结果通知`,
                        });
                    }
                }
                // 

                // }

            }

        }
    }
    //京豆获取
    if (/未开始/.test(hqdd)) {
        console.log("活动未开始")
    } else {
        if (/活动名称/.test(hqdd)) {
            var xinxi = hqdd.split("活动名称")

        } else if (/店铺信息/.test(hqdd)) {
            var xinxi = hqdd.split("店铺信息")
        } else if (/活动时间/.test(hqdd)) {
            var xinxi = hqdd.split("活动时间")
        } else if (/活动时间/.test(hqdd)) {
            var xinxi = hqdd.split("活动时间")
        } else {
            var xinxi = hqdd.split("本通知")

        }
        if (/京豆/.test(xinxi[0]) || /个京豆/.test(xinxi[0]) || /直播抽豆/.test(xinxi[0])) {
            jingdou(xinxi[0])
        }
        if (/M直播抽豆/.test(hqdd)) {
            return
        }
        //
        //中奖实物
        if (/已填地址/.test(xinxi[0])) {
            if (xb_tzgrsw == "") {//群组

            } else {
                shiwu(hqdd)
            }
        }
    }




    //}
    //检查日志内容是否有未开始
    var pattern = /未开始/
    bl = pattern.test(hqdd)

    var pattern2 = /M签到有礼/
    var patternM = /活动已结束/
    bl2 = pattern2.test(hqdd) && !patternM.test(hqdd)

    var pattern3 = /购物车锦鲤beta/
    bl3 = pattern3.test(hqdd)
    var hd_name = huodong_name(hqdd)
    if (hd_name == false) {
        xb_name = "未知活动"
    } else {
        xb_name = hd_name
    }

    if ((bl || bl2 || bl3)) {//有未开始字样,或M签到有礼,或购物车锦鲤beta

        //匹配2023-09-28 00:00:00至2023-10-30 18:00:00字样
        var datePattern = /\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?[ ]?[至|-][ ]?\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配结果，数组
        var rlt = datePattern.exec(hqdd)
        //匹配开奖时间2023-09-28 00:00:00字样
        var datePattern2 = /开奖时间:\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配开奖时间结果，数组
        var rlt2 = datePattern2.exec(hqdd)
        //去除“开奖时间:”字样
        if (rlt2) {
            rlt2[0] = rlt2[0].replace(/开奖时间:/g, "")
            // Debug(rlt2[0])
        }
        //备注
        var memo
        if (bl3 && rlt2) {//购物车锦鲤
            memo = rlt2[0]//备注
        } else if (rlt) {//未来活动或签到有礼
            memo = rlt[0]//备注
        }
        // Debug("备注时间：" + memo)

        //匹配变量
        var exptPattern = /export \S+=\"\S+\"/
        //匹配结果，字符串
        try {
            var expt = exptPattern.exec(hqdd).toString()//线报信息
            //检查变量是否重复
            var hasThisCron = false
            var cs = cron.get()
            for (i = 0; i < cs.length; i++) {
                if (cs[i].cmd == expt) {
                    if (bl3 && rlt2) {//购物车锦鲤开奖了
                        cron.delete(cs[i].id)
                        break
                    } else {
                        //gertui(xb_tzgrjd, `🔔 测试定时1🎉\n重复定时...`, "")
                        hasThisCron = true
                        break
                    }
                }
            }
            //autMan里没有此变量的定时指令时
            if (!hasThisCron) {
                if (bl3 && rlt2) {//购物车锦鲤开奖活动
                    dateStr = rlt2[0].toString()
                    mins = dateStr.split(":")
                    minuteStart = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    if (minuteStart == "") {
                        minuteStart = "0"
                    }
                    hours = mins[0].split(" ")
                    hourStart = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    if (hourStart == "") {
                        hourStart = "0"
                    }
                    ymd = hours[0].split("-")
                    yearStart = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    monthStart = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    dayStart = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    cn = minuteStart + " " + hourStart + " " + dayStart + " " + monthStart + " *"
                    //添加定时指令
                    id = cron.add({
                        cron: cn,
                        cmd: expt,
                        toSelf: true,
                        toOthers: "",
                        memo: memo,
                    })
                    if (xb_dsgrjd == "") {

                    } else {

                        gertui(xb_dsgrjd, `【自动定时.】购物车锦鲤开奖\n活动时间：${rlt2} \n自动定时：${cn}\n定时内容：${expt}\n`, `${call("timeFormat")("yyyy-MM-dd hh:mm:ss")}`)

                    }
                } else if (rlt) {//未来活动或签到有礼
                    dateStr = rlt[0].toString().split("至")[0]
                    mins = dateStr.split(":")
                    minuteStart = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    if (minuteStart == "") {
                        minuteStart = "0"
                    }
                    hours = mins[0].split(" ")
                    hourStart = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    if (hourStart == "") {
                        hourStart = "0"
                    }
                    ymd = hours[0].split("-")
                    yearStart = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    monthStart = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    dayStart = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    cn = minuteStart + " " + hourStart + " " + dayStart + " " + monthStart + " *"
                    //获取结束时间
                    dateStr = rlt.toString().split("至")[1]
                    mins = dateStr.split(":")
                    minuteEnd = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    if (minuteEnd == "") {
                        minuteEnd = "0"
                    }
                    hours = mins[0].split(" ")
                    hourEnd = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    if (hourEnd == "") {
                        hourEnd = "0"
                    }
                    ymd = hours[0].split("-")
                    yearEnd = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    monthEnd = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                    dayEnd = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")

                    var actType = "\n活动类型：未来活动."
                    if (pattern2.test(hqdd)) {//签到有礼

                        //签到有礼定时
                        if (monthStart == monthEnd) {
                            cn = "0 0 " + dayStart + "-" + dayEnd + " " + monthStart + " *"
                        } else {
                            if (parseInt(monthStart) > parseInt(monthEnd)) {//跨年
                                cn = "0 0 1-31 " + monthStart + "," + monthEnd + " *"
                            } else {
                                cn = "0 0 1-31 " + monthStart + "-" + monthEnd + " *"
                            }
                        }
                        actType = "\n活动类型：签到有礼"
                        if (parseInt(monthStart) >= parseInt(call("timeFormat")("MM").replace(/(^0*)/g, ""))) {
                            if (parseInt(dayStart) >= parseInt(call("timeFormat")("dd").replace(/(^0*)/g, ""))) {
                                id = cron.add({
                                    cron: cn,
                                    cmd: expt,
                                    toSelf: true,
                                    toOthers: "",
                                    memo: rlt,
                                })
                                if (xb_dsgrjd == "") {

                                } else {

                                    gertui(xb_dsgrjd, `【自动定时.】${actType}\n活动时间：${rlt[0]} \n自动定时：${cn}\n定时内容：${expt}\n`, `${call("timeFormat")("yyyy-MM-dd hh:mm:ss")}`)

                                }
                            }
                        }
                    } else {
                        if (parseInt(monthStart) == parseInt(monthEnd)) {
                            cn = `0 ${hourStart} ${dayStart}-${dayEnd} ${monthStart} *`
                        } else {
                            if (parseInt(monthStart) > parseInt(monthEnd)) {//跨年
                                cn = `0 ${hourStart} ${dayStart}-${dayEnd} ${monthStart},${monthEnd} *`
                            } else {
                                cn = `0 ${hourStart} ${dayStart}-${dayEnd} ${monthStart}-${monthEnd} *`
                            }

                        }

                        actType = "\n活动类型：" + xb_name
                        if (parseInt(monthStart) >= parseInt(call("timeFormat")("MM").replace(/(^0*)/g, ""))) {
                            if (parseInt(dayStart) >= parseInt(call("timeFormat")("dd").replace(/(^0*)/g, ""))) {

                                if (xb_dsgrjd == "") {

                                } else {
                                    id = cron.add({
                                        cron: cn,
                                        cmd: expt,
                                        toSelf: true,
                                        toOthers: "",
                                        memo: rlt,
                                    })
                                    gertui(xb_dsgrjd, `【自动定时.】${actType}\n活动时间：${rlt[0]} \n自动定时：${cn}\n定时内容：${expt}\n`, `${call("timeFormat")("yyyy-MM-dd hh:mm:ss")}`)

                                }

                            }
                        }
                    }
                } else {//没有给出明确时间的未来活动
                    let month, day;
                    date = new Date();
                    date.setTime(date.getTime() + 24 * 60 * 60 * 1000);
                    month = date.getMonth() + 1;
                    day = date.getDate();

                    id = cron.add({
                        cron: "0 0 " + day + " " + month + " *",
                        cmd: expt,
                        toSelf: true,
                        toOthers: "",
                        memo: memo,
                    })
                    notifyMasters("【自动定时.】\n" + "活动时间：未知" + "\n自动定时：" + cn + "\n定时内容：" + expt)
                }
            } else {
                Debug("已存在此定时指令")
            }

        } catch (err) { }
    }


    //响应
    var j = {
        "status": "OK",
        "retcode": 0,
    }
    response(j)
}


//获取活动名称
function huodong_name(data) {
    let activityNameMatch = data.match(/活动名称:(.*?)\n/);  // 正则匹配活动名称
    if (activityNameMatch) {
        let activityName = activityNameMatch[1].trim();  // 提取活动名称并去除两端空格
        //console.log(`活动名称: ${activityName}`);
        return activityName
    } else {
        return false
    }
}

//---------------
function jingdou(data) {
    console.log(`开始提取京豆。。`)
    let tongji_jd = 0, doudshu = 0
    if (xb_tzmf == "") {

    } else {
        jd_dou = parseInt(xb_tzmf)
    }

    let neiron = data.split("\n")

    // 正则表达式：匹配【】内的用户名和京豆数量
    let filteredRecords = {};
    var lingqu = /已领取/
    var jfdh = /等级/

    neiron.forEach(record => {
        console.log(record)
        // 提取京豆数量
        if (/个京豆/.test(record)) {
            var matches = record.match(/(\d+)个京豆/g);
        } else if (/京豆/.test(record)) {
            var matches = record.match(/(\d+)京豆/g);
        } else {
            var matches = record.match(/(\d+)豆/g);
        }
        // 提取用户名
        let usernameMatches = record.match(/【([^】]+)】/);

        if (matches && usernameMatches) {
            let username = decodeURIComponent(usernameMatches[1]); // 提取用户名
            if (!filteredRecords[username]) {
                filteredRecords[username] = 0;
            }
            // 初始化用户名的京豆总和

            //  gertui(xb_tzgrjd, `全部数据\n${matches}\n`,call("timeFormat")("yyyy-MM-dd hh:mm:ss"))
            // 遍历所有京豆数量
            tongji_jd = tongji_jd + 1
            matches.forEach(match => {

                if (/兑换京豆/.test(record) || /等级不足/.test(record) || /已领取/.test(record)) {

                } else {

                    // gertui(xb_tzgrjd, `🔔 又薅到豆子了...🎉\n${record}  + ${tongji_jd}\n`, call("timeFormat")("yyyy-MM-dd hh:mm:ss"))
                    if (/个京豆/.test(record)) {
                        let beanCount = parseInt(match.replace('个京豆', '')); // 提取并转换京豆数量
                        if (beanCount >= jd_dou || !lingqu.test(match) || !jfdh.test(match)) { // 如果京豆数量大于等于jd_dou
                            filteredRecords[username] += beanCount; // 合并京豆数量
                        }
                    } else if (/京豆/.test(record)) {
                        let beanCount = parseInt(match.replace('京豆', '')); // 提取并转换京豆数量
                        if (beanCount >= jd_dou || !lingqu.test(match) || !jfdh.test(match)) { // 如果京豆数量大于等于jd_dou
                            filteredRecords[username] += beanCount; // 合并京豆数量
                        }
                    } else {
                        let beanCount = parseInt(match.replace('豆', '')); // 提取并转换京豆数量
                        console.log(`${usernameMatches},${beanCount}`)
                        if (beanCount >= jd_dou || !lingqu.test(match) || !jfdh.test(match)) { // 如果京豆数量大于等于jd_dou
                            filteredRecords[username] += beanCount; // 合并京豆数量
                        }
                    }

                }
            });
        }
    });

    // 输出合并后的结果
    if (tongji_jd > 0) {
        for (let username in filteredRecords) {
            let beanCount = filteredRecords[username];
            if (beanCount >= jd_dou) { // 如果京豆数量大于等于jd_dou
                //  gertui(xb_tzgrjd, `🔔 又薅到..豆子了🎉\n【${username}】 ${beanCount}豆🐶\n`,call("timeFormat")("yyyy-MM-dd hh:mm:ss"))
                doudou_tj += `【${username}】 ${beanCount}豆🐶\n`
                doudshu = doudshu + parseInt(beanCount)
            }
        }


        if (/豆/.test(doudou_tj)) {
            fengexinx(doudou_tj, doudshu)
        }
    }


}


function ts_jk(data) {

    try {
        request({
            method: "post",
            url: `${xb_atm}/qd_ts`,
            body: data,
            headers: {},
            dataType: "json",
            timeOut: 10000
        })

    } catch (err) { }
}

//群组推送
function qutui(qd, xx, time) {
    let tz_zd = qd.split(",")
    for (i = 0; i < tz_zd.length; i++) {
        let qd_zd = tz_zd[i].split(":")
        push({
            imType: qd_zd[0],
            userID: "",
            title: "",
            groupCode: qd_zd[1],
            content: `${xx}\n通知时间:${time}`,
        });

    }
}
function fengexinx(txt, dddjd) {
    let arr = []
    let tz_zd = txt.split("\n")

    if (tz_zd.length > 35) {


        arr = fenge(txt)
        for (let i = 0; i < arr.length; i++) {
            console.log(`本次获取到了数据${arr.length}--\n${arr[i]}`);
            if (xb_atm == "") {

            } else {
                try {
                    ts_jk({ "message": `🔔 又有${tz_zd.length - 1}群友薅到豆子了🎉\n${arr[i]}\n本次总收${dddjd}京豆\n通知时间:${call("timeFormat")("yyyy-MM-dd hh:mm:ss")}` })
                } catch (err) { }
            }
            if (xb_tzgrjd == "") {//个人

            } else {
                gertui(xb_tzgrjd, `🔔 又有${tz_zd.length - 1}群友薅到豆子了🎉\n${arr[i]}\n本次总收${dddjd}京豆\n`, call("timeFormat")("yyyy-MM-dd hh:mm:ss"))
            }
            if (xb_tzqzjd == "") {//群组

            } else {
                qutui(xb_tzqzjd, `🔔 又有${tz_zd.length - 1}群友薅到豆子了🎉\n${arr[i]}\n本次总收${dddjd}京豆\n`, call("timeFormat")("yyyy-MM-dd hh:mm:ss"))
            }
        }

    } else {
        if (xb_atm == "") {

        } else {
            try {
                ts_jk({ "message": `🔔 又有${tz_zd.length - 1}群友薅到豆子了🎉\n${txt}\n本次总收${dddjd}京豆\n通知时间:${call("timeFormat")("yyyy-MM-dd hh:mm:ss")}` })
            } catch (err) { }
        }
        if (xb_tzgrjd == "") {//个人

        } else {
            gertui(xb_tzgrjd, `🔔 又有${tz_zd.length - 1}群友薅到豆子了🎉\n${txt}\n本次总收${dddjd}京豆\n`, call("timeFormat")("yyyy-MM-dd hh:mm:ss"))
        }
        if (xb_tzqzjd == "") {//群组

        } else {
            qutui(xb_tzqzjd, `🔔 又有${tz_zd.length - 1}群友薅到豆子了🎉\n${txt}\n本次总收${dddjd}京豆`, call("timeFormat")("yyyy-MM-dd hh:mm:ss"))
        }
    }

}

function fenge(txt) {
    let textArr = [];
    let text_name = "";
    let tz_zd = txt.split("\n");
    tz_zd.forEach((el, index) => {
        text_name += `${el}\n`;
        if ((index + 1) % 35 === 0) {
            textArr.push(text_name);
            text_name = ``;
        }
    })
    text_name ? textArr.push(text_name) : ""

    return textArr
}


//个人推送

function gertui(qd, xx, time) {
    let tz_zd = qd.split(",")
    for (i = 0; i < tz_zd.length; i++) {
        let qd_zd = tz_zd[i].split(":")
        push({
            imType: qd_zd[0],
            userID: qd_zd[1],
            title: "",
            groupCode: "",
            content: `${xx}通知时间:${time}`,
        });

    }
}
//实物

function shiwu(data) {

    // gertui(xb_tzgrsw, `🔔 又薅到实物了🎉\n${data}`, "")
    let neiron = data.split("\n")
    for (i = 0; i < neiron.length; i++) {
        if (/已填地址/.test(neiron[i])) {
            // Debug(neiron[i]+"+---"+neiron.length)
            // 使用正则表达式提取键值对
            let prizeNameMatch = neiron[i].match(/prizeName=([^,]+)/);
            let ptpinMatch = neiron[i].match(/ptpin=([^,]+)/);

            // 提取地址信息，假设地址信息是从字符串中的最后一部分获取
            var addressInfo = neiron[i].split(',').slice(-2, -1)[0];  // 获取最后第二个逗号分隔的部分，即地址信息
            if (addressInfo == "已填地址") {
                var addressInfo = neiron[i].split(',').slice(-3, -1)[0];  // 获取最后第二个逗号分隔的部分，即地址信息
            }
            // 获取匹配的结果或默认值
            let prizeName = prizeNameMatch ? prizeNameMatch[1] : null;
            let ptpin = ptpinMatch ? ptpinMatch[1] : null;
            if (ptpin == "" || prizeName == "") {

            } else {
                dd += `账号:${ptpin}\n商品:${prizeName}\n地址:${addressInfo}\n`
            }

        }
    }
    if (/已填地址/.test(dd)) {
        gertui(xb_tzgrsw, `🔔 ..又薅到实物🎉\n${dd}\n`, call("timeFormat")("yyyy-MM-dd hh:mm:ss"))

    } else {
        gertui(xb_tzgrsw, `🔔 又薅到实物🎉\n${dd}\n`, call("timeFormat")("yyyy-MM-dd hh:mm:ss"))
    }


}
//转数组并,判断黑名单
function hmd(text) {
    let keywordList = bucketGet("who_tz", "xbhmd")
    // let keywordList = ""
    if (keywordList == "") {
        return false
    }
    const regexPattern = new RegExp(zm_zsz(keywordList).join("|"), "g");
    const result = regexPattern.test(text);
    if (result) {
        return true
    } else {
        return false
    }
}
function zm_zsz(txt) {
    const array = txt.split(',');
    return array
}
//推送消息
function tuisong(tzqd, qh, data) {
    console.log(`开始推送-用户ID：${qh}，推送内容：${data}`)
    push({
        imType: tzqd,
        userID: qh,
        title: "种豆助力推送结果:",
        groupCode: "",
        content: data,
    });
}
function qtuisong(tzqd, qh, data) {
    console.log(`开始推送-用户ID：${qh}，推送内容：${data}`)
    push({
        imType: tzqd,
        userID: "",
        title: "种豆助力推送结果:",
        groupCode: qh,
        content: data,
    });
}




mian()

