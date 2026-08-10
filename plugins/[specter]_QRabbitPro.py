//[pin:true]
//[disable:false]
//[title: QRabbitPro]
//[rule: 扫码] 匹配规则，多个规则时向下依次写多个
//[rule: 短信] 匹配规则，多个规则时向下依次写多个
//[rule: 口令] 匹配规则，多个规则时向下依次写多个
//[rule: 账密] 匹配规则，多个规则时向下依次写多个
//[rule: 登录] 匹配规则，多个规则时向下依次写多个
//[rule: 登陆] 匹配规则，多个规则时向下依次写多个
//[rule: 兔子检测] 匹配规则，多个规则时向下依次写多个
//[icon: https://pic.ziyuan.wang/2023/12/10/guest_77c52d3e94aa7.png]图标链接地址，支持http和https
//[author: specter]作者,可以自定义，不定义的话，上传时会增加为aut云注册的用户名,收费插件一定要填写aut云账号
//[version: 1.5.1] 版本格式：1.0.0，不定义的话，上传时会自动增加此头注，默认为1.0.0 
//[class: 工具类]建议从工具类、查询类、娱乐类、餐饮类、影音类、生活类、图片类、游戏类等中选择，也可自定义
//[platform: qq,wx,tg]适用的平台 qq\wx\tg\wxmp之间选择，中间用英文逗号隔开
//[public: true] 是否公开发布？值为true 或 false，不定义的话，上传aut云时会自动设置为true
//[price: 0] 上架价格
//[service: 2607401955]售后联系方式，service不完整，将不会审核上架
//[description: QRabbitPro扫码、短信、口令。<br>指令：登录，登陆，短信，扫码，口令，账密，兔子检测。发送兔子检测自动检测并更换可用反代，支持设置插件定时自动更换。插件需要打开权限:cloud数据,jdNotify数据,qls数据。<br>更新日志(支持联动【QRabbitPro账密】,【京东账密】,【BBK账密】,【鹿飞账密协议版】插件，需要先下载对应插件) <br>] 使用方法尽量写具体
//[priority: 9999] 优先级，数字越大表示优先级越高
//[param: {"required":true,"key":"QRabbitPro.QRabbitPro_url","bool":false,"placeholder":"输入兔子地址","name":"地址","desc":"输入兔子地址"}]
//[param: {"required":true,"key":"QRabbitPro.QRabbitPro_username","bool":false,"placeholder":"输入兔子面板管理员账号，确保填写的账号能正常登陆兔子后台面板！","name":"账号","desc":"输入兔子面板管理员账号"}]
//[param: {"required":true,"key":"QRabbitPro.QRabbitPro_password","bool":false,"placeholder":"输入兔子面板管理员密码，确保填写的密码能正常登陆兔子后台面板！","name":"密码","desc":"输入兔子面板管理员密码"}]
//[param: {"required":true,"key":"QRabbitPro.closePush","bool":true,"placeholder":"是否关闭详细登陆日志推送","name":"详细推送","desc":"是否关闭详细登陆日志推送"}]
//[param: {"required":true,"key":"QRabbitPro.jdqr","bool":true,"placeholder":"是否开启扫码","name":"扫码","desc":"是否开启扫码"}]
//[param: {"required":true,"key":"QRabbitPro.kouling","bool":true,"placeholder":"是否开启口令","name":"口令","desc":"是否开启口令"}]
//[param: {"required":true,"key":"QRabbitPro.jdsms","bool":true,"placeholder":"是否开启短信","name":"短信","desc":"是否开启短信"}]
//[param: {"required":true,"key":"QRabbitPro.useQRabbitPro","bool":true,"placeholder":"开启QRabbitPro账密","name":"开启QRabbitPro账密","desc":"开启QRabbitPro账密,需要先下载QRabbitPro账密插件，并给QRabbitPro插件打开qls权限"}]
//[param: {"required":true,"key":"QRabbitPro.jdaccount","bool":true,"placeholder":"开启无头账密","name":"开启无头账密","desc":"开启无头账密,需要先下载京东账密插件"}]
//[param: {"required":true,"key":"QRabbitPro.useBBK","bool":true,"placeholder":"开启BBK账密","name":"开启BBK账密","desc":"开启BBK账密，需要先下载BBK账密插件"}]
//[param: {"required":true,"key":"QRabbitPro.useLufei","bool":true,"placeholder":"开启鹿飞账密","name":"开启鹿飞账密","desc":"开启鹿飞账密，需要先下载鹿飞账密协议版插件"}]
//[param: {"required":true,"key":"QRabbitPro.reminder","bool":false,"placeholder":"温馨提示","name":"温馨提示","desc":"登陆菜单尾巴。"}]


