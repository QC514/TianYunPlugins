
//[disable:false]
//[rule:品赞查询]
//[rule:品赞白名单]
//[rule:品赞签到]
//[rule:品赞新增]
//[rule:品赞api生成]
//[author: xiaoqing]
//[class: 工具类]
//[public: true] 
//[admin: true] 
//[price: 0.5] 上架价格
//[version: 0.1.0] 
//[service: 97393412]
//[description: 支持多账号管理<br/>品赞签到和品赞白名单可去系统定时中设置定时运行<br/>需要到群文件云插件（CryptoJS）放到/plugin/replies内<br/>注册地址：https://www.ipzan.com?pid=rfrgbefv8 <br/>修复多账号加白名单<br/>增加API生成,指令(品赞api生成)<br/>插件交流群：858456556] 

var GetContent = GetContent()
var cookie = ""
var checkJS = false
let text = ""
try {
    importJs("CryptoJS.js")
} catch (err) {
    checkJS = true
}
function mian() {
    if (checkJS) {
        if (isAdmin()) {
            sendText("使用本插件需要安装【CryptoJS】依赖插件，请前往云插件下载该插件")
        }
        return
    }
    if (GetContent == "品赞新增") {
        add_user()
        return
    }
    bind = GetBind()
    if (bind !== false) {
        let accounts = []
        if (GetContent == "品赞api生成") {
            for (i = 0; i < bind.length; i++) {
                accounts[i] = `【${i + 1}】${bind[i]}`
            }
            sendText("请选择要【删除优惠劵】的账号：\n" + accounts.join("\\n"))
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

            var user_add = JSON.parse(bucketGet("who_zan", PIN))
            // sendText(JSON.stringify(user_add)+"-"+PIN)
            login(PIN, user_add.loginPassword)
            extract(PIN,user_add.no)
            return
        }
        if (GetContent == "品赞查询") {
            for (i = 0; i < bind.length; i++) {
                var user_add = JSON.parse(bucketGet("who_zan", bind[i]))
                userProduct(bind[i], user_add.no, user_add.userId)
            }
            sendText(text)

        } else if (GetContent == "品赞白名单") {
            for (let j = 0; j < bind.length; j++) {
                var user_add = JSON.parse(bucketGet("who_zan", bind[j]))
                let time_who = Date.parse(new Date()).toString();//获取到毫秒的时间戳，精确到毫秒
                time_who = parseInt(time_who / 1000);
                var data = `${user_add.loginPassword}:${user_add.extractionKey}:${time_who}`;
                const key = CryptoJS.enc.Utf8.parse(user_add.signKey);
                var encryptedData = CryptoJS.AES.encrypt(data, key, {
                    mode: CryptoJS.mode.ECB,
                    padding: CryptoJS.pad.Pkcs7,
                });
                var sign = encryptedData.ciphertext.toString();

                let ip = format()
                sendText(ip)
                whiteList(user_add.no, ip, sign, bind[j])
            }
        } else if (GetContent == "品赞签到") {
            for (i = 0; i < bind.length; i++) {
                var user_add = JSON.parse(bucketGet("who_zan", bind[i]))
                login(bind[i], user_add.loginPassword)
                find(bind[i], cookie)
            }
        }
    } else {
        sendText("没有获取到账号数据")
        return
    }
}

function extract(ID,ddh) {
    try {
        body = request({
            method: "get",
            url: `https://service.ipzan.com/home/core-get-url?num=1&no=${ddh}&minute=1&format=json&protocol=1&pool=quality&mode=whitelist`,
            //body: mdmd,
            headers: {
                Accept: 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
                Host: 'service.ipzan.com',
                Connection: 'Keep-Alive',
                Origin: 'https://www.ipzan.com',
                Authorization: 'Bearer ' + cookie,
                Referer: 'https://www.ipzan.com/user/extractapi',
                'Content-Type': 'application/json'
            },
            dataType: "json",
            timeOut: 30000
        })
        Debug(JSON.stringify(body))
        if (body.code == 0) {
            phone = hidePhoneNumber(ID)
            sendText(`账号[${phone}]\nAPI生成成功:\n${body.data.url}\n温馨提示：默认生成格式是JSON,如果需要txt,把format后面的json改成txt\n其他看说明
minute=占用时长 值为1 3 5 10 15 30	
pool=优质IP: quality,普通IP池: ordinary
num=提取数量
如果有以上的可在API中修改`)
           // userWreceiveallet(phone, body.data.user_id, body.data.balance, cookie)
        } else {
            sendText(`账号[${user}] 登录失败`)
        }
    } catch (err) {
    }
}
function hidePhoneNumber(phoneNumber) {
    return phoneNumber.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
}
function whiteList(ddh, ipp, sisgn, ID) {
    for (let i = 0; i < 3; i++) {
        try {
            data = {
                no: ddh,
                ip: ipp,
                sign: sisgn,
                replace: 1
            }
            body = request({
                method: "post",
                url: `https://service.ipzan.com/whiteList-add`,
                body: data,
                headers: {
                    "Content-Type": "application/json"
                },
                dataType: "json",
                timeOut: 30000
            })
            Debug(JSON.stringify(body))
            if (body.code == 0) {
                i = 30
                sendText(`手机号:${hidePhoneNumber(ID)}\n加白状态:${body.data}\n添加IP:${ipp}`)
                sleep(1000)
            } else {
                sleep(1000)
            }
        } catch (err) {
        }
    }
}
function userProduct(phone, ddh, userId) {
    try {

        body = request({
            method: "get",
            url: `https://service.ipzan.com/userProduct-get?no=${ddh}&userId=${userId}`,
            //body: data,
            headers: {
                "Content-Type": "application/json"
            },
            dataType: "json",
            timeOut: 30000
        })
        Debug(JSON.stringify(body))
        if (body.code == 0) {
            phone = hidePhoneNumber(phone)
            text += `手机号:${phone}
账号余额:${body.data.balance}
--------------\n`
        }
    } catch (err) {
    }
}

