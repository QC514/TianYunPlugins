//[disable:false]
//[rule: 旧农场推送] 

//[rule: 新农场奖品推送] 
//[author: xiaoqing] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]
//[public: true] 
//[price: 3] 
//[version: 1.6.6] 
//[admin: true] 
//[platform: qq,wx,tg,wb,qb]
//[priority: 9999999999]
//[service: 97393412]
//[description: 指令：【旧农场推送】【新农场奖品推送】设置定时推送即可<br/>取消新农场推送，只需要设置定时推送新版农场的未使用奖品即可<br/>增加自定义接口搭建教程看群精华内容有教程说明<br/>3.31  更新多渠道通知推送<br/>应该是支持所有方式吧，可能不一定支持公众号以外<br/>3.29 修复旧版农场<br/>1.仅支持代理池<br/>2.仅支持代理池，例如：http://192.168.3.5：7350<br/>兼容最新版本奥特曼,需要给[qinglong数据]权限<br/>操作入口:后台系统管理-插件权限-qinglong数据[打开]<br/>插件交流群：858456556]
// [param: {"required":true,"key":"who_tong.ncql","placeholder":"容器名称","name":"青龙名称","desc":"获取名方法:奥特曼后台-容器管理--对接容器--名称"}]
// [param: {"required":true,"key":"who_tong.h5st_api","placeholder":"http://110.40.165.213:39000","name":"自建H5接口","desc":"填写你搭建好的地址：http://110.40.165.213:39000"}]

// [param: {"required":true,"key":"who_tong.atmbb","bool":true,"placeholder":"false","name":"奥特曼版本开关","desc":"低于2.6.9以下的版本需要打开这个开关"}]
// [param: {"required":true,"key":"who_tong.jd_poxy","placeholder":"http://v2.api.juliangip.com...","name":"代理地址","desc":"巨量是text，,星空/品赞/携趣，都是JSON,代理池需要带http://"}]
// [param: {"required":true,"key":"who_tong.api_pt","placeholder":"1","name":"代理平台","desc":"巨量=1,星空=2,品赞=3,代理池=4,携取=5,填写你使用平台的数字"}]
// [param: {"required":true,"key":"otto.js_yc","placeholder":"","name":"延迟","desc":"每次检测的延迟,以秒为单位，例如：5，则是每次等待5秒"}]
// [param: {"spliter":true}]
// [param: {"required":true,"key":"who_tong.nc_sm","placeholder":"【领取路径：打开京东APP-我的-东东农场-右上角-记录-去兑换】","name":"奖品记录尾部自定义","desc":"例如：【领取路径：打开京东APP-我的-东东农场-右上角-记录-去兑换】"}]
// [param: {"required":true,"key":"otto.TXfs","placeholder":"wb","name":"推送渠道","desc":"wb,qb,qq,wx,tg，支持多渠道通知"}]
// [param: {"required":false,"key":"otto.TX_ts","bool":true,"placeholder":"false","name":"农场未熟推送","desc":"农场还未成熟的是否推送"}]
// [param: {"required":false,"key":"otto.weizhongzhi","bool":true,"placeholder":"false","name":"农场未种植","desc":"打勾则推送未种植"}]
// [param: {"required":false,"key":"otto.GLY","bool":true,"placeholder":"false","name":"管理员通知","desc":"推送完成后是否推送数据给管理员"}]
var GetContent = GetContent()
var nc_h5 = ""
var h5_ver = ""
var nc_ua = ""
var yanci = parseInt(get("js_yc"))
var juliang = bucketGet("who_tong", "jd_poxy")
var h5st_api = bucketGet("who_tong", "h5st_api")
var pingtai = parseInt(bucketGet("who_tong", "api_pt"))
var pro = ""//http代理

var UserPro_zs = 0//非JDck
var UserPro_CK = 0//总CK量
var UserPro_true = 0//成功
var UserPro_no_true = 0//未成熟
var UserPro_false = 0//未种植
var UserPro_null = 0//失效
var UserPro_no_false = 0//火爆
var H5ST = ""