let url = '';
let BotApiToken = '';
// 以下内容不要动
let num = "";
let code = "";
var uid = "";
let select = "";
let token = "";
var tongzi = "QRabbitPro";
var container_id = ''
let userId = GetUserID()
var platform = GetImType()
var Content = GetContent()
var Admin = isAdmin();

if (!bucketGet(tongzi, "container_id")) {
    bucketSet(tongzi, "container_id", 'switch');
}

const useQRabbitPro = bucketGet(tongzi, 'useQRabbitPro');
const jdaccount = bucketGet(tongzi, 'jdaccount');
const useBBK = bucketGet(tongzi, 'useBBK');
const useLufei = bucketGet(tongzi, 'useLufei');

const isAccount = jdaccount === 'true' || useBBK === 'true' || useLufei === 'true' || useQRabbitPro === 'true';

if (isAccount) {
    let isimport = true;

    try {
        if (useQRabbitPro === 'true') {
            importJs("specter:QRabbitPro账密.js");
        } else if (useBBK === 'true') {
            importJs("specter:BBK账密.js");
        } else if (useLufei === 'true') {
            importJs("specter:鹿飞账密协议版.js");
        } else {
            importJs("specter:京东账密.js");
        }
        main();
    } catch (error) {
        Debug(error);
        isimport = false;
    }

    if (!isimport) {
        try {
            if (useQRabbitPro === 'true') {
                importJs("QRabbitPro账密.js");
            } else if (useBBK === 'true') {
                importJs("BBK账密.js");
            } else if (useLufei === 'true') {
                importJs("鹿飞账密协议版.js");
            } else {
                importJs("京东账密.js");
            }
            main();
        } catch (e) {
            notifyMasters(e);
            notifyMasters("未安装所需账密插件，请前往订阅源specter安装");
            main();
        }
    }
} else {
    main();
}

