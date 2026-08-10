//[disable:false]
//[author: qingge] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]
//[public: true] 
//[icon: http://www.icosky.com/icon/png/System/Boomy/Group+of+users.png]
//[price: 188] 
//[version: 1.0.0] 
//[admin: false] 
//[platform: qq,wx,tg,wb,qb]
//[priority: 9999999999]
//[service: 97393412]
//[description: 数据适配作者[specter]的数据<br/>自动化账密登录功能，适配了一个第三方的自动化登录接口，使用前需要在插件云配置中设置接口地址<br/>增加自动绑定渠道以及记录账密数据<br/>6.7 增加支持其他根据推送失效PIN进行自动账密登录刷新]

//[rule:^自动(帐密|账密|帐密登陆|帐密登录|重置|查询)$]
//[rule:^帐密(登陆|登录)$]
//[rule:^账密(登陆|登录)$]
//[rule:^账密添加+([\s\S]+)$]
// [param: {"required":true,"key":"who_tong.zdh_host","placeholder":"phone接口地址","name":"BBK.接口","desc":"http://192.168.3.154:8000,后面不要带/"}]
// [param: {"required":true,"key":"who_tong.bbk_qly","placeholder":"容器名称","name":"源青龙名称","desc":"获取名方法:奥特曼后台-容器管理--对接容器--名称"}]
// [param: {"required":true,"key":"who_tong.zdh_msg","placeholder":"登陆成功提示","name":"源青龙名称","desc":"自定义通知消息内容，默认为：登录成功..，如果接口有特殊提示需要通知用户，可以在这里自定义提示消息"}]

let userId = GetUserID();//获取用户ID
var GetContent = GetContent()
var imType = ImType()
var checkJS = false
let containerEnv = [];


var zmqly = bucketGet("who_tong", "bbk_qly")//青龙
try {
    importJs("qinglong.js");
    importJs("who-hs.js");
} catch (err) {
    checkJS = true
}
const config = getConfig();

function getConfig() {
    return {
        qlName: bucketGet("who_tong", "bbk_qly") || "",
        dx_host: bucketGet("who_tong", "zdh_host") || "",
        zdh_msg: bucketGet("who_tong", "zdh_msg") || "登录成功..",
    };
}
function ql_cookie() {
    if (!config.qlName) {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置");
        return;
    }
    console.log("当前配置的青龙名称:" + config.qlName)
    const containerData = qls(config.qlName);
    if (!containerData) {
        notifyMasters("未找到对应的青龙容器，请检查青龙名称是否正确");
        return;
    }
    Debug(`指定获取青龙容器名称:${config.qlName}`);
    try {
        container = Qinglong(
            containerData.host,
            containerData.client_id,
            containerData.client_secret
        );
        containerEnv = container.ApiQL("envs", "", "get", "").data || [];
    } catch (e) {
        notifyMasters("【今日京豆排名】链接容器【" + config.qlName + "】失败，请检查配置是否正确或网络是否正常");
        return;
    }
}
function asse(text) {
    get_tx(text)
    let choice = input(180000, 1000)//表示等待用户输入，等待用户输入时间为30秒
    if (choice == 'q') {
        get_tx('退出成功')//给会话用户发送信息
        return false
    }
    if (choice == '') {
        get_tx('输入超时，自动退出程序')
        return false
    }

    // get_tx(choice)
    return choice
}
function getCaption(obj, text) {
    let index = obj.lastIndexOf(text) + text.length - 1;

    obj = obj.substring(index + 1, obj.length);
    return obj;
}
function jdck(cookie) {
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
            // body = JSON.parse(body)
            console.log(JSON.stringify(body))
            if (body.islogin == "0") {
                return false
            } else {
                return true
            }
        }
    } catch (e) { return true }
}

