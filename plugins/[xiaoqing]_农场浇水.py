//[disable:false]
//[title: 农场浇水]
//[author: xiaoqing] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]
//[price: 2]
//[service: 97393412]
//[admin: false]
//[priority: 99]
//[version: 0.7.9] 
//[public: true] 
//[platform: qq,wxmp,wx,tb,tg,web,wb]
//[description: 温馨说明：新版农场浇水,旧版农场浇水<br/>修复新农场浇水,需自建接口,群内精华消息有教程<br/>需要给qinglong/qls权限,获取名方法:奥特曼后台-容器管理--对接容器--名称<br/>增加毫秒级别延迟,如果不设置毫秒延迟默认使用【秒延迟】<br/>增加新农场一次浇水50水滴<br/>5-5 删除旧版农场<br/>插件交流群：858456556] 
//[rule: 农场浇水] 
//[rule: 浇水] 
//[rule: 慢浇水]
// [param: {"required":true,"key":"otto.js_ql","placeholder":"容器名称","name":"青龙名称","desc":"获取名方法:奥特曼后台-容器管理--对接容器--名称"}]
// [param: {"required":true,"key":"who_tong.h5st_js","placeholder":"http://110.40.165.213:39000","name":"自建H5接口","desc":"填写你搭建好的地址：http://110.40.165.213:39000"}]
// [param: {"required":true,"key":"who_tong.atmbb","bool":true,"placeholder":"false","name":"奥特曼版本开关","desc":"低于2.6.9以下的版本需要打开这个开关"}]
// [param: {"required":false,"key":"otto.who_sq","bool":true,"placeholder":"false","name":"授权控制","desc":"暂时没有作用"}]

// [param: {"spliter":true}]
// [param: {"required":false,"key":"who_tong.js_kg","bool":true,"placeholder":"false","name":"群聊浇水开关","desc":"打开则禁用群内使用浇水(只能私聊)，关闭则群内/私聊浇水"}]
// [param: {"required":true,"key":"otto.js_poxy","placeholder":"http://v2.api.juliangip.com...","name":"代理地址","desc":"巨量是text，,星空/品赞/携趣，都是JSON,代理池需要带http://"}]
// [param: {"required":true,"key":"otto.js_pt","placeholder":"1","name":"代理平台","desc":"巨量=1,星空=2,品赞=3,代理池=4,携取=5,填写你使用平台的数字"}]
// [param: {"required":true,"key":"otto.js_yc","placeholder":"","name":"秒延迟","desc":"说明：【毫秒延迟】没有设置时则使用这个延迟，每次浇水的延迟,以秒为单位，例如：5，则是每次等待5秒"}]
// [param: {"required":true,"key":"otto.js_hmyc","placeholder":"","name":"毫秒延迟","desc":"每次浇水的延迟,以（毫秒）为单位，例如：5000，则是每次等待5秒"}]