// Main 入口
function main() {
    var ispeizhi = bucketGet(tongzi, "IsPeiZhi");
    Debug(Content)
    if (Content == '兔子检测' && isAdmin()) {
        rabbitTest()
        return
    } else if (Content == '') {
        rabbitTest()
        return
    }
    try {
        let isURL = bucketGet(tongzi, 'QRabbitPro_url')
        if (isURL) {
            bucketSet(tongzi, "IsPeiZhi", "true");
            ispeizhi = 'true'
        }
    } catch (error) {

    }
    if (ispeizhi == "false" || ispeizhi == "") {
        if (isAdmin()) {
            try {
                const messages = [
                    "请告知我你的QRabbitPro登录地址，示例：http://123.123.123.123:5702",
                    "请告知我你的QRabbitPro的管理员账号",
                    "请告知我你的QRabbitPro的管理员密码",
                    "请告知我是否开启京东扫码登录(开启输入true，关闭输入false)",
                    "请告知我是否开启口令登录(开启输入true，关闭输入false)",
                    "请告知我是否开启短信登录(开启输入true，关闭输入false)",
                    "请告知我是否开启账密登录(开启输入true，关闭输入false)",
                ];
                const answers = [];

                for (const message of messages) {
                    sendText(message);
                    const answer = ShuRu();
                    if (!answer) {
                        return false;
                    }
                    answers.push(answer);
                }

                bucketSet(tongzi, "QRabbitPro_url", answers[0]);
                bucketSet(tongzi, "QRabbitPro_username", answers[1]);
                bucketSet(tongzi, "QRabbitPro_password", answers[2]);
                bucketSet(tongzi, "jdqr", answers[3]);
                bucketSet(tongzi, "kouling", answers[4]);
                bucketSet(tongzi, "jdsms", answers[5]);
                bucketSet(tongzi, "jdaccount", answers[6]);
                // bucketSet(tongzi, "BotApiToken", answers[4]);

                url = bucketGet(tongzi, 'QRabbitPro_url')
                if (url[url.length - 1] == '/') {
                    url = url.substring(0, url.length - 1);
                }
                if (getql()) {
                    sendText("配置成功。");
                    bucketSet(tongzi, "IsPeiZhi", "true");
                }
                return
            } catch {
                sendText("配置出现问题，请检查并重新配置！");
                bucketSet(tongzi, "IsPeiZhi", "false");
            }
        } else {
            sendText("当前插件未初始化配置，请联系管理员");
            return
        }
    }

    let option = []
    url = bucketGet(tongzi, 'QRabbitPro_url')
    // BotApiToken = bucketGet(tongzi, 'BotApiToken')
    if (url[url.length - 1] == '/') {
        url = url.substring(0, url.length - 1);
    }
    let username = bucketGet(tongzi, 'QRabbitPro_username')
    let password = bucketGet(tongzi, 'QRabbitPro_password')
    if (username == "" || username == null) {
        notifyMasters("未配置QRabbitPro的管理员账号，对我说“重置qr”后重新配置")
        return
    } else {
        getToken(username, password)
    }
    option.push(bucketGet(tongzi, 'jdqr'))
    option.push(bucketGet(tongzi, 'kouling'))
    option.push(bucketGet(tongzi, 'jdsms'))
    option.push(isAccount ? 'true' : 'false')

    container_id = bucketGet(tongzi, 'container_id')
    if (container_id == 'switch') {
        container_id = switchql()
        if (!container_id) {
            sendText("没有可用容器，请联系管理员")
            return
        }
    }

    if (Content == '短信' && bucketGet(tongzi, 'jdsms') == 'true') {
        smsWskey()
    } else if (Content == '口令' && bucketGet(tongzi, 'kouling') == 'true') {
        koulingWskey()
    } else if (Content == '扫码' && bucketGet(tongzi, 'jdqr') == 'true') {
        qrWskey()
    } else if (Content == '账密' && isAccount) {
        AccountSecret()
    } else {
        getLoginMethod(option);
    }
}

function findUniqueItemIndex(arr) {
    const validItems = arr.filter(item => item === 'true');
    return validItems.length === 1 ? arr.indexOf('true') : -1;
}

function getLoginMethod(option) {
    const loginMethods = [
        { name: "京东扫码登录", func: qrWskey },
        { name: "口令登陆", func: koulingWskey },
        { name: "短信登录", func: smsWskey }
    ];

    if (isAccount && typeof AccountSecret === 'function') {
        loginMethods.push({ name: "账密登录（免三天一登）", func: AccountSecret });
    }

    const uniqueIndex = findUniqueItemIndex(option);
    if (uniqueIndex > 0 && uniqueIndex < loginMethods.length) {
        return loginMethods[uniqueIndex].func();
    }

    const availableMethods = option
        .slice(0, loginMethods.length) // Ensure option and loginMethods have the same length
        .map((item, index) => item === 'true' ? loginMethods[index] : null)
        .filter(Boolean);

    if (availableMethods.length === 0) {
        sendText('没有可用的登录方式');
        return;
    }

    const promptText = availableMethods
        .map((method, index) => `【${index + 1}】${method.name}`)
        .join('\n');

    let reminderText = '';
    if (bucketGet(tongzi, 'reminder')) {
        reminderText += `\n温馨提示：${bucketGet(tongzi, 'reminder')}`;
    }

    sendText(`请选择你要登录的方式\n(回复【】内的数字即可)\n${promptText}${reminderText}`);

    Debug(container_id + '兔子登陆容器');
    const select = input(30000);
    Debug(select);

    const selectedMethod = availableMethods[parseInt(select) - 1];
    if (selectedMethod) {
        selectedMethod.func();
    } else {
        sendText('无效选择，已退出');
    }
}

