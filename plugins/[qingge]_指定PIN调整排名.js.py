
//[disable:false]
//[title: 指定PIN调整排名]
//[rule:调整]
//[author: qingge] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]
//[public: true] 
//[price: 2] 
//[version: 0.3.1] 
//[admin: false] 
//[platform: qq,wx,tg,wb,qb]
//[priority: 9999999999]
//[service: 97393412]
//[description: 指定PIN调整CK变量排名,指令：调整（可以自己修改指令）]
// [param: {"required":true,"key":"otto.ql_name","placeholder":"填写你需要调用的容器名字","name":"容器名称","desc":"填写你需要调用的容器名字"}]

let pins=0
var ql_name = bucketGet("otto", "ql_name")
var checkJS = false
var containerEnv
var container
try {
    importJs("qinglong.js");
} catch (err) {
    checkJS = true
}
function mian() {
    if (checkJS) {
        if (isAdmin()) {
            notifyMasters("请到群内下载【qinglong】依赖插件放到plugin/replies")
        }
        return
    }
    if (isAdmin() || imType == "croncmd") {
    } else {
        sendText("叼毛!不要乱搞咯")
        return
    }
    // 选择判断
    let POIN = ShuRu("请输入你需要指定调整的PIN(退出发送：q)\n温馨提示：中文PIN需要用乱码的,不是中文")
    if (POIN == false || POIN == '' || POIN == 'q') {
        return
    }
    cook(POIN)
    
}

function ShuRu(name) {
    sendText(name)
    var msg = input(60000, 6000)
    if (msg == "q" || msg == "Q" || msg == "") {
        //sendText("已退出会话");
        return false
    } else {
        return msg
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
function cook(PIN) {
    Debug(`指定获取青龙容器名称:${ql_name}`)
    if (ql_name) {
    } else {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置")
        return
    }
    let containerData = qls(ql_name)
    // 获取容器对象


    try {
        container = Qinglong(containerData.host, containerData.client_id, containerData.client_secret)
        containerEnv = container.ApiQL("envs", "", "get", "").data
    } catch (e) {
        notifyMasters("【种豆得豆助力】链接容器【" + ql_name + "】失败，请检查配置是否正确或网络是否正常")
        return
    }

    let cookieObj = containerEnv.filter(function (_data) {
        pins=pins+1
        return _data.name == "JD_COOKIE" && _data.value.indexOf(PIN) != -1
    });

    let msg
    // 判断有没有找到相应ck对象
    if (cookieObj.length == 0) {
        sendText("找不到该账号:" + decodeURIComponent(PIN))
        return false
    }
    sendText(`输入你需要调整到排名位置\n找到PIN:${PIN}\n当前排名:${pins}`)
    let wabao = input(30000, 1000)//表示等待用户输入，等待用户输入时间为30秒
    if (wabao == 'q' || wabao == '' || isNaN(wabao) || wabao < 0) {
        sendText('输入错误，自动退出程序')
        return
    }
    let data = {"fromIndex":parseInt(pins),"toIndex":parseInt(wabao)-1}
    msg = container.ApiQL(`envs/${cookieObj[0].id}/move`, "", "PUT", data)
    if(msg.code==200){
        sendText("调整完毕")
    }else{
        sendText(`调整失败`)
    }

}
mian()