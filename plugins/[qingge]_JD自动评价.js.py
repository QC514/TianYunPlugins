//[disable:false]
//[title: JD自动评价]
//[author: qingge] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]
//[price: 2]
//[service: 97393412]
//[admin: false]
//[priority: 99]
//[version: 0.1.0] 
//[public: true] 
//[platform: qq,wxmp,wx,tb,tg,web,wb]
//[description: 队列式评价,定时检测用户提交的评价PIN，进行有序运行完成并通知用户<br/>温馨说明：本插件依赖于6dy的评价本] 
//[rule: ^(评价|自动评价|检测评价|评价重置|评价版本)$] 
// [param: {"required":true,"key":"otto.js_ql","placeholder":"容器名称","name":"青龙名称","desc":"获取名方法:奥特曼后台-容器管理--对接容器--名称"}]
// [param: {"required":true,"key":"who_tong.h5st_api","placeholder":"http://110.40.165.213:39000","name":"自建H5接口","desc":"填写你搭建好的地址：http://110.40.165.213:39000"}]
//[param: {"spliter":true}]
// [param: {"required":true,"key":"who_tong.zd_poxy","placeholder":"http://v2.api.juliangip.com...","name":"代理地址","desc":"巨量是text，,星空/品赞/携趣，都是JSON,代理池需要带http://"}]
// [param: {"required":true,"key":"who_tong.zd_pt","placeholder":"1","name":"代理平台","desc":"巨量=1,星空=2,品赞=3,代理池=4,携取/51代理=5,不使用代理=7,填写你使用平台的数字"}]
var checkJS = false
//[cron: 5 */1 * * *]
try {
    importJs("qinglong.js");
} catch (err) {
    checkJS = true
}
var imType = ImType()
var GetContent = GetContent()
var juliang = bucketGet("who_tong", "zd_poxy")
var pingtai = bucketGet("who_tong", "zd_pt")
var H5ST = bucketGet("who_tong", "h5st_api")
let exchangeRemind = ""
let container
let containerEnv
var host_api = "", nc_ua = "", jddToken = "", nc_h5 = "", text = "", h5_ver = "", h5st_4 = "", rentou = "", markedPin = "", yqm = "", wabao_jf = 0, code_cs = 0, daili_kg = false, pro = ""
//s
function tijiao() {
    //var ql_kg = get("ql_kg")//调用开关
    if (H5ST == "") {
        host_api = "http://113.45.206.6:3006"
    } else {
        host_api = H5ST
    }
    if (checkJS) {
        if (isAdmin()) {
            notifyMasters("使用本插件需要安装【qinglong】依赖插件，请前往云插件下载该插件")
        }
        return
    }

    var ql_a = ""
    let ql_toke = ""
    let ckxa = ""
    let ckx = ""
    let message = false, pinsx = 0
    //媒介
    imType = ImType()
    //用户id
    userId = GetUserID()
    //绑定的京东账号
    bind = bucketKeys("pin" + imType.toUpperCase(), userId)
    // try {
    var ql_name = bucketGet("otto", "js_ql")
    Debug(`指定获取青龙容器名称:${ql_name}`)
    if (ql_name) {
    } else {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置")
        return
    }
    let containerData = qls(ql_name)
    // 获取容器对象
    exchangeRemind += `---新农场奖品明细---\n`
    for (let j = 0; j < 5; j++) {
        try {
            container = Qinglong(containerData.host, containerData.client_id, containerData.client_secret)
            containerEnv = container.ApiQL("envs", "", "get", "").data
            j = 6
        } catch (e) {
            // notifyMasters("【新农场奖品记录】链接容器【" + ql_name + "】失败，请检查配置是否正确或网络是否正常")
            // return
            sleep(2000)
        }


        let accounts = []
        // 获取容器对象
        if (bind.length == 0) {
            sendText("您还没登陆账号,请你先发送：登陆")
        } else {
            let accounts = []
            for (i = 0; i < bind.length; i++) {
                accounts[i] = `【${i + 1}】${bind[i]}`
            }
            sendText(".请选择要查询[京东评价]的账号：\n\n" + accounts.join("\\n") + "")
            let choice = input(30000, 1000)//表示等待用户输入，等待用户输入时间为30秒
            if (choice == 'q') {
                sendText('退出成功')//给会话用户发送信息
                return
            }
            if (choice == '') {
                sendText('输入超时，自动退出程序')
                return
            }
            if (isNaN(choice) || choice > bind.length || choice < 0) {
                sendText('输入错误，自动退出程序')
                return
            }
            let PIN = bind[choice - 1]
            // 判断有没有找到相应ck对象
            let cookieObj = null
            for (let i = 0; i < containerEnv.length; i++) {
                const item = containerEnv[i]
                if (item.name != "JD_COOKIE") {
                    continue
                }

                const isMatch = item.value.indexOf(PIN) != -1
                if (item.status == 0) {
                    pinsx++
                    if (isMatch) {
                        //sendText(`找到账号:${decodeURIComponent(PIN)}对应的CK\n${item.value}`)
                        cookieObj = item
                        break
                    }
                    continue
                }

                if (isMatch && item.status == 1) {
                    text += `账号:${decodeURIComponent(PIN)}\n您的账号已失效`
                    message = true
                    cookieObj = item
                    break
                }
            }
            if (!cookieObj) {
                //sendText("找不到该账号:" + decodeURIComponent(PIN))
            } else {
                if (message) {
                } else {
                    allpins = bucketKeys("who_pingjia")

                    let pingjia = bucketGet("who_pingjia", PIN)
                    if (pingjia == "") {
                        text += `账号:${decodeURIComponent(PIN)}\n已经提交自动评价任务列表\n前面剩余排队人数:${allpins.length}个\n每次最多评价10个，评价完会提醒\n请耐心等待任务完成通知`
                        bucketSet("who_pingjia", PIN, imType)

                        breakIn("检测评价")
                    } else {
                        text += `账号:${decodeURIComponent(PIN)}\n您已提交过自动评价任务，请勿重复提交`
                    }

                }

                //invitehelp(cookieObj[0].value)
                sendText(text)

            }

        }

    }
}
function lsrw(qls_name, PIN, qdtz) {
    // sleep(10000)
    //sendText(PIN + "----")
    let message = false, pinsx = 0, renwuid = 0
    allpins = bucketKeys("qls")
    if (checkJS) {
        if (isAdmin()) {
            notifyMasters("使用订阅【官方】中安装【qinglong】依赖插件，请前往云插件下载该插件")
        }
        return
    }




    for (let j = 0; j < allpins.length; j++) {
        var containerData = JSON.parse(bucketGet("qls", String(allpins[j])))
        if (containerData.name == qls_name) {
            // 获取容器对。象
            var container
            try {
                container = Qinglong(containerData.host, containerData.client_id, containerData.client_secret)
                containerEnv = container.ApiQL("envs", "", "get", "").data
                //获取任务ID
                let tainer_crons = container.GetCrons(encodeURIComponent("评价"))
                if (tainer_crons.data && tainer_crons.code == 200) {
                    sendText: (".........")
                    for (let m = 0; m < tainer_crons.data.data.length; m++) {
                        if (tainer_crons.data.data[m].command.indexOf("6dylan6_jdpro") != -1) {
                            //sendText(`脚本：${tainer_crons.data.data[m].name}----开始运行\n${tainer_crons.data.data[m].command}`)
                            renwuid = parseInt(tainer_crons.data.data[m].id)
                            m = 9999
                            //tongbu(container, `${tainer_crons.data.data[m].id}`, PIN, qdtz)
                        }

                    }
                }
                // sendText(containerEnv.length)
                let hasMatchedCookie = false
                for (let k = 0; k < containerEnv.length; k++) {
                    const itemValue = containerEnv[k]
                    if (itemValue["name"] != "JD_COOKIE") {
                        continue
                    }

                    const isMatch = itemValue["value"].indexOf(PIN) > -1
                    if (itemValue["status"] == 0) {
                        pinsx = pinsx + 1
                        if (isMatch) {
                            hasMatchedCookie = true
                            break
                        }
                        continue
                    }

                    if (!hasMatchedCookie && isMatch && itemValue["status"] == 1) {
                        text += `您的账号已失效`
                        message = true
                        break
                    }
                }
                // sendText(`账号:${decodeURIComponent(PIN)}\n开始提交自动评价任务\nCK位置：${pinsx}\n${message}`)
                if (message) {
                    bucketSet("who_pingjia", PIN)
                    //sendText(text)
                    let pintz = bucketGet("pin" + qdtz.toUpperCase(), PIN)
                    TXfs_tuisong(qdtz, pintz, `===自动评价通知===..
 东东账号->${decodeURIComponent(PIN)}
 ${text}`)
                } else {
                    //sendText(`账号:${decodeURIComponent(PIN)}\n开始提交自动评价任务\nCK位置：${pinsx}`)
                    let daSta = {
                        "labels": "6DY",
                        "command": "task 6dylan6_jdpro/jd_AutoEval.js desi JD_COOKIE " + pinsx,
                        "schedule": "0 0 * * *",
                        "labels": [],
                        "name": "带图评价晒单",
                        "id": renwuid
                    }
                    //sendText(JSON.stringify(daSta))
                    let data = container.Runtemp(daSta)
                    // sendText(JSON.stringify(data))
                    if (data.code == 200) {
                        //修过任务成功
                        bucketSet("who_pingjia", PIN)
                        tongbu(container, renwuid, PIN, qdtz)
                    } else {



                    }

                }


                j = 9999

            } catch (e) {
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


function tongbu(container, id, pin, qdtz) {


    let data = container.RunCrons([id])
    // sendText(JSON.stringify(data) + "----")
    if (data.code == 200) {

        //sendText(`邀请码:${hideMiddlePart(jd_fish_code)}\n本次扣取积分:${by_dckfjf}\n当前剩余积分:${qd.day}\n您的任务..开始助力`)
        sleep(3000)
        //if (tainer_crons.code == 200) {
        //  console.warn(JSON.stringify(tainer_crons) + "----")
        //   if (tainer_crons.data.total == 1) {
        for (let k = 0; k < 500; k++) {
            let data = LogCrons(id)
            //console.warn(JSON.stringify(data))
            data = data.data
            if (data.indexOf("带图评价晒单, 结束") != -1) {
                let obj = data.split("\n")
                for (let j = 0; j < obj.length; j++) {
                    if (obj[j].indexOf("当前有") > -1) {
                        //  txt += `${obj[j]}\n`

                    } else if (obj[j].indexOf("去评价") > -1) {
                        let pingjianc = obj[j].split("去评价")
                        txt += `${pingjianc[1]}\n`
                    }
                }
                //sendText(`账号[${decodeURIComponent(pin)}]评价任务已完成..`)
                if (data.indexOf("没有待晒单的订单") != -1) {
                    var txt = `没有待晒单的订单`
                }

                let pintz = bucketGet("pin" + qdtz.toUpperCase(), pin)
                TXfs_tuisong(qdtz, pintz, `===自动评价通知===
东东账号->${decodeURIComponent(pin)}
评价任务完成
${txt}`)
                // sendText(`邀请码:${hideMiddlePart(jd_fish_code)}\n您的任务已完成..`)
                k = 9999999
                //  bucketSet("who_tong", "by_kongzhi", false)
            } else {
                if (k == 1) {
                    //sendText(`邀请码:${hideMiddlePart(jd_fish_code)}\n助力还未完成....稍等片刻`)
                }
                sleep(8 * 1000)
            }
        }
        // }

        //  }
    } else {
        //sendText(`${containerData.name},运行失败`)

    }
}



//私聊推送
function TXfs_tuisong(tx, qh, data) {
    push({
        imType: tx,
        userID: qh,
        title: "",
        groupCode: "",
        content: data,
    })
}
function mian() {

    var ql_name = bucketGet("otto", "js_ql")
    Debug(`指定获取青龙容器名称:${ql_name}`)
    if (ql_name) {
    } else {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置")
        return
    }
    if (GetContent == "评价" || GetContent == "自动评价") {
        tijiao()
    } else if (GetContent == "评价重置") {
        bucketSet("who_tong", "pjjd", false)
        sendText("评价任务重置完成")
    } else if (GetContent == "评价版本") {
        sendText(`使用说明：本插件依赖于6dy的评价本
版本：0.0.7
使用说明：
1.评价重置：用于奥特曼中途停止时无法定时运行检测评价任务
2.检测评价：用于检测用户提交的PIN进行执行评价任务
3.用户指令：评价，自动评价
更新内容：
`)
    } else {
        let pjjd = bucketGet("who_tong", "pjjd")
        if (pjjd == "true") {
            sendText("有评价任务正在运行中，请稍后再试")
            return
        }
        bucketSet("who_tong", "pjjd", true)
        allpsins = bucketKeys("who_pingjia")
        if (allpsins.length == 0) {
            // sendText("当前没有待评价任务")
            bucketSet("who_tong", "pjjd", false)
            return
        }
        for (let i = 0; i < allpsins.length; i++) {
            //sendText(`---评价任务队列---\n账号:${decodeURIComponent(allpsins[i])}\n任务标识:jd_auto_eval_pin`)
            let data = bucketGet("who_pingjia", allpsins[i])

            lsrw(ql_name, allpsins[i], data)
        }
        bucketSet("who_tong", "pjjd", false)
    }
}

mian()
//fen("pt_key=app_openAAJmsL_zADDhBNKYskbb6Muc-1412-em60IGVNbGixd1k5pjc-WXsvTwsNTnyjP6bO2cOWpSPGU;pt_pin=jd_77e069d2e921d;")