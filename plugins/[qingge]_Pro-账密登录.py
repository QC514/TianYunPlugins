//[disable:true]
//[author: qingge] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]从工具类、查询类、娱乐类、餐饮类、影音类、生活类、图片类、游戏类等中选择
//[public: true] 是否公开发布？值为true或false，不设置则上传aut云时会自动设置为true
//[price: 3.88] 上架价格

//[rule:^帐密(检测刷新|登陆|登录|删除|黑名单刷新|临时刷新)$]
//[rule:^账密(检测刷新|登陆|登录|删除|黑名单刷新|临时刷新)$]
//[rule:^(密码登录|pro账密)$]
//[version: 1.5.5] 
//[admin: false] 
//[platform: qq,wx,tg,wb,qb]
//[priority: -1000]
// [title: Pro-账密登录]

//[service: Q:97393412]
//[description: 内置指令：账密登录<br/>刷新CK不要用渠道管理员去执行该指令，否则会把PIN绑定到你名下。如需修改地址请你到插件配置中的(执行定时)内修改<br/> 4.25 新增使用账密登录时显示CK状态,需要：jdNotify数据 桶权限<br/> 7-4 增加获取实时CK开关，获取青龙内的PIN在获取jdNotify进行判断是否有效<br/> 7-10 新增刷新帐密时IP黑,自定义指令调用拨号切换IP类插件<br/>7.20 增加黑名单开关，不开启默认到设置的验证次数后删除帐密，开启后不删除帐密,达到设定次数后会加入黑名单,等更新成功或用户主动登录后移除黑名单,单独刷新黑名单的指令：账密黑名单刷新<br/>7.29 新增临时刷新,不推送失败通知用户：账密临时刷新<br/>8.11 显示未使用帐密数据<br/>8.17 剔除刷新时推送链接<br/>9.14 自定义黑名单刷新延迟 ] 
// [param: {"required":true,"key":"who_tong.prohttp","placeholder":"http://192.168.3.45:1234","name":"NarkPro地址","desc":"NarkPro地址,例如:http://192.168.3.45:1234"}]
// [param: {"required":true,"key":"who_tong.prokey","placeholder":"pro的密钥","name":"BotToken","desc":"BotToken设置在pro后台--全局配置--BotApiToken"}]
// [param: {"required":false,"key":"who_tong.pro_qzkg","bool":true,"placeholder":"false","name":"IP频繁","desc":"提示频繁,默认不退出,打开则遇到操作频繁会退出刷新"}]

// [param: {"spliter":true}]
// [param: {"required":true,"key":"who_tong.bbk_qly","placeholder":"容器名称","name":"源青龙名称","desc":"获取名方法:奥特曼后台-容器管理--对接容器--名称"}]
// [param: {"required":false,"key":"who_tong.pro_Notify","bool":true,"placeholder":"false","name":"获取实时CK","desc":"默认使用青龙内CK,打开则使用jdNotify内的CK进行判断是否有效"}]
// [param: {"required":true,"key":"who_tong.bbk_ckyc","placeholder":"","name":"检测更新延迟","desc":"填写数字，以秒为单位"}]
// [param: {"required":true,"key":"who_tong.bbk_hmdyc","placeholder":"","name":"黑名单检测延迟","desc":"填写数字，以秒为单位,黑名单不填写则默认使用上面的延迟"}]
// [param: {"required":true,"key":"who_tong.pro_hei","placeholder":"","name":"黑IP调用","desc":"黑IP时调用爱快重播例如：爱快拨号"}]

// [param: {"required":true,"key":"who_tong.bbk_tzqd","placeholder":"","name":"通知渠道","desc":"wb,qq"}]
// [param: {"required":true,"key":"who_tong.bbk_zmdel","placeholder":"","name":"验证次数","desc":"提示多少次后未更新删除账密数据,输入数字。例如:10,不填写则不会删除验证的账密数据"}]
// [param: {"required":false,"key":"who_tong.pro_hmd","bool":true,"placeholder":"false","name":"过滤黑名单","desc":"默认不开启,需要开启过滤黑名单则需打勾，配合：验证的次数"}]

// [param: {"spliter":true}]
// [param: {"required":false,"key":"who_tong.pro_yxkg","bool":true,"placeholder":"false","name":"CK有效","desc":"默认不开启CK有效时停止登录,需要禁止有效CK继续登录则需打勾"}]
// [param: {"required":false,"key":"who_tong.pro_qlkg","bool":true,"placeholder":"false","name":"群聊开关","desc":"打开则只能私聊使用账密登录"}]
// [param: {"required":true,"key":"who_tong.bbk_aqyz","placeholder":"","name":"安全验证引导语","desc":"请你点击上方链接过一下验证后在发送:账密登陆"}]
// [param: {"required":true,"key":"who_tong.bbk_fxyz","placeholder":"","name":"短信指令","desc":"需要过验证，请去京东app登录过验证以后再发 XXXX"}]
// [param: {"required":true,"key":"who_tong.pro_zdyts","placeholder":"","name":"登陆成功后自定义提示","desc":"wb,qq"}]
// [param: {"required":true,"key":"who_tong.bbk_ismin","placeholder":"","name":"安全验证通知群组","desc":"出现验证/密码错误等等情况推送到指定群组,渠道:群组ID,例如：wx:1564654654,qq:1564654654"}]
//[cron: 5 0,1,8,12,14,20 * * *]
var bbk_ckyc = parseInt(bucketGet("who_tong", "bbk_ckyc"))//检测更新延迟
var bbk_hmdyc = parseInt(bucketGet("who_tong", "bbk_hmdyc"))//检测更新延迟
var narkProHost = bucketGet("who_tong", "prohttp")
var pro_hei = bucketGet("who_tong", "pro_hei")
var narkProToken = bucketGet("who_tong", "prokey")
var pro_yxkg = bucketGet("who_tong", "pro_yxkg")
var zmqly = bucketGet("who_tong", "bbk_qly")//青龙
var stxs = bucketGet("who_tong", "bbk_tzqd")//通知渠道
var ismin = bucketGet("who_tong", "bbk_ismin")//青龙
var bbk_zmdel = parseInt(bucketGet("who_tong", "bbk_zmdel"))//通知多少次后未更新删除
var pro_hmd = bucketGet("who_tong", "pro_hmd")//开启过滤黑名单

var pro_zdyts = bucketGet("who_tong", "pro_zdyts")//青龙
var pro_qzkg = bucketGet("who_tong", "pro_qzkg")//操作频繁退出任务
var bbk_fxyz = bucketGet("who_tong", "bbk_fxyz")//操作频繁退出任务
var pro_Notify = bucketGet("who_tong", "pro_Notify")//获取实时CK

var content = GetContent()
var UserId = GetUserID()
var imType = ImType()
var checkJS = false
var code = "", PIN_HB = [], phon = "", qdjc = "", jd_pin = "", CK = "", wz = "", tuichu = 0
var cg = 0//登录成功
var dx = 0//出现短信
var sb = 0//其他原因
var zs = 0//总数量
var yx = 0//有效账号
var ysx = 0//失效数量
var qt = 0 //其他原因
var hmd = 0//黑名单用户
var qtbl = 0//不是账密
try {
    importJs("qinglong.js");
} catch (err) {
    checkJS = true
};
//登录;
function Login(username, password) {
    for (let i = 0; i < 5; i++) {
        let data = {
            username: username,
            password: password,
            BotApitoken: String(narkProToken)
        }
       // console.log(JSON.stringify(data))
        
        try {
            let body = request({
                url: narkProHost + '/Pwd/Login',//地址
                //url: 'http://120.46.178.47:1080/Pwd/Login',//地址
                headers: {//请求头
                    "Content-Type": "application/json"
                },
                method: "post",//网络请求方法get,post,put,delete
                dataType: "json",//数据类型json(json数据类型)、location(跳转页)
                body: JSON.stringify(data),
                timeOut: 90000//单位为毫秒ms，也可以都小写timeout
            })
console.log(JSON.stringify(body))
           // Debug(`${qdjc}:` + body.message)
            if (body) {
                i = 6
                return body
            }
        } catch (e) { }

    }
}