function rabbitTest() {
    notifyMasters('正在检测ServerHost···')
    url = bucketGet(tongzi, 'QRabbitPro_url')
    if (url[url.length - 1] == '/') {
        url = url.substring(0, url.length - 1);
    }
    let host =
        [
            "mr.yanyuwangluo.cn",
            "mr.118918.xyz",
            "jd-orgin.1888866.xyz",
            "rabbit.cfyes.tech",
            "host.257999.xyz",
            "mr-orgin.1888866.xyz",
            "fd.gp.mba:6379",
            "log.madrabbit.eu.org",
            "mr.108168.xyz:10188",
            "mr.5gyh.com",
            "rabbit.gushao.club",
            "mr.yanyuwangluo.cn:1202"
        ]

    let available = host.reduce((acc, item) => {
        let time
        try {
            time = checkHost(item);
        } catch (error) {
            Debug(error)
        }
        if (time) acc.push({ url: item, time });
        return acc;
    }, [])
        .sort((a, b) => a.time - b.time)
    Debug(JSON.stringify(available))
    if (available.length == 0) {
        notifyMasters('当前无可用ServerHost，请联系管理员')
        return
    }

    let fastUrl = available[0].url
    Debug(fastUrl)
    available = available.map(item => `🔗：${item.url}\n⚡：${item.time}ms`);

    available.unshift('当前可用ServerHost：');
    notifyMasters(available.join('\n'))

    let username = bucketGet(tongzi, 'QRabbitPro_username')
    let password = bucketGet(tongzi, 'QRabbitPro_password')
    if (username == "" || username == null) {
        notifyMasters("未配置QRabbitPro的管理员账号，对我说“重置qr”后重新配置")
        return
    } else if (fastUrl) {
        getToken(username, password)
        getConfig(fastUrl)
    }
}

function checkHost(ServerHost) {
    const MAX_ATTEMPTS = 3;
    const requestDuration = [];

    for (let count = 0; count < MAX_ATTEMPTS; count++) {
        const startTime = Date.now();

        try {
            const body = request({
                url: `http://${ServerHost}/ping`,
                method: "get",
                timeOut: 4000,
            });

            if (body === "pong!") {
                const duration = Date.now() - startTime;
                requestDuration.push(duration);
            } else {
                break;
            }
        } catch (error) {
            Debug(error);
            break;
        }
    }

    Debug(`${ServerHost} 测试耗时：${requestDuration}`);

    const avg = requestDuration.length > 0
        ? requestDuration.reduce((sum, time) => sum + time, 0) / requestDuration.length
        : 0;

    return Math.round(avg);
}

function getToken(username, password) {
    let body = request({
        url: url + "/admin/auth",
        method: "post",
        body: {
            "username": username,
            "password": password
        },
        dataType: "json",
        timeOut: 60000
    })
    if (body && body.access_token) {
        token = body.access_token
    } else if (body) {
        Debug(JSON.stringify(body))
        notifyMasters(body.msg)
    } else {
        Debug(JSON.stringify(body))
        notifyMasters('访问兔子出错，请检查兔子地址')
    }
}

function getConfig(ServerHost) {
    let body = request({
        url: url + "/admin/GetConfig",
        method: "get",
        headers: {
            Authorization: "Bearer " + token,
        },
        dataType: "json",
        timeOut: 60000
    })
    if (body.username) {
        let data = body
        data.ServerHost = ServerHost
        saveConfig(data)
    }
}

function saveConfig(data) {
    let body = request({
        url: url + "/admin/SaveConfig",
        method: "post",
        headers: {
            Authorization: "Bearer " + token,
        },
        body: JSON.stringify(data),
        dataType: "json",
        timeOut: 60000
    })
    if (body.code == 0) {
        notifyMasters("ServerHost已更新为：" + data.ServerHost)
    }
}

