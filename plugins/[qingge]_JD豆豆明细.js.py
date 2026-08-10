//[open_source: false]
// [author: qingge]
// [create_at: 2022-12-25 05:00:00]
// [version: v1.1.1]
// [title: JD豆豆明细]
// [class: 查询类]
// [description: 指令：豆豆明细，输出当天豆豆收入明细以及总豆,和最新收入动态,增加查询全部]
// [platform: qq,wx,tg]
// [public:true]
// [price: 2.00]
// [disable:false]
//[rule:^指定明细+([\s\S]+)$]
// [rule: raw ^豆豆明细$]
// [service:282617666]
var GetContent = GetContent()
//媒介
var imType = ImType()
//用户id

var array = []
var userId = GetUserID()
function mian() {
    var cookie = ""
    if (GetContent == "豆豆明细") {
        //绑定的京东账号
        jds = bucketKeys("pin" + imType.toUpperCase(), userId)
        cookie = ""
        if (jds.length == 0) {
            sendText("没有与你绑定的账号，请对我说：“登陆”")
        } else if (jds.length == 1) {
            jnStr = bucketGet("jdNotify", jds[0])
            Debug(jnStr)
            jn = JSON.parse(jnStr)
            cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
        } else {
            jdsIndex = []
            for (i = 0; i < jds.length; i++) {
                jdsIndex[i] = (i + 1) + ". " + decodeURIComponent(jds[i])
            }
            sendText("请选择要查询的账号：0.查询全部\n" + jdsIndex.join("\\n"))
            var index = input(30000)
            if (index == "" || index == "q" || index == "Q") {
                sendText("取消查询明细任务")
                return
            }
            if (index) {
                if (index == 0) {
                    for (let i = 0; i < jds.length; i++) {

                        jnStr = bucketGet("jdNotify", jds[i])
                        jn = JSON.parse(jnStr)

                        cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                        getJingBeanBalanceDetail(cookie)
                    }
                } else {
                    i = parseInt(index)
                    jnStr = bucketGet("jdNotify", jds[i - 1])
                    jn = JSON.parse(jnStr)

                    cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"

                    Debug(cookie)
                }

            }
        }

    } else {
        let password = getCaption(GetContent, '+');
        if (password == "") {
            sendText("没有发送你需要查的PIN")
            return
        }
        jnStr = bucketGet("jdNotify", password)
        Debug(jnStr)
        jn = JSON.parse(jnStr)
        cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
        Debug(cookie)
    }
    if (index == 0) {

    } else {
        if (cookie) {
            getJingBeanBalanceDetail(cookie)

        }
    }

}
function asse(text) {
    sendText(text)
    let choice = input(120000, 1000)//表示等待用户输入，等待用户输入时间为30秒
    if (choice == 'q') {
        sendText('退出成功')//给会话用户发送信息
        return false
    }
    if (choice == '') {
        sendText('输入超时，自动退出程序')
        return false
    }

    // sendText(choice)
    return choice
}
function getCaption(obj, text) {
    let index = obj.lastIndexOf(text) + text.length - 1;

    obj = obj.substring(index + 1, obj.length);
    return obj;
}

function getJingBeanBalanceDetail(cookie) {
    let pina = cookie.match(/(?<=pt_pin=)[^;]+/g)
    var descriptionCategories = {};
    var totalAmounts = {};
    var dayAmounts = {};
    let mingxi = ""
    let mount = 0
    let QCX = ""
    var ddd = 1
    var nsn = 0
    //Debug("总豆查询")
    for (d = 0; d < 10; d++) {
        let today = timeFmt("yyyy-MM-dd")
        try {
            body = encodeURIComponent(JSON.stringify({ "pageSize": "100", "page": ddd.toString() }))
            request({
                "url": "https://bean.m.jd.com/beanDetail/detail.json?page=" + ddd,
                "body": "body=" + body + "&appid=ld",
                "headers": {
                    'User-Agent': "Mozilla/5.0 (Linux; Android 12; SM-G9880) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36 EdgA/106.0.1370.47",
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Cookie': cookie,
                },
                timeOut: 30000
            }, function (error, response, header, body) {
                if (body) {
                    Debug(JSON.stringify(body))
                    obj = JSON.parse(body)
                    if (obj.code == 0) {
                        for (i = 0; i < obj.jingDetailList.length; i++) {
                            dateStr = obj.jingDetailList[i].date
                            if (dateStr.slice(0, 10) == today) {
                                nsn = nsn + 1
                                if (nsn <= 5) {
                                    QCX += `${dateStr},${obj.jingDetailList[i].eventMassage},${obj.jingDetailList[i].amount}\n`
                                }
                                let doudou = parseInt(obj.jingDetailList[i].amount)
                                var desc = obj.jingDetailList[i].eventMassage
                                // 检查描述是否已存在于描述分类中
                                if (descriptionCategories[desc] !== undefined) {
                                    // 如果存在，累加金额
                                    descriptionCategories[desc] += doudou;
                                } else {
                                    // 如果不存在，创建新的条目并设置金额
                                    descriptionCategories[desc] = doudou;
                                }

                                // 更新总金额统计
                                if (totalAmounts[desc] !== undefined) {
                                    totalAmounts[desc] += doudou;
                                } else {
                                    totalAmounts[desc] = doudou;
                                }
                                mount = mount + doudou
                            } else {
                                // sendText("下面数据非当天,退出")

                            }
                            //msgs.push("【" + dateStr.slice(11) + "】" +  + " " + obj.jingDetailList[i].eventMassage)
                        }
                        // msgs.push("n.下一页，q.退出")
                        //sendText(msgs.join("\\n"))

                    } else {
                        sendText("您的账号已失效:" + pina)
                        d = 999999
                    }
                    ddd = ddd + 1
                }

            })
        } catch (e) { }
    }
    QCX += "-----具体收入明细-----\n"
    for (var desc in totalAmounts) {
        QCX += desc + ": " + totalAmounts[desc] + "\n"
        // mount = mount + parseInt(totalAmounts[desc])
    }

    mingxi += `账号:${pina} 京豆[${mount}]\n-----最近收入动态-----\n${QCX}`
    if (mount == "0" || mount == 0) {

    } else {
        sendText(mingxi)
    }

}
mian()