function sx_mian() {
    let startTime = Date.now();  // 记录任务开始时间

    qdjc = "pro-" + content, pro_name = ""
    if (checkJS) {
        if (isAdmin()) {
            notifyMasters("到群内下载[qinglong.js]上传到plugin/replies的文件内")
        }
        return
    }
    Debug(`指定获取青龙容器名称:${zmqly}`)
    if (zmqly) {
        // ql_a = qls(ql_name)
    } else {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置")
    }
    let containeta = qls(zmqly)
    let container = ""
    let containerEnv = ""
    for (let qx = 0; qx < 5; qx++) {
        try {
            container = Qinglong(containeta.host, containeta.client_id, containeta.client_secret)
            containerEnv = container.ApiQL("envs", "", "get", "").data
            qx = 10
        } catch (e) {
            notifyMasters("【Pro账密登录】链接容器【" + zmqly + "】失败，请检查配置是否正确或网络是否正常")
            sleep(500)
        }
    }
    let cookieObj = containerEnv.filter(function (_data) {
        return _data.name == "JD_COOKIE"
    });


    for (let j = 0; j < cookieObj.length; j++) {//ckx.length
        var pina = cookieObj[j].value.match(/(?<=pt_pin=)[^;]+/g)
        //jd_pin=pina
        var pin_ck = bucketGet("AutoJdck", pina)
        if (pin_ck == "") {
            //Debug("未发现该用户有账密,跳过登录" + decodeURIComponent(pina))
        } else {
            pin_ck = JSON.parse(pin_ck)
            zs = zs + 1
            // Debug("发现该用户有账密+" + decodeURIComponent(pina) + "\n" )
            if (pro_hmd == "true") {
                //开启过滤黑名单
                var zm_hmd = bucketGet("who_pro_hmd", pina)
                if (zm_hmd == "") {

                } else {
                    console.log(`黑名单用户：${pina}`)
                    hmd = hmd + 1
                    continue
                }
            }
            if (pro_Notify == "true") {

                if (cookieObj[j].status == 1) {
                    var jc_ck = false
                } else {
                    let jnStr = bucketGet("jdNotify", pina)
                    jn = JSON.parse(jnStr)
                    cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                    var jc_ck = jdck(cookie)
                }

            } else {
                if (cookieObj[j].status == 1) {
                    var jc_ck = false
                } else {
                    var jc_ck = jdck(cookieObj[j].value)
                }

            }

            if (jc_ck) {
                // console.log("CK有效,跳过刷新+" + decodeURIComponent(pina) + "--" + cookieObj[j].status)
                yx = yx + 1
            } else {
                var qd = stxs.split(",")
                Debug(`该用户CK失效\n
${decodeURIComponent(pina)}
成功数量-->${cg}
失败数量-->${dx}
其他数量-->${qt}
错密数量-->${sb}
黑名单数-->${hmd}`)
                ysx = ysx + 1

                let data = sx_proxz(pin_ck.account, pin_ck.password, pina)
                if (data.fhz == false) {
                    if (data.login == "需要认证请在微信中打开地址认证之后再来登录") {

                        if (GetContent == "账密登录" || GetContent == "账密登陆" || GetContent == "帐密登陆" || GetContent == "帐密登陆" || content == "密码登录") {
                        } else {
                            if (tongzhikaiguan) {


                                for (let k = 0; k < qd.length; k++) {
                                    bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                    push({
                                        imType: qd[k],
                                        userID: bind,
                                        title: "JD账号->账密更新失败",
                                        groupCode: "",
                                        content: `===JD账号->账密更新失败===
东东账号->${pina}
失败原因->需要验证码登录
处理方法->您的账号已失效,请您重新登陆
发送指令：账密登录`});
                                }
                            }
                            if (bbk_zmdel == "") {

                            } else {
                                var pin_del = bucketGet("AutoJdpin", pina)
                                if (pin_del == "") {
                                    pin_del = 0
                                    bucketSet("AutoJdpin", pina, 1)
                                } else {
                                    if (parseInt(pin_del) >= bbk_zmdel) {
                                        if (pro_hmd == "true") {
                                            //开启过滤黑名单
                                            bucketSet("who_pro_hmd", pina, pina)
                                        } else {
                                            notifyMasters(pina + "该账密数据已达到设定次数未过验证,删除掉,并重置")
                                            bucketDel("AutoJdck", pina)
                                            bucketDel("AutoJdpin", pina)
                                        }


                                    } else {
                                        bucketSet("AutoJdpin", pina, parseInt(pin_del) + 1)
                                    }
                                }
                            }

                        }
                        PIN_HB.push(pina + ",原因:安全验证")
                    } else if (data.login == "您的账号在当前应用已注销，无法继续使用，如需使用请重新注册新账号") {
                        bucketDel("AutoJdck", pina)
                        bucketDel("AutoJdpin", pina)
                        if (tongzhikaiguan) {
                            for (let k = 0; k < qd.length; k++) {
                                bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                push({
                                    imType: qd[k],
                                    userID: bind,
                                    title: "JD账号->账密更新失败",
                                    groupCode: "",
                                    content: `===JD账号->账密更新失败===
东东账号->${pina}
登录失败->${data.login}
处理方法:您注销了京东健康,请您下载[京东健康]授权登陆后在尝试`,
                                });
                            }
                        }
                        PIN_HB.push(pina + ",原因:您注销了京东健康,无法使用账密登录")
                        bucketSet("AutoJdck", pinn)
                        // j = 99999999
                    } else if (data.login == "您的账号因安全原因被暂时封镜，请将账号和联系方式发送到shensu@id.com，我们将尽快为您处理" || data.login == "您的账号因安全原因被暂时封锁，请将账号和联系方式发送到shensu@jd.com，我们将尽快为您处理") {
                        bucketDel("AutoJdck", pina)
                        bucketSet("AutoJdck", pinn)
                        if (tongzhikaiguan) {
                            for (let k = 0; k < qd.length; k++) {
                                bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                push({
                                    imType: qd[k],
                                    userID: bind,
                                    title: "JD账号->账密更新失败",
                                    groupCode: "",
                                    content: `===JD账号->账密更新失败===
东东账号->${pina}
登录失败->${data.login}
原因:您注销了京东健康,无法使用账密登录`,
                                });
                            }
                        }
                    } else if (data.login == "账号或密码不正确" || data.login == `账号或密码不正确，若您使用境外手机号登录，请在手机号前加"四位国家区号"，不足则补0，如"0001"、"0355"，或通过短信验证码登录`) {
                        PIN_HB.push(decodeURIComponent(pina) + ",原因:" + data.login)
                        bucketSet("AutoJdck", pina)
                    } else if (data.login == "操作过于频繁" || data.login == "操作过于频繁，请24小时后再试，或先使用其他方式登录") {
                        PIN_HB.push(decodeURIComponent(pina) + ",原因:操作过于频繁")
                        pro_name = "操作过于频繁"
                        if (pro_qzkg == "true") {
                            j = 99999999
                        }
                        if (bbk_zmdel == "") {

                        } else {
                            var pin_del = bucketGet("AutoJdpin", pina)
                            if (pin_del == "") {
                                pin_del = 0
                                bucketSet("AutoJdpin", pina, 1)
                            } else {
                                if (parseInt(pin_del) >= bbk_zmdel) {
                                    if (pro_hmd == "true") {
                                        //开启过滤黑名单
                                        bucketSet("who_pro_hmd", pina, pina)
                                    } else {
                                        notifyMasters(pina + "该账密数据已达到设定次数未过验证,删除掉,并重置")
                                        bucketDel("AutoJdck", pina)
                                        bucketDel("AutoJdpin", pina)
                                    }
                                } else {
                                    bucketSet("AutoJdpin", pina, parseInt(pin_del) + 1)
                                }
                            }
                        }
                        if (tongzhikaiguan) {
                            for (let k = 0; k < qd.length; k++) {
                                bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                if (bbk_fxyz == "") {
                                    push({
                                        imType: qd[k],
                                        userID: bind,
                                        title: "JD账号->账密更新失败",
                                        groupCode: "",
                                        content: `===JD账号->账密更新失败===
东东账号->${pina}
登录失败->操作过于频繁
处理方法->联系管理员处理或者使用指令操作：登录`,
                                    });
                                } else {
                                    push({
                                        imType: qd[k],
                                        userID: bind,
                                        title: "JD账号->账密更新失败",
                                        groupCode: "",
                                        content: `===JD账号->账密更新失败===
东东账号->${pina}
登录失败->操作过于频繁
处理方法->请您使用指令操作：${bbk_fxyz}`,
                                    });
                                }
                            }
                        }
                    } else if (data.login == `触发未知验证码,请使用扫码登录`) {
                        PIN_HB.push(decodeURIComponent(pina) + ",原因:IP噶了")
                        pro_name = "IP噶了"
                        j = 99999999
                        if (pro_hei == "") {

                        } else {
                            breakIn("pro_hei")
                        }
                    } else if (data.login == "您的账号存在安全风险，为了您的资产及隐私安全，请电话联系京东客服（950618)" || data.login == "您的账号存在风险，为了您的账号安全请到京东商城App登录" || data.login == "您的账号存在风险，为了您的账号安全，打开京东商城APP重新登录，风险解除后即可正常使用") {
                        PIN_HB.push(decodeURIComponent(pina) + ",原因:可能出现人脸")
                        if (bbk_zmdel == "") {

                        } else {
                            var pin_del = bucketGet("AutoJdpin", pina)
                            if (pin_del == "") {
                                pin_del = 0
                                bucketSet("AutoJdpin", pina, 1)
                            } else {
                                if (parseInt(pin_del) >= bbk_zmdel) {
                                    if (pro_hmd == "true") {
                                        //开启过滤黑名单
                                        bucketSet("who_pro_hmd", pina, pina)
                                    } else {
                                        notifyMasters(pina + "该账密数据已达到设定次数未过验证,删除掉,并重置")
                                        bucketDel("AutoJdck", pina)
                                        bucketDel("AutoJdpin", pina)
                                    }
                                } else {
                                    bucketSet("AutoJdpin", pina, parseInt(pin_del) + 1)
                                }
                            }
                        }
                        if (tongzhikaiguan) {
                            for (let k = 0; k < qd.length; k++) {
                                bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                if (bbk_fxyz == "") {
                                    push({
                                        imType: qd[k],
                                        userID: bind,
                                        title: "JD账号->账密更新失败",
                                        groupCode: "",
                                        content: `===JD账号->账密更新失败===
东东账号->${pina}
失败原因->需要过人脸验证
处理方法->请去京东app登录过人脸验证以后再发：登录`,
                                    });
                                } else {
                                    push({
                                        imType: qd[k],
                                        userID: bind,
                                        title: "JD账号->账密更新失败",
                                        groupCode: "",
                                        content: `===JD账号->账密更新失败===
东东账号->${pina}
失败原因->需要过人脸验证
处理方法->请去京东app登录过人脸验证以后再发：${bbk_fxyz}`,
                                    });
                                }

                            }
                        }
                    } else {
                        PIN_HB.push(decodeURIComponent(pina) + ",原因:" + data.login)
                    }

                }
                if (tuichu >= 30) {
                    pro_name = "尝试30次没有账号正常刷新,退出刷新"
                    j = 99999999
                }
                if (content == "账密黑名单刷新" || content == "帐密黑名单刷新") {
                    if (bbk_hmdyc) {
                        sleep(bbk_hmdyc * 1000)
                    } else {
                        sleep(bbk_ckyc * 1000)
                    }
                } else {
                    sleep(bbk_ckyc * 1000)
                }
            }
        }
    }
    if (pro_name == "") {
        pro_name = "Pro刷新任务完成"
    }
    let endTime = Date.now();  // 记录任务结束时间
    let durationInMs = endTime - startTime;  // 计算任务的运行时长（毫秒）
    const durationInMinutes = durationInMs / 60000;  // 转换为分钟
    notifyMasters(`${content}-JD账密刷新数据:
总账密数-->${zs}
有效数量-->${yx}
失效数量-->${ysx}
成功数量-->${cg}
失败数量-->${dx}
其他数量-->${qt}
错密数量-->${sb}
黑名单数-->${hmd}
刷新状态-->${pro_name}
运行时长-->${durationInMinutes.toFixed(2)} 分钟`)
    if (ismin == "") {
        notifyMasters(PIN_HB.join("\n") + "\n")
    } else {
        var jd_grqd = ismin.split(",")
        for (let k = 0; k < jd_grqd.length; k++) {
            let grqd = jd_grqd[k].split(":")
            push({
                imType: grqd[0],
                userID: "",
                title: "",
                groupCode: grqd[1],
                content: PIN_HB.join("\n") + "\n",
            });
        }
    }
}
function sx_proxz(p, w, pinn) {
    let dt = 0
    let login_zm = Login(p, w)
    //console.log(`${qdjc}:${JSON.stringify(login_zm)}`)
    try {
        if (login_zm.success == false) {
            if (login_zm.message == "需要认证请在微信中打开地址认证之后再来登录") {
                tuichu = 0
                dx = dx + 1
                return { "login": login_zm.message, "fhz": false, "url": login_zm.data.jmp_url }
            } else if (login_zm.message == "账号或密码不正确" || login_zm.message == `账号或密码不正确，若您使用境外手机号登录，请在手机号前加"四位国家区号"，不足则补0，如"0001"、"0355"，或通过短信验证码登录`) {
                bucketSet("AutoJdck", pinn)
                breakIn("CK删除+" + pinn)
                tuichu = 0
                sb = sb + 1
                return { "login": login_zm.message, "fhz": false }
            } else if (login_zm.message == "您的账号在当前应用已注销，无法继续使用，如需使用请重新注册新账号") {
                tuichu = 0
                bucketSet("AutoJdck", pinn)
                qt = qt + 1
                return { "login": login_zm.message, "fhz": false }
            } else if (login_zm.message == "操作过于频繁" || login_zm.message == "操作过于频繁，请24小时后再试，或先使用其他方式登录") {
                qt = qt + 1
                //sendText(`失败原因:${login_zm.message}`)
                pro_name = "操作过于频繁"
                tuichu = 0
                return { "login": login_zm.message, "fhz": false }
            } else if (login_zm.message == "没有权限") {
                //sendText(`失败原因:${login_zm.message}`)
                tuichu = 0
                return { "login": login_zm.message, "fhz": false }
            } else if (login_zm.message == "您的账号存在安全风险，为了您的资产及隐私安全，请电话联系京东客服（950618)" || login_zm.message == "您的账号存在风险，为了您的账号安全，打开京东商城APP重新登录，风险解除后即可正常使用" || login_zm.message == "您的账号存在风险，为了您的账号安全请到京东商城App登录") {
                //sendText(`失败原因:${login_zm.message}`)
                dx = dx + 1
                return { "login": login_zm.message, "fhz": false }
            } else if (login_zm.message == "触发未知验证码,请使用扫码登录") {
                qt = qt + 1
                return { "login": login_zm.message, "fhz": false }
            } else if (login_zm.message.indexOf("封禁") > -1 || login_zm.message.indexOf("安全原因被暂时") > -1) {
                tuichu = 0
                //sendText(`失败原因:${login_zm.message}`)
                qt = qt + 1
                return { "login": login_zm.message, "fhz": false }

            } else {
                dt = dt + 1
                tuichu = tuichu + 1
                if (dt == 10) {
                    return { "login": login_zm.message, "fhz": false }
                } else {
                    sleep(2000)
                }
                return sx_proxz(p, w, pinn)
            }
        } else {
            tuichu = 0
            cg = cg + 1
            ck = login_zm.data.ck
            var pina = ck.match(/(?<=pt_pin=)[^;]+/g)
            bucketDel("AutoJdpin", pina)
            bucketSet("who_pro_hmd", pina)
            sendText(`登录成功：${pina}\n${pro_zdyts}`)
            if (content == "账密登录" || content == "账密登陆" || content == "pro账密" || content == "密码登录") {
                pro_zm = JSON.stringify({ "account": p, "password": w, "cookie": ck, "user": UserId, "platform": imType })
                bucketSet("AutoJdck", pina, pro_zm)
                bucketSet("Autophone", pina, p)
                notifyMasters(`======JD帐密登陆通知======
[登陆用户]：${UserId}
[登陆平台]：${imType}
[登陆账户]：${pina}
[登陆时间]：${call("timeFormat")("yyyy-MM-dd HH:MM:SS")}
[登陆方式]：账密登陆`)
            } else {
                let data = bucketGet("AutoJdck", pina)
                pin_ck = JSON.parse(data)
                pro_zm = JSON.stringify({ "account": p, "password": w, "cookie": ck, "user": pin_ck.user, "platform": pin_ck.platform })
                bucketSet("AutoJdck", pina, pro_zm)
            }
            breakIn(ck)
            return { "login": pina, "fhz": true }
        }
    } catch (e) {
        Debug(e)
    }


}
function hmd_mian() {
    let startTime = Date.now();  // 记录任务开始时间

    qdjc = "pro-" + content, pro_name = ""
    if (checkJS) {
        if (isAdmin()) {
            notifyMasters("到群内下载[qinglong.js]上传到plugin/replies的文件内")
        }
        return
    }
    Debug(`指定获取青龙容器名称:${zmqly}`)
    if (zmqly) {
        // ql_a = qls(ql_name)
    } else {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置")
    }
    let containeta = qls(zmqly)
    let container = ""
    let containerEnv = ""
    for (let qx = 0; qx < 5; qx++) {
        try {
            container = Qinglong(containeta.host, containeta.client_id, containeta.client_secret)
            containerEnv = container.ApiQL("envs", "", "get", "").data
            qx = 10
        } catch (e) {
            notifyMasters("【Pro账密登录】链接容器【" + zmqly + "】失败，请检查配置是否正确或网络是否正常")
            sleep(500)
        }
    }
    let cookieObj = containerEnv.filter(function (_data) {
        return _data.name == "JD_COOKIE"
    });


    for (let j = 0; j < cookieObj.length; j++) {//ckx.length
        var pina = cookieObj[j].value.match(/(?<=pt_pin=)[^;]+/g)
        //jd_pin=pina
        var pin_ck = bucketGet("AutoJdck", pina)
        if (pin_ck == "") {
            //Debug("未发现该用户有账密,跳过登录" + decodeURIComponent(pina))
        } else {
            pin_ck = JSON.parse(pin_ck)
            zs = zs + 1
            // Debug("发现该用户有账密+" + decodeURIComponent(pina) + "\n" )
            if (pro_hmd == "true") {
                //开启过滤黑名单
                var zm_hmd = bucketGet("who_pro_hmd", pina)
                if (zm_hmd == "") {
                    continue
                } else {
                    console.log(`黑名单.用户：${pina}`)
                    hmd = hmd + 1

                }
            }
            if (pro_Notify == "true") {

                if (cookieObj[j].status == 1) {
                    var jc_ck = false
                } else {
                    let jnStr = bucketGet("jdNotify", pina)
                    jn = JSON.parse(jnStr)
                    cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                    var jc_ck = jdck(cookie)
                }

            } else {
                if (cookieObj[j].status == 1) {
                    var jc_ck = false
                } else {
                    var jc_ck = jdck(cookieObj[j].value)
                }

            }

            if (jc_ck) {
                console.log("CK有效,跳过刷新+" + decodeURIComponent(pina) + "--" + cookieObj[j].status)
                yx = yx + 1
            } else {
                var qd = stxs.split(",")
               Debug(`该用户CK失效\n
${decodeURIComponent(pina)}
成功数量-->${cg}
失败数量-->${dx}
其他数量-->${qt}
错密数量-->${sb}
黑名单数-->${hmd}`)
                ysx = ysx + 1

                let data = sx_proxz(pin_ck.account, pin_ck.password, pina)
                if (data.fhz == false) {
                    if (data.login == "需要认证请在微信中打开地址认证之后再来登录") {

                        if (GetContent == "账密登录" || GetContent == "账密登陆" || GetContent == "帐密登陆" || GetContent == "帐密登陆" || content == "密码登录") {
                        } else {
                            if (tongzhikaiguan) {


                                for (let k = 0; k < qd.length; k++) {
                                    bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                    push({
                                        imType: qd[k],
                                        userID: bind,
                                        title: "JD账号->账密更新失败",
                                        groupCode: "",
                                        content: `===JD账号->账密更新失败===
东东账号->${pina}
失败原因->需要验证码登录
处理方法->您的账号已失效,请您重新登陆
发送指令：账密登录`});
                                }
                            }
                            if (bbk_zmdel == "") {

                            } else {
                                var pin_del = bucketGet("AutoJdpin", pina)
                                if (pin_del == "") {
                                    pin_del = 0
                                    bucketSet("AutoJdpin", pina, 1)
                                } else {
                                    if (parseInt(pin_del) >= bbk_zmdel) {
                                        if (pro_hmd == "true") {
                                            //开启过滤黑名单
                                            bucketSet("who_pro_hmd", pina, pina)

                                        } else {
                                            notifyMasters(pina + "该账密数据已达到设定次数未过验证,删除掉,并重置")
                                            bucketDel("AutoJdck", pina)
                                            bucketDel("AutoJdpin", pina)
                                        }
                                        bucketSet("AutoJdpin", pina, parseInt(pin_del) + 1)

                                    } else {
                                        bucketSet("AutoJdpin", pina, parseInt(pin_del) + 1)
                                    }
                                }
                            }

                        }
                        PIN_HB.push(pina + ",原因:安全验证")
                    } else if (data.login == "您的账号在当前应用已注销，无法继续使用，如需使用请重新注册新账号") {
                        bucketDel("AutoJdck", pina)
                        bucketDel("AutoJdpin", pina)
                        if (tongzhikaiguan) {
                            for (let k = 0; k < qd.length; k++) {
                                bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                push({
                                    imType: qd[k],
                                    userID: bind,
                                    title: "JD账号->账密更新失败",
                                    groupCode: "",
                                    content: `===JD账号->账密更新失败===
东东账号->${pina}
登录失败->${data.login}
原因:您注销了京东健康,请您下载[京东健康]授权登陆后在尝试`,
                                });
                            }
                        }
                        PIN_HB.push(pina + ",原因:您注销了京东健康,无法使用账密登录")
                        bucketSet("AutoJdck", pinn)
                        // j = 99999999
                    } else if (data.login == "您的账号因安全原因被暂时封镜，请将账号和联系方式发送到shensu@id.com，我们将尽快为您处理" || data.login == "您的账号因安全原因被暂时封锁，请将账号和联系方式发送到shensu@jd.com，我们将尽快为您处理") {
                        bucketDel("AutoJdck", pina)
                        bucketSet("AutoJdck", pinn)
                        if (tongzhikaiguan) {
                            for (let k = 0; k < qd.length; k++) {
                                bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                push({
                                    imType: qd[k],
                                    userID: bind,
                                    title: "JD账号->账密更新失败",
                                    groupCode: "",
                                    content: `===JD账号->账密更新失败===
东东账号->${pina}
登录失败->${data.login}
原因:您注销了京东健康,无法使用账密登录`,
                                });
                            }
                        }
                    } else if (data.login == "账号或密码不正确" || data.login == `账号或密码不正确，若您使用境外手机号登录，请在手机号前加"四位国家区号"，不足则补0，如"0001"、"0355"，或通过短信验证码登录`) {
                        PIN_HB.push(decodeURIComponent(pina) + ",原因:" + data.login)
                        breakIn("CK删除+" + pina)
                        bucketSet("AutoJdck", pina)
                    } else if (data.login == "操作过于频繁" || data.login == "操作过于频繁，请24小时后再试，或先使用其他方式登录") {
                        PIN_HB.push(decodeURIComponent(pina) + ",原因:操作过于频繁")
                        if (pro_qzkg == "true") {
                            j = 99999999
                        }
                        if (bbk_zmdel == "") {

                        } else {
                            var pin_del = bucketGet("AutoJdpin", pina)
                            if (pin_del == "") {
                                pin_del = 0
                                bucketSet("AutoJdpin", pina, 1)
                            } else {
                                if (parseInt(pin_del) >= bbk_zmdel) {
                                    if (pro_hmd == "true") {
                                        //开启过滤黑名单
                                        bucketSet("who_pro_hmd", pina, pina)
                                    } else {
                                        notifyMasters(pina + "该账密数据已达到设定次数未过验证,删除掉,并重置")
                                        bucketDel("AutoJdck", pina)
                                        bucketDel("AutoJdpin", pina)
                                    }
                                } else {
                                    bucketSet("AutoJdpin", pina, parseInt(pin_del) + 1)
                                }
                            }
                        }
                        if (tongzhikaiguan) {
                            for (let k = 0; k < qd.length; k++) {
                                bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                if (bbk_fxyz == "") {
                                    push({
                                        imType: qd[k],
                                        userID: bind,
                                        title: "JD账号->账密更新失败",
                                        groupCode: "",
                                        content: `===JD账号->账密更新失败===
东东账号->${pina}
登录失败->操作过于频繁
处理方法->请您使用指令操作：登录`,
                                    });
                                } else {
                                    push({
                                        imType: qd[k],
                                        userID: bind,
                                        title: "JD账号->账密更新失败",
                                        groupCode: "",
                                        content: `===JD账号->账密更新失败===
东东账号->${pina}
登录失败->操作过于频繁
处理方法->请您使用指令操作：${bbk_fxyz}`,
                                    });
                                }
                            }
                        }
                    } else if (data.login == `触发未知验证码,请使用扫码登录`) {
                        PIN_HB.push(decodeURIComponent(pina) + ",原因:IP噶了")
                        pro_name = "IP噶了"
                        j = 99999999
                        if (pro_hei == "") {

                        } else {
                            breakIn("pro_hei")
                        }
                    } else if (data.login == "您的账号存在安全风险，为了您的资产及隐私安全，请电话联系京东客服（950618)" || data.login == "您的账号存在风险，为了您的账号安全请到京东商城App登录") {
                        PIN_HB.push(decodeURIComponent(pina) + ",原因:可能出现人脸")
                        if (bbk_zmdel == "") {

                        } else {
                            var pin_del = bucketGet("AutoJdpin", pina)
                            if (pin_del == "") {
                                pin_del = 0
                                bucketSet("AutoJdpin", pina, 1)
                            } else {
                                if (parseInt(pin_del) >= bbk_zmdel) {
                                    if (pro_hmd == "true") {
                                        //开启过滤黑名单
                                        bucketSet("who_pro_hmd", pina, pina)


                                    } else {
                                        notifyMasters(pina + "该账密数据已达到设定次数未过验证,删除掉,并重置")
                                        bucketDel("AutoJdck", pina)
                                        bucketDel("AutoJdpin", pina)
                                    }
                                    bucketSet("AutoJdpin", pina, parseInt(pin_del) + 1)
                                } else {
                                    bucketSet("AutoJdpin", pina, parseInt(pin_del) + 1)
                                }
                            }
                        }
                        if (tongzhikaiguan) {
                            for (let k = 0; k < qd.length; k++) {
                                bind = bucketGet("pin" + qd[k].toUpperCase(), pina)
                                if (bbk_fxyz == "") {
                                    push({
                                        imType: qd[k],
                                        userID: bind,
                                        title: "JD账号->账密更新失败",
                                        groupCode: "",
                                        content: `===JD账号->账密更新失败===
东东账号->${pina}
登录失败->需要过验证
失败原因->请去京东app登录过验证以后再发：登录`,
                                    });
                                } else {
                                    push({
                                        imType: qd[k],
                                        userID: bind,
                                        title: "JD账号->账密更新失败",
                                        groupCode: "",
                                        content: `===JD账号->账密更新失败===
东东账号->${pina}
登录失败->需要过验证
失败原因->请去京东app登录过验证以后再发：${bbk_fxyz}`,
                                    });
                                }

                            }
                        }
                    } else {
                        PIN_HB.push(decodeURIComponent(pina) + ",原因:" + data.login)
                    }

                }
                if (tuichu >= 30) {
                    pro_name = "尝试30次没有账号正常刷新,退出刷新"
                    j = 99999999
                }
                if (content == "账密黑名单刷新" || content == "帐密黑名单刷新") {
                    if (bbk_hmdyc) {
                        sleep(bbk_hmdyc * 1000)
                    } else {
                        sleep(bbk_ckyc * 1000)
                    }
                } else {
                    sleep(bbk_ckyc * 1000)
                }
            }
        }
    }
    if (pro_name == "") {
        pro_name = "Pro刷新任务完成"
    }
    let endTime = Date.now();  // 记录任务结束时间
    let durationInMs = endTime - startTime;  // 计算任务的运行时长（毫秒）
    const durationInMinutes = durationInMs / 60000;  // 转换为分钟
    notifyMasters(`${content}-JD账密刷新数据:
总账密数-->${zs}
有效数量-->${yx}
失效数量-->${ysx}
成功数量-->${cg}
失败数量-->${dx}
其他数量-->${qt}
错密数量-->${sb}
黑名单数-->${hmd}
刷新状态-->${pro_name}
运行时长-->${durationInMinutes.toFixed(2)} 分钟`)
    if (ismin == "") {
        notifyMasters(PIN_HB.join("\n") + "\n")
    } else {
        var jd_grqd = ismin.split(",")
        for (let k = 0; k < jd_grqd.length; k++) {
            let grqd = jd_grqd[k].split(":")
            push({
                imType: grqd[0],
                userID: "",
                title: "",
                groupCode: grqd[1],
                content: PIN_HB.join("\n") + "\n",
            });
        }
    }
}
function mian() {
    qdjc = "pro-账密登陆", p = "", w = ""
    if (checkJS) {
        if (isAdmin()) {
            notifyMasters(qdjc + ",到群内下载[qinglong.js]上传到plugin/replies的文件内")
        }
        return
    }
    let bind = bucketKeys("pin" + imType.toUpperCase(), UserId)
    var ptpin = "", data = "", pro_zm = ""
    if (bind.length == 0) {
        //sendText("没有与你绑定的账号，请你先登录")
        p = asse("输入您绑定[JD]的手机号/用户名.")
        if (p == false) {

        } else {
            w = asse("输入您[JD]的登录密码")
            if (w == false) {

            } else {
                data = proxz(p, w)
            }


        }
    } else {

        ptpin += "请选择你的操作，输入数字\n[0] 新增账号\n"
        let dat = 0, ck_zt = ""
        for (let j = 0; j < bind.length; j++) {
            //sendText(bind[j])
            var jnStr = bucketGet("jdNotify", bind[j])
            var pin_ck = bucketGet("AutoJdck", bind[j])

            if (pin_ck == "") {
                //sendText("没有存在")
                if (jnStr == "") {

                    ck_zt = "失效"
                } else {
                    jn = JSON.parse(jnStr)
                    cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                    let jc_ck = jdck(cookie)
                    if (jc_ck) {
                        ck_zt = "有效"
                    } else {
                        ck_zt = "失效"
                    }
                }
                dat = dat + 1
                ptpin += `[${j + 1}] ${hideMiddlePart(decodeURIComponent(bind[j]))} [未使用账密]${ck_zt}\n`

            } else {
                let phon = JSON.parse(pin_ck)
                jn = JSON.parse(jnStr)
                cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                let jc_ck = jdck(cookie)
                if (jc_ck) {
                    ck_zt = "有效"
                } else {
                    ck_zt = "失效"
                }
                dat = dat + 1
                ptpin += `[${j + 1}] ${hideMiddlePart(decodeURIComponent(bind[j]))} [${phone(phon.account)}]${ck_zt}\n`


            }
        }
        if (dat == 0) {
            p = asse("输入您绑定[JD]的手机号/用户名..")
            if (p == false) {

            } else {
                w = asse("输入您[JD]的登录密码")
                if (w == false) {

                } else {
                    //sendText(`${p}-${w}`)

                    data = proxz(p, w)
                }
            }
        } else {
            sendText(ptpin)
            var choice = input(30000, 1000)//表示等待用户输入，等待用户输入时间为30秒
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
            if (choice == 0) {
                //sendText("输入您的手机号")
                p = asse("输入您绑定[JD]的手机号/用户名")
                if (p == false) {

                } else {
                    w = asse("输入您[JD]的登录密码")
                    if (w == false) {

                    } else {

                        data = proxz(p, w)

                    }
                }

            } else {
                // sendText("您选择的账号:" + decodeURIComponent(bind[choice - 1]) + "\n开始登录验证..")
                var pin_ck = bucketGet("AutoJdck", bind[choice - 1])
                if (pin_ck == "") {
                    p = asse("输入您绑定[JD]的手机号/用户名..")
                    if (p == false) {
                        return
                    } else {
                        w = asse("输入您[JD]的登录密码")
                        if (w == false) {
                            return
                        }
                    }
                } else {
                    pin_ck = JSON.parse(pin_ck)
                    p = pin_ck.account
                    w = pin_ck.password
                }


                if (pro_yxkg == "" || pro_yxkg == "false") {
                    sendText("您选择的账号:" + decodeURIComponent(bind[choice - 1]) + "\n开始登录验证..")
                    data = proxz(p, w)
                } else {
                    var jnStr = bucketGet("jdNotify", bind[choice - 1])
                    jn = JSON.parse(jnStr)
                    cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                    let jc_ck = jdck(cookie)
                    if (jc_ck) {
                        // ck_zt = "有效"
                        sendText(`您的账号[${decodeURIComponent(bind[choice - 1])}]有效,无需更新`)
                    } else {
                        // ck_zt = "失效"
                        sendText("您选择的账号:" + decodeURIComponent(bind[choice - 1]) + "\n开始登录验证..")
                        data = proxz(p, w)
                    }
                }

            }
        }
    }
    try {
        if (data.fhz == false) {
            if (data.login == "需要认证请在微信中打开地址认证之后再来登录") {
                let twsxt = ShuRu(`需要完成异地登陆验证:${data.url}\n请你完成上方的安全验证后再回复：1\n[温馨提示:如果输入验证码后回复1后没有反应，就使用验证码登录的方式登录]\n取消账密登录发送：q`)
                if (twsxt == "已退出会话" || twsxt == "") {
                    sendText(`取消账密登录任务`)
                } else {
                    data = proxz(p, w)
                    if (data.fhz == false) {
                        sendText(`请你完成上方的登录验证后\n重新账密登录发送指令\n取消账密登录发送：q`)
                    }
                }
            } else if (data.login == "账号或密码不正确") {
                sendText(`您的密码错误，请核对密码后在重新登录`)
            } else if (data.login == "操作过于频繁" || data.login == "操作过于频繁，请24小时后再试，或先使用其他方式登录") {
                if (bbk_fxyz == "") {
                    sendText(`操作过于频繁，请使用短信登录：登录`)
                } else {
                    sendText(`操作过于频繁，请使用:${bbk_fxyz}`)
                }
                notifyMasters("IP黑了。请尽快切换IP")
            } else if (data.login == "没有权限") {
                sendText(`没有权限`)
                notifyMasters(`Pro密钥您还没有配置，请您到pro后台设置和插件配置中的密钥一致`)
            } else if (/您的账号存在安全风险/.test(data.login)) {
                if (bbk_fxyz == "") {
                    sendText(`需要过人脸验证:\n请去京东app登录过验证以后再发：登录`)
                } else {
                    sendText(`需要过人脸验证:\n请去京东app登录过验证以后再发：${bbk_fxyz}`)
                }

            } else if (data.login == "您的账号存在安全风险，为了您的资产及隐私安全，请电话联系京东客服（950618)" || data.login == "您的账号存在风险，为了您的账号安全请到京东商城App登录" || data.login == "您的账号存在风险，为了您的账号安全，打开京东商城APP重新登录，风险解除后即可正常使用") {
                if (bbk_fxyz == "") {
                    sendText(`需要过人脸验证:\n请去京东app登录过验证以后再发：登录`)
                } else {
                    sendText(`需要过人脸验证:\n请去京东app登录过验证以后再发：${bbk_fxyz}`)
                }
            } else if (data.login.indexOf("封禁") > -1 || data.login.indexOf("安全原因被暂时封") > -1) {
                sendText(data.login)
            } else if (data.login == "触发未知验证码,请使用扫码登录") {
                sendText("请您先使用验证码登录,指令:登录")
                notifyMasters("IP黑了。请尽快切换IP")
            } else {
                sendText(`未知原因：` + data.login + "\n请您先使用验证码登录,指令:登录")
            }
        }
    } catch (e) {
        if (bbk_fxyz == "") {
            sendText(`需要过人脸验证:\n请去京东app登录过验证以后再发：登录`)
        } else {
            sendText(`需要过人脸验证:\n请去京东app登录过验证以后再发：${bbk_fxyz}`)
        }
    }
}
function proxz(p, w) {
    let dt = 0
    let login_zm = Login(p, w)
    console.log(`${qdjc}:${JSON.stringify(login_zm)}`)
    try {
        if (login_zm.success == false) {
            if (login_zm.message == "需要认证请在微信中打开地址认证之后再来登录") {
                dx = dx + 1
                return { "login": login_zm.message, "fhz": false, "url": login_zm.data.jmp_url }
            } else if (login_zm.message == "账号或密码不正确" || login_zm.message == `账号或密码不正确，若您使用境外手机号登录，请在手机号前加"四位国家区号"，不足则补0，如"0001"、"0355"，或通过短信验证码登录`) {
                sb = sb + 1
                return { "login": login_zm.message, "fhz": false }
            } else if (login_zm.message == "您的账号在当前应用已注销，无法继续使用，如需使用请重新注册新账号") {
                sb = sb + 1
                return { "login": login_zm.message, "fhz": false }
            } else if (login_zm.message == "操作过于频繁" || login_zm.message == "操作过于频繁，请24小时后再试，或先使用其他方式登录") {
                //sendText(`失败原因:${login_zm.message}`)
                return { "login": login_zm.message, "fhz": false }

            } else if (login_zm.message == "没有权限") {
                //sendText(`失败原因:${login_zm.message}`)
                return { "login": login_zm.message, "fhz": false }
                // } else if (/您的账号存在安全风险/.test(data.login)) {
            } else if (login_zm.message == "您的账号存在安全风险，为了您的资产及隐私安全，请电话联系京东客服（950618)" || login_zm.message == "您的账号存在风险，为了您的账号安全请到京东商城App登录" || login_zm.message == "您的账号存在风险，为了您的账号安全，打开京东商城APP重新登录，风险解除后即可正常使用") {
                //sendText(`失败原因:${login_zm.message}`)
                dx = dx + 1

            } else if (login_zm.message == `触发未知验证码,请使用扫码登录`) {
                dx = dx + 1
                return { "login": login_zm.message, "fhz": false }
            } else if (login_zm.message.indexOf("封禁") > -1 || login_zm.message.indexOf("安全原因被暂时封") > -1) {
                dx = dx + 1
                return { "login": login_zm.message, "fhz": false }
            } else {
                dt = dt + 1
                if (dt == 10) {
                    return { "login": login_zm.message, "fhz": false }
                } else {
                    sleep(3000)
                }
                return proxz(p, w)
            }
        } else {
            cg = cg + 1
            ck = login_zm.data.ck
            var pina = ck.match(/(?<=pt_pin=)[^;]+/g)
            bucketDel("AutoJdpin", pina)
            bucketSet("who_pro_hmd", pina)
            sendText(`登录成功：${pina}\n${pro_zdyts}`)
            if (content == "账密登录" || content == "账密登陆" || content == "pro账密" || content == "密码登录") {
                pro_zm = JSON.stringify({ "account": p, "password": w, "cookie": ck, "user": UserId, "platform": imType })
                bucketSet("AutoJdck", pina, pro_zm)
                bucketSet("Autophone", pina, p)
                notifyMasters(`======JD帐密登陆通知======
[登陆用户]：${UserId}
[登陆号码]：${p}
[登陆平台]：${imType}
[登陆账户]：${pina}
[登陆时间]：${formatDate(new Date())}
[登陆方式]：账密登陆`)

            } else {
                let data = bucketGet("AutoJdck", pina)
                pin_ck = JSON.parse(data)
                pro_zm = JSON.stringify({ "account": p, "password": w, "cookie": ck, "user": pin_ck.user, "platform": pin_ck.platform })
                bucketSet("AutoJdck", pina, pro_zm)
            }
            breakIn(ck)
            return { "login": pina, "fhz": true }
        }
    } catch (e) {
        Debug(e)
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
function TXfs_tuisong(tx, qh, data) {
    //console.log(`开始推送-渠道：${tx},用户ID：${qh}，推送内容：${data}`)
    push({
        imType: tx,
        userID: qh,
        title: "",
        groupCode: "",
        content: data,
    })
}
function ShuRu(dd) {
    sendText(dd)
    var msg = input(180000, 6000)
    if (msg == "q" || msg == "Q" || msg == "") {
        // sendText("已退出会话");
        return "已退出会话"
    } else {
        return msg;
    }

}
function formatDate(date) {
    const year = date.getFullYear();
    const month = ('0' + (date.getMonth() + 1)).slice(-2);
    const day = ('0' + date.getDate()).slice(-2);
    const hours = ('0' + date.getHours()).slice(-2);
    const minutes = ('0' + date.getMinutes()).slice(-2);
    const seconds = ('0' + date.getSeconds()).slice(-2);
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}
if (content == "账密登录" || content == "账密登陆" || content == "帐密登录" || content == "帐密登陆" || content == "pro账密" || content == "密码登录") {
    var pro_qlkg = bucketGet("who_tong", "pro_qlkg")//私聊开关
    if (pro_qlkg == "false" || pro_qlkg == "" || pro_qlkg == false) {

        mian()
    } else {
        let froad = GetChatID()
        if (froad == 0 || froad == "0") {
            mian()

        } else {
            sendText(`未开启群内使用账密登录,请您私聊我操作`)

        }


    }

} else if (content == "账密黑名单刷新" || content == "帐密黑名单刷新") {
    var tongzhikaiguan = true//通知用户开关
    if (isAdmin() || imType == "croncmd") {
        hmd_mian()

    } else {

        sendText("叼毛!不要乱搞咯")



    }

} else if (content == "帐密临时刷新" || content == "账密临时刷新") {
    var tongzhikaiguan = false//通知用户开关
    if (isAdmin() || imType == "croncmd") {
        sx_mian()

    } else {

        sendText("叼毛!不要乱搞咯")



    }
} else if (content == "账密删除") {
    var ptpin = ""
    let bind = bucketKeys("pin" + imType.toUpperCase(), UserId)
    if (bind.length == 0) {
        sendText("您没有账密数据,无需删除")
    } else {
        if (bind.length == 1) {
            bucketSet("AutoJdck", bind[0])
        } else {
            ptpin += "请选择你的需要删除的账密，输入数字\n"
            for (let j = 0; j < bind.length; j++) {
                //sendText(bind[j])
                var pin_ck = bucketGet("AutoJdck", bind[j])
                if (pin_ck == "") {

                } else {
                    let phon = JSON.parse(pin_ck)
                    ptpin += `[${j + 1}] ${hideMiddlePart(decodeURIComponent(bind[j]))} [${phone(phon.account)}]\n`
                }

            }
            sendText(ptpin)
            var choice = input(30000, 1000)//表示等待用户输入，等待用户输入时间为30秒
            if (choice == 'q' || choice == "Q" || choice == '' || choice == undefined || choice == "undefined") {
                sendText('退出成功')//给会话用户发送信息
            }
            if (isNaN(choice) || choice > bind.length || choice < 0) {
                sendText('输入错误，自动退出程序')
            } else {
                bucketSet("AutoJdck", bind[choice - 1])
                sendText(`${bind[choice - 1]},删除完成`)
            }
        }

    }

} else {
    var tongzhikaiguan = true//通知用户开关
    sx_mian()
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
function phone(mobile) {
    return mobile.slice(0, 3) + '****' + mobile.slice(8)
}

function jdck(cookie) {
    for (let i = 0; i < 5; i++) {
        try {
            body = request({
                method: "post",
                url: `https://plogin.m.jd.com/cgi-bin/ml/islogin`,
                headers: {
                    "Cookie": cookie,
                    "User-Agent": UserAgents(),
                    "referer": "https://gold.jd.com/",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                dataType: "json",
                timeOut: 30000
            })
            if (body) {
                i = 9
                // body = JSON.parse(body)
                if (body.islogin == "1") {
                    return true
                } else {
                    return false
                }

            }
        } catch (e) { }
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
function isJsonString(str) {
    try {
        const obj = JSON.parse(str);
        return (typeof obj === 'object' && obj !== null);
    } catch (e) {
        return false;
    }
}
function hideMiddlePart(str, startLength = 2, endLength = 5) {
    if (str.length <= startLength + endLength) {
        return str;
    }
    const hiddenPart = `***`
    return str.substring(0, startLength) + hiddenPart + str.substring(str.length - endLength);
}

function UserAgents() {
    var USER_AGENTS = [
        "jdltapp;iPad;3.7.0;14.4;network/wifi;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;android;3.7.0;10;2346663656561603-4353564623932316;network/wifi;model/ONEPLUS A5010;addressid/0;aid/2dfceea045ed292a;oaid/;osVer/29;appBuild/1436;psn/BS6Y9SAiw0IpJ4ro7rjSOkCRZTgR3z2K|10;psq/5;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/10.5;jdv/;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/oppo;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ONEPLUS A5010 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
        "jdltapp;iPhone;3.7.0;14.1;59d6ae6e8387bd09fe046d5b8918ead51614e80a;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone12,1;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/;pv/1.26;apprpd/;ref/JDLTSubMainPageViewController;psq/0;ads/;psn/59d6ae6e8387bd09fe046d5b8918ead51614e80a|3;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.1;Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;13.5;22d679c006bf9c087abf362cf1d2e0020ebb8798;network/wifi;ADID/10857A57-DDF8-4A0D-A548-7B8F43AC77EE;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone12,1;addressid/2378947694;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/15.7;apprpd/Allowance_Registered;ref/JDLTTaskCenterViewController;psq/6;ads/;psn/22d679c006bf9c087abf362cf1d2e0020ebb8798|22;jdv/0|kong|t_1000170135|tuiguang|notset|1614153044558|1614153044;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;android;3.7.0;10;2616935633265383-5333463636261326;network/UNKNOWN;model/M2007J3SC;addressid/1840745247;aid/ba9e3b5853dccb1b;oaid/371d8af7dd71e8d5;osVer/29;appBuild/1436;psn/t7JmxZUXGkimd4f9Jdul2jEeuYLwxPrm|8;psq/6;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/5.6;jdv/;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/xiaomi;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 10; M2007J3SC Build/QKQ1.200419.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045135 Mobile Safari/537.36",
        "jdltapp;iPhone;3.7.0;14.3;d7beab54ae7758fa896c193b49470204fbb8fce9;network/4g;ADID/97AD46C9-6D49-4642-BF6F-689256673906;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;android;3.7.0;9;D246836333735-3264353430393;network/4g;model/MIX 2;addressid/138678023;aid/bf8bcf1214b3832a;oaid/308540d1f1feb2f5;osVer/28;appBuild/1436;psn/Z/rGqfWBY/h5gcGFnVIsRw==|16;psq/3;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 9;osv/9;pv/13.7;jdv/;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/xiaomi;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 9; MIX 2 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045135 Mobile Safari/537.36",
        "jdltapp;iPhone;3.7.0;14.4;eb5a9e7e596e262b4ffb3b6b5c830984c8a5c0d5;network/wifi;ADID/5603541B-30C1-4B5C-A782-20D0B569D810;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,2;addressid/1041002757;hasOCPay/0;appBuild/101;supportBestPay/0;pv/34.6;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/5;ads/;psn/eb5a9e7e596e262b4ffb3b6b5c830984c8a5c0d5|44;jdv/0|androidapp|t_335139774|appshare|CopyURL|1612612940307|1612612944;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;21631ed983b3e854a3154b0336413825ad0d6783;network/3g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,4;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.47;apprpd/;ref/JDLTSubMainPageViewController;psq/8;ads/;psn/21631ed983b3e854a3154b0336413825ad0d6783|9;jdv/0|direct|-|none|-|1614150725100|1614225882;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;13.5;500a795cb2abae60b877ee4a1930557a800bef1c;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone8,1;addressid/669949466;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/9.11;apprpd/;ref/JDLTSubMainPageViewController;psq/10;ads/;psn/500a795cb2abae60b877ee4a1930557a800bef1c|11;jdv/;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPad;3.7.0;14.4;f5e7b7980fb50efc9c294ac38653c1584846c3db;network/wifi;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPad6,3;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/231.11;pap/JA2020_3112531|3.7.0|IOS 14.4;apprpd/;psn/f5e7b7980fb50efc9c294ac38653c1584846c3db|305;usc/kong;jdv/0|kong|t_1000170135|tuiguang|notset|1613606450668|1613606450;umd/tuiguang;psq/2;ucp/t_1000170135;app_device/IOS;utr/notset;ref/JDLTRedPacketViewController;adk/;ads/;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;19fef5419f88076c43f5317eabe20121d52c6a61;network/wifi;ADID/00000000-0000-0000-0000-000000000000;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,8;addressid/3430850943;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/10.4;apprpd/;ref/JDLTSubMainPageViewController;psq/3;ads/;psn/19fef5419f88076c43f5317eabe20121d52c6a61|16;jdv/0|kong|t_1001327829_|jingfen|f51febe09dd64b20b06bc6ef4c1ad790#/|1614096460311|1614096511;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "jdltapp;iPhone;3.7.0;12.2;f995bc883282f7c7ea9d7f32da3f658127aa36c7;network/4g;ADID/9F40F4CA-EA7C-4F2E-8E09-97A66901D83E;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,4;addressid/525064695;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/11.11;apprpd/;ref/JDLTSubMainPageViewController;psq/2;ads/;psn/f995bc883282f7c7ea9d7f32da3f658127aa36c7|22;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 12.2;Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;android;3.7.0;10;5366566313931326-6633931643233693;network/wifi;model/Mi9 Pro 5G;addressid/0;aid/5fe6191bf39a42c9;oaid/e3a9473ef6699f75;osVer/29;appBuild/1436;psn/b3rJlGi AwLqa9AqX7Vp0jv4T7XPMa0o|5;psq/4;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/5.4;jdv/;ref/HomeFragment;partner/xiaomi;apprpd/Home_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; Mi9 Pro 5G Build/QKQ1.190825.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045135 Mobile Safari/537.36",
        "jdltapp;iPhone;3.7.0;14.4;4e6b46913a2e18dd06d6d69843ee4cdd8e033bc1;network/3g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,2;addressid/666624049;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/54.11;apprpd/MessageCenter_MessageMerge;ref/MessageCenterController;psq/10;ads/;psn/4e6b46913a2e18dd06d6d69843ee4cdd8e033bc1|101;jdv/0|kong|t_2010804675_|jingfen|810dab1ba2c04b8588c5aa5a0d44c4bd|1614183499;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.2;c71b599e9a0bcbd8d1ad924d85b5715530efad06;network/wifi;ADID/751C6E92-FD10-4323-B37C-187FD0CF0551;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,8;addressid/4053561885;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/263.8;apprpd/;ref/JDLTSubMainPageViewController;psq/2;ads/;psn/c71b599e9a0bcbd8d1ad924d85b5715530efad06|481;jdv/0|kong|t_1001610202_|jingfen|3911bea7ee2f4fcf8d11fdf663192bbe|1614157052210|1614157056;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.2;Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;2d306ee3cacd2c02560627a5113817ebea20a2c9;network/4g;ADID/A346F099-3182-4889-9A62-2B3C28AB861E;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,3;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/;pv/1.35;apprpd/Allowance_Registered;ref/JDLTTaskCenterViewController;psq/0;ads/;psn/2d306ee3cacd2c02560627a5113817ebea20a2c9|2;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;28355aff16cec8bcf3e5728dbbc9725656d8c2c2;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,2;addressid/833058617;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.10;apprpd/;ref/JDLTWebViewController;psq/9;ads/;psn/28355aff16cec8bcf3e5728dbbc9725656d8c2c2|5;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;13.5;24ddac73a3de1b91816b7aedef53e97c4c313733;network/4g;ADID/598C6841-76AC-4512-AA97-CBA940548D70;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone11,6;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/12.6;apprpd/;ref/JDLTSubMainPageViewController;psq/5;ads/;psn/24ddac73a3de1b91816b7aedef53e97c4c313733|23;jdv/0|kong|t_1000170135|tuiguang|notset|1614126110904|1614126110;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;d7732ba60c8ff73cc3f5ba7290a3aa9551f73a1b;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone12,1;addressid/25239372;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/8.6;apprpd/;ref/JDLTSubMainPageViewController;psq/5;ads/;psn/d7732ba60c8ff73cc3f5ba7290a3aa9551f73a1b|14;jdv/0|kong|t_1001226363_|jingfen|5713234d1e1e4893b92b2de2cb32484d|1614182989528|1614182992;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;ca1a32afca36bc9fb37fd03f18e653bce53eaca5;network/wifi;ADID/3AF380AB-CB74-4FE6-9E7C-967693863CA3;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone8,1;addressid/138323416;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/72.12;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/ca1a32afca36bc9fb37fd03f18e653bce53eaca5|109;jdv/0|kong|t_1000536212_|jingfen|c82bfa19e33a4269a5884ffc614790f4|1614141246;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;android;3.7.0;10;7346933333666353-8333366646039373;network/wifi;model/ONEPLUS A5010;addressid/138117973;aid/7d933f6583cfd097;oaid/;osVer/29;appBuild/1436;psn/T/eqfRSwp8VKEvvXyEunq09Cg2MUkiQ5|17;psq/4;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/11.4;jdv/0|kong|t_1001849073_|jingfen|495a47f6c0b8431c9d460f61ad2304dc|1614084403978|1614084407;ref/HomeFragment;partner/oppo;apprpd/Home_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ONEPLUS A5010 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
        "jdltapp;android;3.7.0;11;4626269356736353-5353236346334673;network/wifi;model/M2006J10C;addressid/0;aid/dbb9e7655526d3d7;oaid/66a7af49362987b0;osVer/30;appBuild/1436;psn/rQRQgJ 4 S3qkq8YDl28y6jkUHmI/rlX|3;psq/4;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 11;osv/11;pv/3.4;jdv/;ref/HomeFragment;partner/xiaomi;apprpd/Home_Main;eufv/1;Mozilla/5.0 (Linux; Android 11; M2006J10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045513 Mobile Safari/537.36",
        "jdltapp;iPhone;3.7.0;14.4;78fc1d919de0c8c2de15725eff508d8ab14f9c82;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,1;addressid/137829713;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/23.11;apprpd/;ref/JDLTSubMainPageViewController;psq/10;ads/;psn/78fc1d919de0c8c2de15725eff508d8ab14f9c82|34;jdv/0|iosapp|t_335139774|appshare|Wxfriends|1612508702380|1612534293;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;android;3.7.0;10;0373263343266633-5663030363465326;network/wifi;model/Redmi Note 7;addressid/590846082;aid/07b34bf3e6006d5b;oaid/17975a142e67ec92;osVer/29;appBuild/1436;psn/OHNqtdhQKv1okyh7rB3HxjwI00ixJMNG|4;psq/3;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/2.3;jdv/;ref/activityId=8a8fabf3cccb417f8e691b6774938bc2;partner/xiaomi;apprpd/jsbqd_home;eufv/1;Mozilla/5.0 (Linux; Android 10; Redmi Note 7 Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Mobile Safari/537.36",
        "jdltapp;android;3.7.0;10;3636566623663623-1693635613166646;network/wifi;model/ASUS_I001DA;addressid/1397761133;aid/ccef2fc2a96e1afd;oaid/;osVer/29;appBuild/1436;psn/T8087T0D82PHzJ4VUMGFrfB9dw4gUnKG|76;psq/5;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/73.5;jdv/0|kong|t_1002354188_|jingfen|2335e043b3344107a2750a781fde9a2e#/|1614097081426|1614097087;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/yingyongbao;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ASUS_I001DA Build/QKQ1.190825.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,2;addressid/138419019;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/5.7;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/6;ads/;psn/4ee6af0db48fd605adb69b63f00fcbb51c2fc3f0|9;jdv/0|direct|-|none|-|1613705981655|1613823229;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;network/wifi;ADID/F9FD7728-2956-4DD1-8EDD-58B07950864C;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,1;addressid/1346909722;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/30.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/40d4d4323eb3987226cae367d6b0d8be50f2c7b3|39;jdv/0|kong|t_1000252057_0|tuiguang|eba7648a0f4445aa9cfa6f35c6f36e15|1613995717959|1613995723;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;ADID/5D306F0D-A131-4B26-947E-166CCB9BFFFF;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,6;addressid/138164461;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/7.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/d40e5d4a33c100e8527f779557c347569b49c304|7;jdv/0|kong|t_1001226363_|jingfen|3bf5372cb9cd445bbb270b8bc9a34f00|1608439066693|1608439068;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPad;3.7.0;14.5;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPad8,9;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/;pv/1.20;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/5;ads/;psn/d9f5ddaa0160a20f32fb2c8bfd174fae7993c1b4|3;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.5;Mozilla/5.0 (iPad; CPU OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;network/wifi;ADID/31548A9C-8A01-469A-B148-E7D841C91FD0;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/10.5;apprpd/;ref/JDLTSubMainPageViewController;psq/4;ads/;psn/a858fb4b40e432ea32f80729916e6c3e910bb922|12;jdv/0|direct|-|none|-|1613898710373|1613898712;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;13.5;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,2;addressid/2237496805;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/13.6;apprpd/;ref/JDLTSubMainPageViewController;psq/5;ads/;psn/48e495dcf5dc398b4d46b27e9f15a2b427a154aa|15;jdv/0|direct|-|none|-|1613354874698|1613952828;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;android;3.7.0;10;3346332626262353-1666434336539336;network/wifi;model/ONEPLUS A6000;addressid/0;aid/3d3bbb25af44c59c;oaid/;osVer/29;appBuild/1436;psn/ECbc2EqmdSa7mDF1PS1GSrV/Tn7R1LS1|6;psq/8;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/2.67;jdv/0|direct|-|none|-|1613822479379|1613991194;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/oppo;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ONEPLUS A6000 Build/QKQ1.190716.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
        "jdltapp;android;3.7.0;8.1.0;8363834353530333132333132373-43D2930366035323639333662383;network/wifi;model/16th Plus;addressid/0;aid/f909e5f2c464c7c6;oaid/;osVer/27;appBuild/1436;psn/c21YWvVr77Hn6 pOZfxXGY4TZrre1 UOL5hcPbCEDMo=|3;psq/10;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 8.1.0;osv/8.1.0;pv/2.15;jdv/;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/jsxdlyqj09;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 8.1.0; 16th Plus Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045514 Mobile Safari/537.36",
        "jdltapp;android;3.7.0;11;1343467336264693-3343562673463613;network/wifi;model/Mi 10 Pro;addressid/0;aid/14d7cbd934eb7dc1;oaid/335f198546eb3141;osVer/30;appBuild/1436;psn/ZcQh/Wov sNYfZ6JUjTIUBu28 KT0T3u|1;psq/24;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 11;osv/11;pv/1.24;jdv/;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/xiaomi;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 11; Mi 10 Pro Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 Mobile Safari/537.36",
        "jdltapp;android;3.7.0;10;8353636393732346-6646931673935346;network/wifi;model/MI 8;addressid/1969998059;aid/8566972dfd9a795d;oaid/4a8b773c3e307386;osVer/29;appBuild/1436;psn/PhYbUtCsCJo r 1b8hwxjnY8rEv5S8XC|383;psq/14;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/374.14;jdv/0|iosapp|t_335139774|liteshare|CopyURL|1609306590175|1609306596;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/jsxdlyqj09;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
        "jdltapp;iPhone;3.7.0;14.4;6d343c58764a908d4fa56609da4cb3a5cc1396d3;network/wifi;ADID/4965D884-3E61-4C4E-AEA7-9A8CE3742DA7;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,1;addressid/70390480;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.24;apprpd/MyJD_Main;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fafter%2Findex.action%3FcategoryId%3D600%26v%3D6%26entry%3Dm_self_jd;psq/4;ads/;psn/6d343c58764a908d4fa56609da4cb3a5cc1396d3|17;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;13.6.1;4606ddccdfe8f343f8137de7fea7f91fc4aef3a3;network/4g;ADID/C6FB6E20-D334-45FA-818A-7A4C58305202;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone10,1;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/5.9;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/8;ads/;psn/4606ddccdfe8f343f8137de7fea7f91fc4aef3a3|5;jdv/0|iosapp|t_335139774|liteshare|Qqfriends|1614206359106|1614206366;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.6.1;Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;3b6e79334551fc6f31952d338b996789d157c4e8;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,1;addressid/138051400;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/14.34;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/12;ads/;psn/3b6e79334551fc6f31952d338b996789d157c4e8|46;jdv/0|kong|t_1001707023_|jingfen|e80d7173a4264f4c9a3addcac7da8b5d|1613837384708|1613858760;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;android;3.7.0;10;1346235693831363-2373837393932673;network/wifi;model/LYA-AL00;addressid/3321567203;aid/1d2e9816278799b7;oaid/00000000-0000-0000-0000-000000000000;osVer/29;appBuild/1436;psn/45VUZFTZJkhP5fAXbeBoQ0   O2GCB I|7;psq/5;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/5.8;jdv/0|iosapp|t_335139774|liteshare|CopyURL|1614066210320|1614066219;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/huawei;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; LYA-AL00 Build/HUAWEILYA-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36",
        "jdltapp;iPhone;3.7.0;14.3;c2a8854e622a1b17a6c56c789f832f9d78ef1ba7;network/wifi;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone12,5;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/3.9;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/8;ads/;psn/c2a8854e622a1b17a6c56c789f832f9d78ef1ba7|6;jdv/0|direct|-|none|-|1613541016735|1613823566;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;android;3.7.0;9;;network/wifi;model/MIX 2S;addressid/;aid/f87efed6d9ed3c65;oaid/94739128ef9dd245;osVer/28;appBuild/1436;psn/R7wD/OWkQjYWxax1pDV6kTIDFPJCUid7C/nl2hHnUuI=|3;psq/13;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 9;osv/9;pv/1.42;jdv/;ref/activityId=8a8fabf3cccb417f8e691b6774938bc2;partner/xiaomi;apprpd/jsbqd_home;eufv/1;Mozilla/5.0 (Linux; Android 9; MIX 2S Build/PKQ1.180729.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 Mobile Safari/537.36",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;android;3.7.0;10;network/wifi;Mozilla/5.0 (Linux; Android 10; Redmi Note 7 Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Mobile Safari/537.36",
        "jdltapp;iPhone;3.7.0;14.4;network/3g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "jdltapp;iPad;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPad6,3;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/231.11;pap/JA2020_3112531|3.7.0|IOS 14.4;apprpd/;psn/f5e7b7980fb50efc9c294ac38653c1584846c3db|305;usc/kong;jdv/0|kong|t_1000170135|tuiguang|notset|1613606450668|1613606450;umd/tuiguang;psq/2;ucp/t_1000170135;app_device/IOS;utr/notset;ref/JDLTRedPacketViewController;adk/;ads/;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;13.5;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone8,1;addressid/669949466;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/9.11;apprpd/;ref/JDLTSubMainPageViewController;psq/10;ads/;psn/500a795cb2abae60b877ee4a1930557a800bef1c|11;jdv/;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;network/3g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,4;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.47;apprpd/;ref/JDLTSubMainPageViewController;psq/8;ads/;psn/21631ed983b3e854a3154b0336413825ad0d6783|9;jdv/0|direct|-|none|-|1614150725100|1614225882;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;network/3g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,4;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.47;apprpd/;ref/JDLTSubMainPageViewController;psq/8;ads/;psn/21631ed983b3e854a3154b0336413825ad0d6783|9;jdv/0|direct|-|none|-|1614150725100|1614225882;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/3.15;apprpd/;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fchat%2Findex.action%3Fentry%3Djd_m_JiSuCommodity%26pid%3D7763388%26lng%3D118.159665%26lat%3D24.504633%26sid%3D31cddc2d58f6e36bf2c31c4e8a79767w%26un_area%3D16_1315_3486_0;psq/12;ads/;psn/c10e0db6f15dec57a94637365f4c3d43e05bbd48|4;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/3.15;apprpd/;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fchat%2Findex.action%3Fentry%3Djd_m_JiSuCommodity%26pid%3D7763388%26lng%3D118.159665%26lat%3D24.504633%26sid%3D31cddc2d58f6e36bf2c31c4e8a79767w%26un_area%3D16_1315_3486_0;psq/12;ads/;psn/c10e0db6f15dec57a94637365f4c3d43e05bbd48|4;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/3.15;apprpd/;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fchat%2Findex.action%3Fentry%3Djd_m_JiSuCommodity%26pid%3D7763388%26lng%3D118.159665%26lat%3D24.504633%26sid%3D31cddc2d58f6e36bf2c31c4e8a79767w%26un_area%3D16_1315_3486_0;psq/12;ads/;psn/c10e0db6f15dec57a94637365f4c3d43e05bbd48|4;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,6;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/2813715704;pv/67.38;apprpd/MyJD_Main;ref/https%3A%2F%2Fh5.m.jd.com%2FbabelDiy%2FZeus%2F2ynE8QDtc2svd36VowmYWBzzDdK6%2Findex.html%3Flng%3D103.957532%26lat%3D30.626962%26sid%3D4fe8ef4283b24723a7bb30ee87c18b2w%26un_area%3D22_1930_49324_52512;psq/4;ads/;psn/5aef178f95931bdbbde849ea9e2fc62b18bc5829|127;jdv/0|direct|-|none|-|1612588090667|1613822580;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone12,1;addressid/3104834020;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.6;apprpd/;ref/JDLTSubMainPageViewController;psq/5;ads/;psn/c633e62b5a4ad0fdd93d9862bdcacfa8f3ecef63|6;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,1;addressid/1346909722;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/30.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/40d4d4323eb3987226cae367d6b0d8be50f2c7b3|39;jdv/0|kong|t_1000252057_0|tuiguang|eba7648a0f4445aa9cfa6f35c6f36e15|1613995717959|1613995723;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.3;network/wifi;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,1;addressid/1346909722;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/30.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/40d4d4323eb3987226cae367d6b0d8be50f2c7b3|39;jdv/0|kong|t_1000252057_0|tuiguang|eba7648a0f4445aa9cfa6f35c6f36e15|1613995717959|1613995723;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,6;addressid/138164461;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/7.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/d40e5d4a33c100e8527f779557c347569b49c304|7;jdv/0|kong|t_1001226363_|jingfen|3bf5372cb9cd445bbb270b8bc9a34f00|1608439066693|1608439068;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,6;addressid/138164461;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/7.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/d40e5d4a33c100e8527f779557c347569b49c304|7;jdv/0|kong|t_1001226363_|jingfen|3bf5372cb9cd445bbb270b8bc9a34f00|1608439066693|1608439068;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,6;addressid/138164461;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/7.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/d40e5d4a33c100e8527f779557c347569b49c304|7;jdv/0|kong|t_1001226363_|jingfen|3bf5372cb9cd445bbb270b8bc9a34f00|1608439066693|1608439068;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;13.5;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,2;addressid/2237496805;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/13.6;apprpd/;ref/JDLTSubMainPageViewController;psq/5;ads/;psn/48e495dcf5dc398b4d46b27e9f15a2b427a154aa|15;jdv/0|direct|-|none|-|1613354874698|1613952828;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;android;3.7.0;10;network/wifi;model/ONEPLUS A6000;addressid/0;aid/3d3bbb25af44c59c;oaid/;osVer/29;appBuild/1436;psn/ECbc2EqmdSa7mDF1PS1GSrV/Tn7R1LS1|6;psq/8;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/2.67;jdv/0|direct|-|none|-|1613822479379|1613991194;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/oppo;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ONEPLUS A6000 Build/QKQ1.190716.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
        "jdltapp;android;3.7.0;8.1.0;network/wifi;model/16th Plus;addressid/0;aid/f909e5f2c464c7c6;oaid/;osVer/27;appBuild/1436;psn/c21YWvVr77Hn6 pOZfxXGY4TZrre1 UOL5hcPbCEDMo=|3;psq/10;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 8.1.0;osv/8.1.0;pv/2.15;jdv/;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/jsxdlyqj09;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 8.1.0; 16th Plus Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045514 Mobile Safari/537.36",
        "jdltapp;android;3.7.0;11;network/wifi;model/Mi 10 Pro;addressid/0;aid/14d7cbd934eb7dc1;oaid/335f198546eb3141;osVer/30;appBuild/1436;psn/ZcQh/Wov sNYfZ6JUjTIUBu28 KT0T3u|1;psq/24;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 11;osv/11;pv/1.24;jdv/;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/xiaomi;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 11; Mi 10 Pro Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 Mobile Safari/537.36",
        "jdltapp;android;3.7.0;10;network/wifi;model/MI 8;addressid/1969998059;aid/8566972dfd9a795d;oaid/4a8b773c3e307386;osVer/29;appBuild/1436;psn/PhYbUtCsCJo r 1b8hwxjnY8rEv5S8XC|383;psq/14;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/374.14;jdv/0|iosapp|t_335139774|liteshare|CopyURL|1609306590175|1609306596;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/jsxdlyqj09;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone8,4;addressid/1477231693;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/21.15;apprpd/MyJD_Main;ref/https%3A%2F%2Fgold.jd.com%2F%3Flng%3D0.000000%26lat%3D0.000000%26sid%3D4584eb84dc00141b0d58e000583a338w%26un_area%3D19_1607_3155_62114;psq/0;ads/;psn/2c822e59db319590266cc83b78c4a943783d0077|46;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,1;addressid/70390480;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.24;apprpd/MyJD_Main;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fafter%2Findex.action%3FcategoryId%3D600%26v%3D6%26entry%3Dm_self_jd;psq/4;ads/;psn/6d343c58764a908d4fa56609da4cb3a5cc1396d3|17;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,1;addressid/70390480;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.24;apprpd/MyJD_Main;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fafter%2Findex.action%3FcategoryId%3D600%26v%3D6%26entry%3Dm_self_jd;psq/4;ads/;psn/6d343c58764a908d4fa56609da4cb3a5cc1396d3|17;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,1;addressid/70390480;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.24;apprpd/MyJD_Main;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fafter%2Findex.action%3FcategoryId%3D600%26v%3D6%26entry%3Dm_self_jd;psq/4;ads/;psn/6d343c58764a908d4fa56609da4cb3a5cc1396d3|17;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,1;addressid/70390480;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.24;apprpd/MyJD_Main;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fafter%2Findex.action%3FcategoryId%3D600%26v%3D6%26entry%3Dm_self_jd;psq/4;ads/;psn/6d343c58764a908d4fa56609da4cb3a5cc1396d3|17;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPhone;3.7.0;14.4;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone12,3;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/;pv/3.49;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/7;ads/;psn/9e0e0ea9c6801dfd53f2e50ffaa7f84c7b40cd15|6;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        "jdltapp;iPad;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPad7,5;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.14;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/3;ads/;psn/956c074c769cd2eeab2e36fca24ad4c9e469751a|8;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    ]
    return USER_AGENTS[parseInt(Math.random() * USER_AGENTS.length)]
}
function WB_TS(tx, qh, data) {
    console.log(`开始推送-渠道：${tx},用户ID：${qh}，推送内容：${data}`)
    push({
        imType: tx,
        userID: qh,
        groupCode: "",
        content: data,
    });
}