function mian() {


    bind = bucketKeys("pin" + imType.toUpperCase(), userId)
    if (bind.length == 0) {
        //get_tx("没有与你绑定的账号，请你先登录")
        p = asse("输入您绑定[JD]的手机号.......")
        if (p == false) {
            return
        } else {
            w = asse("输入您[JD]的登录密码")
            if (w == false) {
                return
            } else {
                pin = phone(p)
            }
        }

    } else {
        ql_cookie()
        var ptpin = ""
        ptpin += "请选择你的操作，输入数字\n[0] 新增账号\n"
        let dat = 0
        for (let j = 0; j < bind.length; j++) {
            //get_tx(bind[j])
            var pin_ck = bucketGet("AutoJdck", bind[j])

            if (pin_ck == "") {
                //get_tx("没有存在")
                const cookieObj = getAllCookies(containerEnv);
                for (let i = 0; i < cookieObj.length; i++) {
                    const cookie = cookieObj[i].value;
                    const pin = getPin(cookie);
                    //if (cookieObj[j].status !== 0) continue;
                    if (bind[j] === pin) {
                        //sendText(`正在验证账号[${decodeURIComponent(bind[j])}]的登录状态...`)
                        var jc_ck = jdck(cookie)
                        if (jc_ck) {
                            var CK_ZTID = `有效\n`
                        } else {
                            var CK_ZTID = `失效\n`
                        }
                        break;
                    }
                }
                ptpin += `[${j + 1}] ${hideMiddlePart(decodeURIComponent(bind[j]))} [未使用过] ${CK_ZTID}\n`
                dat = dat + 1
            } else {
                let phon = JSON.parse(pin_ck)
                let jnStr = bucketGet("jdNotify", bind[j])
                if (jnStr == "") {
                    var CK_ZTID = "未登录\n"
                } else {

                    const cookieObj = getAllCookies(containerEnv);
                    for (let i = 0; i < cookieObj.length; i++) {
                        const cookie = cookieObj[i].value;
                        const pin = getPin(cookie);
                        //if (cookieObj[j].status !== 0) continue;
                        if (bind[j] === pin) {
                            //sendText(`正在验证账号[${decodeURIComponent(bind[j])}]的登录状态...`)
                            var jc_ck = jdck(cookie)
                            if (jc_ck) {
                                var CK_ZTID = `有效\n`
                            } else {
                                var CK_ZTID = `失效\n`
                            }
                            break;
                        }
                    }
                }

                dat = dat + 1
                ptpin += `[${j + 1}] ${hideMiddlePart(decodeURIComponent(bind[j]))} [${phone(phon.account)}] ${CK_ZTID}\n`

            }
        }
        if (dat == 0) {
            p = asse("输入您绑定[JD]的手机号..")
            if (p == false) {
                return
            } else {
                w = asse("输入您[JD]的登录密码...")
                if (w == false) {
                    return
                } else {
                    //get_tx("开始登录验证..")
                    pin = phone(p)
                }
            }

        } else {
            get_tx(ptpin + "\n---------------\n如果账号有效则不需要再次登陆更新\n-->输入q退出")
            let choice = input(30000, 1000)//表示等待用户输入，等待用户输入时间为30秒
            if (choice == 'q') {
                get_tx('退出成功')//给会话用户发送信息
                return
            }
            if (choice == '') {
                get_tx('输入超时，自动退出程序')
                return
            }
            if (isNaN(choice) || choice > bind.length || choice < 0) {
                get_tx('输入错误，自动退出程序')
                return

            }
            if (choice == 0) {
                //get_tx("输入您的手机号")
                p = asse("输入您绑定[JD]的手机号")
                if (p == false) {
                    return
                } else {
                    w = asse("输入您[JD]的登录密码")
                    if (w == false) {
                        return
                    } else {
                        //get_tx(`${p}-${w}`)
                        // get_tx("开始登录验证..")
                        pin = phone(p)
                    }
                }
            } else {
                get_tx("您选择的账号:" + decodeURIComponent(bind[choice - 1]) + "\n开始登录验证..")

                var jnStr = bucketGet("jdNotify", bind[choice - 1])
                jn = JSON.parse(jnStr)
                cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                let jc_ck = jdck(cookie)
                if (jc_ck) {
                    get_tx(`当前账号[${decodeURIComponent(bind[choice - 1])}]有效,无需登录`)
                    return
                }
                var pin_ck = bucketGet("AutoJdck", bind[choice - 1])
                if (pin_ck == "") {
                    p = asse("输入您绑定[JD]的手机号...")
                    if (p == false) {
                        return
                    } else {
                        w = asse("输入您[JD]的登录密码..")
                        if (w == false) {
                            return
                        } else {
                            //get_tx(`${p}-${w}`)
                            // get_tx("开始登录验证..")
                            //pin = phone(p)
                            let data = JSON.stringify({ "account": p, "password": w, "cookie": "", "user": userId, "platform": imType })
                            bucketSet("AutoJdck", bind[choice - 1], data)
                        }
                    }
                } else {
                    pin_ck = JSON.parse(pin_ck)
                    p = pin_ck.account
                    w = pin_ck.password

                }
                pin = bind[choice - 1]

            }
        }



    }
    write_phone(p, w, 0)
    get_tx(`开始登录验证..${decodeURIComponent(pin)}\n请不要走开，正在为您自动登录...`)
    sleep(20 * 1000)
    // get_tx("正在登录状态...")
    if (send_status(p)) {
        //bucketSet("AutoJdck", ck_pin, data)
        login_status(p, w)
        delete_phone(p)
    }

}
//写入手机号-密码
function write_phone(phone, pward, sx) {
    for (let j = 0; j < 5; j++) {
        try {
            body = request({
                method: "get",
                url: `${config.dx_host}/phone/write?phone=${phone}&password=${pward}&sx=${sx}`,
                headers: {},
                dataType: "json",
                timeOut: 30000
            })
            if (body) {
                // body = JSON.parse(body)
                console.log(JSON.stringify(body))
                if (body.code == 0) {
                    //get_tx("账号密码写入成功")
                    j = 999
                }
            }
        } catch (e) { }
    }
}
//写入验证码
function write_code(phone, code) {
    for (let j = 0; j < 5; j++) {
        try {
            body = request({
                method: "get",
                url: `${config.dx_host}/code/write?phone=${phone}&code=${code}`,
                headers: {},
                dataType: "json",
                timeOut: 30000
            })
            if (body) {
                // body = JSON.parse(body)
                console.log(JSON.stringify(body))
                if (body.code == 0) {
                    //get_tx("验证码写入成功")
                    j = 999
                }
            }
        } catch (e) { }
    }
}