function getql() {
    Debug(url + "/api/Config")
    let ischoose = false
    let body = request({
        url: url + "/api/Config",
        method: "get",//网络请求方法get,post,put,delete
        timeOut: 60000//单位为毫秒ms，也可以都小写timeout
    })
    Debug(body)
    let b = JSON.parse(body);
    if (b.success) {
        let list = b.data.list;
        let str = '请选择QRabbitPro登陆容器：\n0.根据剩余容量智能切换\n'
        list.forEach((item, index) => {
            str += `${index + 1}.${item.container_name}\n最大容量：${item.container_capacity}\n剩余容量：${checkql(item.container_id)}\n`
        })
        sendText(str)
        let index = input(30000)
        if (index) {
            if (parseInt(index) == 0) {
                bucketSet(tongzi, "container_id", 'switch');
            } else {
                container_id = list[parseInt(index) - 1].container_id
                bucketSet(tongzi, "container_id", container_id);
            }
            ischoose = true
        }
        Debug('container_id:' + container_id)
    } else {
        notifyMasters('QRabbitPro没有可用容器')
    }
    return ischoose
}

function checkql(container_id) {
    let ckcount = ''
    request({
        url: url + "/api/QLConfig?container_id=" + container_id,
        method: "get",//网络请求方法get,post,put,delete
        timeOut: 60000//单位为毫秒ms，也可以都小写timeout
    }, function (error, response, header, body) {
        Debug(body)
        let b = JSON.parse(body);
        ckcount = b.data.ckcount;
        Debug(container_id + 'container_id:' + ckcount)

    })
    return ckcount
}

function switchql() {
    let container_id = ''
    try {
        request({
            url: url + "/api/Config",
            method: "get",//网络请求方法get,post,put,delete
            timeOut: 60000//单位为毫秒ms，也可以都小写timeout
        }, function (error, response, header, body) {
            Debug(body)
            let b = JSON.parse(body);
            let list = b.data.list;
            for (const item of list) {
                if (checkql(item.container_id) > 0) {
                    container_id = item.container_id
                    return
                }
            }
            Debug('container_id:' + container_id)
        })
        if (container_id) {
            return container_id
        } else {
            notifyMasters('QRabbitPro没有可用容器,请在QRabbitPro后台页面添加容器')
            return false
        }
    } catch (error) {
        notifyMasters('获取QRabbitPro容器出错,请在QRabbitPro后台页面添加容器：' + error)
        return false
    }
}

function ShuRu() {
    var msg = input(60000, 6000)
    if (msg == null) {
        sendText("超时，60秒内未回复，取消本次配置。")
        return false
    } else if (msg == "q" || msg == "Q") {
        sendText("已退出会话");
        return false
    } else {
        return msg;
    }
}

function retimg(img) {
    const username = bucketGet("cloud", "username")
    const password = bucketGet("cloud", "password")
    const ib = encodeURIComponent(img)
    let body = request({
        url: "http://aut.zhelee.cn/imgUpload",
        method: "post",
        dataType: "json",
        formData: {
            username: username,
            password: password,
            imgBase64: ib
        },
    })
    if (body && body.code == 200) {
        // Debug(JSON.stringify(body))
        if (body.code == "200") {
            Debug(body.result.path)
            let res = sendImage(body.result.path)
            Debug(res)
            if (res == '<nil>') {
                pictureBed(img)
            }
        } else {
            sendText("发送二维码图片出现问题，请联系管理员")
        }
    } else {
        Debug(JSON.stringify(body))
        pictureBed(img)
    }
}

function pictureBed(img) {
    if (img.startsWith('data:image/jpg;base64,')) img = img.split(',')[1]
    let bodys = request({
        url: "http://47.99.156.63:5000/upload",
        method: "post",
        body: {
            image: img
        },
    })
    bodys = JSON.parse(bodys)
    if (bodys.code == "200") {
        // (http://47.99.156.63:5000/310c3f7e-ead0-4d65-bcb3-6e57defa7492.jpeg)
        Debug(bodys.imageUrl.split('/')[3])
        sendImage(bodys.imageUrl)
    } else {
        notifyMasters('请在插件权限打开cloud数据')
        sendText("发送二维码图片出现问题，请联系管理员")
    }
}

function qrWskey() {
    //如果url末尾有/，就去掉
    if (url[url.length - 1] == '/') {
        url = url.substring(0, url.length - 1);
    }
    getQR();
}