function sign_a(_0x256ced, _0x59add5) {
    console.log(_0x256ced + "-----" + _0x59add5)
    var _0x3b0e44 = {
        table: ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "/"],
        UTF16ToUTF8: function (_0x164874) {
            for (var _0x22d31c = [], _0x34b5d0 = _0x164874.length, _0x12ffe3 = 0; _0x12ffe3 < _0x34b5d0; _0x12ffe3++) {
                var _0x60360,
                    _0x57e360,
                    _0x243264 = _0x164874.charCodeAt(_0x12ffe3);

                0 < _0x243264 && _0x243264 <= 127 ? _0x22d31c.push(_0x164874.charAt(_0x12ffe3)) : 128 <= _0x243264 && _0x243264 <= 2047 ? (_0x60360 = 192 | _0x243264 >> 6 & 31, _0x57e360 = 128 | 63 & _0x243264, _0x22d31c.push(String.fromCharCode(_0x60360), String.fromCharCode(_0x57e360))) : 2048 <= _0x243264 && _0x243264 <= 65535 && (_0x60360 = 224 | _0x243264 >> 12 & 15, _0x57e360 = 128 | _0x243264 >> 6 & 63, _0x243264 = 128 | 63 & _0x243264, _0x22d31c.push(String.fromCharCode(_0x60360), String.fromCharCode(_0x57e360), String.fromCharCode(_0x243264)));
            }

            return _0x22d31c.join("");
        },
        UTF8ToUTF16: function (_0x2f5e6d) {
            for (var _0x2e1ff5 = [], _0x1fe47c = _0x2f5e6d.length, _0x36c899 = 0, _0x36c899 = 0; _0x36c899 < _0x1fe47c; _0x36c899++) {
                var _0xddba5e,
                    _0x1c66d1,
                    _0x4e11bc = _0x2f5e6d.charCodeAt(_0x36c899);

                0 == (_0x4e11bc >> 7 & 255) ? _0x2e1ff5.push(_0x2f5e6d.charAt(_0x36c899)) : 6 == (_0x4e11bc >> 5 & 255) ? (_0x1c66d1 = (31 & _0x4e11bc) << 6 | 63 & (_0xddba5e = _0x2f5e6d.charCodeAt(++_0x36c899)), _0x2e1ff5.push(Sting.fromCharCode(_0x1c66d1))) : 14 == (_0x4e11bc >> 4 & 255) && (_0x1c66d1 = (255 & (_0x4e11bc << 4 | (_0xddba5e = _0x2f5e6d.charCodeAt(++_0x36c899)) >> 2 & 15)) << 8 | ((3 & _0xddba5e) << 6 | 63 & _0x2f5e6d.charCodeAt(++_0x36c899)), _0x2e1ff5.push(String.fromCharCode(_0x1c66d1)));
            }

            return _0x2e1ff5.join("");
        },
        encode: function (_0x4440be) {
            if (!_0x4440be) {
                return "";
            }

            for (var _0x44c43a = this.UTF16ToUTF8(_0x4440be), _0xa978b5 = 0, _0x4f9c35 = _0x44c43a.length, _0x59ac5c = []; _0xa978b5 < _0x4f9c35;) {
                var _0x4a5bc7 = 255 & _0x44c43a.charCodeAt(_0xa978b5++);

                if (_0x59ac5c.push(this.table[_0x4a5bc7 >> 2]), _0xa978b5 == _0x4f9c35) {
                    _0x59ac5c.push(this.table[(3 & _0x4a5bc7) << 4]);

                    _0x59ac5c.push("==");

                    break;
                }

                var _0x77e2fc = _0x44c43a.charCodeAt(_0xa978b5++);

                if (_0xa978b5 == _0x4f9c35) {
                    _0x59ac5c.push(this.table[(3 & _0x4a5bc7) << 4 | _0x77e2fc >> 4 & 15]);

                    _0x59ac5c.push(this.table[(15 & _0x77e2fc) << 2]);

                    _0x59ac5c.push("=");

                    break;
                }

                var _0xdaed0e = _0x44c43a.charCodeAt(_0xa978b5++);

                _0x59ac5c.push(this.table[(3 & _0x4a5bc7) << 4 | _0x77e2fc >> 4 & 15]);

                _0x59ac5c.push(this.table[(15 & _0x77e2fc) << 2 | (192 & _0xdaed0e) >> 6]);

                _0x59ac5c.push(this.table[63 & _0xdaed0e]);
            }

            return _0x59ac5c.join("");
        },
        decode: function (_0x4de779) {
            if (!_0x4de779) {
                return "";
            }

            for (var _0x44177d = _0x4de779.length, _0x3286ef = 0, _0x5afdd4 = []; _0x3286ef < _0x44177d;) {
                code1 = this.table.indexOf(_0x4de779.charAt(_0x3286ef++));
                code2 = this.table.indexOf(_0x4de779.charAt(_0x3286ef++));
                code3 = this.table.indexOf(_0x4de779.charAt(_0x3286ef++));
                code4 = this.table.indexOf(_0x4de779.charAt(_0x3286ef++));
                c1 = code1 << 2 | code2 >> 4;

                _0x5afdd4.push(String.fromCharCode(c1));

                -1 != code3 && (c2 = (15 & code2) << 4 | code3 >> 2, _0x5afdd4.push(String.fromCharCode(c2)));
                -1 != code4 && (c3 = (3 & code3) << 6 | code4, _0x5afdd4.push(String.fromCharCode(c3)));
            }

            return this.UTF8ToUTF16(_0x5afdd4.join(""));
        }
    };

    function _0x52233c(_0x5136e2, _0xe0d60f) {
        for (var _0x2ab4f3 = _0x3b0e44.encode("".concat(_0x5136e2, "QWERIPZAN1290QWER").concat(_0xe0d60f)), _0x4cc15c = "", _0x1675cf = 0; _0x1675cf < 80; _0x1675cf++) {
            _0x4cc15c += Math.random().toString(16).slice(2);
        }

        _0x2ab4f3 = "".concat(_0x4cc15c.slice(0, 100)).concat(_0x2ab4f3.slice(0, 8)).concat(_0x4cc15c.slice(100, 200)).concat(_0x2ab4f3.slice(8, 20)).concat(_0x4cc15c.slice(200, 300)).concat(_0x2ab4f3.slice(20)).concat(_0x4cc15c.slice(300, 400));
        return _0x2ab4f3;
    }

    return {
        account: _0x52233c(_0x256ced, _0x59add5),
        source: "ipzan-home-one"
    };
}