//获取号码
function get_phone() {
    // notifyMasters(config.dx_host)
    for (let j = 0; j < 5; j++) {
        //try {
        let body = request({
            method: "get",
            url: `${config.dx_host}/phone/list`,
            headers: {
                accept: "application/json"
            },
            dataType: "json",
            timeOut: 30000
        })
        if (body) {

            // body = JSON.parse(body)
            if (body.数据总数 == 0) {
                //get_tx("验证码写入成功")
                j = 999
                return true
            } else {
                return false
            }
        }
        //  } catch (e) { }
    }
}
//是否发短信成功
function send_statug(phone) {
    let name_code = false
    for (let j = 0; j < 120; j++) {
        try {
            body = request({
                method: "get",
                url: `${config.dx_host}/code/send_status/${phone}`,
                headers: {},
                dataType: "json",
                timeOut: 30000
            })
            if (body) {
                // body = JSON.parse(body)
                // console.log(JSON.stringify(body))
                if (body.code == 0 && body.data.tips == "短信发送成功") {
                    code = asse(`${yc_phone(phone)},收到验证码请在120秒内输入验证码\n如果你刚才发过，请重新发送验证码\n输入q退出`)
                    if (code == false) {

                        return
                    } else {
                        get_tx(`您输入的验证码是:${code}\n正在为您自动登录...`)
                        write_code(phone, code)
                    }
                    j = 999
                    return true
                } else if (body.code == 0 && body.data.tips == "登陆成功") {
                    // get_tx("登录成功..")
                    j = 999
                    return true
                } else if (body.code == 0 && body.data.tips == "准备验证") {
                    console.log("准备验证中...请不要走开，正在为您自动登录...")
                    if (name_code) {
                        get_tx("准备验证中...请不要走开，正在为您自动登录...")
                        name_code = false
                    }
                    sleep(3000)
                } else if (body.code == 0 && body.data.tips == "登录超时") {
                    get_tx(`${yc_phone(phone)},登录超时，请您重新发送：账密登录`)

                    j = 999
                    return false
                } else if (body.code == 0 && body.data.tips == "密码错误") {
                    get_tx(`${yc_phone(phone)},密码错误，请确认密码后,重新发送指令操作`)

                    j = 999
                    return false
                } else if (body.code == 0 && body.data.tips == "人脸认证") {
                    get_tx(`${yc_phone(phone)},出现人脸认证\n请您先使用【京东】APP验证码登录,并完成人脸认证后\n再使用自动登录功能,发送：账密登录`)
                    j = 999
                    return false
                } else if (body.code == 404) {
                    console.warn("还没获取到验证码,继续轮询")
                    sleep(3000)
                } else {
                    console.warn("还没获取到验证码,继续轮询")
                    sleep(3000)
                }
            }
        } catch (e) { }
    }
}