function smsWskey() {
    //如果url末尾有/，就去掉
    if (url[url.length - 1] == '/') {
        url = url.substring(0, url.length - 1);
    }
    // 启动提示语
    sendText("京东短信登录，请输入手机号");
    // 获取内容
    let num = input(30000, 100);
    let regExp = /^1[3456789]\d{9}$/;
    if (regExp.test(num)) {
        getSMS(num)
    } else {
        sendText("请输入正确的手机号,已退出");
        return
    }
}

function getSMS(num) {
    let GetSMSUrl = url + "/sms/sendSMS";
    // let GetSMSUrl = url + "/bot/mck/sendSMS" + `?BotApiToken=${BotApiToken}`;
    // 发送请求
    request({
        "url": GetSMSUrl, //请求链接
        "method": "post", //请求方法
        headers: {//请求头
            Connection: "Keep-Alive ",
            Accept: 'application/json,text/plain,*/*',
            'Accept-Language': 'zh-cn'
        },
        dataType: "json",
        body: {
            "Phone": num,
            "container_id": container_id
        },
        timeOut: 60000
    }, function (error, response, header, body) {
        Debug(JSON.stringify(body))
        if (body.success) {
            sendText('验证码发送成功，请输入六位验证码')
            verifyCode(num);
        } else {
            Debug("AutoCaptcha")
            AutoCaptcha(num, 1)
        }
        //网络请求处理函数
    })
}

function AutoCaptcha(num, count) {
    if (count > 10) {
        sendText('验证码发送失败')
        return
    }
    request({
        url: url + "/sms/AutoCaptcha",
        // url: url + "/bot/mck/AutoCaptcha" + `?BotApiToken=${BotApiToken}`,
        method: "post",//网络请求方法get,post,put,delete
        dataType: "json",
        body: {
            "Phone": num
        },
        timeOut: 60000//单位为毫秒ms，也可以都小写timeout
    }, function (error, response, header, body) {
        try {
            Debug(JSON.stringify(body))
            if (body.success) {
                sendText('验证码发送成功，请输入六位验证码')
                verifyCode(num);
            } else if (body.message == "'img'") {
                sendText('验证码发送失败')
            } else {
                count++
                Debug("重试验证码")
                sleep(1000)
                AutoCaptcha(num, count)
            }
        } catch (e) {
            Debug(e)
        }
    })
}

function verifyCode(num) {
    let code = input(50000, 100);
    if (code.length != 6) {
        sendText('验证码格式错误,已退出')
        return
    }
    let getCkUrl = url + '/sms/VerifyCode'
    // let getCkUrl = url + '/bot/mck/VerifyCode' + `?BotApiToken=${BotApiToken}`
    request({
        "url": getCkUrl, //请求链接
        "method": "post", //请求方法
        headers: {//请求头
            Connection: "Keep-Alive ",
            Accept: 'application/json,text/plain,*/*',
            'Accept-Language': 'zh-cn'
        },
        dataType: "json",
        body: {
            "Phone": num,
            "Code": code,
            "container_id": container_id
        },
        timeOut: 60000
    }, function (error, response, header, body) {
        Debug(JSON.stringify(body))
        var bodyck = body
        if (bodyck.code == "200") {
            Debug('登陆成功')
            // breakIn(bodyck.ck)
            // updatePtKey(bodyck.ck)
            getCk(bodyck.pin, container_id, 'sms')
        } else if (bodyck.code == "555") {
            Debug(JSON.stringify(body))
            notifyMasters("短信登录出现问题:" + JSON.stringify(body))
            sendText(bodyck.message)
            let img64 = 'data:image/jpg;base64,' + bodyck.RiskQRCode;
            retimg(img64)
        } else if (bodyck.code == "505") {
            rabbitTest()
            notifyMasters("短信登录出现问题:" + JSON.stringify(body))
        } else if (bodyck.code != '56' && bodyck.code != '57') {
            Debug(JSON.stringify(body))
            const tip = bodyck.msg || bodyck.message
            sendText(tip)
            if (tip == '连接服务器失败') {
                rabbitTest()
            }
            if (tip !== '验证码输入错误') {
                notifyMasters("短信登录出现问题:" + JSON.stringify(body))
            }
        }
        //网络请求处理函数
    })
}