var h5st_api = bucketGet("who_tong", "h5st_js")//自建接口
var jd_yc = bucketGet("otto", "js_yc")
var js_hmyc = bucketGet("otto", "js_hmyc")
var nonchang = bucketGet("who_tong", "js_kg")
var nx_h5 = true
var pro = ""
var h5_ver = ""
var nc_h5 = "",jddToken=""
var nc_ua = ""
var juliang = get("js_poxy")
var pingtai = get("js_pt")
var hb_sj = 0
var H5ST = ""
function mian() {
    if (h5st_api == "") {
        H5ST = "http://113.45.206.6:3006"
    }else{
        H5ST=h5st_api
    }
    //var ql_kg = get("ql_kg")//调用开关
    if (nonchang == "true") {
        Debug("开启禁用群内浇水")
        if (GetChatID() == 0 || GetChatID() == "0") {

        } else {
            sendText("请私聊机器人使用该指令")
            return
        }
    } else {
        Debug("未开启禁用群内查询")
    }
    if (juliang == "") {
        notifyMasters("你没有设置代理api地址")
        return
    }
    if (pingtai == "") {
        notifyMasters("你没有设置代理-平台\n巨量=1,星空=2,品赞=3")
        return
    }
    var http_api = bucketGet("who_tong", "atmbb")
    var ql_a = ""
    let ql_toke = ""
    let ckxa = ""
    let ckx = ""
    let message = ""
    //媒介
    imType = ImType()
    //用户id
    userId = GetUserID()
    //绑定的京东账号
    bind = bucketKeys("pin" + imType.toUpperCase(), userId)
    // try {
    if (bind.length == 0) {
        sendText("没有与你绑定的账号，请你先登录")
    } else {

        var ql_name = bucketGet("otto", "js_ql")
        Debug(`指定获取青龙容器名称:${ql_name}`)
        if (ql_name) {
            if (http_api == "true") {
                var ql_a = JSON.parse(ql_cs(ql_name))
            } else {
                var ql_a = qls(ql_name)

            }
        } else {
            notifyMasters("未设置青龙名称,请你到插件云配置中设置")
        }


        ql_toke = ql_dl(ql_a.host, ql_a.client_id, ql_a.client_secret)
        for (let i = 0; i < bind.length; i++) {
            message += `编号:${i}--${decodeURIComponent(bind[i])}\n`
        }
        if (bind.length !== 1) {
            sendText(`${message}\n选择要浇水的账号数字：？？\n输入【q】退出任务`)
            var inp1 = input(80000)
            if (inp1 == "q" || inp1 == "Q" || inp1 == "") {
                sendText("退出操作")
            }

        } else {
            inp1 = 0
        }
        var shouquan = get("who_sq")//代理开关功能
        if (shouquan == "true" || shouquan == true) {
            let who_time = user_vip_jc(bind[inp1])
            if (who_time == true) {

            } else {
                sendText("账号：" + decodeURIComponent(bind[inp1]) + "\n已经到期，如需继续代挂\请联系管理员")
                return
            }
        }
        ckx = ql_token(ql_a.host, ql_toke.token_type, ql_toke.token)
        for (let j = 0; j < ckx.length; j++) {
            let pina = decodeURIComponent(ckx[j].value.match(/(?<=pt_pin=)[^;]+/g))
            if (pina == decodeURIComponent(bind[inp1])) {
                sendText(`请选择浇水模式：
【1】新版农场浇水
【2】新版农场快速浇水
[请在60秒选择模式] `)

                let fs = ShuRu()
                if (fs == 1) {
                    sendText("开始执行新版农场浇水任务...\n不要重复使用执行..")
                    daili()
                    h5_4_xnc(ckx[j].value)
                    return
                } else if (fs == 2) {
                    sendText("开始执行新版农场浇水任务...\n不要重复使用执行..")
                    daili()
                    h5_k4_xnc(ckx[j].value)
                    return
                } else {
                    sendText(`选择超时退出本次任务`)
                }
            }
        }
    }
    //} catch (err) {
    //    Debug(err)
    //}
}
function getCaption(obj, text) {
    let index = obj.lastIndexOf(text) + text.length - 1;

    obj = obj.substring(index + 1, obj.length);
    return obj;
}
function user_vip_jc(ID) {
    let user = bucketGet("who_user_vip", ID)
    if (user == "") {
        return false
    } else {
        var time = Date.parse(new Date()).toString();//获取到毫秒的时间戳，精确到毫秒
        time = parseInt(time / 1000);
        if (user <= time) {
            //sendText("已经到期")
            return false
        } else {
            //sendText("还未到期")
            return true
        }

    }
}
function ShuRu() {
    var msg = input(60000, 6000)
    if (msg == "q" || msg == "Q") {
        sendText("已退出会话");
        return
    } else if (msg == 1 || msg == "1") {
        return 1;
    } else if (msg == 2 || msg == "2") {
        return 2;
    } else if (msg == 3 || msg == "3") {
        return 3;
    } else {
        return msg
    }

}
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
function jd_js(ck) {
    let data = {
        "cardType": "fastCard"
    }
    let body = request({
        url: `https://api.m.jd.com/client.action?functionId=userMyCardForFarm&body=` + JSON.stringify(data) + `&appid=wh5`,
        method: "get",
        headers: {
            "Host": "api.m.jd.com",
            "Accept": "*/*",
            "Origin": "https://carry.m.jd.com",
            "User-Agent": "jdapp;android;12.0.8;;;M/5.0;appBuild/98854;ef/1;ep/%7B%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%22%2C%22ts%22%3A1689974148503%2C%22ridx%22%3A-1%2C%22cipher%22%3A%7B%22sv%22%3A%22CJO%3D%22%2C%22ad%22%3A%22DtHvZwZsZWZwCNSnD2SnZq%3D%3D%22%2C%22od%22%3A%22YWYzDJYyCQC0CJYnCJK3Zq%3D%3D%22%2C%22ov%22%3A%22CzK%3D%22%2C%22ud%22%3A%22DtHvZwZsZWZwCNSnD2SnZq%3D%3D%22%7D%2C%22ciphertype%22%3A5%2C%22version%22%3A%221.2.0%22%2C%22appname%22%3A%22com.jingdong.app.mall%22%7D;jdSupportDarkMode/0;Mozilla/5.0 (Linux; Android 11; M2012K10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046247 Mobile Safari/537.36",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Referer": "https://carry.m.jd.com/",
            "Cookie": ck
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    //sendText(JSON.stringify(body))
    return body
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
var pftj = 0

function h5_nc(ck) {
    let on = {
        "appId": "0c010",
        "appid": "signed_wh5",
        "version": "3.1"
    }
    let od = {
        "type": "",
        "version": 24,
        "channel": 1,
        "babelChannel": "121",
        "lat": "0",
        "lng": "0"
    }
    let water = {
        "functionId": "waterGoodForFarm",
        "config": on,
        "body": od
    }
    for (let k = 0; k < 60000; k++) {
        if (nx_h5) {
            //sendText(JSON.stringify(water))
            let body = request({
                url: H5ST + "/universal",
                method: "post",
                body: water,
                headers: {
                    //    "Host": "h5.xss333.top:8001",
                    "Content-Type": "application/json",
                },
                dataType: "json",//数据类型json(json数据类型)、location(跳转页)
                timeOut: 30000
            })
            Debug(JSON.stringify(body))
            if (body.code = 200) {
                jd_ncjs(ck, body.data, body.ua)
                if (js_hmyc == "") {
                    if (jd_yc == "") {
                        sleep(3000)
                    } else {
                        sleep(parseInt(jd_yc) * 1000)
                    }

                } else {
                    sleep(parseInt(js_hmyc))
                }

            }
        } else {
            // sendText("退出浇水任务")
            return
        }
    }
}
function jd_ncjs(cook, h5, u_a) {
    var str = cook.match(/(?<=pt_pin=)[^;]+/g)
    let pin = decodeURIComponent(str)

    let data = request({
        useproxy: true,
        proxyAddr: pro,
        url: `https://api.m.jd.com/client.action?` + h5,
        method: "get",
        headers: {
            "Host": "api.m.jd.com",
            "Accept": "*/*",
            "origin": "https://carry.m.jd.com",
            "referer": "https://carry.m.jd.com/",
            "User-Agent": u_a,
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Cookie": cook
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })

    Debug(JSON.stringify(data))
    if (data) {


        /*if (data.code == 0) {
            let cs = 6000 - data.treeEnergy
           //sendText(pin + "，浇水成功\n剩下水滴：" + data.totalEnergy + "\n总浇" + data.treeEnergy + "\n还需" + cs + "滴水")
            nx_h5 = true
          sleep(2000)
        }*/
        if (data.code == 0) {
            hb_sj = 0
            pftj = 0
            if (data.treeEnergy % 500 == 0) {
                let cs = 6000 - data.treeEnergy;
                sendText(pin + "\n【本次浇水】 500\n【剩余水滴】 " + data.totalEnergy + "\n【总浇水量】 " + data.treeEnergy + "\n【还需浇水】 " + cs + "\n正在运行，请勿重新发送指令");
            }
            nx_h5 = true;
        }

        if (data.code == 403 || data.code == 404 || data.code == 400) {
            hb_sj = hb_sj + 1
            // sendText("操作过快403...稍等5秒")
            nx_h5 = true
            daili()
        }
        if (data.code == 402) {
            hb_sj = hb_sj + 1
            //sleep(5000)
            nx_h5 = false
            daili()
            return
        }
        if (data.code == 6) {
            sendText(pin + "\n水果成熟了，退出本次浇水任务")
            nx_h5 = false
        }
        if (data.code == 1) {
            hb_sj = hb_sj + 1
            pftj = pftj + 1
            if (pftj == 10) {
                sendText(pin + ",可能该账号风控，退出本次浇水任务")
                nx_h5 = false
                return
            } else {
                //  sendText(pin + "\n请勿重复操作...稍等5秒")
            }

            nx_h5 = true
            daili()

        }
        if (data.code == 7) {
            sendText(pin + ",水滴不足10，退出本次浇水任务")
            nx_h5 = false
            return
        }
        if (data.code == 8) {
            sendText(pin + "水果成熟了，退出本次浇水任务")
            nx_h5 = false
            return
        }
        if (data.code == 3) {
            sendText(pin + ",CK失效，退出本次浇水任务")
            nx_h5 = false
            return
        }
    } else {
        //sendText("代理失效了？")
        hb_sj = hb_sj + 1
        daili()
        //   sendText(ippro)
    }
}

function xncjs(cook, h5, u_a) {

    var str = cook.match(/(?<=pt_pin=)[^;]+/g)
    let pin = decodeURIComponent(str)
    let isRepeated = false; // 添加一个flag变量
    try {
        let data = request({
            useproxy: true,
            proxyAddr: pro,
            url: `https://api.m.jd.com/client.action?appid=signed_wh5&functionId=farm_water`,
            method: "post",
            body:`${h5}&x-api-eid-token=${jddToken.token}` ,
            headers: {
                "Host": "api.m.jd.com",
                "Accept": "application/json, text/plain, */*",
               "x-rp-client": "h5_1.0.0",
                "origin": " https://h5.m.jd.com",
                "x-referer-page": " https://h5.m.jd.com/pb/015686010/Bc9WX7MpCW7nW9QjZ5N3fFeJXMH/index.html",
                "referer": "https://h5.m.jd.com/",
                "User-Agent": u_a,
                "Accept-Language": "zh-CN,zh-Hans;q=0.9",
                 "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": cook
            },
            dataType: "json",//数据类型json(json数据类型)、location(跳转页)
            timeOut: 30000
        })
        if (data) {
            Debug(pin+"新版农场-" + JSON.stringify(data))
            if (data.code == 0) {
                if (data.data.bizCode == 0) {
                    hb_sj = 0
                    nx_h5 = true
                    pftj = pftj + 1
                    if (pftj == 100) {
                        pftj = 0
                        sendText(`账号:${pin}\n剩余水滴:${data.data.result.bottleWater}\n浇水进度:${data.data.result.currentProcess}%\n浇水结果:${data.data.result.waterTips}`)
                    }
                }
                if (data.data.bizCode == 4) {
                    sendText(data.data.bizMsg)//水滴不足
                    nx_h5 = false
                }
                if (data.data.bizCode == 3) {
                    sendText(data.data.bizMsg + ",浇水完成")//种植完成
                    nx_h5 = false
                }
                if (data.data.bizCode == 6) {
                    sendText(pin+",浇水完成"+data.data.bizMsg )//种植完成
                    nx_h5 = false
                }
                if (data.data.bizCode == -30001) {
                    sendText(pin+",账号失效！请先登录后在发送浇水指令")//种植完成
                    nx_h5 = false
                }
                if (data.data.bizCode == -1001) {
                    hb_sj = hb_sj + 1
                    // sendText(data.data.bizMsg)//火爆
                    sleep(3000)
                    nx_h5 = true
                    daili()

                }
            }
            if (data.code == -30001) {
                sendText("账号失效！请先登录后在发送浇水指令")//种植完成
                nx_h5 = false
            }
            if (data.code == 404 || data.code == 403 || data.code == 400 || data.code == 405) {
                hb_sj = hb_sj + 1
                nx_h5 = true
                sleep(3000)
                daili()
            }
        } else {
            hb_sj = hb_sj + 1
            nx_h5 = true
            daili()
        }
    } catch (err) {
        //    Debug(err)
    }
}

function xin_ua() {

    let body = request({
        url: `${H5ST}/UA`,
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
            h5_ver = ucxa[2]
        }
        return true
    } else {
        return false
    }
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
    //  sendText(body)
    return body
}
function daili() {//选择代理模式
    //巨量=1,星空=2,品赞=3
    if (pingtai == 3 || pingtai == "3") {
        //sendText("当前使用--品赞")
        pro = `http://${pinzan()}`
    } else if (pingtai == 2 || pingtai == "2") {
        //sendText("当前使用--星空")

        pro = `http://${xk()}`
    } else if (pingtai == 1 || pingtai == "1") {
        //sendText("当前使用--巨量")

        pro = `http://${proxy()}`
    } else if (pingtai == 4 || pingtai == "4") {
        //sendText("当前使用--代理池")

        pro = juliang
    } else if (pingtai == 5 || pingtai == "5") {
        //sendText("当前使用--携取")
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
    if (body) {
        if (body.code == 0) {
            var IOP = `${body.data[0].IP}:${body.data[0].Port}`
            return IOP
        }
    }

}

function ncaua() {
    nc_h5 = ""
    nc_ua = ""
    let body = request({
        url: `${H5ST}/UA`,
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
            h5_ver = ucxa[2]
        }
        return true
    } else {
        return false
    }
}
function jToken(data) {

    let body = request({
        url: `${H5ST}/jddToken`,
        method: "post",
        body: { "url": data },
        headers: {
            "Content-Type": "application/json",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    if (body) {
       //Debug(JSON.stringify(body))
        if (body.code = 200) {
            jddToken = body.data
            return jddToken
        } else {
            return false
        }

    } else {
        return false
    }
}
function h5_4_xnc(cookie) {//新农场
    pina = cookie.match(/(?<=pt_pin=)[^;]+/g)
    ncaua()
    let home = { "appId": "28981", "fn": "farm_water", "body": {"version":9,"channelParam":"1","waterType":1,"babelChannel":"ttt7","lbsSwitch":true}, "apid": "signed_wh5", "ver": String(h5_ver), "cl": "ios", "code": 1, "ua": nc_ua }
    
    for (let k = 0; k < 60000; k++) {
        xin_h5(home)
        if (nx_h5) {
            jToken("https://h5.m.jd.com/")
            xncjs(cookie, nc_h5, nc_ua)
            if (hb_sj == 10) {
                sendText(pina+",暂时风控的可能,取消继续浇水新版农场任务")
                k = 600001
            }
            sleep(jd_yc * 1000)
        } else {
            sendText("退出浇水任务")
            return
        }

        /* } else {
             notifyMasters("新农场浇水,接口获取失败")
             return
         }*/
    }
}
function h5_k4_xnc(cookie) {//新农场
    pina = cookie.match(/(?<=pt_pin=)[^;]+/g)
    ncaua()
    let home = { "appId": "28981", "fn": "farm_water", "body": {"version":9,"channelParam":"1","waterType":2,"babelChannel":"ttt7","lbsSwitch":true}, "apid": "signed_wh5", "ver": String(h5_ver), "cl": "apple", "user": String(pina), "code": 1, "ua": nc_ua }
    
    for (let k = 0; k < 60000; k++) {
        xin_h5(home)
        if (nx_h5) {
            jToken("https://h5.m.jd.com/")
            xncjs(cookie, nc_h5, nc_ua)
            if (hb_sj == 10) {
                sendText("暂时风控的可能,取消继续浇水新版农场任务")
                k = 600001
            }
            sleep(jd_yc * 1000)
        } else {
            sendText("退出浇水任务")
            return
        }

        /* } else {
             notifyMasters("新农场浇水,接口获取失败")
             return
         }*/
    }
}
function xin_h5(h5_body) {

    let body = request({
        url: `${H5ST}/H5ST_V`,
        method: "post",
        body: h5_body,
        headers: {
            "Content-Type": "application/json",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    if (body) {
        // Debug(JSON.stringify(body))
        if (body.code = 200) {
            nc_h5 = body.data
        }
        return true
    } else {
        return false
    }
}


mian()

