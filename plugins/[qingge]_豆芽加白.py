//[disable:true]
//[title: 豆芽加白]
//[author: qingge] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]
//[price: 0.1]
//[service: 97393412]
//[admin: false]
//[priority: 99]
//[version: 0.0.3] 
//[public: true] 
//[platform: qq,wxmp,wx,tb,tg,web,wb]
//[description: 温馨说明：豆芽定时加白<br/>需要填密钥] 
//[rule: 豆芽加白] 
// [param: {"required":true,"key":"who_tong.douya_authkey","placeholder":"5klPuIIXXXXXXXXXX","name":"豆芽秘钥","desc":"找你合租的渠道拿取秘钥"}]
// [param: {"required":true,"key":"who_tong.douya_IP","placeholder":"192.168.0.1","name":"当前使用的白名单IP","desc":"上次的IP地址"}]
//[cron: */3 * * * *]
var miyao = bucketGet("who_tong", "douya_authkey")
var dy_ip = bucketGet("who_tong", "douya_IP")
var IP = ""
var bmd_lb = ""
var msgs = []
function mian() {

    if (miyao == "") {
        notifyMasters("你没有设置豆芽[秘钥]")
        return
    }
    HQ_ip()
    if (IP !== "" || IP !== null) {
        msgs.push(`-->获取IP成功,${IP}`)
        if (dy_ip == IP) {
            msgs.push(`-->当前IP:${IP}-上次:${dy_ip},当前IP一致`)
            dy_qbbmd()
            if (bmd_lb.includes(IP)) {
                msgs.push(`-->IP:${IP},处于白名单状态`)
                bucketSet("who_tong", "douya_IP", IP)
            } else {
                msgs.push(`-->IP:${IP},未在白名单列表中找到`)
                jiabai()
            }
        } else {
            sendText("当前IP不一样")
            msgs.push(`-->当前IP:${IP}-上次${dy_ip},当前IP不一样`)
            if (dy_ip == "" || dy_ip == null) {

            } else {
                jiadel(dy_ip)
            }
            jiabai()
            dy_qbbmd()
            if (bmd_lb.includes(IP)) {
                msgs.push(`-->IP:${IP},处于白名单状态`)
                bucketSet("who_tong", "douya_IP", IP)
                
            } else {
                msgs.push(`-->IP:${IP},未在白名单列表中找到`)
                jiabai()
            }
        }
        j = 20
    }
    sendText(msgs.join("\n") + "\n")
    msgs = ""
}
function HQ_ip() {
    for (let j = 0; j < 10; j++) {
        request({
            url: "https://4.ipw.cn",
            method: "get",
            //headers: {
            // "Accept": "*/*",
            /*   "Referer": "https://plantearth.m.jd.com/plantBean/index",
              "Accept-Language": "zh-Hans-CN;q=1,en-CN;q=0.9",
              'User-Agent': UA_api,
              'cookie': cookie,
          },*/
            //dataType: "json",
            timeout: 80000
        }, function (error, response, header, body) {
            if (!error) {
                IP = body
                msgs.push(`-->获取IP成功,${IP}`)
                j = 30
                return true
            } else {
                sleep(2000)
            }

        })
    }
}
function jiabai() {//加白
    request({
        url: `https://api.douyadaili.com/proxy/?service=AddWhite&authkey=${miyao}&white=${IP}&format=txt`,
        method: "get",
        //headers: {
        // "Accept": "*/*",
        /*   "Referer": "https://plantearth.m.jd.com/plantBean/index",
          "Accept-Language": "zh-Hans-CN;q=1,en-CN;q=0.9",
          'User-Agent': UA_api,
          'cookie': cookie,
      },*/
        //  dataType: "json",
        timeout: 80000
    }, function (error, response, header, body) {
        msgs.push(`-->豆芽白名单添加：${body}`)

    })
}
function jiadel(data) {//删除
    request({
        url: `https://api.douyadaili.com/proxy/?service=DelWhite&authkey=${miyao}&white=${data}&format=txt`,
        method: "get",
        //headers: {
        // "Accept": "*/*",
        /*   "Referer": "https://plantearth.m.jd.com/plantBean/index",
          "Accept-Language": "zh-Hans-CN;q=1,en-CN;q=0.9",
          'User-Agent': UA_api,
          'cookie': cookie,
      },*/
        //dataType: "json",
        timeout: 80000
    }, function (error, response, header, body) {
        msgs.push(`-->豆芽白名单删除：${body}`)
    })
}
function dy_qbbmd() {//全部白名单
    request({
        url: `https://api.douyadaili.com/proxy/?service=GetWhite&authkey=${miyao}&format=txt`,
        method: "get",
        timeout: 80000
    }, function (error, response, header, body) {
        bmd_lb = body
    })
}
mian()