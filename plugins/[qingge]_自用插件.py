//[disable:false]
//[title: 自用插件]
//[author: qingge] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]
//[price: 99999]
//[service: 97393412]
//[admin: false]
//[priority: 99]
//[version: 0.1.2] 
//[public: true] 
//[platform: qq,wxmp,wx,tb,tg,web,wb]
//[description: 温馨说明：星空加白<br/>需要填key和sign<br/>增加管理员推送加白信息开关<br/>检测到IP不同时才加白] 
//[rule: ^星空(加白|手动加白)$] 
// [param: {"required":true,"key":"who_tong.xkdaili_km","placeholder":"who123456789","name":"卡密验证","desc":"填写卡密验证"}]
// [param: {"required":true,"key":"who_tong.xkdaili_IP","placeholder":"192.168.0.1","name":"当前使用的白名单IP","desc":"上次的IP地址"}]
// [param: {"required":false,"key":"who_tong.xkdaili_gly","bool":true,"placeholder":"false","name":"管理员通知","desc":"默认不推送管理员,打开会推送管理员"}]

//[cron: 15 */11 * * * *]
var GetContent = GetContent()
var key = "XK3C2BE7860490F33083"
var sign = "e1d47f0dc9f46dee2a9f15783ce0d519"


var xkdaili_gly = bucketGet("who_tong", "xkdaili_gly")
var IP = ""
var bmd_lb = ""
var msgs = []

function mian() {
    var dy_km = bucketGet("who_tong", "xkdaili_km")
    if (dy_km == "") {
        notifyMasters("你没有填写卡密，取消加白")
        return
    } else if (dy_km == "whoxk252210") {
        Debug("验证成功")
    } else {
        notifyMasters("卡密验证失败无法加白")
        return
    }
    var dy_ip = bucketGet("who_tong", "xkdaili_IP")

    HQ_ip2()
    if (IP !== "" || IP !== null) {
        msgs.push(`-->获取IP成功,${IP}`)
        if (dy_ip == IP) {
            msgs.push(`-->上次:${dy_ip},当前IP一致`)
            //看情况要不要加重试添加
            if (GetContent == "星空手动加白") {
                jiabai()
            } else {

            }

        } else {
            msgs.push(`-->上次${dy_ip},当前IP不同`)
            if (dy_ip == "" || dy_ip == null) {

            } else {
                jiadel(dy_ip)
            }
            jiabai()
            var dy_ip = bucketGet("who_tong", "xkdaili_IP")
            if (dy_ip == IP) {
                msgs.push(`-->上次:${dy_ip},当前IP一致`)
                sleep(2000)
                jiabai()
            }
        }
    }
    if (xkdaili_gly == "true") {
        notifyMasters(msgs.join("\n") + "\n")
    } else {
        sendText(msgs.join("\n") + "\n")
    }


    msgs = ""
}

function HQ_ip2() {
    tt = 0
    for (let j = 0; j < 5; j++) {
        request({
            url: "https://whois.pconline.com.cn/ipJson.jsp?json=true",
            method: "get",
            dataType: "json",
            timeout: 8000
        }, function (error, response, header, body) {
            Debug(`获取IP结果:${JSON.stringify(body)}`)
            if (!error) {
                if (body.regionCode == 0) {
                    IP = body.ip
                    msgs.push(`-2->获取IP成功,${IP}`)
                    j = 30
                    tt = 1
                }


            } else {
                sleep(2000)
            }

        })
    }
    if (tt == 0) {
HQ_ip3()
    }
}
function HQ_ip3() {
    tt = 0
    for (let j = 0; j < 5; j++) {
        request({
            url: "https://myip.ipip.net/json",
            method: "get",
            dataType: "json",
            timeout: 8000
        }, function (error, response, header, body) {
            Debug(`获取IP结果:${body}`)
            if (!error) {
                if (body.ret == "ok") {
                    IP = body.data.ip
                    msgs.push(`-3->获取IP成功,${IP}`)
                    j = 30
                    tt = 1
                }


            } else {
                sleep(2000)
            }

        })
    }
    if (tt == 0) {

    }
}
function jiabai() {//加白
    try {
        request({
            url: `http://api2.xkdaili.com/tools/XApi.ashx?apikey=${key}&type=addwhiteip&sign=${sign}&flag=8&ip=${IP}`,
            method: "post",

            headers: {
                'Content-Type': 'application/json'
            },
            dataType: "json",
            timeout: 8000
        }, function (error, response, header, body) {
            if (!error) {
                if (body.status == 100) {
                    msgs.push(`-->白名单添加：${body.info}`)
                    bucketSet("who_tong", "xkdaili_IP", IP)
                } else if (body.status == 508) {
                    msgs.push(`-->白名单已存在！`)
                    bucketSet("who_tong", "xkdaili_IP", IP)
                } else {
                    msgs.push(`-->白名单添加：${body.info},${body.status}`)
                }
            }
        })
    } catch (err) {
        return jiabai
    }
}
function jiadel(data) {//删除
    try {
        request({
            url: `http://api2.xkdaili.com/tools/XApi.ashx?apikey=${key}&type=delwhiteip&sign=${sign}&flag=8&ip=${data}`,
            method: "get",
            dataType: "json",
            timeout: 80000
        }, function (error, response, header, body) {
            if (!error) {
                if (body.status == 100) {
                    msgs.push(`-->白名单删除：${body.info}`)
                } else {
                    msgs.push(`-->白名单删除：${body.info},${body.status}`)
                }
            } else {
                return jiadel(data)
            }

        })
    } catch (err) {
        return jiadel(data)
    }
}

mian()