//登录签到
function login(user, password) {
    let mdmd = sign_a(user, password)
    try {
        body = request({
            method: "POST",
            url: `https://service.ipzan.com/users-login`,
            body: mdmd,
            headers: {
                Accept: 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
                Host: 'service.ipzan.com',
                Connection: 'Keep-Alive',
                Origin: 'https://kip.ipzan.com',
                Authorization: 'Bearer undefined',
                Referer: 'https://kip.ipzan.com/',
                'Content-Type': 'application/json'
            },
            dataType: "json",
            timeOut: 30000
        })
        //sendText(JSON.stringify(body))
        if (body.code == 0) {

            cookie = body.data.token
            //sendText(`账号[${user}] 登录成功.[${}]`)
        } else {
            sendText(`账号[${user}] 登录失败`)
        }
    } catch (err) {
    }
}
function find(user, cookie) {
    try {
        body = request({
            method: "get",
            url: `https://service.ipzan.com/home/userWallet-find`,
            //body: mdmd,
            headers: {
                Accept: 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
                Host: 'service.ipzan.com',
                Connection: 'Keep-Alive',
                Origin: 'https://kip.ipzan.com',
                Authorization: 'Bearer ' + cookie,
                Referer: 'https://kip.ipzan.com/',
                'Content-Type': 'application/json'
            },
            dataType: "json",
            timeOut: 30000
        })
        Debug(JSON.stringify(body))
        if (body.code == 0) {
            phone = hidePhoneNumber(user)
            // sendText(`账号[${phone}]\n用户id[${body.data.user_id}]\n当前金币[${body.data.balance}]`)
            userWreceiveallet(phone, body.data.user_id, body.data.balance, cookie)
        } else {
            sendText(`账号[${user}] 登录失败`)
        }
    } catch (err) {
    }
}
function userWreceiveallet(user, user_id, balance, cookie) {
    try {
        body = request({
            method: "get",
            url: `https://service.ipzan.com/home/userWallet-receive`,
            //body: mdmd,
            headers: {
                Accept: 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
                Host: 'service.ipzan.com',
                Connection: 'Keep-Alive',
                Origin: 'https://kip.ipzan.com',
                Authorization: 'Bearer ' + cookie,
                Referer: 'https://kip.ipzan.com/',
                'Content-Type': 'application/json'
            },
            dataType: "json",
            timeOut: 30000
        })
        Debug(JSON.stringify(body))
        if (body.code == 0) {
            sendText(`账号[${user}]\n用户id[${user_id}]\n当前金币[${balance}]\n签到结果:[${body.message}]`)
        } else {
            sendText(`账号[${user}]\n用户id[${user_id}]\n当前金币[${balance}]\n签到结果:[${body.message}]`)
        }
    } catch (err) {
    }
}