function getCaption(obj, text) {
    let index = obj.lastIndexOf(text) + text.length - 1;
    obj = obj.substring(index + 1, obj.length);
    return obj;
}
function ql_cs(name) {//设置容器
    var qls = bucketGet("qinglong", "QLS")
    if (qls) {
        let QLS = JSON.parse(qls)
        for (i = 0; i < QLS.length; i++) {
            if (QLS[i].name === name) {
                let data = {
                    host: QLS[i].host,
                    client_id: QLS[i].client_id,
                    client_secret: QLS[i].client_secret
                }
                Debug("指定获取【" + name + "】的数据")
                return JSON.stringify(data)
            }
        }
    }
}
function qls(uid) {
    allpins = bucketKeys("qls")
    for (let j = 0; j < allpins.length; j++) {
        var ql_a = JSON.parse(bucketGet("qls", String(allpins[j])))
        if (ql_a.name == uid) {
            return ql_a
        }
    }

}

function mian() {
    var ql_a = ""
    if (h5st_api == "") {
        H5ST = "http://jiagang.6dot.cn:3006"
    } else {
        H5ST = h5st_api
    }

    var who_gly = bucketGet("otto", "GLY")//代理开关功能
    //let pina = cookie.match(/(?<=pt_pin=)[^;]+/g)
    let stxs = bucketGet("otto", "TXfs")
    if (stxs == "" || stxs == null) {
        notifyMasters("你还没设置推送渠道\n去云插件的-配置   \n里面设置一下")
    }

    var ql_name = bucketGet("who_tong", "ncql")
    Debug(`指定获取青龙容器名称:${ql_name}`)
    if (ql_name) {
        let http_api = bucketGet("who_tong", "atmbb")
        if (http_api == "true") {
            var ql_a = JSON.parse(ql_cs(ql_name))
            Debug(JSON.stringify(ql_a))
        } else {
            var ql_a = qls(ql_name)

        }
    } else {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置")
    }

    let ql_toke = ql_dl(ql_a.host, ql_a.client_id, ql_a.client_secret)
    let ckx = ql_token(ql_a.host, ql_toke.token_type, ql_toke.token)
    //
    if (who_gly == "true" || who_gly == true) {
        notifyMasters("开始推送【" + GetContent + "】成熟成果-通知")
    }
    for (let j = 0; j < ckx.length; j++) {
        if (ckx[j].name == "JD_COOKIE") {
            if (ckx[j].status == 0) {
                let pina = ckx[j].value.match(/(?<=pt_pin=)[^;]+/g)
                Debug(pina + "-----" + j)
                if (GetContent == "旧农场推送") {
                    Debug(`开始查询旧版农场当前进度：${j},总进度${ckx.length}`)
                    getJdFruit(ckx[j].value, true)
                } else if (GetContent == "新农场奖品推送") {
                    fen(ckx[j].value)
                    sleep(5000)
                } else {
                    Debug(`开始查询新版农场当前进度：${j},总进度${ckx.length}`)
                    farm_home(ckx[j].value, true)
                }
            } else {
                console.log(`JD-变量为禁用状态，` + j + "--" + ckx[j].name)
                UserPro_null = UserPro_null + 1
            }
            UserPro_CK = UserPro_CK + 1
        } else {

            console.log(`非JD-ck变量，` + j)
            UserPro_zs = UserPro_zs + 1
        }


    }
    if (GetContent == "旧农场推送" || GetContent == "新农场推送") {
        if (who_gly == "true" || who_gly == true) {
            notifyMasters(`推送【${GetContent}】成熟成果-任务完成
本次任务结果：
总变量：${ckx.length}
JD变量：${UserPro_CK}
非JD--CK数量：${UserPro_zs}
---------------------
成熟数量：${UserPro_true}
未熟数量：${UserPro_no_true}
未种植数量：${UserPro_false}
---------------------
火爆数量：${UserPro_no_false}
失效数量：${UserPro_null}
失效的数量可能会显示多些数据
`)
        }
    } else {
        if (who_gly == "true" || who_gly == true) {

            notifyMasters(`推送【${GetContent}】奖品记录-任务完成`)
        }
    }
}