function getQR() {
    sendText("请使用手机京东App扫码，可保存到相册扫码,“Q”退出会话。")
    let img64 = ""
    request({
        // url: url + "/bot/GenQrCode" + `?BotApiToken=${BotApiToken}`,
        url: url + "/api/GenQrCode",
        method: "post",//网络请求方法get,post,put,delete
        timeOut: 60000//单位为毫秒ms，也可以都小写timeout
    }, function (error, response, header, body) {
        try {
            Debug(body)
            let b = JSON.parse(body);
            if (b.msg == '连接服务器失败' || b.message == '连接服务器失败') {
                rabbitTest()
            }
            img64 = 'data:image/jpg;base64,' + b.qr;
            retimg(img64)
            GetStatus(b.QRCodeKey, container_id, 'qr')
        } catch (e) {
            Debug(e)
            notifyMasters('获取二维码出现问题:' + e)
        }
    })
}


function koulingWskey() {
    //如果url末尾有/，就去掉
    if (url[url.length - 1] == '/') {
        url = url.substring(0, url.length - 1);
    }
    let kouling = ''
    request({
        // url: url + "/bot/GenQrCode" + `?BotApiToken=${BotApiToken}`,
        url: url + "/api/GenQrCode",
        method: "post",//网络请求方法get,post,put,delete
        timeOut: 60000//单位为毫秒ms，也可以都小写timeout
    }, function (error, response, header, body) {
        Debug(body)
        let b = JSON.parse(body);
        if (b.code == 0) {
            kouling = b.jcommond;
            sendText(kouling)
            sendText("请复制以上口令后打开手机京东App点击确认登录即可,“Q”退出会话。")
            GetStatus(b.QRCodeKey, container_id, 'kouling')
        } else {
            notifyMasters('获取口令出现问题:' + b.msg)
            sendText("获取口令失败")
            if (b.msg == '连接服务器失败' || b.message == '连接服务器失败') {
                rabbitTest()
            }
        }
    })
}

