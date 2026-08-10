//[pin: true]
//[title: 顿顿饿]
//[icon: https://p0.meituan.net/csc/550883f6e156a35f4f3b26985de4beca43115.png]
//[language: es5]
//[price: 0]
//[class: 工具类]
//[author: hicong]
//[version: v1.6.4]
//[open_source: false]
//[platform: wb]
//[public:true]
//[service: 728818890]
//[description: 指令：饿了版本。仅支持青龙版本 >= 2.11.3。反馈QQ群233349587]

//[rule: ^(.*cookie2=.*)$]
//[rule: ^查询$]
//[rule: ^简单查询$]
//[rule: ^代挂$]
//[rule: ^简单代挂$]
//[rule: ^备注$]
//[rule: ^解绑$]
//[rule: ^找回$]
//[rule: ^饿了么授权检测$]
//[rule: ^饿了么授权$]
//[rule: ^饿了版本$]

//==========================配参数据（最下面）===============================
// [param: {"required":false,"key":"sm_ddb_config.disablePrivateChat","placeholder":"","bool":true,"name":"禁用私聊","desc":"开启则插件不开放私聊回复"}]
// [param: {"required":false,"key":"sm_ddb_config.disableGroupChat","placeholder":"","bool":true,"name":"禁用群聊","desc":"开启则插件不开放群聊回复"}]
// [param: {"required":false,"key":"sm_ddb_config.groupWhitelist","placeholder":"","name":"群聊白名单","desc":"留空不填写则表示全监听，填写则只回复设置的群组。多个id用英文逗号分割"}]
// [param: {"required":true,"key":"sm_ddb_config.ql","placeholder":"","name":"任务容器","desc":"后台->青龙管理里面青龙容器的名称，这里设置的是添加授权后ck提交的容器"}]
// [param: {"required":true,"key":"sm_ddb_config.qlCkMax","placeholder":"","name":"任务容器CK最大数量","desc":"不填写默认不限制"}]
// [param: {"required":false,"key":"sm_ddb_config.vipInquiry","placeholder":"","bool":true,"name":"禁止非授权账号查询","desc":"开启则只允许已授权账号进行查询"}]
// [param: {"required":true,"key":"sm_ddb_config.firstMonthIntegral","placeholder":"","name":"首月积分","desc":"单账号首月需要的积分，注意1R = 100积分"}]
// [param: {"required":true,"key":"sm_ddb_config.nextMonthIntegral","placeholder":"","name":"续费积分","desc":"单账号次月续费需要的积分，注意1R = 100积分"}]
// [param: {"required":true,"key":"sm_ddb_config.checkCKRule","placeholder":"","name":"自定义查询命令","desc":"默认：查询"}]
// [param: {"required":true,"key":"sm_ddb_config.addVIPRule","placeholder":"","name":"自定义代挂命令","desc":"默认：代挂"}]
// [param: {"required":true,"key":"sm_ddb_config.failureReply","placeholder":"","name":"自定义CK过期提示","desc":"默认：\\nCK已过期，请速度更新。\\nios用户打开App可刷新CK"}]
// [param: {"required":true,"key":"sm_ddb_config.earlyWarningReply","placeholder":"","name":"自定义CK预警提示","desc":"默认：\\n授权将在24h内过期，请续费。"}]
// [param: {"required":true,"key":"sm_ddb_config.overdueReply","placeholder":"","name":"自定义授权过期提示","desc":"默认：\\n授权已过期，请续费。"}]
// [param: {"required":true,"key":"sm_ddb_config.unboundReply","placeholder":"","name":"自定义无绑定提示","desc":"默认：无已绑定账号，发ck可绑定。\\n账号丢失请发【找回】。"}]