//是否发短信成功
function send_status(phone) {
    let name_code = false
    for (let j = 0; j < 120; j++) {
        try {
            body = request({
                method: "get",
                url: `${config.dx_host}/code/send_status/${phone}`,
                headers: {},
                dataType: "json",
                timeOut: 30000
            })
            if (body) {
                // body = JSON.parse(body)
                // console.log(JSON.stringify(body))
                if (body.code == 0 && body.data.status == "202") {
                    code = asse(`${yc_phone(phone)}\n${body.data.tips}\n请在120秒内输入内容\n如果你刚才发过，请重新发\n输入q退出`)
                    if (code == false) {

                        return
                    } else {
                        get_tx(`您输入的验证码是:${code}\n正在为您自动登录...`)
                        write_code(phone, code)
                    }
                    j = 999
                    return 202
                } else if (body.code == 0 && body.data.status == "200") {
                    // get_tx("登录成功..")
                    j = 999
                    return 200
                } else if (body.code == 0 && body.data.status == "201") {
                    console.log("准备验证中...请不要走开，正在为您自动登录...")
                    if (name_code) {
                        get_tx("准备验证中...请不要走开，正在为您自动登录...")
                        name_code = 201
                    }
                    sleep(3000)
                } else if (body.code == 0 && body.data.status == "408") {
                    get_tx(`${yc_phone(phone)},登录超时，请您重新发送：账密登录`)

                    j = 999
                    return 408
                } else if (body.code == 0 && body.data.status == "400") {
                    get_tx(`${yc_phone(phone)},密码错误，请确认密码后,重新发送指令操作`)

                    j = 999
                    return 400
                } else if (body.code == 0 && body.data.status == "500") {
                    get_tx(`${yc_phone(phone)},出现人脸认证\n请您先使用【京东】APP验证码登录,并完成人脸认证后\n再使用自动登录功能,发送：账密登录`)
                    j = 999
                    return 500
                } else if (body.code == 404) {
                    console.warn("还没获取到验证码,继续轮询")
                    sleep(3000)
                } else {
                    console.warn("还没获取到验证码,继续轮询")
                    sleep(3000)
                }
            }
        } catch (e) { }
    }
}
function yc_phone(mobile) {
    return mobile.slice(0, 3) + '***' + mobile.slice(7)
}
//登录状态
function login_status(phone, word) {
    for (let j = 0; j < 90; j++) {
        try {
            body = request({
                method: "get",
                url: `${config.dx_host}/login/status/${phone}`,
                headers: {},
                dataType: "json",
                timeOut: 30000
            })
            if (body) {
                // body = JSON.parse(body)
                console.log(JSON.stringify(body))
                if (body.code == 200 && body.data.login_state) {
                    if (body.data.user_ck && body.data.user_ck !== "") {

                        let Cookie = body.data.user_ck
                        //sendText("登录成功，正在为您保存账号信息..." + Cookie)
                        let pina = Cookie.match(/(?<=pwdt_id=)[^;]+/g)
                        bucketSet("AutoJdck", pina, JSON.stringify({ "account": phone, "password": word, "cookie": "", "user": userId, "platform": imType }))
                        bucketSet("pin" + imType.toUpperCase(), pina, userId)
                        bucketSet("AutoJdphone", pina, userId)
                    }
                    if (config.zdh_msg && config.zdh_msg !== "") {
                        get_tx(`恭喜用户上车成功[${decodeURIComponent(phone)}]\n${config.zdh_msg}`)
                    } else {
                        get_tx(`恭喜用户上车成功[${decodeURIComponent(phone)}]`)
                    }
                    j = 999
                } else if (body.code == 404) {
                    console.warn(body.message + ",404,继续轮询")
                    sleep(3000)
                } else {
                    console.warn(body.message)
                    sleep(3000)
                }
            } else {
                sleep(3000)
            }

        } catch (e) { }
    }
}
//清除接口数据
function clear_status() {
    for (let j = 0; j < 5; j++) {
        try {
            body = request({
                method: "get",
                url: `${config.dx_host}/clear`,
                headers: {},
                dataType: "json",
                timeOut: 30000
            })
            if (body) {
                // body = JSON.parse(body)
                // console.log(JSON.stringify(body))
                if (body.code == 0) {
                    sendText("正在重置自动化登录接口数据...")

                    j = 999
                }
            }
        } catch (e) { }
    }
}
function list_status() {
    console.log("正在查询接口数据..." + config.dx_host)
    for (let j = 0; j < 5; j++) {
        try {
            body = request({
                method: "get",
                url: `${config.dx_host}/phone/list`,
                headers: {},
                dataType: "json",
                timeOut: 30000
            })
            if (body) {
                // body = JSON.parse(body)
                console.log(JSON.stringify(body))
                if (body.code == 0) {
                    get_tx(`当前接口数据：\n队列账密: ${body.数据总数} 条\n等待刷新: ${body.空闲账号数} 条\n正在刷新: ${body.运行中账号数} 条`)

                    j = 999
                }
            }
        } catch (e) { }
    }
}
//写入手机号-密码
function delete_phone(phone) {
    for (let j = 0; j < 5; j++) {
        try {
            body = request({
                method: "get",
                url: `${config.dx_host}/phone/delete_all/${phone}`,
                headers: {},
                dataType: "json",
                timeOut: 30000
            })
            if (body) {
                // body = JSON.parse(body)
                console.log(JSON.stringify(body))
                if (body.code == 0) {
                    //get_tx("账号密码写入成功")
                    j = 999
                }
            }
        } catch (e) { }
    }
}

if (GetContent == "自动重置") {
    if (isAdmin() || imType == "croncmd") {
        clear_status()
    } else {
        get_tx("叼毛!不要乱搞咯")
        
    }

    

} else if (GetContent == "自动查询" || GetContent == "自动查询") {
    if (isAdmin() || imType == "croncmd") {
        list_status()
    } else {
        get_tx("叼毛!不要乱搞咯")
        
    }
    
} else {
    console.log("..")
    if (GetContent.indexOf("登陆") != -1 || GetContent.indexOf("登录") != -1 || GetContent.indexOf("自动帐密") != -1 || GetContent.indexOf("自动账密") != -1) {
        mian()
    } else {
        console.log("正在验证登录状态..." + GetContent)
        let password = getCaption(GetContent, '+');
        //get_tx("正在验证登录状态..." + password)

        let phone = bucketGet("AutoJdck", password)
        console.log(phone)
        if (!phone) {
            console.log("未找到手机号")
        } else {
            console.log("找到手机号了")
            pin_ck = JSON.parse(phone);
            console.log(pin_ck.account)
            console.log(pin_ck.password)
            write_phone(pin_ck.account, pin_ck.password, 1)
        }
    }
}