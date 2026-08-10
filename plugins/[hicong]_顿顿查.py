//[title: 顿顿查]
//[icon: https://p0.meituan.net/csc/bc0d5491e8f1ad3b7e05d3c9f897dce4125647.png]
//[language: es5]
//[price:0]
//[class:工具类]
//[author:hicong]
//[version:1.0.0]
//[open_source:false]
//[platform:wb]
//[public:true]
//[service:728818890]
//[description:指令：查券、查币。顿顿饿拓展插件，任务容器和仅限授权查询，桶数据共用。反馈QQ群233349587]

//[rule: 查券]
//[rule: 查币]

//获取青龙配置
function getQl() {
    qlsNames = bucketGet('sm_ddb_config', 'ql')
    var qlsKey = bucketKeys('qls')
    if (qlsKey.length == 0) {
        sendText("【顿顿饿】容器管理中对接容器不存在容器，请先对接容器再使用该插件")
        notifyMasters("【顿顿饿】容器管理中对接容器不存在容器，请先对接容器再使用该插件")
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
function elmqltoken(qlpz) {
    var body = request({
        url: qlpz.host + "/open/auth/token?client_id=" + qlpz.client_id + "&client_secret="+ qlpz.client_secret,
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
    var qlselectBody = JSON.parse(body)
    if (qlselectBody.data[0]) {
        return qlselectBody.data
    }
    return false
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
//获取青龙CK
function getQinglongCk(userId) {
    var qlpz = getQl()
    var qltokens = elmqltoken(qlpz)
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

function map(mh5tk, ts, data) {
    var e = call("md5")(mh5tk + "&" + ts + "&" + '12574478' + "&" + JSON.stringify(data))
    return e
}
//获取券列表
function quanList(ck, c) {
    var data = {
        "condition": '',
        "latitude": 30.17853,
        "longitude": 120.221101,
        "tabCode": "HONG_BAO",
        "sourceFrom": "ELEME_WECHAT_MINIAPP",
        "extInfo": "{\"miniAppVersion\":\"10.19.31\"}"
    };
    var databody = "data=" + encodeURIComponent(JSON["stringify"](data));
    var t = Date.now();
    var mh5tktk = c["split"](';')[0];
    var mh5tk = mh5tktk["split"]('_')[0];
    var sign = map(mh5tk, t, data);
    var body = request({
        url: "https://guide-acs.m.taobao.com/h5/mtop.alsc.personal.querypasslist/1.0/2.0/?jsv=2.4.12&appKey=12574478&t=" + t + "&sign=" + sign + "&c=" + c + "&api=mtop.alsc.personal.queryPassList&dataType=json&method=GET&timeout=10000&v=1.0&type=originaljson&ttid=wxece3a9a4c82f58c9%40wechat_android_11.1.5&accountSite=eleme&needLogin=true&ecole=1&_bx-m=1",
        method: "get",
        headers: {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.49(0x18003133) NetType/WIFI Language/zh_CN',
            'x-tap': 'wx',
            'referer': 'https://servicewechat.com/wxece3a9a4c82f58c9/612/page-frame.html',
            'Cookie': ck
        },
        body: databody
    });
    //sendText(body)
    if (JSON.parse(body)['c']) {
        return JSON.parse(body)['c']
    }
    //sendText(body)
    try {
        result = JSON.parse(body).data.result;
        if (!result || !result.passInfoList || !result.passInfoList[0] || !result.passInfoList[0].benefitList) {
            throw new Error('passInfoList is empty or undefined');
        }
        var result = JSON.parse(body).data.result.passInfoList[0].benefitList.map(redPacket => {
            return `${redPacket.title}${redPacket.amountText.yuanText}${redPacket.thresholdText}`
        });
        var resultString = result.join('\n');
    } catch (error) {
        console.error(error);
    }
    return resultString
}

//获取币列表
function biList(mh5tk, ck, yeshu) {
    var jinriLyb
    var startTime = timeFmt("yyyy-MM-dd") + " 00:00:00";
    var data = {
        "templateId": "1404",
        "bizScene": "game_center",
        "convertType": "GAME_CENTER",
        "startTime": startTime,
        "pageNo": yeshu,
        "pageSize": "20"
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
                    var lyb = "";
                    for (let i = 0; i < body["data"]["list"]["length"]; i++) {
                        var _0x4b8946 = body["data"]["list"][i];
                        if (_0x4b8946["detailType"] === "GRANT" && _0x4b8946["gmtModified"]["indexOf"](timeFmt("yyyy-MM-dd")) !== -1) {
                            var desc = _0x4b8946.extInfo.desc
                            var amount = _0x4b8946.amount
                            lyb += (desc + amount + "\n");
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

//查券
function chaquan() {
    var bindUserid = bucketKeys("sm_ddb_userData_WB",
        GetUserID())
    if (bindUserid === false || bindUserid.length == 0) {
        sendText("未查询到已绑定账号，请发ck进行绑定\n\n因Uid变更导致账号丢失请发【找回】。")
        return
    } else {
        var useridArray = bindUserid.map(function(userId, index) {
            return '【' + (index + 1) + '】' + userId
        }).join('\n')
        sendText("【0】全选\n" + useridArray)
        sendText('请选择需要查询的账号，回复【】内的数字即可，多个账号用逗号或空格分割，回复\'q\'退出')
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
            for (var i = 0; i < bindUserid.length; i++) {
                var userId = bindUserid[i]
                var ck = bucketGet("sm_ddb_CKDB", userId)
                xiaoxi += chaxunQuan(ck, userId)

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
                var ck = bucketGet("sm_ddb_CKDB", userId)
                xiaoxi += chaxunQuan(ck, userId)
            }
        }
        sendText(xiaoxi)
    }
}

//查币
function chaBi() {
    var bindUserid = bucketKeys("sm_ddb_userData_WB", GetUserID())
    if (bindUserid === false || bindUserid.length == 0) {
        sendText("未查询到已绑定账号，请发ck进行绑定\n\n因Uid变更导致账号丢失请发【找回】。")
        return
    } else {
        var useridArray = bindUserid.map(function(userId, index) {
            return '【' + (index + 1) + '】' + userId
        }).join('\n')
        sendText("【0】全选\n" + useridArray)
        sendText('请选择需要查询的账号，回复【】内的数字即可，多个账号用逗号或空格分割，回复\'q\'退出')
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
            for (var i = 0; i < bindUserid.length; i++) {
                var userId = bindUserid[i]
                var ck = bucketGet("sm_ddb_CKDB", userId)
                xiaoxi += chaxunBi(ck, userId)

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
                var ck = bucketGet("sm_ddb_CKDB", userId)
                xiaoxi += chaxunBi(ck, userId)
            }
        }
        sendText(xiaoxi)
    }
}

//查询券
function chaxunQuan(ck, userId) {
    var Phone = bucketGet("sm_ddb_phone", userId)
    var beizhu
    if (Phone !== "") {
        var lastFourDigits = Phone.substring(Phone.length - 4);
        beizhu = lastFourDigits
    } else {
        beizhu = userId
    }
    if (bucketGet("sm_ddb_vip", userId) == "" || bucketGet("sm_ddb_vip", userId) < (Date.now() / 1000)) {
        if (bucketGet('sm_ddb_config', 'vipInquiry') === "true" ? true: false) {
            return ("【" + (bucketGet("sm_ddb_remarks", userId) || beizhu) + "】账号未授权\n")
        }
    }
    var checkCkBody = checkCk(ck)
    if (checkCkBody.indexOf("未登录") >= 0) {
        ck = getQinglongCk(userId)
        if (!ck) {
            return ("【" + (bucketGet("sm_ddb_remarks", userId) || beizhu) + "】CK已过期\n")
        }
    }
    var quan = quanList(ck, "19807886494a14e7791c39f1325093cb6e5a331604_1718017744841;559e6f6042cc0e558bf139ab18b7fd6c")
    if (quan) {
        quan = quanList(ck, quan)
        return ("【" + (bucketGet("sm_ddb_remarks", userId) || beizhu) + "】\n" + quan + "\n")
    }
    return
}

//查询币
function chaxunBi(ck, userId) {
    var Phone = bucketGet("sm_ddb_phone", userId)
    var beizhu
    if (Phone !== "") {
        var lastFourDigits = Phone.substring(Phone.length - 4);
        beizhu = lastFourDigits
    } else {
        beizhu = userId
    }
    if (bucketGet("sm_ddb_vip", userId) == "" || bucketGet("sm_ddb_vip", userId) < (Date.now() / 1000)) {
        if (bucketGet('sm_ddb_config', 'vipInquiry') === "true" ? true: false) {
            return ("【" + (bucketGet("sm_ddb_remarks", userId) || beizhu) + "】账号未授权\n")
        }
    }
    var checkCkBody = checkCk(ck)
    if (checkCkBody.indexOf("未登录") >= 0) {
        ck = getQinglongCk(userId)
        if (!ck) {
            return ("【" + (bucketGet("sm_ddb_remarks", userId) || beizhu) + "】CK已过期\n")
        }
    }
    var regexCombined = /(_m_h5_tk=[0-9a-f]+_[0-9]+|_m_h5_tk_enc=[0-9a-f]+);/g;
    ck = ck.replace(regexCombined,
        '')
    ck = ck.replace(/\s+/g,
        '') + ";"
    var shuju
    request({
        url: 'https://waimai-guide.ele.me/h5/mtop.alsc.personal.queryminecenter/1.0/?jsv=2.6.2&appKey=12574478',
        headers: {
            Cookie: ck,
            method: 'GET'
        }
    }, function (error, response, header, body) {
        var str = JSON.stringify(header);
        var mh5tk = str.match(/_m_h5_tk=([^_]+)/)[1];
        var regex1 = /_m_h5_tk=[0-9a-f]+_[0-9]+;/;
        var regex2 = /_m_h5_tk_enc=[0-9a-f]+;/;
        var str1 = str.match(regex1)[0];
        var str2 = str.match(regex2)[0];
        ck = ck +str1 + str2;
        var yeshu = 1
        var yeshuLyb = biList(mh5tk, ck, yeshu)
        shuju = yeshuLyb;
        while (yeshuLyb) {
            yeshu = yeshu + 1;
            yeshuLyb = biList(mh5tk, ck, yeshu)
            shuju += yeshuLyb
        }
        if (!shuju) {
            shuju = 0
        }
    });
    return "【" + (bucketGet("sm_ddb_remarks", userId) || beizhu) + "】\n" + shuju
}

//主进程
function main() {
    var disablePrivateChat = bucketGet('sm_ddb_config', 'disablePrivateChat') === "true" ? true: false
    if (disablePrivateChat && GetChatID() == "") {
        console.log("【顿顿饿】已禁止私聊回复")
        return
    }
    var disableGroupChat = bucketGet('sm_ddb_config', 'disableGroupChat') === "true" ? true: false
    if (disableGroupChat && GetChatID() != 0) {
        console.log("【顿顿饿】已禁止群聊回复")
        return
    }
    let groupWhitelist = bucketGet('sm_ddb_config', 'groupWhitelist').split(/[,，]/);
    if (GetChatID() != 0 && groupWhitelist[0] != "" && groupWhitelist.indexOf(GetChatID().toString()) == -1) {
        console.log("【顿顿饿】非白名单群聊")
        return
    }
    if (GetContent() == "查券") {
        chaquan()
    } else if (GetContent() == "查币") {
        chaBi()
    }
}
main()