//获取青龙配置
function getQl() {
    qlsNames = bucketGet('sm_ddb_config', 'ql')
    var qlsKey = bucketKeys('qls')
    if (qlsKey.length == 0) {
        sendText("【顿顿饿】容器管理中对接容器不存在容器，请先对接容器给QLS权限后再使用该插件")
        notifyMasters("【顿顿饿】容器管理中对接容器不存在容器，请先对接容器给QLS权限后再使用该插件")
        return
    }
    for (var i = 0; i < qlsKey.length; i++) {
        var qls = JSON.parse(bucketGet('qls', qlsKey[i]))
        if (qls.name == qlsNames) {
            return {
                host: qls.host,
                client_id: qls.client_id,
                client_secret: qls.client_secret
            }
        }
    }
    sendText("【顿顿饿】青龙配置中不存在指定的容器")
    notifyMasters("【顿顿饿】青龙配置中不存在指定的容器")
    return
}
//请求青龙面板返回token方法
function qltoken(qlpz) {
    var body = request({
        url: qlpz.host + "/open/auth/token?client_id=" + qlpz.client_id + "&client_secret=" + qlpz.client_secret,
        method: "get",
    });
    var qltokenBody = JSON.parse(body);
    return qltokenBody.data.token;
}
//请求青龙面板查询方法
function qlselect(value, qltokens, qlpz) {
    var body = request({
        url: qlpz.host + "/open/envs?searchValue=" + value,
        method: "get",
        headers: {
            "Authorization": "Bearer " + qltokens,
        }
    });
    //console.log(body)
    var qlselectBody = JSON.parse(body)
    if (qlselectBody.data[0]) {
        return qlselectBody.data
    }
    return false
}
//青龙面板添加方法
function qlinsert(ck, uid, userid, qltokens, qlpz) {
    var body = request({
        url: qlpz.host + "/open/envs",
        method: "post",
        body: [{
            "name": "elmck",
            "value": ck,
            "remarks": uid + "@" + userid,
        }],
        headers: {
            "Authorization": "Bearer " + qltokens,
        }
    });
    var qlinsertBody = JSON.parse(body);
    return qlinsertBody;
}
//请求青龙面板更新方法
function qlupdate(ck, id, uid, userid, qltokens, qlpz) {
    var body = request({
        url: qlpz.host + "/open/envs",
        method: "put",
        body: {
            "name": "elmck",
            "value": ck,
            "id": id,
            "remarks": uid + "@" + userid,
        },
        headers: {
            "Authorization": "Bearer " + qltokens,
        }
    });
    var qlupdateBody = JSON.parse(body);
    return qlupdateBody;
}
//青龙面板删除方法
function qldelete(id, qltokens, qlpz) {
    var body = request({
        url: qlpz.host + "/open/envs",
        method: "delete",
        body: [id],
        headers: {
            "Authorization": "Bearer " + qltokens,
        }
    });
    //sendText(body)
    return body;
}
//查询饿了么方法
function checkCk(ck) {
    var body = request({
        url: "https://restapi.ele.me/eus/v5/user_detail",
        method: "get",
        headers: {
            "cookie": ck,
        },
    })
    return body;
}
//更新青龙
function updateQinglong(userId, ck) {
    var qlpz = getQl()
    var qltokens = qltoken(qlpz)
    var qlid = qlselect(userId, qltokens, qlpz)
    if (!qlid) {
        var qlbody = qlinsert(ck, GetUserID(), userId, qltokens, qlpz)
        if (qlbody.code !== 200) {
            sendText("上传青龙出错,请联系管理员")
            return false
        }
        return true
    }
    var qlbody = qlupdate(ck, qlid[0].id, GetUserID(), userId, qltokens, qlpz)
    if (qlbody.code !== 200) {
        sendText("更新青龙出错,请联系管理员")
        return false
    }
    return true
}
//检查青龙授权
function checkQinglongSq() {
    var qlpz = getQl()
    var qltokens = qltoken(qlpz)
    var qlid = qlselect("elmck", qltokens, qlpz)
    if (!qlid) {
        console.log("未找到青龙CK")
        return
    }
    qlid = qlid.map(function (item) {
        var userIdValue = item.value.split(';').filter(function (pair) {
            return pair.trim().startsWith('USERID=');
        })[0];
        var parts = userIdValue.split('=');
        userIdValue = parts.length > 1 ? parts[1] : '';

        return {
            id: item.id,
            value: userIdValue
        }
    })

    for (let i = 0; i < qlid.length; i++) {
        var item = qlid[i];
        var vipTime = bucketGet("sm_ddb_vip",
            item.value)
        if (vipTime === false || vipTime === null || vipTime === "") {
            console.log(item.value + "未授权")
            sendText(item.value + "未授权")
            qldelete(item.id, qltokens, qlpz)
        }
        if (vipTime < (Date.now() / 1000)) {
            console.log(item.value + "授权过期")
            sendText(item.value + "授权过期")
            qldelete(item.id, qltokens, qlpz)
        }
    }

    //console.log(qlid)
}
//检查青龙CK
function checkQinglongCk(userId) {
    var qlpz = getQl()
    var qltokens = qltoken(qlpz)
    var qlid = qlselect(userId, qltokens, qlpz)
    if (!qlid) {
        return false
    }
    var ck = qlid[0].value
    var checkCkBody = checkCk(ck)
    if (checkCkBody.indexOf("未登录") >= 0) {
        return false
    }
    return true
}
//获取青龙CK
function getQinglongCk(userId) {
    var qlpz = getQl()
    var qltokens = qltoken(qlpz)
    var qlid = qlselect(userId, qltokens, qlpz)
    if (!qlid) {
        return false
    }
    var ck = qlid[0].value
    var checkCkBody = checkCk(ck)
    if (checkCkBody.indexOf("未登录") >= 0) {
        return false
    }
    return ck
}
//获取青龙CK数量
function getQinglongCkNum() {
    var qlpz = getQl()
    var qltokens = qltoken(qlpz)
    var qlid = qlselect("elmck", qltokens, qlpz)
    if (!qlid) {
        return false
    }
    var ckNum = qlid.length
    return ckNum
}
//简单查询
function jiandanChaxun() {
    var bindUserid = bucketKeys("sm_ddb_userData_WB", GetUserID())
    var unboundReply = bucketGet("sm_ddb_config", "unboundReply") || "无已绑定账号，发ck可绑定。\n账号丢失请发【找回】。"
    if (bindUserid === false || bindUserid.length == 0) {
        sendText(unboundReply)
        return
    } else {
        sendText("请选择要查询的数据：\n【1】今日乐园币\n【2】总乐园币\n【3】剩余授权时间")
        sendText("输入序号，回复'q'退出")
        var msg = input(60000)
        if (msg == '') {
            sendText('输入超时，自动退出程序')
            return
        }
        if (msg == 'q' || msg == 'Q') {
            sendText('退出成功')
            return
        }
        var leixing
        if (msg == "1") {
            leixing = "今日乐园币"
        } else if (msg == "2") {
            leixing = "总乐园币"
        } else if (msg == "3") {
            sendText("获取数据中，请稍后")
            var useridArray = bindUserid.map(function (userId, index) {
                var ck = bucketGet("sm_ddb_CKDB", userId)
                var shuju = jiandanVipTime(userId)
                var Phone = bucketGet("sm_ddb_phone", userId)
                var beizhu
                if (Phone !== "") {
                    //var firstFourDigits = Phone.substring(0, 3);
                    var lastFourDigits = Phone.substring(Phone.length - 4);
                    beizhu = lastFourDigits
                } else {
                    beizhu = userId
                }
                return (index + 1) + '.[' + (bucketGet("sm_ddb_remarks", userId) || beizhu) + "] " + shuju
            }).join('\n')
            sendText('剩余授权时间（天）' + "\n" + useridArray)
            return
        } else {
            sendText("输入错误")
            return
        }
        sendText("获取数据中，请稍后")
        var useridArray = bindUserid.map(function (userId, index) {
            var ck = bucketGet("sm_ddb_CKDB", userId)
            var shuju = jiandanZichan(ck, userId, leixing)
            var Phone = bucketGet("sm_ddb_phone", userId)
            var beizhu
            if (Phone !== "") {
                //var firstFourDigits = Phone.substring(0, 3);
                var lastFourDigits = Phone.substring(Phone.length - 4);
                beizhu = lastFourDigits
            } else {
                beizhu = userId
            }
            return (index + 1) + '.[' + (bucketGet("sm_ddb_remarks", userId) || beizhu) + "] " + shuju
        }).join('\n')
        sendText(leixing + "\n" + useridArray)
        return
    }
}
//查询
function chaxun() {
    var bindUserid = bucketKeys("sm_ddb_userData_WB",
        GetUserID())
    var unboundReply = bucketGet("sm_ddb_config",
        "unboundReply") || "无已绑定账号，发ck可绑定。\n账号丢失请发【找回】。"
    if (bindUserid === false || bindUserid.length == 0) {
        sendText(unboundReply)
        return
    } else {
        if (bindUserid.length == 1) {
            var userId = bindUserid[0]
            var ck = bucketGet("sm_ddb_CKDB", userId)
            zichan(ck, userId)
            return
        }
        var useridArray = bindUserid.map(function (userId, index) {
            return '【' + (index + 1) + '】' + userId
        }).join('\n')
        sendText("请选择要查询的账号：\n【0】全部\n" + useridArray)
        sendText("输入你的账号序号，逗号或空格分割，回复'q'退出")
        var msg = input(60000)
        if (msg == '') {
            sendText('输入超时，自动退出程序')
            return
        }
        if (msg == 'q' || msg == 'Q') {
            sendText('退出成功')
            return
        }
        var msgNumbers = msg.split(/[，,\s]+/)
        sendText("获取数据中，请稍后")
        if (msgNumbers.indexOf('0') !== -1) {
            for (var i = 0; i < bindUserid.length; i++) {
                var userId = bindUserid[i]
                var ck = bucketGet("sm_ddb_CKDB", userId)
                zichan(ck, userId)
            }
            return
        } else {
            for (var i = 0; i < msgNumbers.length; i++) {
                var msgNumber = msgNumbers[i]
                var index = parseInt(msgNumber, 10) - 1
                if (isNaN(index) || index < 0 || index >= bindUserid.length) {
                    sendText('无效的序列号:' + (index + 1))
                    break
                }
                var userId = bindUserid[index]
                var ck = bucketGet("sm_ddb_CKDB", userId)
                zichan(ck, userId)
            }
            return
        }
    }
}
//简单代挂
function jiandanDaigua() {
    var bindUserid = bucketKeys("sm_ddb_userData_WB", GetUserID())
    var unboundReply = bucketGet("sm_ddb_config", "unboundReply") || "无已绑定账号，发ck可绑定。\n账号丢失请发【找回】。"
    if (bindUserid === false || bindUserid.length == 0) {
        sendText(unboundReply)
        return
    } else {
        sendText("---------价格---------\n首月：" + bucketGet("sm_ddb_config", "firstMonthIntegral") + "积分/月\n续费：" + bucketGet("sm_ddb_config", "nextMonthIntegral") + "积分/月")
        sendText('请认真输入需要操作的账号USERID，逗号或空格分割，回复\'q\'退出')
        var msg = input(60000)
        if (msg == '') {
            sendText('输入超时，自动退出程序')
            return
        }
        if (msg == 'q' || msg == 'Q') {
            sendText('退出成功')
            return
        }
        var useridArray = msg.split(/[，,\s]+/)
        var xiaoxi = ""
        sendText('请输入需要的数量（单位：月），回复\'q\'退出')
        var msg = input(60000)
        if (msg == '') {
            sendText('输入超时，自动退出程序')
            return
        }
        if (msg == 'q' || msg == 'Q') {
            sendText('退出成功')
            return
        }
        var num = Number(msg);
        if (isNaN(num)) {
            sendText('输入错误')
            return
        }
        for (var i = 0; i < useridArray.length; i++) {
            var userId = useridArray[i]
            var ck = bucketGet("sm_ddb_CKDB", userId)
            xufei(ck, userId, num)
        }
        return
    }
}
//代挂
function daigua() {
    var bindUserid = bucketKeys("sm_ddb_userData_WB", GetUserID())
    var unboundReply = bucketGet("sm_ddb_config", "unboundReply") || "无已绑定账号，发ck可绑定。\n账号丢失请发【找回】。"
    if (bindUserid === false || bindUserid.length == 0) {
        sendText(unboundReply)
        return
    } else {
        var useridArray = bindUserid.map(function (userId, index) {
            var Phone = bucketGet("sm_ddb_phone", userId)
            var newPhone
            if (Phone !== "") {
                var firstFourDigits = Phone.substring(0, 3);
                var lastFourDigits = Phone.substring(Phone.length - 4);
                newPhone = firstFourDigits + "****" + lastFourDigits
            } else {
                newPhone = null
            }
            var vipTime = bucketGet("sm_ddb_vip", userId)
            if (vipTime == "") {
                vipTime = "\n授权过期：未授权"
            } else if (vipTime < (Date.now() / 1000)) {
                vipTime = "\n授权过期：已过期"
            } else {
                vipTime = "\n授权过期：" + timeFmt("yyyy-MM-dd", parseInt(vipTime, 10))
            }
            return '【' + (index + 1) + '】' + userId + '\n' + '手机号码：' + newPhone + vipTime
        }).join('\n')
        var maxLines = 600;
        var lines = useridArray.split('\n');
        var segments = [];

        for (var i = 0; i < lines.length; i += maxLines) {
            segments.push(lines.slice(i, i + maxLines).join('\n'));
        }

        segments.forEach(function (segment) {
            sendText("---------价格---------\n首月：" + bucketGet("sm_ddb_config", "firstMonthIntegral") + "积分/月\n续费：" + bucketGet("sm_ddb_config", "nextMonthIntegral") + "积分/月\n\n---------账号---------\n" + segment);
        });
        sendText("输入你的账号序号，逗号或空格分割，'0'为全部选择，回复'q'退出")
        var msg = input(60000)
        if (msg == '') {
            sendText('输入超时，自动退出程序')
            return
        }
        if (msg == 'q' || msg == 'Q') {
            sendText('退出成功')
            return
        }
        var msgNumbers = msg.split(/[，,\s]+/)
        var xiaoxi = ""
        if (msgNumbers.indexOf('0') !== -1) {
            sendText('请输入需要的数量（单位：月），回复\'q\'退出')
            var msg = input(60000)
            if (msg == '') {
                sendText('输入超时，自动退出程序')
                return
            }
            if (msg == 'q' || msg == 'Q') {
                sendText('退出成功')
                return
            }
            var num = Number(msg);
            if (isNaN(num)) {
                sendText('输入错误')
                return
            }
            for (var i = 0; i < bindUserid.length; i++) {
                var userId = bindUserid[i]
                var ck = bucketGet("sm_ddb_CKDB", userId)
                xufei(ck, userId, num)
            }
            return
        } else {
            sendText('请输入需要的数量（单位：月），回复\'q\'退出')
            var msg = input(60000)
            if (msg == '') {
                sendText('输入超时，自动退出程序')
                return
            }
            if (msg == 'q' || msg == 'Q') {
                sendText('退出成功')
                return
            }
            var num = Number(msg);
            if (isNaN(num)) {
                sendText('输入错误')
                return
            }
            for (var i = 0; i < msgNumbers.length; i++) {
                var msgNumber = msgNumbers[i]
                var index = parseInt(msgNumber, 10) - 1
                if (isNaN(index) || index < 0 || index >= bindUserid.length) {
                    sendText('无效的序列号:' + (index + 1))
                    break
                }
                var userId = bindUserid[index]
                var ck = bucketGet("sm_ddb_CKDB", userId)
                xufei(ck, userId, num)
            }
            return
        }
    }
}
//备注
function beizhu() {
    var bindUserid = bucketKeys("sm_ddb_userData_WB", GetUserID())
    var unboundReply = bucketGet("sm_ddb_config", "unboundReply") || "无已绑定账号，发ck可绑定。\n账号丢失请发【找回】。"
    if (bindUserid === false || bindUserid.length == 0) {
        sendText(unboundReply)
        return
    } else {
        var useridArray = bindUserid.map(function (userId, index) {
            var Phone = bucketGet("sm_ddb_phone", userId)
            var newPhone
            if (Phone !== "") {
                var firstFourDigits = Phone.substring(0, 3);
                var lastFourDigits = Phone.substring(Phone.length - 4);
                newPhone = firstFourDigits + "****" + lastFourDigits
            } else {
                newPhone = null
            }
            return '【' + (index + 1) + '】' + userId + "\n手机号码：" + newPhone + "\n当前备注：" + (bucketGet("sm_ddb_remarks", userId) || null)
        }).join('\n')
        var xiaoxi = ""
        sendText("请选择要备注的账号：\n" + useridArray)
        sendText("输入你的账号序号，逗号或空格分割，回复'q'退出")
        var msg = input(60000)
        if (msg == '') {
            sendText('输入超时，自动退出程序')
            return
        }
        if (msg == 'q' || msg == 'Q') {
            sendText('退出成功')
            return
        }
        var msgNumbers = msg.split(/[，,\s]+/)
        sendText("请输入要设置的备注：")
        var msg = input(60000)
        if (msg == '') {
            sendText('输入超时，自动退出程序')
            return
        }
        if (msg == 'q' || msg == 'Q') {
            sendText('退出成功')
            return
        }
        var msgBeizhu = msg
        for (var i = 0; i < msgNumbers.length; i++) {
            var msgNumber = msgNumbers[i]
            var index = parseInt(msgNumber, 10) - 1
            if (isNaN(index) || index < 0 || index >= bindUserid.length) {
                sendText('无效的序列号:' + (index + 1))
                break
            }
            var userId = bindUserid[index]
            bucketSet("sm_ddb_remarks", userId, msgBeizhu)
            xiaoxi += userId + " 备注：" + msgBeizhu + "\n"
        }
        sendText(xiaoxi)
    }
}
//解绑
function jiebang() {
    var bindUserid = bucketKeys("sm_ddb_userData_WB", GetUserID())
    if (bindUserid === false || bindUserid.length == 0) {
        sendText("未查询到已绑定账号")
        return
    } else {
        var useridArray = bindUserid.map(function (userId, index) {
            return '【' + (index + 1) + '】' + userId
        }).join('\n')
        sendText("请选择要解绑的账号：\n【0】全部\n" + useridArray)
        sendText("输入你的账号序号，逗号或空格分割，回复'q'退出")
        var msg = input(60000)
        if (msg == '') {
            sendText('输入超时，自动退出程序')
            return
        }
        if (msg == 'q' || msg == 'Q') {
            sendText('退出成功')
            return
        }
        var xiaoxi = ""
        var msgNumbers = msg.split(/[，,\s]+/)
        if (msgNumbers.indexOf('0') !== -1) {
            for (var i = 0; i < bindUserid.length; i++) {
                var userId = bindUserid[i]
                bucketDel("sm_ddb_userData_WB", userId)
                xiaoxi += userId + "解绑成功\n"
            }
        } else {
            for (var i = 0; i < msgNumbers.length; i++) {
                var msgNumber = msgNumbers[i]
                var index = parseInt(msgNumber, 10) - 1
                if (isNaN(index) || index < 0 || index >= bindUserid.length) {
                    sendText('无效的序列号:' + (index + 1))
                    break
                }
                var userId = bindUserid[index]
                bucketDel("sm_ddb_userData_WB", userId)
                xiaoxi += userId + "解绑成功\n"
            }
        }
        sendText(xiaoxi)
    }
}
//找回
function zhaohui() {
    sendText("请发送一个绑定的CK")
    var msg = input(60000)
    if (msg == '') {
        sendText('输入超时，自动退出程序')
        return
    }
    if (msg == 'q' || msg == 'Q') {
        sendText('退出成功')
        return
    }
    var checkCkBody = checkCk(msg)
    checkCkBody = JSON.parse(checkCkBody)
    if (!checkCkBody.user_id) {
        sendText("无效COOKIE，自动退出程序")
        return
    }
    var Uid = bucketGet("sm_ddb_userData_WB", checkCkBody.user_id)
    if (Uid == "") {
        sendText("未查询到ck绑定关系")
        return
    }
    if (Uid == GetUserID()) {
        sendText("无需找回")
        return
    }
    var useridArray = bucketKeys("sm_ddb_userData_WB", Uid)
    if (useridArray === false || useridArray.length == 0) {
        sendText("未查询到uid绑定关系")
        return
    }
    var succ = ""
    for (var i = 0; i < useridArray.length; i++) {
        var number = useridArray[i]
        bucketSet("sm_ddb_userData_WB", number, GetUserID())
        succ += number + "找回成功\n"
    }
    if (bucketGet("yg_xq_ql", Uid)) {
        var rq = bucketGet("yg_xq_ql", Uid)
        bucketSet("yg_xq_ql", GetUserID(), rq)
        bucketDel("yg_xq_ql", Uid)
    }
    sendText(succ + "\n原UID:" + Uid + "\n现UID:" + GetUserID())

    return
}
//检查ck
function jianchaShouquan() {
    console.log("开始检查青龙授权")
    sendText("开始检查青龙授权")
    checkQinglongSq()
    console.log("开始检查青龙变量")
    sendText("开始检查青龙变量")
    var yujingCk = []
    var shixiaoCk = []
    var wushouquanCk = []
    var useridArray = bucketAllKeys("sm_ddb_vip")
    for (var i = 0; i < useridArray.length; i++) {
        var userId = useridArray[i]
        var vipTime = bucketGet("sm_ddb_vip", userId)
        if (vipTime > (Date.now() / 1000)) {
            //console.log("授权未过期")
            if (vipTime - (Date.now() / 1000) < 86400) {
                yujingCk.push(userId)
            }
            var ck = bucketGet("sm_ddb_CKDB", userId)
            var checkCkBody = checkCk(ck)
            if (checkCkBody.indexOf("未登录") >= 0) {
                var youxiao = checkQinglongCk(userId)
                if (!youxiao) {
                    shixiaoCk.push(userId)
                }
            }
            sleep(100)
            continue
        } else {
            //var ck = bucketGet("sm_ddb_CKDB",userId)
            wushouquanCk.push(userId)
            //console.log("授权过期")
            sleep(100)
            continue
        }
    }
    console.log("失效:" + shixiaoCk)
    sendText("失效:" + shixiaoCk)
    console.log("无授权:" + wushouquanCk)
    sendText("无授权:" + wushouquanCk)
    console.log("开始推送消息")
    sendText("开始推送消息")
    tuisong(shixiaoCk, wushouquanCk, yujingCk)
    console.log("推送消息完毕")
    sendText("推送消息完毕")
}
//饿了么授权
function shouquan() {
    sendText('请认真输入需要操作的账号USERID，逗号或空格分割，回复\'q\'退出')
    var msg = input(60000)
    if (msg == '') {
        sendText('输入超时，自动退出程序')
        return
    }
    if (msg == 'q' || msg == 'Q') {
        sendText('退出成功')
        return
    }
    var useridArray = msg.split(/[，,\s]+/)
    var xiaoxi = ""
    sendText('请输入要增加的授权天数，回复\'q\'退出')
    var msg = input(60000)
    if (msg == '') {
        sendText('输入超时，自动退出程序')
        return
    }
    if (msg == 'q' || msg == 'Q') {
        sendText('退出成功')
        return
    }
    var num = Number(msg);
    if (isNaN(num)) {
        sendText('输入错误')
        return
    }
    for (var i = 0; i < useridArray.length; i++) {
        var userId = useridArray[i]
        var vipTime = bucketGet("sm_ddb_vip", userId)
        if (vipTime == "") {
            sendText("未查询到授权数据，从当前时间增加天数")
            vipTime = Date.now() / 1000
        }
        setTime = parseInt(vipTime, 10) + (86400 * num)
        bucketSet("sm_ddb_vip", userId, setTime)
        sendText("授权成功")
    }
}
//续费
function xufei(ck, userId, num) {
    if (num <= 0) {
        sendText("佛祖保佑，永无 bug")
        return
    }
    if (num % 1 !== 0) {
        sendText('输入错误')
        return
    }
    var leixing = "月卡续费"
    var danjia = Number(bucketGet("sm_ddb_config", "nextMonthIntegral"))
    var shouyue = danjia
    var vipTime = bucketGet("sm_ddb_vip", userId)
    if (vipTime == "") {
        if (bucketGet("sm_ddb_config", "qlCkMax") !== "") {
            var qlCkMax = Number(bucketGet("sm_ddb_config", "qlCkMax"))
            if (qlCkMax <= getQinglongCkNum()) {
                sendText("容器已满")
                notifyMasters("容器已满\n设置任务容器CK最大数量:" + qlCkMax + "\n当前任务容器CK最大数量:" + getQinglongCkNum())
                return
            }
        }
        leixing = "月卡首月"
        if (num > 1) {
            leixing = "月卡首月、续费"
        }
        shouyue = Number(bucketGet("sm_ddb_config", "firstMonthIntegral"))
    }
    var jifen = bucketGet(("sm_gaia_userData_" + GetImType().toUpperCase()), GetUserID()) || null
    if (jifen == null) {
        bucketSet("sm_gaia_userData_" + GetImType().toUpperCase(), GetUserID(), `{"balance":0,"isBlacklist":false,"registrationTime":"${timeFmt()}"}`)
        jifen = bucketGet(("sm_gaia_userData_" + GetImType().toUpperCase()), GetUserID())
    }
    jifen = JSON.parse(jifen)
    if (jifen.balance < (danjia * (num - 1)) + shouyue) {
        sendText("========结算========\n【类型】" + leixing + "\n【数量】" + num + "\n【总价】" + ((danjia * (num - 1)) + shouyue) + "\n【结果】余额不足\n" + "【账号】" + userId);
        return
    }
    var setTime
    if (vipTime < (Date.now() / 1000)) {
        if (bucketGet("sm_ddb_config", "qlCkMax") !== "") {
            var qlCkMax = Number(bucketGet("sm_ddb_config", "qlCkMax"))
            if (qlCkMax <= getQinglongCkNum()) {
                sendText("容器已满")
                notifyMasters("容器已满\n设置任务容器CK最大数量:" + qlCkMax + "\n当前任务容器CK最大数量:" + getQinglongCkNum())
                return
            }
        }
        setTime = Math.round(Date.now() / 1000) + (2592000 * num)
    } else {
        setTime = parseInt(vipTime, 10) + (2592000 * num)
    }
    bucketSet("sm_ddb_vip", userId, setTime)
    var newBalance = jifen.balance - (danjia * (num - 1)) - shouyue
    jifen.balance = newBalance
    bucketSet(("sm_gaia_userData_" + GetImType().toUpperCase()), GetUserID(), JSON.stringify(jifen))
    sendText("========结算========\n【类型】" + leixing + "\n【数量】" + num + "\n【总价】" + ((danjia * (num - 1)) + shouyue) + "\n【结果】支付成功\n" + "【账号】" + userId);
    var checkCkBody = checkCk(ck)
    if (checkCkBody.indexOf("未登录") >= 0) {
        return
    }
    var updateQlCk = updateQinglong(userId, ck)
    return
}
//总乐园币
function getZongLyb(mh5tk, ck) {
    var zongLyb
    data = {
        "bizScene": "IDIOM",
        "bizParam": "{\"type\":\"ggetGold\"}",
        "bizMethod": "queryIndex"
    };
    var body = "data=" + encodeURIComponent(JSON["stringify"](data));
    var t = Date.now();
    var sign = map(mh5tk, t, data);
    request({
        url: 'https://shopping.ele.me/h5/mtop.alsc.playgame.mini.game.dispatch/1.0/?jsv=2.6.1&appKey=12574478&t=' + t + '&sign=' + sign + '&api=mtop.alsc.playgame.mini.game.dispatch&v=1.0&type=originaljson&dataType=json&timeout=5000&subDomain=shopping&mainDomain=ele.me&H5Request=true&pageDomain=ele.me&ttid=h5%40chrome_android_87.0.4280.141&SV=5.0',
        method: 'POST',
        headers: {
            authority: 'shopping.ele.me',
            accept: 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            origin: 'https://r.ele.me',
            pragma: 'no-cache',
            referer: 'https://r.ele.me/linkgame/index.html?navType=3&spm-pre=a2ogi.13162730.zebra-ele-login-module-9089118186&spm=a13.b_activity_kb_m71293.0.0',
            cookie: ck
        },
        body: body
    },
        function (error, response, header, body) {

            if (!error && response["statusCode"] === 200) {
                body = JSON.parse(body)
                body = JSON.parse(body.data.data)
                zongLyb = body.num
            } else {
                zongLyb = '异常'
            }
        });
    return zongLyb
}
//今日乐园币
function getJinriLyb(mh5tk, ck, yeshu) {
    var jinriLyb
    var startTime = timeFmt("yyyy-MM-dd") + " 00:00:00";
    var data = {
        "templateId": "1404", "bizScene": "game_center", "convertType": "GAME_CENTER", "startTime": startTime, "pageNo": yeshu, "pageSize": "20"
    };
    var body = "data=" + encodeURIComponent(JSON["stringify"](data));
    var t = Date.now();
    var sign = map(mh5tk,
        t,
        data);
    request({
        url: 'https://mtop.ele.me/h5/mtop.koubei.interaction.center.common.querypropertydetail/1.0/?jsv=2.7.1&appKey=12574478&t=' + t + '&sign=' + sign + '&api=mtop.koubei.interaction.center.common.querypropertydetail&v=1.0',
        method: 'POST',
        headers: {
            authority: 'mtop.ele.me',
            accept: 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            cookie: ck,
            origin: 'https://tb.ele.me',
            pragma: 'no-cache',
            referer: 'https://tb.ele.me/wow/alsc/mod/b9ee9e6451bc8eda7a6afcbb?spm=a2ogi.13162730.zebra-ele-login-module-9089118186&spm=a2ogi.13162730.zebra-ele-login-module-9089118186&spm-pre=a13.b_activity_kb_m71293.ebridge.login'
        },
        body: body
    },
        function (error, response, header, body) {
            if (!error && response["statusCode"] === 200) {
                var body = JSON.parse(body);
                //console.log(body);
                if (body.data.list) {
                    var lyb = 0;
                    for (let i = 0; i < body["data"]["list"]["length"]; i++) {
                        var _0x4b8946 = body["data"]["list"][i];
                        if (_0x4b8946["detailType"] === "GRANT" && _0x4b8946["gmtModified"]["indexOf"](timeFmt("yyyy-MM-dd")) !== -1) {
                            lyb += Number(_0x4b8946["amount"]);
                        }
                    }
                }
                jinriLyb = lyb
            } else {
                return null;
            }
        });
    return jinriLyb
}
//吃货豆
function getChd(ck) {
    var todayDou
    request({
        url: 'https://h5.ele.me/restapi/svip_biz/v1/supervip/foodie/records?latitude=39.90498795617771&limit=20&longitude=116.40528968768549&offset=0',
        headers: {
            Cookie: ck
        }
    },
        function (error, response, header, body) {
            if (!error && response["statusCode"] === 200) {
                var _0x1edc17 = JSON["parse"](body);
                if (_0x1edc17.records && _0x1edc17.records.length > 0) {
                    //console.log(_0x1edc17);
                    var jinriDouLB = _0x1edc17.records
                    todayDou = 0;
                    for (let i = 0; i < jinriDouLB.length; i++) {
                        var now = new Date();
                        var currentYear = now.getFullYear();
                        var currentMonth = String(now.getMonth() + 1).padStart(2, '0');
                        var currentDay = String(now.getDate()).padStart(2, '0');
                        var currentDateString = currentYear + '-' + currentMonth + '-' + currentDay;
                        var createdDate = jinriDouLB[i].createdTime.split(' ')[0];
                        if (createdDate === currentDateString) {
                            todayDou += jinriDouLB[i].count;
                        } else { }
                    }
                } else {
                    //console.error('jinriDouLB is null or undefined');
                    todayDou = 0
                }
                //console.log(todayDou);
                sumDou = _0x1edc17["peaCount"]
            }
        });
    return {
        zongChd: sumDou,
        jinriChd: todayDou
    }
}
//笔笔返
function getBibifan(ck) {
    var bibiFan
    request({
        url: 'https://httpizza.ele.me/walletUserV2/storedcard/queryBalanceBycardType?cardType=platform',
        headers: {
            Cookie: ck,
            referer: 'https://r.ele.me/alsc-wallet/home.html?channel=grzx'
        }
    },
        function (error, response, header, body) {
            if (!error && response["statusCode"] === 200) {
                const _0x1edc17 = JSON["parse"](body);
                //console.log(_0x1edc17);
                bibiFan = _0x1edc17["data"]["totalAmount"];
            }
        });
    return bibiFan
}
//简单VipTime
function jiandanVipTime(userId) {
    var vipTime = bucketGet("sm_ddb_vip", userId)
    if (vipTime == "") {
        vipTime = "未授权"
    } else if (vipTime < (Date.now() / 1000)) {
        vipTime = "已过期"
    } else {
        //vipTime = timeFmt("yyyy-MM-dd", parseInt(vipTime, 10))
        vipTime = Math.round(((vipTime - (Date.now() / 1000)) / 86400) * 100) / 100
    }
    return vipTime
}
//简单资产
function jiandanZichan(ck, userId, leixing) {
    var regexCombined = /(_m_h5_tk=[0-9a-f]+_[0-9]+|_m_h5_tk_enc=[0-9a-f]+);/g;
    ck = ck.replace(regexCombined,
        '')
    ck = ck.replace(/\s+/g,
        '') + ";"
    var vipTime = bucketGet("sm_ddb_vip",
        userId)
    if (vipTime === false || vipTime === null || vipTime === "") {
        if (bucketGet('sm_ddb_config', 'vipInquiry') === "true" ? true : false) {
            return "未授权"
        }
    }
    if (vipTime < (Date.now() / 1000)) {
        if (bucketGet('sm_ddb_config', 'vipInquiry') === "true" ? true : false) {
            return "授权过期"
        }
    }
    //vipTime = timeFmt("yyyy-MM-dd", parseInt(vipTime, 10))
    var checkCkBody = checkCk(ck)
    checkCkBody = JSON.parse(checkCkBody)
    if (!checkCkBody.username) {
        ck = getQinglongCk(userId)
        if (!ck) {
            return "CK无效"
        }
        var checkCkBody = checkCk(ck)
        checkCkBody = JSON.parse(checkCkBody)
    }
    var shuju
    request({
        url: 'https://waimai-guide.ele.me/h5/mtop.alsc.personal.queryminecenter/1.0/?jsv=2.6.2&appKey=12574478',
        headers: {
            Cookie: ck,
            method: 'GET'
            //'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
        }
    }, function (error, response, header, body) {
        var str = JSON.stringify(header);
        var mh5tk = str.match(/_m_h5_tk=([^_]+)/)[1];
        var regex1 = /_m_h5_tk=[0-9a-f]+_[0-9]+;/;
        var regex2 = /_m_h5_tk_enc=[0-9a-f]+;/;
        var str1 = str.match(regex1)[0];
        var str2 = str.match(regex2)[0];
        ck = ck + str1 + str2;
        if (leixing == "今日乐园币") {
            var yeshu = 1
            var yeshuLyb = getJinriLyb(mh5tk, ck, yeshu)
            shuju = yeshuLyb;
            while (yeshuLyb) {
                yeshu = yeshu + 1;
                yeshuLyb = getJinriLyb(mh5tk, ck, yeshu)
                shuju += yeshuLyb
            }
            if (!shuju) {
                shuju = 0
            }
        } else if (leixing == "总乐园币") {
            shuju = getZongLyb(mh5tk, ck)
        }
    });
    return shuju
}
//资产
function zichan(ck, userId) {
    var regexCombined = /(_m_h5_tk=[0-9a-f]+_[0-9]+|_m_h5_tk_enc=[0-9a-f]+);/g;
    ck = ck.replace(regexCombined,
        '')
    ck = ck.replace(/\s+/g,
        '') + ";"
    var vipTime = bucketGet("sm_ddb_vip",
        userId)
    if (vipTime == "") {
        vipTime = "未授权"
        if (bucketGet('sm_ddb_config', 'vipInquiry') === "true" ? true : false) {
            sendText(userId + "未授权")
            return
        }
    }
    if (vipTime < (Date.now() / 1000)) {
        if (bucketGet('sm_ddb_config', 'vipInquiry') === "true" ? true : false) {
            sendText(userId + "授权过期")
            return
        }
    }
    if (vipTime !== "未授权") {
        vipTime = timeFmt("yyyy-MM-dd", parseInt(vipTime, 10))
    }
    var checkCkBody = checkCk(ck)
    checkCkBody = JSON.parse(checkCkBody)
    if (!checkCkBody.username) {
        ck = getQinglongCk(userId)
        if (!ck) {
            phone = bucketGet("sm_ddb_phone", userId)
            if (phone === "") {
                phone = null
            } else {
                var firstFourDigits = phone.substring(0, 3);
                var lastFourDigits = phone.substring(phone.length - 4);
                phone = firstFourDigits + "****" + lastFourDigits
            }
            sendText("=====ElmCK过期=====\n备注：" + (bucketGet("sm_ddb_remarks", userId) || null) + "\n用户ID：" + userId + "\n手机号：" + phone)
            return
        } else {
            var checkCkBody = checkCk(ck)
            checkCkBody = JSON.parse(checkCkBody)
        }
    }
    request({
        url: 'https://waimai-guide.ele.me/h5/mtop.alsc.personal.queryminecenter/1.0/?jsv=2.6.2&appKey=12574478',
        headers: {
            Cookie: ck,
            method: 'GET'
            //'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
        }
    }, function (error, response, header, body) {
        var str = JSON.stringify(header);
        //console.log(str)
        var mh5tk = str.match(/_m_h5_tk=([^_]+)/)[1];
        var regex1 = /_m_h5_tk=[0-9a-f]+_[0-9]+;/;
        var regex2 = /_m_h5_tk_enc=[0-9a-f]+;/;
        //console.log("mh5tk:" + mh5tk)
        var str1 = str.match(regex1)[0];
        //console.log("str1:" + str1)
        var str2 = str.match(regex2)[0];
        //console.log("str2:" + str2)
        ck = ck + str1 + str2;
        //console.log("新:" + ck)
        var zongLyb = getZongLyb(mh5tk, ck)
        var chihuodou = getChd(ck)
        var yeshu = 1
        var yeshuLyb = getJinriLyb(mh5tk, ck, yeshu)
        var jinriLyb = yeshuLyb;
        while (yeshuLyb) {
            yeshu = yeshu + 1;
            yeshuLyb = getJinriLyb(mh5tk, ck, yeshu)
            jinriLyb += yeshuLyb
        }
        if (!jinriLyb) {
            jinriLyb = 0
        }
        var bibifan = getBibifan(ck) / 100
        //var checkCkBody = checkCk(ck);
        //checkCkBody = JSON.parse(checkCkBody)
        bucketSet("sm_ddb_phone", checkCkBody.user_id, checkCkBody.mobile)
        var newPhone
        if (checkCkBody.mobile !== null) {
            var firstFourDigits = checkCkBody.mobile.substring(0, 3);
            var lastFourDigits = checkCkBody.mobile.substring(checkCkBody.mobile.length - 4);
            newPhone = firstFourDigits + "****" + lastFourDigits
        } else {
            newPhone = null
        }
        sendText("【用户ID】" + checkCkBody.user_id + "\n【用户名】" + checkCkBody.username + "\n【手机号】" + newPhone + "\n【总吃货豆】" + chihuodou.zongChd + "\n【总乐园币】" + zongLyb + "\n【今日吃货豆】" + chihuodou.jinriChd + "\n【今日乐园币】" + jinriLyb + "\n【笔笔返余额】" + bibifan + "\n【云授权到期】" + vipTime);
        return
    });
}
function map(mh5tk, ts, data) {
    var e = call("md5")(mh5tk + "&" + ts + "&" + '12574478' + "&" + JSON.stringify(data))
    return e
}
//推送失效ck
function tuisong(shixiaoCk, wushouquanCk, yujingCk) {
    var imTypes = bucketGet("sm_ddb_config",
        "imTypes") || "wb"
    for (var i = 0; i < shixiaoCk.length; i++) {
        var userId = shixiaoCk[i]
        var uid = bucketGet("sm_ddb_userData_WB", userId)
        if (uid == "") {
            continue
        }
        var phone = bucketGet("sm_ddb_phone", userId) || null
        var beizhu = bucketGet("sm_ddb_remarks", userId) || null
        var failureReply = bucketGet("sm_ddb_config", "failureReply").replace(/\\n/g, '\n') || "\nCK已过期，请速度更新。\nios用户打开App可刷新CK"
        var text = "=====ElmCK过期通知=====\n备注：" + beizhu + "\n用户ID：" + userId + "\n手机号：" + phone + "\n" + failureReply
        expiredPush(imTypes, uid, userId, phone, text)
        sleep(1000)
    }

    //推送授权过期
    for (var i = 0; i < wushouquanCk.length; i++) {
        var userId = wushouquanCk[i]
        var uid = bucketGet("sm_ddb_userData_WB", userId)
        if (uid == "") {
            continue
        }
        var phone = bucketGet("sm_ddb_phone", userId) || null
        var beizhu = bucketGet("sm_ddb_remarks", userId) || null
        var overdueReply = bucketGet("sm_ddb_config", "overdueReply").replace(/\\n/g, '\n') || "\n授权已过期，请续费。"
        var text = "=====Elm授权过期通知=====\n备注：" + beizhu + "\n用户ID：" + userId + "\n手机号：" + phone + "\n" + overdueReply
        expiredPush(imTypes, uid, userId, phone, text)
        sleep(1000)
    }

    //推送预警信息
    for (var i = 0; i < yujingCk.length; i++) {
        var userId = yujingCk[i]
        var uid = bucketGet("sm_ddb_userData_WB", userId)
        if (uid == "") {
            continue
        }
        var phone = bucketGet("sm_ddb_phone", userId) || null
        var beizhu = bucketGet("sm_ddb_remarks", userId) || null
        var earlyWarningReply = bucketGet("sm_ddb_config", "earlyWarningReply").replace(/\\n/g, '\n') || "\n授权将在24h内过期，请续费。"
        var text = "=====Elm授权预警通知=====\n备注：" + beizhu + "\n用户ID：" + userId + "\n手机号：" + phone + "\n" + earlyWarningReply
        expiredPush(imTypes, uid, userId, phone, text)
        sleep(1000)
    }
}