function GetStatus(QRCodeKey, container_id, loginType) {
    Debug(QRCodeKey + container_id)
    try {
        var a = 0;
        var s = 0;
        while (s == 0) {
            var c = input(2000);
            // if (c == "q" || c == "Q") {
            if (c) {
                sendText("已退出")
                s = 1;
                break;
            }
            request({
                // url: url + "/bot/QrCheck" + `?BotApiToken=${BotApiToken}`,
                url: url + "/api/QrCheck",
                method: "POST",//网络请求方法get,post,put,delete
                timeout: 20000,
                dataType: "json",
                body: {
                    "QRCodeKey": QRCodeKey,
                    "token": BotApiToken,
                    "container_id": container_id,
                }
            }, function (error, response, header, body) {
                Debug(JSON.stringify(body))
                var bodyck = body
                if (bodyck.code == "200") {
                    Debug('登陆成功')
                    // breakIn(bodyck.ck)
                    // updatePtKey(bodyck.ck)
                    getCk(bodyck.pin, container_id, loginType)
                    s = 1;
                } else if (bodyck.code == "500") {
                    Debug(bodyck.errorMsg)
                    sendText(bodyck.errorMsg)
                    notifyMasters("扫码登录出现问题:" + bodyck.errorMsg)
                    s = 1;
                } else if (bodyck.code == "202") {
                    sendText("登陆失败，您的账号存在风险,请验证后重新扫码")
                    var a = bodyck.errorMsg;
                    a = a.match(/href=\"(\S*)\" /)[1];
                    sendText(a)
                    s = 1;
                } else if (bodyck.code == "502") {
                    sendText("二维码已失效，请重新获取二维码")
                    s = 1;
                } else if (bodyck.code == "220") {
                    sendText("登陆失败，您的账号存在安全风险，请使用短信登录")
                    s = 1;
                } else if (bodyck.code != '56' && bodyck.code != '57') {
                    Debug(bodyck.code + bodyck.msg)
                    sendText(bodyck.msg)
                    notifyMasters("扫码登录出现问题:" + JSON.stringify(bodyck))
                    s = 1;
                }
            })

            a = a + 1;
            if (a == 70) {
                s = 1;
                sendText("未扫码，退出")
            }
        }
    } catch (e) {
        Debug(e)
        sendText("出现问题，请咨询群主")
        notifyMasters("扫码登录出现问题，请检查配置~")
        notifyMasters(e)
    }
}

function encodeIfStartsWithChinese(str) {
    // 正则表达式匹配中文字符
    const chineseRegex = /^[\u4e00-\u9fa5]/;

    // 判断字符串是否以中文开头
    if (chineseRegex.test(str)) {
        // 如果是，返回 encodeURIComponent 编码后的字符串
        return encodeURIComponent(str);
    } else {
        // 如果不是，返回原字符串
        return str;
    }
}

function getCk(pin, container_id, loginType) {
    pin = encodeIfStartsWithChinese(pin);
    let body = request({
        url: url + "/env/search",
        method: "post",
        headers: { Authorization: "Bearer " + token },
        body: { pin, container_id },
        dataType: "json",
        timeOut: 60000
    });

    if (body.code === 0) {
        Debug(JSON.stringify(body));
        const item = body.data.find(item => item.pin === pin);
        if (item) {
            handleLogin(item, loginType, pin);
            return;
        }
    } else {
        Debug(JSON.stringify(body));
        notifyMasters(body.msg);
    }
}

function sendLoginNotification(userId, platform, pin, loginType) {
    const loginTypeMap = {
        'sms': '短信登陆',
        'qr': '扫码登陆',
        'kouling': '口令登陆'
    };
    notifyMasters(`======JD登陆通知======
[登陆用户]：${userId}
[登陆平台]：${platform}
[登陆账户]：${decodeURIComponent(pin)}
[登陆方式]：${loginTypeMap[loginType]}
[登陆时间]：${getCurrentTime()}`);
}

function handleLogin(item, loginType, pin) {
    let closePush = bucketGet(tongzi, 'closePush');
    if (closePush !== 'true') {
        sendLoginNotification(userId, platform, pin, loginType);
    }
    const cookie = loginType === 'sms' ? item.mck : item.appck;
    breakIn(cookie);
    sendText(`${decodeURIComponent(pin)}登陆成功`);
    bucketSet("pin" + platform.toUpperCase(), pin, userId);
    updatePtKey(cookie);
}

/**
 * 获取当前时间 格式：yyyy-MM-dd HH:MM:SS
 */
function getCurrentTime() {
    var date = new Date();//当前时间
    var month = zeroFill(date.getMonth() + 1);//月
    var day = zeroFill(date.getDate());//日
    var hour = zeroFill(date.getHours());//时
    var minute = zeroFill(date.getMinutes());//分
    var second = zeroFill(date.getSeconds());//秒

    //当前时间
    var curTime = date.getFullYear() + "-" + month + "-" + day
        + " " + hour + ":" + minute + ":" + second;

    return curTime;
}

function zeroFill(i) {
    if (i >= 0 && i <= 9) {
        return "0" + i;
    } else {
        return i;
    }
}

function updatePtKey(cookie) {
    var pt_key_pattern = /pt_key=([^;]*)/;
    var pt_pin_pattern = /pt_pin=([^;]*)/;
    var pt_key_match = pt_key_pattern.exec(cookie);
    var pt_pin_match = pt_pin_pattern.exec(cookie);
    let data = bucketGet("jdNotify", pt_pin_match[1])
    if (data) {
        const originData = JSON.parse(data);
        originData.PtKey = pt_key_match[1];
        bucketSet("jdNotify", pt_pin_match[1], JSON.stringify(originData));
    } else {
        let info = { "ID": pt_pin_match[1], "Pet": false, "Fruit": false, "DreamFactory": false, "Note": "", "PtKey": pt_key_match[1], "AssetCron": "", "PushPlus": "", "LoginedAt": "2024-07-07T11:22:03+08:00", "ClientID": "uUUT8eVZ_x5c" }
        bucketSet("jdNotify", pt_pin_match[1], JSON.stringify(info));
    }
}