function fen(cookie) {
    var stxs = bucketGet("otto", "TXfs")
    var pina = cookie.match(/(?<=pt_pin=)[^;]+/g)
    var exchangeRemind = ""
    //exchangeRemind += `账号:${pina}新农场奖品明细\n`
    let body = request({
        url: "https://api.m.jd.com/client.action?appid=signed_wh5&client=android&clientVersion=12.2.2&screen=393*0&wqDefault=false&build=98996&osVersion=10&networkType=wifi&d_brand=HUAWEI&d_model=LIO-AN00&partner=wandoujia&uuid=1603337356666383-5653262383665353&t=1716562149021&body={\"version\":3,\"type\":1}&functionId=farm_award_detail&x-api-eid-token=jdd03FSQYC33R2BEHZAJPE6M7HEA2C2UPHEL2WY6DDNQNXXJ7LJTCHVCGZ5ROMCLNDGIF3IL3QLF5HFYNQMV5SEVVCRLJVAAAAAMPVMJSVQYAAAAAC445IEJ2UJKLYUX",
        method: "GET",
        //body: "",
        headers: {
            "Host": "api.m.jd.com",
            "content-length": "430",
            "accept": "application/json, text/plain, */*",
            "x-rp-client": "h5_1.0.0",
            "content-type": "application/javascript",
            "user-agent": 'jdapp;android;12.2.2;;;M/5.0;appBuild/98996;ef/1;ep/{"hdid":"JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw = ","ts":1716562108402,"ridx":-1,"cipher":{"sv":"CJK = ","ad":"YJKzD2VwDtrvDWSyEQY1DG == ","od":"","ov":"Ctu = ","ud":"YJKzD2VwDtrvDWSyEQY1DG == "},"ciphertype":5,"version":"1.2.0","appname":"com.jingdong.app.mall"};jdSupportDarkMode/0;Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046283 Mobile Safari/537.36',
            "x-referer-page": "https://h5.m.jd.com/pb/015686010/Bc9WX7MpCW7nW9QjZ5N3fFeJXMH/index.html",
            "origin": "https://h5.m.jd.com",
            "x-requested-with": "com.jingdong.app.mall",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://h5.m.jd.com/",
            // "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": String(cookie)
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 10000
    })
    try {
        if (body) {
            if (body.code == 0) {
                //Debug(JSON.stringify(body.data.result))
                let vulue = body.data.result.plantAwards
                for (let RuleList of vulue) {
                    if (RuleList["couponKind"] === 1) {
                        exchangeRemind = `${RuleList["exchangeRemind"]}\n${RuleList["skuName"]}--未使用`
                        var qd = stxs.split(",")
                        for (let k = 0; k < qd.length; k++) {
                            bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                            console.log(`开始推送-用户：${bind},账号：${decodeURIComponent(pina)}，通讯方式：${qd[k].toUpperCase()}`)
                            let zdysm = bucketGet("who_tong", "nc_sm")
                            tuisong(qd[k], bind, `账号：${decodeURIComponent(pina)}\n${exchangeRemind}\n[新农场水果已成熟-请尽快使用]\n${zdysm}`)
                        }
                        //return
                    } else {
                        if (RuleList["awardStatus"] === 1 && RuleList["awardType"] === 2) {
                            exchangeRemind = `${RuleList["exchangeRemind"]}\n${RuleList["skuName"]}`
                            var qd = stxs.split(",")
                            for (let k = 0; k < qd.length; k++) {
                                bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                console.log(`开始推送-用户：${bind},账号：${decodeURIComponent(pina)}，通讯方式：${qd[k].toUpperCase()}`)
                                let zdysm = bucketGet("who_tong", "nc_sm")
                                tuisong(qd[k], bind, `账号：${decodeURIComponent(pina)}\n${exchangeRemind}\n[新农场水果已成熟-请尽快使用]\n${zdysm}`)
                            }
                            //return
                        }
                    }
                }
            }
        }
    } catch (err) {
        //sendText(`账号:${pina},没有发现有新农场奖品记录`)
    }
    sleep(2000)
}
function add_user() {//新增账号

    var phone = ShuRu("请输入--青龙地址")
    if (phone == false) {
        sendText("青龙地址-输入超时,取消任务")
        return false
    } else {
        var loginPassword = ShuRu("请输入青龙--Client ID")
        if (loginPassword == false) {
            sendText("Client ID-输入超时,取消任务")
            return false
        } else {
            var userId = ShuRu("请输入青龙--Client Secret")
            if (userId == false) {
                sendText("Client Secret-输入超时,取消任务")
                return false
            } else {
                sendText("全部输入完成！")
                var data = {
                    host: phone,
                    client_id: loginPassword,
                    client_secret: userId
                }
                bucketSet("otto", "nc-QL", JSON.stringify(data))
                return true
            }
        }
    }
}
function ShuRu(name) {
    sendText(name)
    var msg = input(60000, 6000)
    if (msg == "q" || msg == "Q") {
        sendText("已退出会话");
        return
    } else {
        return msg;
    }

}
//东东农场



function xin_h5(h5_body) {

    let body = request({
        url: H5ST + "/getForFarm",
        method: "post",
        body: h5_body,
        headers: {
            "Content-Type": "application/json",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    if (body) {
        if (body.code = 200) {
            nc_h5 = body.data
        }
        return true
    } else {
        return false
    }
}
function xin_ua() {
    nc_h5 = ""
    nc_ua = ""

    let body = request({
        url: H5ST + "/UA",
        method: "post",
        body: {},
        headers: {
            "Content-Type": "application/json",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    if (body) {
        if (body.code = 200) {
            nc_ua = body.data
            var ucxa = nc_ua.split(";")
            //sendText(ucxa[2])
            h5_ver = ucxa[2]
        }
        return true
    } else {
        return false
    }
}
function getJdFruit(cookie) {
    var DL_ts = bucketGet("otto", "TX_ts")//代理开关功能
    var weizhongzhi = bucketGet("otto", "weizhongzhi")//代理开关功能
    try {
        stxs = bucketGet("otto", "TXfs")
        let pina = cookie.match(/(?<=pt_pin=)[^;]+/g)
        bind = bucketGet("pin" + stxs.toUpperCase(), pina)

        for (let i = 0; i < 3; i++) {
            daili()
            xin_ua()

            request({
                useproxy: true,
                proxyAddr: pro,
                url: "https://api.m.jd.com?functionId=gotNewUserTaskForFarm",
                method: "post",
                body: 'body=%7B%22version%22%3A24%2C%22channel%22%3A1%2C%22babelChannel%22%3A%22121%22%2C%22lat%22%3A%220%22%2C%22lng%22%3A%220%22%7D&appid=wh5',
                headers: {
                    "accept": "*/*",
                    //"accept-encoding": "gzip, deflate, br",
                    "accept-language": "zh-CN,zh;q=0.9",
                    "cookie": cookie,
                    "origin": "https://carry.m.jd.com/",
                    "referer": "https://carry.m.jd.com/",
                    "User-Agent": nc_ua,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                timeout: 80000
            }, function (error, response, header, body) {
                // console.log("检查东东农场的数据：" + JSON.stringify(body))
                if (!error) {

                    let obj = JSON.parse(body)
                    if (obj) {
                        if (obj.code == "7" || obj.code == "7") {
                            if (typeof obj.farmUserPro !== "undefined") {
                                console.log("查询旧版农场成功：" + decodeURIComponent(pina) + "，已浇水：" + obj.farmUserPro.treeEnergy + "滴,")
                                ojbk = 100 * obj.farmUserPro.treeEnergy / obj.farmUserPro.treeTotalEnergy
                                objk = Math.round(ojbk)
                                if (objk == 100 || objk == "100" || objk == 100.00 || objk == "100.00") {
                                    //console.log(pina + "水果成熟了" + objk)
                                    //console.log(`开始推送-用户：${bind},账号：${pina}`)
                                    UserPro_true = UserPro_true + 1
                                    var qd = stxs.split(",")
                                    for (let k = 0; k < qd.length; k++) {
                                        Debug(qd[k])
                                        bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                        console.log(`开始推送-用户：${bind},账号：${decodeURIComponent(pina)}，通讯方式：${qd[k]}`)
                                        TXfs_tuisong(qd[k], bind, `东东农场旧版:
账号：${decodeURIComponent(pina)}
种植物品：${obj.farmUserPro.name}
剩余水滴：${obj.farmUserPro.totalEnergy}
[旧版农场水果已成熟-请尽快领取以及种植]
【领取路径：打开京东APP-我的-东东农场-左上角-回旧版-去兑换】`)
                                    }
                                } else {
                                    // sendText(pina + "水果还没成熟")
                                    UserPro_no_true = UserPro_no_true + 1
                                    if (DL_ts == "true" || DL_ts == true) {
                                        var qd = stxs.split(",")
                                        for (let k = 0; k < qd.length; k++) {
                                            Debug(qd[k])
                                            bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                            console.log(`开始推送-用户：${bind},账号：${decodeURIComponent(pina)}，通讯方式：${qd[k]}`)
                                            TXfs_tuisong(qd[k], bind, `=======农场通知-未熟=======
东东账号：${decodeURIComponent(pina)}
种植物品：${obj.farmUserPro.name}
已浇水滴：${obj.farmUserPro.treeEnergy}
种植进度：${objk.toFixed(2)}%
剩余水滴：${obj.farmUserPro.totalEnergy}`)
                                        }
                                    }
                                }
                                sleep(2000)
                            } else {
                                console.log(decodeURIComponent(pina) + "，没有农场信息，可能没有种植")
                                console.log("检查东东农场的数据：" + JSON.stringify(obj))

                                if (weizhongzhi == "true" || weizhongzhi == true) {
                                    var qd = stxs.split(",")
                                    for (let k = 0; k < qd.length; k++) {
                                        Debug(qd[k])
                                        bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                        console.log(`开始推送-用户：${bind},账号：${decodeURIComponent(pina)}，通讯方式：${qd[k]}`)
                                        TXfs_tuisong(qd[k], bind, `=======农场通知-未种植=======
东东账号：${decodeURIComponent(pina)}
【您是不是还没有在[东东农场]上种植水果？】`)
                                    }
                                }
                                UserPro_false = UserPro_false + 1

                            }
                            i = 5
                        } else if (obj.code == "3" || obj.code == "3") {
                            console.log("检查东东农场的数据：\n账号：" + decodeURIComponent(pina) + ",CK失效")
                            UserPro_null = UserPro_null + 1
                            sleep(2000)
                            i = 5
                        } else if (obj.code == "400" || obj.code == "402" || obj.code == "404") {
                            console.log("检查东东农场的数据：\n账号：" + decodeURIComponent(pina) + "，农场数据：火爆，重试中")
                            UserPro_no_false = UserPro_no_false + 1
                            sleep(8000)
                        } else {
                            console.log("检查东东农场的数据：\n账号：" + decodeURIComponent(pina) + "，农场数据：" + JSON.stringify(obj))
                            UserPro_no_false = UserPro_no_false + 1
                            sleep(8000)
                            i = 5
                        }
                    }


                }
            })


        }
    } catch (err) {
        Debug("请求失败.再次尝试")

    }
}
//新版农场
function farm_home(cookie) {
    var DL_ts = bucketGet("otto", "TX_ts")//代理开关功能
    let pina = cookie.match(/(?<=pt_pin=)[^;]+/g)
    var weizhongzhi = bucketGet("otto", "weizhongzhi")//代理开关功能
    stxs = bucketGet("otto", "TXfs")
    bind = bucketGet("pin" + stxs.toUpperCase(), pina)
    xin_ua()
    for (let k = 0; k < 4; k++) {
        daili()
        try {
            let home = { "appId": "c57f6", "fn": "farm_home", "body": { "version": 1 }, "apid": "signed_wh5", "ver": String(h5_ver), "cl": "ios", "code": 1, "user": String(pina), "ua": nc_ua }

            H5_dylanv(home)
            let body = request({
                useproxy: true,
                proxyAddr: pro,
                url: `https://api.m.jd.com/client.action?${nc_h5}`,
                method: "get",
                //body: ,
                headers: {
                    "Host": "api.m.jd.com",
                    // "content-length": "1348",
                    "accept": "application/json, text/plain, */*",
                    "x-rp-client": "h5_1.0.0",
                    "content-type": "application/x-www-form-urlencoded",
                    "user-agent": nc_ua,
                    "x-referer-page": "https://h5.m.jd.com/pb/015686010/Bc9WX7MpCW7nW9QjZ5N3fFeJXMH/index.html",
                    "origin": "https://h5.m.jd.com",
                    "x-requested-with": "com.jingdong.app.mall",
                    "sec-fetch-site": "same-site",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-dest": "empty",
                    "referer": "https://h5.m.jd.com/",
                    //"accept-encoding": "gzip, deflate, br",
                    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Cookie": cookie,
                },
                dataType: "json",
                timeOut: 80000
            })
            Debug(JSON.stringify(body))
            if (body.code == 0) {
                if (body.data.bizCode == 0) {
                    if (typeof body.data.result.skuName !== "undefined") {
                        console.log("查询新版农场成功：" + decodeURIComponent(pina) + "，进度：" + body.data.result.treeFullStage + "," + body.data.result.waterTips)
                        if (body.data.result.treeFullStage == 5 || body.data.result.treeFullStage == "5") {
                            //成熟
                            UserPro_true = UserPro_true + 1
                            var qd = stxs.split(",")
                            for (let q = 0; q < qd.length; q++) {
                                Debug(qd[q])
                                bind = bucketGet("pin" + qd[q].toUpperCase(), pina)
                                console.log(`开始推送-用户：${bind},账号：${decodeURIComponent(pina)}，通讯方式：${qd[q]}`)
                                TXfs_tuisong(qd[q], bind, `=======新农场通知-已熟=======
 东东账号：${decodeURIComponent(pina)}
 种植物品：${body.data.result.skuName}
 剩余水滴：${body.data.result.bottleWater}
【新农场水果已成熟-请尽快领取以及种植】`)
                            }
                            sleep(2000)
                            return
                        } else {
                            //未熟
                            UserPro_no_true = UserPro_no_true + 1
                            if (DL_ts == "true" || DL_ts == true) {
                                var qd = stxs.split(",")
                                for (let q = 0; q < qd.length; q++) {
                                    Debug(qd[q])
                                    bind = bucketGet("pin" + qd[q].toUpperCase(), pina)
                                    console.log(`开始推送-用户：${bind},账号：${decodeURIComponent(pina)}，通讯方式：${qd[q]}`)
                                    TXfs_tuisong(qd[q], bind, `=======新农场通知-未熟=======
东东账号：${decodeURIComponent(pina)}
种植物品：${body.data.result.skuName}
种植进度：${body.data.result.treeFullStage}/5,${body.data.result.waterTips}
剩余水滴：${body.data.result.bottleWater}`)
                                }
                            }
                            sleep(2000)
                            return
                        }
                    } else {
                        if (weizhongzhi == "true" || weizhongzhi == true) {
                            var qd = stxs.split(",")
                            for (let q = 0; q < qd.length; q++) {
                                Debug(qd[q])
                                bind = bucketGet("pin" + qd[q].toUpperCase(), pina)
                                console.log(`开始推送-用户：${bind},账号：${decodeURIComponent(pina)}，通讯方式：${qd[q]}`)
                                TXfs_tuisong(qd[q], bind, `=======新农场通知-未种植=======
东东账号：${decodeURIComponent(pina)}
【您是不是还没有在[新东东农场]上种植水果？】`)
                            }
                        }
                        UserPro_false = UserPro_false + 1
                        sleep(2000)
                    }
                    k = 5
                }
            } else {
                sleep(8000)

            }
        } catch (err) {
        }
    }
}

function h5st_nc(h5_body) {

    let body = request({
        url: H5ST + "/home",
        method: "post",
        body: h5_body,
        headers: {
            "Content-Type": "application/json",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    if (body) {
        if (body.code = 200) {
            nc_h5 = body.data
            nc_ua = body.ua
        }
        return true
    } else {
        return false
    }
}
function H5_dylanv(home) {
    let body = request({
        url: `${H5ST}/H5ST_V`,
        method: "post",
        body: home,
        headers: {
            "Content-Type": "application/json",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 10000
    })
    if (body) {
        if (body.code = 200) {
            nc_h5 = body.data
            nc_ua = body.ua
        }
        return true
    } else {
        return false
    }
}
//推送数据

function TXfs_tuisong(tx, qh, data) {
    console.log(`开始推送-渠道：${tx},用户ID：${qh}，推送内容：${data}`)
    push({
        imType: tx,
        userID: qh,
        title: "",
        groupCode: "",
        content: data,
    });
}
function tuisong(tx, qh, data) {
    console.log(`开始推送-渠道：${tx},用户ID：${qh}，推送内容：${data}`)
    push({
        imType: tx,
        userID: qh,
        title: "东东农场新版:",
        groupCode: "",
        content: data,
    });
}
//青龙配置
function ql_tokex(wz, token_type, tokend) {
    let data1 = request({
        url: wz + "/open/envs",
        method: "get",
        headers: {
            accept: "application/json",
            Authorization: token_type + " " + tokend
        },
        "timeOut": 90000,
        dataType: "json",
    })
    msg1 = JSON.stringify(data1)
    return msg1
}
function ql_token(wz, token_type, tokend) {
    let data1 = request({
        url: wz + "/open/envs",
        method: "get",
        headers: {
            accept: "application/json",
            Authorization: token_type + " " + tokend
        },
        "timeOut": 90000,
        dataType: "json",
    })
    msg1 = JSON.stringify(data1.data)
    msg1 = JSON.stringify(msg1)
    msg1 = JSON.parse(msg1)
    msg1 = JSON.parse(msg1)
    return msg1
}
function ql_dl(ql_host, ql_client_id, ql_client_secret) {
    token = request({
        url: ql_host + "/open/auth/token?client_id=" + ql_client_id + "&client_secret=" + ql_client_secret,
        method: "get",
        headers: {
            accept: "application/json"
        },
        "timeOut": 90000,
        dataType: "json",
    })
    console.log(token.data.token)
    return token.data
}

function proxy() {//巨量
    let body = request({
        url: juliang,
        method: "get",
        // body: water,
        headers: {
            //"Host": "h5.xss333.top:8001",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        dataType: "text",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    Debug("巨量" + body)
    return body
}
function daili() {//选择代理模式
    sleep(yanci * 1000)
    sleep(2000)
    //巨量=1,星空=2,品赞=3
    Debug("当前数字--" + pingtai)
    if (pingtai == 3 || pingtai == "3") {
        Debug("当前使用--品赞")
        pro = `http://${pinzan()}`
    } else if (pingtai == 2 || pingtai == "2") {
        Debug("当前使用--星空")

        pro = `http://${xk()}`
    } else if (pingtai == 1 || pingtai == "1") {
        Debug("当前使用--巨量")

        pro = `http://${proxy()}`
    } else if (pingtai == 4 || pingtai == "4") {
        Debug("当前使用--代理池")

        pro = juliang
    } else if (pingtai == 5 || pingtai == "5") {
        Debug("当前使用--携取")
        pro = `http://${xiequ()}`
    }
    Debug(`当前使用IP:${pro}`)
}
function xk() {
    let body = request({
        url: juliang,
        method: "get",
        // body: water,
        headers: {
            //"Host": "h5.xss333.top:8001",
            "Content-Type": "application/json; charset=utf-8",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    Debug(JSON.stringify(body))
    if (body) {
        if (body.status == 100) {
            var IOP = `${body.data[0].ip}:${body.data[0].port}`
            return IOP
        }
    }
}
function pinzan() {
    let body = request({
        url: juliang,
        method: "get",
        // body: water,
        headers: {
            //"Host": "h5.xss333.top:8001",
            "Content-Type": "application/json; charset=utf-8",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    Debug(JSON.stringify(body))
    if (body) {
        if (body.code == 0) {
            var IOP = `${body.data.list[0].ip}:${body.data.list[0].port}`
            return IOP
        }
    }

}
function xiequ() {
    let body = request({
        url: juliang,
        method: "get",
        // body: water,
        headers: {
            //"Host": "h5.xss333.top:8001",
            "Content-Type": "application/json; charset=utf-8",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    Debug(JSON.stringify(body))
    if (body) {

        if (body.code == 0) {
            var IOP = `${body.data[0].IP}:${body.data[0].Port}`
            return IOP
        }
    }

}
mian()