//推送方法
function expiredPush(type, uid, userId, phone, text) {
    let typeArr = ['qq',
        'qb',
        'wx',
        'wb',
        'tb']
    for (let j = 0; j < typeArr.length; j++) {
        let type2 = typeArr[j]
        push(
            {
                imType: type2,
                userID: uid,
                content: text,
            }
        )
    }
}
//主进程
function main() {
    var disablePrivateChat = bucketGet('sm_ddb_config', 'disablePrivateChat') === "true" ? true : false
    if (disablePrivateChat && GetChatID() == "") {
        //私聊
        return
    }
    var disableGroupChat = bucketGet('sm_ddb_config', 'disableGroupChat') === "true" ? true : false
    if (disableGroupChat && GetChatID() != 0) {
        //群聊
        return
    }
    let groupWhitelist = bucketGet('sm_ddb_config', 'groupWhitelist').split(/[,，]/);
    if (GetChatID() != 0 && groupWhitelist[0] != "" && groupWhitelist.indexOf(GetChatID().toString()) == -1) {
        //白名单
        return
    }
    var checkCKRule = bucketGet("sm_ddb_config", "checkCKRule") || "查询"
    var addVIPRule = bucketGet("sm_ddb_config", "addVIPRule") || "代挂"
    var qlpz = getQl()
    var cookies = GetContent()
    cookies = cookies.replace(" ", "") + ";"
    cookies = cookies.replace("：", ";")
    cookies = cookies.replace(":", ";")
    var hasCookie2 = cookies.includes('cookie2=')
    var hasSID = cookies.includes('SID=')
    var hasUserID = cookies.includes('USERID=')
    if (hasCookie2 && hasSID && hasUserID) {
        var checkCkBody = checkCk(cookies)
        if (checkCkBody.indexOf("未登录") >= 0) {
            sendText("无效COOKIE，自动退出程序")
            return
        }
        var startIndex = cookies.indexOf('USERID=') + 'USERID='.length;
        var endIndex = cookies.indexOf(';', startIndex);
        if (endIndex === -1) {
            endIndex = cookies.length;
        }
        var userId = cookies.substring(startIndex, endIndex);
        checkCkBody = JSON.parse(checkCkBody)
        var updateAutCk = bucketSet("sm_ddb_CKDB", checkCkBody.user_id, cookies)
        //查询是否过期：未过期发送 更新成功提示、否则发送 代挂提示
        var vipTime = bucketGet("sm_ddb_vip", checkCkBody.user_id)
        bucketSet("sm_ddb_phone", checkCkBody.user_id, checkCkBody.mobile)
        var newPhone
        if (checkCkBody.mobile !== null) {
            var firstFourDigits = checkCkBody.mobile.substring(0, 3);
            var lastFourDigits = checkCkBody.mobile.substring(checkCkBody.mobile.length - 4);
            newPhone = firstFourDigits + "****" + lastFourDigits
        } else {
            newPhone = null
        }
        if (vipTime > (Date.now() / 1000)) {
            bucketSet("sm_ddb_userData_WB", checkCkBody.user_id, GetUserID())
            var updateQlCk = updateQinglong(checkCkBody.user_id, cookies)
            if (updateQlCk) {
                vipTime = Math.round(((vipTime - (Date.now() / 1000)) / 86400) * 100) / 100
                sendText("[" + newPhone + "]更新成功\n距离授权过期还有" + vipTime + "天")
            }
            return
        } else {
            if (bucketGet("sm_ddb_config", "qlCkMax") !== "") {
                var qlCkMax = Number(bucketGet("sm_ddb_config", "qlCkMax"))
                if (qlCkMax <= getQinglongCkNum()) {
                    sendText("容器已满")
                    notifyMasters("容器已满\n设置任务容器CK最大数量:" + qlCkMax + "\n当前任务容器CK最大数量:" + getQinglongCkNum())
                    return
                }
            }
            bucketSet("sm_ddb_userData_WB", checkCkBody.user_id, GetUserID())
            sendText("[" + newPhone + "]登记成功\n快发送【" + addVIPRule + "】完善饿了么代挂服务。")
            return
        }
    } else if (GetContent() == checkCKRule) {
        chaxun()
    } else if (GetContent() == "简单查询") {
        jiandanChaxun()
    } else if (GetContent() == addVIPRule) {
        daigua()
    } else if (GetContent() == "简单代挂") {
        jiandanDaigua()
    } else if (GetContent() == "备注") {
        beizhu()
    } else if (GetContent() == "解绑") {
        jiebang()
    } else if (GetContent() == "找回") {
        zhaohui()
    } else if (isAdmin() && GetContent() == "饿了么授权检测") {
        jianchaShouquan()
    } else if (isAdmin() && GetContent() == "饿了么授权") {
        shouquan()
    } else if (isAdmin() && GetContent() == "饿了版本") {
        sendText("🔔当前版本v1.6.4\n用户指令:\n上车方法: 直接发CK\n查询指令: 查询 || 简单查询\n代挂指令: 代挂 || 简单代挂\n解绑指令: 解绑\n备注指令: 备注\n======================\n管理员指令:\n授权账号指令: 饿了么授权\n授权检测指令: 饿了么授权检测\n(可奥特曼-定时推送-自处理)\n======================")
    }
}
main()