function format() {//获取本地ip
    for (i = 0; i < 5; i++) {
        body = request({
            method: "get",
            url: `http://myip.ipip.net/json`,
            //body: data,
            headers: {
                "Content-Type": "application/json"
            },
            dataType: "json",
            timeOut: 30000
        })
        if (body) {
            if (body.ret == "ok") {
                i = 6
                return body.data.ip
            } else {
                sleep(2000)
            }
        } else {
            sleep(2000)
        }


    }

}
/*

*/

function GetBind() {
    let allpins = []
    let pin = []
    allpins = bucketKeys("who_zan")
    if (allpins == 0) {
        //sendText("没有")
        return false
    } else {
        // sendText("有的")
        for (let j = 0; j < allpins.length; j++) {
            bucketGet("who_zan", allpins[j])
            pin.push(allpins[j])
        }
        return pin
    }



}
function add_user() {//新增账号
    sendText(`增加账号需要以下数据:
手机号
密码
ID 号
签名秘钥
套餐提取密匙
套餐购买编号`)
    var phone = ShuRu("请输入品赞--手机号")
    if (phone == false) {
        sendText("手机号-输入超时,取消任务")
        return
    }
    var loginPassword = ShuRu("请输入品赞--密码")
    if (loginPassword == false) {
        sendText("密码-输入超时,取消任务")
        return
    }
    var userId = ShuRu("请输入品赞--ID 号")
    if (userId == false) {
        sendText("密码-输入超时,取消任务")
        return
    }
    var signKey = ShuRu("请输入品赞--签名秘钥")
    if (signKey == false) {
        sendText("签名秘钥-输入超时,取消任务")
        return
    }
    var extractionKey = ShuRu("请输入品赞--套餐提取密匙")
    if (extractionKey == false) {
        sendText("套餐提取密匙-输入超时,取消任务")
        return
    }
    var no = ShuRu("请输入品赞--套餐购买编号")
    if (no == false) {
        sendText("套餐购买编号-输入超时,取消任务")
        return
    }
    sendText("全部输入完成！如下继续新增账号发送：品赞新增")
    var data = {
        loginPassword: loginPassword,
        userId: userId,
        signKey: signKey,
        extractionKey: extractionKey,
        no: no
    }
    bucketSet("who_zan", phone, JSON.stringify(data))
}
function add_api() {//新增账号

    var phone = ShuRu("请输入品赞api--手机号")
    if (phone == false) {
        sendText("手机号-输入超时,取消任务")
        return
    }
    var loginPassword = ShuRu("请输入品赞--密码")
    if (loginPassword == false) {
        sendText("密码-输入超时,取消任务")
        return
    }
    var userId = ShuRu("请输入品赞--ID 号")
    if (userId == false) {
        sendText("密码-输入超时,取消任务")
        return
    }
    var signKey = ShuRu("请输入品赞--签名秘钥")
    if (signKey == false) {
        sendText("签名秘钥-输入超时,取消任务")
        return
    }
    var extractionKey = ShuRu("请输入品赞--套餐提取密匙")
    if (extractionKey == false) {
        sendText("套餐提取密匙-输入超时,取消任务")
        return
    }
    var no = ShuRu("请输入品赞--套餐购买编号")
    if (no == false) {
        sendText("套餐购买编号-输入超时,取消任务")
        return
    }
    sendText("全部输入完成！如下继续新增账号发送：品赞新增")
    var data = {
        loginPassword: loginPassword,
        userId: userId,
        signKey: signKey,
        extractionKey: extractionKey,
        no: no
    }
    bucketSet("who_zan", phone, JSON.stringify(data))
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
mian()
