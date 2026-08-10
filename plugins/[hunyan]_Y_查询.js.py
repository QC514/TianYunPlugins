// [title: Y_查询]
// [author: hunyan]
//[language: nodejs]
//[class: 查询类]
//[service: 2946148573] 售后联系方式
//[disable:false] 禁用开关，true表示禁用，false表示可用
//[admin: false] 是否为管理员指令
//[rule: ?] 匹配规则，多个规则时向下依次写多个
//[cron: 0 0 0 0 0] cron定时，支持5位域和6位域
//[priority: 100] 优先级，数字越大表示优先级越高
//[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
//[open_source: false]是否开源
//[icon: https://bbs.autman.cn/assets/files/2024-01-09/1704801305-15693-y.png]图标链接地址，请使用48像素的正方形图标，支持http和https
//[version: 2.1.1]版本号
//[public:true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
//[price: 2.7] 上架价格
//[description: 2.1.1修复E卡数量较多时数据不对的问题,路由方式查询使用缓存的昵称。<br />2.1.0修复部分失效查询，删除plus分查询，新增省钱币，汪贝，健康能量查询，新增昵称缓存，修复部分已知bug<br />2.0.8压缩sign和h5st，减小插件体积<br />2.0.7自动安装缺失的依赖<br />2.0.6修复某个ck未找到时直接结束的问题<br />2.0.5低版本nodejs的replaceAll报错问题<br />2.0.4修复新农场奖励不显示，修复玩一玩奖票<br />2.0.2修复小bug<br />全新的2.0版本，支持了代理请求，支持自定义查询内容，新增京豆明细。使用请确保触发规则是? 本插件通过旁路处理，不会影响其他插件处理。尽量使用新版本的autMan(最好大于2.8.3)，低版本不保证使用体验(低于2.6.5版本不支持青龙查找ck进行查询)。] 使用方法尽量写具体
// [router: /jd/Query]
// [method: get]
//[bypass: true]是否通过旁路并行处理
// [param: {"required":true,"key":"Y_Query.detail","placeholder":"","name":"京豆明细触发指令","desc":"京豆明细触发指令，多个指令用逗号分隔"}]
// [param: {"required":true,"key":"Y_Query.info","placeholder":"","name":"资产查询触发指令","desc":"资产查询触发指令，多个指令用逗号分隔"}]
// [param: {"required":false,"key":"Y_Query.queryall","placeholder":"","bool":true,"name":"默认全部查询","desc":"是否开启默认全部查询，开启后不会提示选择查询账号直接查询当前账号下的全部京东账号资产"}]
// [param: {"required":false,"key":"Y_Query.usecachenick","placeholder":"","bool":true,"name":"使用缓存昵称","desc":"开启后在选择查询账号时显示缓存的昵称"}]
// [param: {"required":true,"key":"Y_Query.notice","placeholder":"","name":"绑定提示","desc":"用户未绑定京东账号的提示"}]
// [param: {"required":true,"key":"Y_Query.invalid","placeholder":"","name":"失效提示","desc":"查询时用户Cookie失效的提示"}]
// [param: {"required":false,"key":"Y_Query.qlname","placeholder":"","name":"青龙容器","desc":"后台->容器管理-->对接容器显示的序号。(兼容性保留，填写下方名称时此处填写不生效)"}]
// [param: {"required":false,"key":"Y_Query.qlnames","placeholder":"","name":"青龙容器","desc":"后台->容器管理-->对接容器显示的名称。"}]
// [param: {"required":true,"key":"Y_Query.usertoken","placeholder":"","name":"http请求token","desc":"本插件可作为路由插件，请求地址【http://ip:端口/jd/Query】，get请求，cookie、token和type作为参数(cookie必须url编码)，传入token必须与此处填写一致,type:0查询京豆明细，1查询资产。（这里乱填即可）"}]
//[param: {"spliter":true}]
// [param: {"required":false,"key":"Y_Query.qlonly","placeholder":"","bool":true,"name":"仅使用青龙查询","desc":"开启时，不从缓存桶中查找Cookie"}]
//[param: {"spliter":true}]
// [param: {"required":false,"key":"Y_Query.proxy","placeholder":"","bool":true,"name":"启用代理","desc":"启用时使用代理进行请求，支持隧道代理(代理池)暂不支持密码"}]
// [param: {"required":false,"key":"Y_Query.proxyip","placeholder":"","name":"代理ip","desc":"隧道代理/代理池的ip，使用autMan本机代理池时可填写127.0.0.1"}]
// [param: {"required":false,"key":"Y_Query.proxyport","placeholder":"","name":"代理端口","desc":"隧道代理/代理池的端口"}]
//[param: {"spliter":true}]
// [param: {"required":false,"key":"Y_Query.jingxiang","placeholder":"","bool":true,"name":"京享值","desc":"查询京享值"}]
// [param: {"required":false,"key":"Y_Query.jingdou","placeholder":"","bool":true,"name":"京豆","desc":"查询京豆"}]
// [param: {"required":false,"key":"Y_Query.eka","placeholder":"","bool":true,"name":"E卡","desc":"查询E卡"}]
// [param: {"required":false,"key":"Y_Query.chaoshika","placeholder":"","bool":true,"name":"超市卡","desc":"查询超市卡"}]
// [param: {"required":false,"key":"Y_Query.wangbei","placeholder":"","bool":true,"name":"汪贝","desc":"查询汪贝"}]
// [param: {"required":false,"key":"Y_Query.huafeijifen","placeholder":"","bool":true,"name":"话费积分","desc":"查询话费积分"}]
// [param: {"required":false,"key":"Y_Query.wanyiwan","placeholder":"","bool":true,"name":"玩一玩","desc":"查询玩一玩奖票"}]
// [param: {"required":false,"key":"Y_Query.jdh","placeholder":"","bool":true,"name":"健康能量","desc":"查询健康能量"}]
// [param: {"required":false,"key":"Y_Query.shengqianbi","placeholder":"","bool":true,"name":"省钱币","desc":"查询省钱币"}]
// [param: {"required":false,"key":"Y_Query.zhongdou","placeholder":"","bool":true,"name":"种豆得豆","desc":"查询种豆得豆"}]
// [param: {"required":false,"key":"Y_Query.nongchang","placeholder":"","bool":true,"name":"东东农场","desc":"查询东东农场"}]
// [param: {"required":false,"key":"Y_Query.xinnongchang","placeholder":"","bool":true,"name":"新农场","desc":"查询新农场"}]
// [param: {"required":false,"key":"Y_Query.shiyong","placeholder":"","bool":true,"name":"试用","desc":"查询试用"}]
// [param: {"required":false,"key":"Y_Query.linqi","placeholder":"","bool":true,"name":"临期京豆","desc":"查询临期京豆"}]
// [param: {"required":false,"key":"Y_Query.hongbao","placeholder":"","bool":true,"name":"红包","desc":"查询红包"}]

// 检测axios安装情况
let dtest = testDependency("axios");
if (!dtest) {
    // 安装axios
    let res = installDependency("axios");
    console.log(res);
}

// 引入中间件模块
const { Sender, getSenderID, notifyMasters,bucketKeys, bucketSet} = require('./middleware.js');
// 获取发送者ID
const senderID = getSenderID();
let { getImtype, getUserID, reply, listen, getRouterParams, bucketGet, getMessage, setContinue, bucketAll,bucketAllKeys } = new Sender(senderID);
const axios = require('axios');
const CryptoJS = require('crypto-js');
const {Agent} = require("node:https");
const qs = require('qs');
const bucketN = "Query";
if (!bucketAll) {
    bucketAll = mybucketAll;
}
if((typeof String.prototype.replaceAll) !== 'function'){
    String.prototype.replaceAll = function (s1, s2) {
        return this.replace(new RegExp(s1, "gm"), s2);
    };
}
let useProxy = false;
let proxyip = "";
let proxyport = 0;
let queryList = {};
// 青龙面板操作
class Qinglong {

    constructor(ql_ipport, client_id, client_secret) {
        this.ql_ipport = ql_ipport;
        this.client_id = client_id;
        this.client_secret = client_secret;
        this.token = ""
    }

    async getToken() {
        //连接青龙获取token
        const qltoken = await this.request({
            // 内置http请求函数
            url:
                this.ql_ipport +
                "/open/auth/token?client_id=" +
                this.client_id +
                "&client_secret=" +
                this.client_secret,
            //请求链接
            method: "get",
            //请求方法
        });
        this.token = qltoken.data.token;
    }

    async request(options) {
        const axios = require('axios');
        const config = {
            url: options.url,//地址
            headers: options.headers ? options.headers : undefined,
            method: options.method ? options.method : "get",//网络请求方法get,post,put,delete
            data: options.body ? options.body : "",
            timeout: 30000//单位为毫秒ms，也可以都小写timeout
        }
        try {
            let res = await axios(config)
            return res.data
        } catch (error) {
            console.log(error);
            return false
        }
    }

    async ApiQL(api, apd, method, body = "") {
        if (!this.token) {
            console.log("进入获取token");
            await this.getToken()
        }
        const url = this.ql_ipport + "/open/" + api + apd
        const json = await this.request({
            url: url,
            method: method,
            headers: {
                "Content-Type": "application/json;charset=UTF-8",
                Authorization: "Bearer " + this.token,
            },
            body: body ? body : {},
        });
        return json
    }
};

class jdSign {
    sign(functionId, body, client = "android", clientVersion = '12.2.0') {
        let eid = this.randomeid()
        if (body.hasOwnProperty("eid")) {
            eid = body.eid
        }
        body = JSON.stringify(body)
        const {ep, ts, jduuid, d_brand} = this.getep()
        const version = [[0, 2], [1, 1], [2, 0]];
        const r1r2 = version[Math.floor(Math.random() * version.length)];
        const r1 = r1r2[0];
        const r2 = r1r2[1];
        const sv = "1" + r1 + r2;
        const all_arg = `functionId=${functionId}&body=${body}&uuid=${jduuid}&client=${client}&clientVersion=${clientVersion}&st=${ts}&sv=${sv}`;
        const by = this.stringToBytes(all_arg)
        const back_base64 = this.sign_core(by)
        const sign = CryptoJS.MD5(back_base64).toString();
        const ext = encodeURIComponent('{"prstate":"0","pvcStu":"1"}');
        const partner = d_brand.toLowerCase();
        const convertUrl = `body=${encodeURIComponent(body)}&clientVersion=${clientVersion}&build=98935&client=${client}&partner=${partner}&sdkVersion=31&lang=zh_CN&harmonyOs=0&networkType=wifi&ext=${ext}&oaid=${jduuid}&eid=${eid}&ef=1&ep=${encodeURIComponent(ep)}&st=${ts}&sign=${sign}&sv=${sv}`;
        return {
            fn: functionId,
            body: convertUrl,
            data: {
                functionId,
                body,
                clientVersion,
                client,
                partner,
                sdkVersion: '31',
                lang: 'zh_CN',
                harmonyOs: '0',
                networkType: 'wifi',
                ext,
                oaid: jduuid,
                eid,
                ef: '1',
                ep: encodeURIComponent(ep),
                st: ts,
                sign,
                sv,
                convertUrl,
            },
        };
    }

    sign_core(inarg) {
        let key = this.stringToBytes('80306f4370b39fd5630ad0529f77adb6')
        let mask = [0x37, 0x92, 0x44, 0x68, 0xA5, 0x3D, 0xCC, 0x7F, 0xBB, 0xF, 0xD9, 0x88, 0xEE, 0x9A, 0xE9, 0x5A]
        let array = []
        for (let i = 0; i < inarg.length; i++) {
            let r0 = inarg[i]
            let r2 = mask[i & 0xf]
            let r4 = key[i & 7]
            r0 = r2 ^ r0
            r0 = r0 ^ r4
            r0 = r0 + r2
            r2 = r2 ^ r0
            let r1 = key[i & 7]
            r2 = r2 ^ r1
            array[i] = r2 & 0xff
        }
        // console.log(array)
        return this.base64(array)
    }

    bytesToString(params, ascii) { //该方法只适用于utf-8编码和ascii编码,参数为byte数组
        var result = "";
        if (ascii) {
            for (var i = 0; i < params.length; i++) {
                result += String.fromCharCode(params[i]);
            }
            return result;
        }
        for (var i = 0; i < params.length; i++) {
            if (params[i] >= 0xf8) { //超过0xf8=11111000,属于不合法字符
                result += String.fromCharCode(params[i]);
            } else if (params[i] >= 0xf0) { //0xf0=11110000,表示该起始字节有3个后续字节
                var bits = (params[i] & 0x07) << 18 | (params[i + 1] & 0x3f) << 12 | (params[i + 2] & 0x3f) << 6 | (params[i + 3] & 0x3f);
                result += String.fromCharCode(bits);
                i += 3;
            } else if (params[i] >= 0xe0) { //0xe0=11100000,表示该起始字节有2个后续字节
                var bits = (params[i] & 0x0f) << 12 | (params[i + 1] & 0x3f) << 6 | (params[i + 2] & 0x3f);
                result += String.fromCharCode(bits);
                i += 2;
            } else if (params[i] >= 0xc0) { //0xc0=11000000,表示该起始字节有1个后续字节
                var bits = (params[i] & 0x1f) << 6 | (params[i + 1] & 0x3f);
                result += String.fromCharCode(bits);
                i++;
            } else { //[227,132,128],[194,128]的情形已经融入到上面的判断语句中
                result += String.fromCharCode(params[i]);
            }
        }
        return result;
    }

    base64(params, ascii) { //将byte数组(或字符串)转换成base64
        var BASE64C = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 43, 47];
        if (params == null) return null;
        if (typeof params === "string") params = stringToBytes(params, ascii); //该方法只适用于utf-8编码和ascii编码
        var result = new Array(); //每3个字节一组,重组为4个字节一组
        var index = 0;
        for (var i = 0; i < parseInt(params.length / 3) * 3; i += 3) { //除3取整再乘3可以取到最后面的3的倍数个
            var bits = (params[i] & 0xff) << 16 | (params[i + 1] & 0xff) << 8 | (params[i + 2] & 0xff); //&0xff表示由byte转int,<<表示向左移多少位,高位会被丢弃,低位会补0
            result[index++] = BASE64C[(bits >>> 18) & 0x3f]; //&0x3f表示保留6位数(类似对64求余),>>表示向右移多少位,低位会被丢弃,高位补0(无符号)或1(有符号),>>>表示向右移多少位,高位补0(无符号)
            result[index++] = BASE64C[(bits >>> 12) & 0x3f];
            result[index++] = BASE64C[(bits >>> 6) & 0x3f];
            result[index++] = BASE64C[bits & 0x3f];
        }
        if (params.length % 3 == 1) { //多余1个加两个=号
            var bits = (params[params.length - 1] & 0xff) << 4;
            result[index++] = BASE64C[(bits >>> 6) & 0x3f];
            result[index++] = BASE64C[bits & 0x3f];
            result[index++] = 61; //stringToBytes('=')
            result[index] = 61;
        } else if (params.length % 3 == 2) { //多余2个加一个=号
            var bits = (params[params.length - 2] & 0xff) << 10 | (params[params.length - 1] & 0xff) << 2;
            result[index++] = BASE64C[(bits >>> 12) & 0x3f];
            result[index++] = BASE64C[(bits >>> 6) & 0x3f];
            result[index++] = BASE64C[bits & 0x3f];
            result[index] = 61;
        }
        return this.bytesToString(result);
    }

    stringToBytes(param, ascii) { //该方法只适用于utf-8编码和ascii编码(适用于生成文件),参数为string
        var bytes = [];
        if (ascii) {
            for (var i = 0; i < param.length; i++) {
                bytes.push(param.charCodeAt(i));
            }
            return bytes;
        }
        for (var i = 0; i < param.length; i++) {
            var c = param.charCodeAt(i);
            if (c == 0) { //兼容ascii编码向utf8转码,一般用不到
                bytes.push(0xe3); //0xe3=227
                bytes.push(0x84); //0x84=132
                bytes.push(0x80); //0x80=128
            } else if (c < 0x80) { //c < 128,首位为0,剩余7位
                bytes.push(c);
            } else if (c < 0x100) { //c < 256,兼容ascii编码向utf8转码,一般用不到
                bytes.push(0xc2); //0xc2=194
                bytes.push(c);
            } else if (c < 0x800) { //c < 2048,首位为110,表示该起始字节有1个后续字节,剩余5位
                bytes.push(((c >> 6) & 0x1f) | 0xc0); //0xC0=11000000,&0x1f表示取低5位(高位补0)
                bytes.push((c & 0x3f) | 0x80); //0x80=10000000,&0x3f表示取低6位(对64求余)
            } else if (c < 0x10000) { //c < 65536,首位为1110,表示该起始字节有2个后续字节,剩余4位
                bytes.push(((c >> 12) & 0x0f) | 0xe0); //0xE0=11100000,&0x0f表示取低4位(对16求余,高位补0)
                bytes.push(((c >> 6) & 0x3f) | 0x80);
                bytes.push((c & 0x3f) | 0x80);
            } else if (c < 0x10ffff) { //c < 2097152,首位为11110,表示该起始字节有3个后续字节,剩余3位
                bytes.push(((c >> 18) & 0x07) | 0xf0); //0xF0=11110000,&0x07表示取低3位(高位补0)
                bytes.push(((c >> 12) & 0x3f) | 0x80);
                bytes.push(((c >> 6) & 0x3f) | 0x80);
                bytes.push((c & 0x3f) | 0x80);
            } else return null; //超过0x10ffff,属于不合法字符
        }
        return bytes;
    }

    randomeid() {
        return "eidAaf8081218as20a2GM" + this.randomstr(20) + "7FnfQYOecyDYLcd0rfzm3Fy2ePY4UJJOeV0Ub840kG8C7lmIqt3DTlc11fB/s4qsAP8gtPTSoxu"
    }

    randomstr(num) {
        let string = '';
        let str1 = "abcdefghijklmnopqrstuvwxyz0123456789"
        for (let i = 0; i < num; i++) {
            string += str1.charAt(Math.floor(Math.random() * str1.length));
        }
        return string;
    }

    uuidv1() {
        return `${this.randomhex(8)}-${this.randomhex(4)}-${this.randomhex(4)}-${this.randomhex(4)}-${this.randomhex(12)}`
    }

    randomhex(num) {
        let string = '';
        let str1 = "abcdef0123456789"
        for (let i = 0; i < num; i++) {
            string += str1.charAt(Math.floor(Math.random() * str1.length));
        }
        return string;
    }

    randomnum(num) {
        let string = '';
        let str1 = "0123456789"
        for (let i = 0; i < num; i++) {
            string += str1.charAt(Math.floor(Math.random() * str1.length));
        }
        return string;
    }

    base64Encode(str) {
        const b64s = Buffer.from(str, "utf-8").toString("base64")
        return this.translate(b64s, "KLMNOPQRSTABCDEFGHIJUVWXYZabcdopqrstuvwxefghijklmnyz0123456789+/", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/")
    }

    translate(str, str1, str2) {
        let str3 = ''
        for (let i = 0; i < str.length; i++) {
            for (let j = 0; j < str1.length; j++) {
                if (str[i] === str1[j]) {
                    str3 += str2[j]
                }
            }
        }
        return str3
    }

    getep() {
        let jduuid = this.uuidv1().replace(/-/g, '').slice(0, 16)
        let ts = Date.now()
        let area = this.randomnum(2) + '_' + this.randomnum(4) + '_' + this.randomnum(5) + '_' + this.randomnum(4)
        const d_brand_model = {
            "OPPO": ["PAFM00", "PDEM10", "PDRM00", "PENM00", "PGW110"],
            "Xiaomi": ["23078PND5G", "2211133C", "M1902F1A"],
            "HUAWEI": ["LIO-AL00", "OCE-AN10", "JER-AN20", "RTE-AL00"]
        }
        const d_brand = Object.keys(d_brand_model)[Math.floor(Math.random() * (Object.keys(d_brand_model).length))]
        const d_model = d_brand_model[d_brand][Math.floor(Math.random() * (d_brand_model[d_brand].length))]
        const wifiBssid = `TP_LINK_${this.randomstr(6)}`
        const osVersion = ["10", "11", "12"][Math.floor(Math.random() * (["10", "11", "12"].length))]
        const screen = ["640x1136", "750x1334", "1080x1920"][Math.floor(Math.random() * (["640x1136", "750x1334", "1080x1920"].length))]
        const ep = JSON.stringify({
            "hdid": "JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=",
            "ts": ts,
            "ridx": -1,
            "cipher": {
                "area": this.base64Encode(area),
                "d_model": this.base64Encode(d_model),
                "wifiBssid": this.base64Encode(wifiBssid),
                "osVersion": this.base64Encode(osVersion),
                "d_brand": this.base64Encode(d_brand),
                "screen": this.base64Encode(screen),
                "uuid": this.base64Encode(jduuid),
                "aid": this.base64Encode(jduuid),
                "openudid": this.base64Encode(jduuid)
            },
            "ciphertype": 5,
            "version": "1.2.0",
            "appname": "com.jingdong.app.mall",
        })
        return {ep, ts, jduuid, d_brand}
    }
}

class H5ST43 {
    constructor(ua,pin) {
        this.ua = ua;
        this.pin = pin;
    }
    async h5st(functionId,appId,body,appid) {
        const {timems: fmtTime, ts} = this.getFmtTime();
        const fp = this.getfp();
        let rdm = this.getRdm({
            "size": 10,
            "dictType": "max",
            "customDict": null
        })
        const bb = "4.3";
        let rbparamt = {
            "wc": 1,
            "wd": 0,
            "l": "zh-CN",
            "ls": "zh-CN,en-US",
            "ml": 0,
            "pl": 0,
            "av": this.ua.match(/M\/5\.0.+/)[0],
            "ua": this.ua,
            "sua": this.ua.match(/Mozilla\/5.0 \((.*?)\)/)[1],
            "pp": {},
            "extend": {
                "wd": 0,
                "l": 0,
                "ls": 0,
                "wk": 0,
                "bu1": "0.1.5",
                "bu2": 0,
                "bu3": 14,
                "bu4": 0
            },
            "pp1": "",
            "w": 407,
            "h": 904,
            "ow": 407,
            "oh": 810,
            "pr": 3,
            "re": "",
            "random": rdm,
            "referer": "",
            "v": "h5_file_v4.3.3",
            "ai": appId,
            "fp": fp
        }
        const rbparam = this.tkAes(rbparamt)
        const rdts = Date.now()
        const rdb = {
            "version": "4.3",
            "fp": fp,
            "appId": appId,
            "timestamp": rdts,
            "platform": "web",
            "expandParams": rbparam,
            "fv": "h5_file_v4.3.3"
        }
        const algoRes = await this.getRdAndTk(rdb)
        let tk = algoRes.data.result.tk
        let algo = algoRes.data.result.algo
        let rd = algo.match(/rd='(\S*)';/)[1];
        const text1 = tk + fp + fmtTime + "22" + appId + rd
        const ey5s = this.algoVm(functionId,algo,text1,body,appid,tk)
        const ey5 = ey5s.ey5
        const fts = ey5s.ts
        const ey8Data = JSON.stringify({
            "sua": this.ua.match(/Mozilla\/5.0 \((.*?)\)/)[1],
            "pp": {
                "p1": this.pin
            },
            "extend": {
                "wd": 0,
                "l": 0,
                "ls": 0,
                "wk": 0,
                "bu1": "0.1.5",
                "bu2": -1,
                "bu3": 14,
                "bu4": 0
            },
            "random": rdm,
            "v": "h5_file_v4.3.3",
            "fp": fp
        }, null, 2)
        const ey8 = await this.ey8Aes(ey8Data);
        const h5st43 = `${fmtTime};${fp};${appId};${tk};${ey5};${bb};${ts};${ey8}`
        return {h5st:h5st43,t:fts}
    }

    algoVm(functionId,algo,text1,body,appid,tk=""){
        let ey1 = "";
        switch (algo.match(/return algo.(\S*)}/)[1]) {
            case "HmacMD5(str,tk);":
                ey1 = CryptoJS.HmacMD5(text1, tk).toString()
                // console.log("这是第一次HmacMD5:" + ey1)
                break
            case "MD5(str);":
                ey1 = CryptoJS.MD5(text1).toString()
                // console.log("这是第一次MD5:" + ey1)
                break
            case "HmacSHA256(str,tk);":
                ey1 = CryptoJS.HmacSHA256(text1, tk).toString()
                // console.log("这是第一次Hmacsha256:" + ey1)
                break
            case "HmacSHA512(str,tk);":
                ey1 = CryptoJS.HmacSHA512(text1, tk).toString()
                // console.log("这是第一次Hmacsha512:" + ey1)
                break
            case "SHA256(str);":
                ey1 = CryptoJS.SHA256(text1).toString()
                // console.log("这是第一次sha256:" + ey1)
                break
            case "SHA512(str);":
                ey1 = CryptoJS.SHA512(text1).toString()
                // console.log("这是第一次sha512:" + ey1)
                break
            default:
                ey1 = CryptoJS.HmacSHA512(text1, tk).toString()
                console.log("这是默认Hmacsha512:" + ey1)
                console.log(algo.match(/return algo.(\S*)}/)[1]);
        }
        const signBody = CryptoJS.SHA256(JSON.stringify(body)).toString()
        const ts = Date.now();
        const text2 = `appid:${appid}&body:${signBody}&client:android&clientVersion:12.2.0&functionId:${functionId}`
        // const text2 = `appid:${appid}&body:${signBody}&functionId:${functionId}`
        const ey5 = CryptoJS.HmacSHA256(text2,ey1).toString();
        return {ey5,ts}
    }

    getFmtTime() {
        const date = new Date();
        const year = date.getFullYear();
        const mon = ("0" + (date.getMonth() + 1)).slice(-2);
        const da = ("0" + date.getDate()).slice(-2);
        const h = ("0" + date.getHours()).slice(-2);
        const m = ("0" + date.getMinutes()).slice(-2);
        const s = ("0" + date.getSeconds()).slice(-2);
        const ms = ("0" + date.getMilliseconds()).slice(-3);
        const timems = "" + year + mon + da + h + m + s + ms;
        const ts = date.getTime();
        return {timems, ts};
    }
    getfp() {
        function iC() {
            const X = "kl9i1uct6d";
            const U = aC(X, 3);
            const et = uC();
            const J = fC(X, U);
            const Q = {size: et, num: J};
            const $ = cC(Q) + U + cC({
                size: 12 - et, num: J,
            }) + et;
            const Z = $.split("");
            const tt = Array.prototype.slice.call(Z, 0, 10);
            const V = Array.prototype.slice.call(Z, 10);
            var nt = [];
            for (; tt.length > 0;) nt.push((35 - parseInt(tt.pop(), 36)).toString(36));
            nt = Array.prototype.concat(nt, V);
            return nt.join("");
        }

        function aC(t, r) {
            var D, B = [], j = t.length, _ = tC(t);
            try {
                for (_.s(); !(D = _.n()).done;) {
                    var M = D.value;
                    if (Math.random() * j < r && (B.push(M), --r == 0)) break;
                    j--;
                }
            } catch (t) {
                _.e(t);
            } finally {
                _.f();
            }
            for (var E = "", O = 0; O < B.length; O++) {
                var P = (Math.random() * (B.length - O)) | 0;
                (E += B[P]), (B[P] = B[B.length - O - 1]);
            }
            return E;
        }

        function uC() {
            return (10 * Math.random()) | 0;
        }

        function fC(t, r) {
            for (var d = 0; d < r.length; d++) {
                var y = Array.prototype.indexOf.call(t, r[d]);
                y !== -1 && (t = t.replace(r[d], ""));
            }
            return t;
        }

        function cC(t) {
            var _ = t.size, g = t.num;
            for (var y = ""; _--;) y += g[(Math.random() * g.length) | 0];
            return y;
        }

        function tC(t, r) {
            var nt;
            if (typeof Object.Symbol === "undefined" || null == t[Symbol.iterator]) {
                if (Array.isArray(t) || (nt = rC(t)) || (r && t && typeof t.length === "number")) {
                    nt && (t = nt);
                    var tt = 0, rt = function () {
                    };
                    return {
                        s: rt, n: function () {
                            var r = {};
                            if (((r.done = !0), tt >= t.length)) return r;
                            var e = {};
                            return (e.done = !1), (e.value = t[tt++]), e;
                        }, e: function (t) {
                            throw t;
                        }, f: rt,
                    };
                }
                throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
            }
            var et, ot = !0, it = !1;
            return {
                s: function () {
                    nt = t[Symbol.iterator]();
                }, n: function () {
                    var n = nt.next();
                    return (ot = n.done), n;
                }, e: function (t) {
                    (it = !0), (et = t);
                }, f: function () {
                    try {
                        !ot && nt.return != null && nt.return();
                    } finally {
                        if (it) throw et;
                    }
                },
            };
        }

        function rC(t, r) {
            if (!t) return;
            if (typeof t === "string") return nC(t, r);
            var D = t.slice(8, -1);
            D === "Object" && t.constructor && (D = t.constructor.name);
            if (D === "Map" || D === "Set") return Array.from(t);
            if ("Arguments" === D || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/["test"](D)) return nC(t, r);
        }

        function nC(t, r) {
            (r == null || r > t.length) && (r = t.length);
            for (var h = 0, l = new Array(r); h < r; h++) l[h] = t[h];
            return l;
        }

        return iC()
    }
    getRdm() {
        var t, r = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {}, n = r.size,
            e = void 0 === n ? 10 : n, o = r.dictType, i = void 0 === o ? "number" : o, u = r.customDict, a = "";
        if (u && "string" == typeof u) t = u; else switch (i) {
            case "alphabet":
                t = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
                break;
            case "max":
                t = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-";
                break;
            default:
                t = "0123456789";
        }
        for (; e--;) a += t[(Math.random() * t.length) | 0];
        return a;
    }
    tkAes(word) {
        let srcs;
        const key = CryptoJS.enc.Utf8.parse('wm0!@w-s#ll1flo(');
        const iv = CryptoJS.enc.Utf8.parse('0102030405060708');
        let encrypted = '';
        if (typeof (word) == 'string') {
            srcs = CryptoJS.enc.Utf8.parse(word);
            encrypted = CryptoJS.AES.encrypt(srcs, key, {
                iv: iv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            });
        } else if (typeof (word) == 'object') {//对象格式的转成json字符串
            let data = JSON.stringify(word);
            srcs = CryptoJS.enc.Utf8.parse(data);
            encrypted = CryptoJS.AES.encrypt(srcs, key, {
                iv: iv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            })
        }
        return encrypted.ciphertext.toString();
    }
    ey8Aes(word) {
        let srcs;
        const key = CryptoJS.enc.Utf8.parse('&d74&yWoV.EYbWbZ');
        const iv = CryptoJS.enc.Utf8.parse('0102030405060708');
        let encrypted = '';
        if (typeof (word) == 'string') {
            srcs = CryptoJS.enc.Utf8.parse(word);
            encrypted = CryptoJS.AES.encrypt(srcs, key, {
                iv: iv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            });
        } else if (typeof (word) == 'object') {//对象格式的转成json字符串
            let data = JSON.stringify(word);
            srcs = CryptoJS.enc.Utf8.parse(data);
            encrypted = CryptoJS.AES.encrypt(srcs, key, {
                iv: iv,
                mode: CryptoJS.mode.CBC,
                padding: CryptoJS.pad.Pkcs7
            })
        }
        // console.log(encrypted.ciphertext.toString())
        return encrypted.ciphertext.toString();
    }
    async getRdAndTk(body) {
        const options = {
            url: 'https://cactus.jd.com/request_algo?g_ty=ajax',
            headers: {
                "accept": "application/json",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "no-cache",
                "content-type": "application/json",
                "pragma": "no-cache",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "x-requested-with": "com.jd.jdlite",
                "Referer": "https://bnzf.jd.com/",
                "Referrer-Policy": "strict-origin-when-cross-origin"
            },
            data: JSON.stringify(body)
        };
        return await this.reqpost(options);

    }
    reqpost(options) {
        return new Promise((resolve, reject) => {
            options.method = "POST"
            if(useProxy){
                options.proxy = {
                    host: proxyip,
                    port: proxyport,
                    protocol: 'http'
                }
            }
            axios(options)
                .then(response => {
                    resolve(response.data);
                })
                .catch(error => {
                    reject(error);
                });
        });
    }
}

class UserAgent {
    UARAM(tjb = false) {
        const dictionary = {
            "A": "K",
            "B": "L",
            "C": "M",
            "D": "N",
            "E": "O",
            "F": "P",
            "G": "Q",
            "H": "R",
            "I": "S",
            "J": "T",
            "K": "A",
            "L": "B",
            "M": "C",
            "N": "D",
            "O": "E",
            "P": "F",
            "Q": "G",
            "R": "H",
            "S": "I",
            "T": "J",
            "e": "o",
            "f": "p",
            "g": "q",
            "h": "r",
            "i": "s",
            "j": "t",
            "k": "u",
            "l": "v",
            "m": "w",
            "n": "x",
            "o": "e",
            "p": "f",
            "q": "g",
            "r": "h",
            "s": "i",
            "t": "j",
            "u": "k",
            "v": "l",
            "w": "m",
            "x": "n"
        };
        const cipher = {
            "ud": "",
            "sv": "",
            "iad": ""
        };
        let sv = this.randomA([12, 13, 14, 15, 16], 1) + "." + this.randomA([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 1) + "." + this.randomA([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 1),
            jdb = this.randomA([10, 11, 12], 1) + "." + this.randomA([0, 1, 2, 3, 4, 5, 6, 7, 8], 1) + "." + this.randomA([0, 1, 2, 3, 4, 5], 1),
            liteb = this.randomA([4, 5, 6], 1) + "." + this.randomA([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 1) + "." + this.randomA([0, 1, 2, 3, 4, 5], 1),
            ep = {
                "ciphertype": 5,
                "cipher": cipher,
                "ts": parseInt(new Date().getTime() / 1000),
                "hdid": "",
                "version": "1.2.0",
                "appname": "",
                "ridx": -1
            };
        ep.cipher.sv = this.base64(sv).split("").map(item => dictionary[item] || item).join("");
        ep.cipher.ud = this.base64(this.randomStr(40)).split("").map(item => dictionary[item] || item).join("");
        ep.appname = "com.jingdong.app.mall";
        ep.hdid = "JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=";
        let jdUa = "jdapp;android;" + "12.2.0" + ";;;M/5.0;appBuild/98990;ef/1;ep/" + encodeURIComponent(JSON.stringify(ep)) + ";jdSupportDarkMode/0;Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046269 Mobile Safari/537.36";
        ep.appname = "com.jd.jdmobilelite";
        ep.hdid = "ViZLFbOc+bY6wW3m9/8iSFjgglIbmHPOGSM9aXIoBes=";
        ep.ridx = 1;
        let liteUa = "jdltapp;android;" + liteb + ";;;M/5.0;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;hasOCPay/0;appBuild/1338;supportBestPay/0;jdSupportDarkMode/0;ef/1;ep/" + encodeURIComponent(JSON.stringify(ep)) + ";Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046269 Mobile Safari/537.36";
        return tjb ? liteUa : jdUa;
    }

    base64(str) {
        return Buffer.from(str, "utf-8").toString("base64");
    }

    randomStr(num) {
        let str = "0123456789abcdef",
            fstr = "";
        for (let i = 0; i < num; i++) {
            fstr += str[Math.ceil(100000000 * Math.random()) % str.length];
        }
        return fstr;
    }

    randomA(arr, num) {
        let narr = new Array();
        for (let arrKey in arr) {
            narr.push(arr[arrKey]);
        }
        let temArr = new Array();
        for (let i = 0; i < num; i++) {
            if (narr.length > 0) {
                let randNum = Math.floor(Math.random() * narr.length);
                temArr[i] = narr[randNum];
                narr.splice(randNum, 1);
            } else {
                break;
            }
        }
        return temArr;
    }
}

class $ {
    get(options, callback = () => {
    }) {
        return new Promise((resolve, reject) => {
            const adaptedOptions = this._adaptToAxiosOptions(options, 'GET');
            axios(adaptedOptions)
                .then(response => {
                    callback(null, response, response.data);
                    resolve(response);
                })
                .catch(error => {
                    callback(error, null, null);
                    resolve(error);
                });
        });
    }

    post(options, callback = () => {
    }) {
        return new Promise((resolve, reject) => {
            const adaptedOptions = this._adaptToAxiosOptions(options, 'POST');
            axios(adaptedOptions)
                .then(response => {
                    callback(null, response, response.data);
                    resolve(response);
                })
                .catch(error => {
                    callback(error, null, null);
                    resolve(error);
                });
        });
    }

    _adaptToAxiosOptions(options, defaultMethod) {
        // 确保options中包含method
        options.method = options.method || defaultMethod;

        options.headers = options.headers || {};

        // 根据HTTP方法调整请求体属性名
        if (options.method.toUpperCase() === 'GET') {
            delete options.data; // GET请求通常不带请求体
        } else {
            options.data = options.body || options.data; // 确保data属性存在
            delete options.body; // 移除可能存在的body属性，避免混淆
        }
        if (useProxy) {
            options.proxy = {
                host: proxyip,
                port: proxyport,
                protocol: 'http'
            }
        }


        return options;
    }
}

class Base {
    constructor(ck, istjb = false) {
        this.Cookie = ck;
        this.$ = new $();
        this.pin = this.Cookie.match(/pt_pin=(.*?);/)[1];
        this.UA = new UserAgent().UARAM(istjb);
        this.sign = new jdSign();
        this.h5st = new H5ST43(this.UA, this.pin);
        // this.apitoken = new XApiEidToken(this.$,this.UA)
        this.eidtoken = "";
    }

    async commonRequestByH5st(functionId, body, appId, appid, extraHeader = {}, myurl = "",st=false,myh5st=this.h5st) {
        const {h5st,t} = await myh5st.h5st(functionId, appId, body, appid)
        const mybody = {
            appid: appid,
            // loginType: 2,
            // loginWQBiz: "",
            screen: "407*859",
            wqDefault: false,
            build: 98990,
            osVersion: 15,
            networkType: "UNKNOWN",
            d_brand: "Redmi",
            d_model: "Redmi K50 Ultra",
            partner: "jingdong",
            functionId: functionId,
            body: JSON.stringify(body),
            client: 'android',
            clientVersion: '12.2.0',
            h5st: h5st,
            'x-api-eid-token': this.eidtoken
        }
        if (st){
            mybody.t = t
        }else {
            mybody.timestamp= t
        }
        const options = {
            url: myurl.length > 9 ? myurl : `https://api.m.jd.com/client.action`,
            headers: {
                'cookie': this.Cookie,
                'user-agent': this.UA,
                "Connection": "keep-alive",
                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'x-requested-with': 'com.jingdong.app.mall'
            },
            body: qs.stringify(mybody),
            httpsAgent: new Agent({
                ciphers: "TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256"
            })
        }
        Object.assign(options.headers, extraHeader)
        // console.log(options)
        return new Promise((resolve, reject) => {
            this.$.post(options, (err, resp, data) => {
                if (err) {
                    resolve(err)
                }
                try {
                    data = JSON.parse(data)
                    resolve(data)
                } catch (e) {
                    resolve(data)
                }
            })
        })
    }

    async commonRequestBySign(functionId, body, extraHeader = {}, myurl = "") {
        // if (this.eidtoken === ""){
        //     this.eidtoken = await this.apitoken.getToken()
        // }
        const sign = this.sign.sign(functionId, body)
        const options = {
            url: myurl.length > 9 ? myurl : `https://api.m.jd.com/client.action?functionId=${functionId}`,
            headers: {
                'cookie': this.Cookie,
                'user-agent': this.UA,
                "Connection": "keep-alive",
                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'x-requested-with': 'com.jingdong.app.mall'
            },
            body: `${sign.body}&x-api-eid-token=${this.eidtoken}`,
            httpsAgent: new Agent({
                ciphers: "TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384"
            })
        }
        Object.assign(options.headers, extraHeader)
        // console.log(options)
        return new Promise((resolve, reject) => {
            this.$.post(options, (err, resp, data) => {
                if (err) {
                    reject(err)
                }
                try {
                    // console.log(resp)
                    data = JSON.parse(data)
                    resolve(data)
                } catch (e) {
                    // console.log(e)
                    resolve(data)
                }
            })
        })
    }
}

class Query extends Base {
    constructor(cookie) {
        super(cookie);
        this.UserName = decodeURIComponent(cookie.match(/pt_pin=([^; ]+)(?=;?)/) && cookie.match(/pt_pin=([^; ]+)(?=;?)/)[1]);
        this.myMap = new Map();
        this.plusDetail = true;
        this.nickName = "";
        this.levelName = "";
        this.beanCount = "";
        this.JingXiang = "";
        this.guoqi = "";
        this.todayIncomeBean = 0;
        this.todayOutcomeBean = 0;
        this.yesterdayIncomeBean = 0;
        this.yesterdayOutcomeBean = 0;
        this.isplus = false;
        this.JdFarmProdName = "";
        this.JdtreeEnergy = 0;
        this.JdtreeTotalEnergy = 0;
        this.TotalEnergy = 0;
        this.treeState = "";
        this.JdwaterD = 0;
        this.newFarminfo = "";
        this.newFarmWater = 0;
        this.redPackmsg = "";
        this.eCardInfo = "";
        this.plustotalScore = "";
        this.plusPeriod = "";
        this.plusAccountInfo = "";
        this.plusBaiScore = ""
        this.plusActive = ""
        this.plusShop = ""
        this.plusShopAfter = ""
        this.hfjifen = "";
        this.jdtrycount = "";
        this.waitdrawname = "";
        this.waitdrawcount = "";
        this.planlastbean = "";
        this.planlastgrowth = "";
        this.plangrowth = "";
        this.plandateDesc = "";
        this.supperMarket = "";
        this.farmAwardsNew = "";
        this.wanyiwanP = 0;
        this.wangBeiUsable = 0;
        this.wangBeiTotal = 0;
        this.wangBeiUsed = 0;
        this.jdhEng = 0;
        this.shengB = 0;
    }

    async beanDetail() {
        await Promise.allSettled([
            this.jingxiang(), // 京享值
            this.userBean(), // 全部京豆
            this.todayBean() // 今日京豆明细
        ])
        let arrayObj = Array.from(this.myMap);
        arrayObj.sort(function (a, b) {
            return a[1] - b[1]
        })
        let msg = `【账号:${this.nickName || this.UserName}】京豆详情统计 收入：${this.todayIncomeBean}京豆\n`
        for (const [key, value] of arrayObj) {
            msg += "【" + value + "豆" + "】 " + key + '\n'
        }
        console.log(msg)
        return msg
    }

    async jdQuery() {
        console.log("Y_查询------>开始查询")
        console.time("Y_查询耗时")
        const querys = [];
        for (const key in queryList) {
            if (Object.hasOwnProperty.call(queryList, key)) {
                const element = queryList[key];
                if (element) {
                    querys.push(this[key]())
                }
            }
        }
        // await Promise.allSettled([
        //     this.jingxiang(), // 京享值
        //     this.isPlus(), // 是否Plus
        //     // this.plusScores(), // Plus分数
        //     this.userBean(),// 全部京豆
        //     this.bean(), // 京豆
        //     this.eCard(), // 京东E卡
        //     this.superMarket(), // 超市卡
        //     this.wangBei(), // 超市汪贝
        //     this.hfJifen(), // 话费积分
        //     this.wanyiwan(), // 玩一玩
        //     this.jdh(),// 健康能量
        //     this.miniSheng(),// 省钱币
        //     this.plantBean(), // 种豆得豆
        //     this.jdFarm(), // 农场
        //     this.jdFarmNew(), // 新农场
        //     this.newFarmAwards(), // 新农场奖励
        //     this.trialCount(), // 试用数量
        //     this.trialWaitdraw(), // 待领取试用
        //     this.beanGuoqi(), //临期京豆
        //     this.redPack(), // 红包
        // ])
        await Promise.allSettled(querys)
        console.log("Y_查询------>查询结束")
        console.timeEnd("Y_查询耗时")
        const rmsg = this.show()
        console.log(rmsg)
        return rmsg
    }


    show() {
        let msg = ""
        msg += `【账号】${this.nickName||this.UserName}`
        if (this.JingXiang){
            msg += `(京享值:${this.JingXiang})`
        }
        msg +='\n'
        if (this.levelName || this.isplus || this.plustotalScore) {
            msg += `【账号信息】`
            if (this.levelName) {
                if (this.levelName.length > 2) {
                    this.levelName = this.levelName.substring(0, 1)
                }
                switch (this.levelName) {
                    case "注":
                        this.levelName = "😊普通"
                        break;
                    case "钻":
                        this.levelName = "💎钻石"
                        break;
                    case "金":
                        this.levelName = "🥇金牌"
                        break;
                    case "银":
                        this.levelName = "🥈银牌"
                        break;
                    case "铜":
                        this.levelName = "🥉铜牌"
                        break;
                }
            }
            if (this.isplus){
                msg += `${this.levelName}Plus会员`
            }else {
                msg += `${this.levelName}会员`
            }
            if (this.plustotalScore){
                msg += `\n✨账号Plus分详情\n【Plus分数】${this.plustotalScore}`
                msg += `\n【分数周期】${this.plusPeriod}`
                if (this.plusDetail){
                    msg += `【账户信息】${this.plusAccountInfo}\n【信用价值】${this.plusBaiScore}\n【购物合规】${this.plusActive}\n【购物历史】${this.plusShop}\n【售后行为】${this.plusShopAfter}`
                }
            }
            msg += '\n'
        }
        msg +=`🍿账户资产\n【今日京豆】收${this.todayIncomeBean}豆`
        if (this.todayOutcomeBean) {
            msg += `,支${this.todayOutcomeBean}豆`
        }
        msg +='\n'
        msg += `【昨日京豆】收${this.yesterdayIncomeBean}豆`
        if (this.yesterdayOutcomeBean){
            msg += `,支${this.yesterdayOutcomeBean}豆`
        }
        msg += '\n'
        if (this.beanCount) {
            msg += `【当前京豆】${this.beanCount}豆(≈${(this.beanCount / 100).toFixed(2)}R)\n`
        }else {
            msg += `【当前京豆】获取失败！\n`
        }
        if (this.eCardInfo){
            msg += `【礼卡余额】${this.eCardInfo}\n`
        }
        if (this.supperMarket){
            msg += `【京东超市】${this.supperMarket}\n`
        }
        if (this.wangBeiTotal){
            msg += `【超市汪贝】可用 ${this.wangBeiUsable} 贝\n`
        }
        if (this.hfjifen){
            msg += `【话费积分】${this.hfjifen}分\n`
        }
        if (this.wanyiwanP){
            msg += `【玩玩奖券】${this.wanyiwanP}券\n`
        }
        if (this.jdhEng){
            msg += `【健康能量】${this.jdhEng}能量\n`
        }
        if (this.shengB){
            msg += `【省钱币】${this.shengB}币\n`
        }
        if (this.planlastbean||this.planlastgrowth||this.plangrowth||this.plandateDesc){
            msg += `【种豆得豆】成长值:${this.plangrowth+","+this.plandateDesc}\n【上期京豆】${this.planlastbean}\n【上期成长】${this.planlastgrowth}\n`
        }
        if (this.JdFarmProdName){
            if (this.JdtreeEnergy){
                if (this.treeState===2||this.treeState===3){
                    msg +=`【东东农场】${this.JdFarmProdName} 可以兑换了！\n【农场水滴】${this.TotalEnergy}滴\n`;
                }else {
                    if (this.JdwaterD.toString()!=="Infinity"&&this.JdwaterD.toString()!=="-Infinity"){
                        msg +=`【东东农场】${this.JdFarmProdName}(${((this.JdtreeEnergy/this.JdtreeTotalEnergy)*100).toFixed(0)}%,${this.JdwaterD}天)\n【农场水滴】${this.TotalEnergy}滴\n`
                    }else {
                        msg +=`【东东农场】${this.JdFarmProdName}(${((this.JdtreeEnergy/this.JdtreeTotalEnergy)*100).toFixed(0)}%)\n【农场水滴】${this.TotalEnergy}滴\n`
                    }
                }
            }else {
                if (this.treeState===1){
                    msg += `【东东农场】${this.JdFarmProdName}种植中...\n【农场水滴】${this.TotalEnergy}滴\n`
                }else {
                    msg += `【东东农场】${this.JdFarmProdName}状态异常${this.treeState}...\n【农场水滴】${this.TotalEnergy}滴\n`
                }
            }
        }
        if (this.newFarminfo){
            msg += `【新东东农场】${this.newFarminfo}\n`
            msg += `【新农场水滴】${this.newFarmWater}滴\n`
        }
        if (this.farmAwardsNew){
            msg += `${this.farmAwardsNew}`
        }
        if (this.jdtrycount){
            msg += `【申请中试用】${this.jdtrycount}件商品申请中,${this.waitdrawcount}件试用待领取\n`
        }
        if (this.waitdrawname){
            msg += `【待领取试用】${this.waitdrawname}\n`
        }
        if (this.guoqi){
            msg += `💸💸💸临期京豆明细💸💸💸\n${this.guoqi}`
        }
        msg += `🧧红包明细\n${this.redPackmsg}`
        return msg
    }

    async todayBean() {
        //前一天的0:0:0时间戳
        const tm = parseInt((Date.now() + 28800000) / 86400000) * 86400000 - 28800000 - (24 * 60 * 60 * 1000);
        // 今天0:0:0时间戳
        const tm1 = parseInt((Date.now() + 28800000) / 86400000) * 86400000 - 28800000;
        let page = 1,
            t = 0,
            todayArr = [];
        const testB = await this.getJingBeanBalanceDetail1(page);
        if (testB && testB.jingDetailList && testB.jingDetailList.length > 0) {
            do {
                let response = await this.getJingBeanBalanceDetail1(page);
                if (response && response.code == 0) {
                    page++;
                    let detailList = response.jingDetailList;
                    if (detailList && detailList.length > 0) {
                        for (let item of detailList) {
                            const date = item.date.replace(/-/g, '/') + "+08:00";
                            if (new Date(date).getTime() >= tm1 && (!item['eventMassage'].includes("退还") && !item['eventMassage'].includes("物流") && !item['eventMassage'].includes('扣赠'))) {
                                todayArr.push(item);
                            } else if (tm > new Date(date).getTime()) {
                                t = 1;
                                break;
                            }
                        }
                    } else {
                        t = 1;
                    }
                } else if (response && response.code === "3") {
                    console.log(`cookie已过期，或者填写不规范，跳出`)
                    t = 1;
                } else {
                    console.log(`未知情况：${JSON.stringify(response)}`);
                    console.log(`未知情况，跳出`)
                    t = 1;
                }
            } while (t === 0);
        } else {
            do {
                let response = await this.getJingBeanBalanceDetail(page);
                if (response && response.code === "0") {
                    page++;
                    let detailList = response.detailList;
                    if (detailList && detailList.length > 0) {
                        for (let item of detailList) {
                            const date = item.date.replace(/-/g, '/') + "+08:00";
                            if (new Date(date).getTime() >= tm1 && (!item['eventMassage'].includes("退还") && !item['eventMassage'].includes("物流") && !item['eventMassage'].includes('扣赠'))) {
                                todayArr.push(item);
                            } else if (tm > new Date(date).getTime()) {
                                t = 1;
                                break;
                            }
                        }
                    } else {
                        t = 1;
                    }
                } else if (response && response.code === "3") {
                    console.log(`cookie已过期，或者填写不规范，跳出`)
                    t = 1;
                } else {
                    console.log(`未知情况：${JSON.stringify(response)}`);
                    console.log(`未知情况，跳出`)
                    t = 1;
                }
            } while (t === 0);
        }
        let strtemp = "";
        for (let item of todayArr) {
            if (Number(item.amount) > 0) {
                this.todayIncomeBean += Number(item.amount);
                strtemp = item.eventMassage;
                strtemp = strtemp.replace("参加[", "").replace("]-奖励", "").replace("]店铺活动-奖励", "");
                strtemp = strtemp.replace("京东自营旗舰店", "(自营)").replace("京东自营官方旗舰店", "(自营官方)");
                strtemp = strtemp.replace("（", "(").replace("）", ")");
                strtemp = strtemp.replace("官方旗舰店", "(官方)");
                strtemp = strtemp.replace("旗舰店", "(旗舰)").replace("专营店", "(专营)").replace("专卖店", "(专卖)");
                this.myMap.set(strtemp, 0)
            }
        }
        for (let item of todayArr) {
            if (Number(item.amount) > 0) {
                strtemp = item.eventMassage;
                strtemp = strtemp.replace("参加[", "").replace("]-奖励", "").replace("]店铺活动-奖励", "");
                strtemp = strtemp.replace("京东自营旗舰店", "(自营)").replace("京东自营官方旗舰店", "(自营官方)");
                strtemp = strtemp.replace("（", "(").replace("）", ")");
                strtemp = strtemp.replace("官方旗舰店", "(官方)");
                strtemp = strtemp.replace("旗舰店", "(旗舰)").replace("专营店", "(专营)").replace("专卖店", "(专卖)");
                this.myMap.set(strtemp, parseInt(this.myMap.get(strtemp)) + parseInt(item.amount))
            }
        }
    }

    async beanGuoqi() {
        try {
            const data = await this.commonRequestBySign("jingBeanDetail", {"pageSize": "20", "page": "1"})
            if (data?.others?.jingBeanExpiringInfo?.detailList) {
                const {detailList = []} = data?.others?.jingBeanExpiringInfo;
                detailList.map(item => {
                    this.guoqi += `【${(item['eventMassage']).replace("即将过期京豆", "").replace("年", "-").replace("月", "-").replace("日", "")}】过期${item['amount']}豆\n`;
                })
            }
        } catch (e) {
            console.log("临期京豆查询 " , e)
        }
    }

    async isPlus() {
        try {
            const data = await this.commonRequestByH5st("user_getUserInfo_v2", {
                "qids": "6_2_5_18_1_7_9_11_12_14_16_17_25",
                "checkLevel": 1,
                "signType": 1003,
                "topicId": 176,
                "contentType": "1_2_3_4_5_8_9_11_12_16_18",
                "skuSourceId": 600008
            },"b63ff","plus_business",{
                'referer': 'https://plus.m.jd.com/index?detainer=1398XHSIWsjshwe12&resourceExportId=1010210',
                'x-referer-page': 'https://plus.m.jd.com/index',
                'origin': 'https://plus.m.jd.com',
                'x-requested-with': 'com.jingdong.app.mall'
            })
            if (data.code === '1711000') {
                this.isplus = !!data.rs.plusUserBaseInfo.endDays;
            }
        } catch (e) {
            console.log("是否开通plus ",e)
        }
    }

    async userBean(){
        let options = {
            url: 'https://lop-proxy.jd.com/JingIntegralApi/userAccount',
            data: JSON.stringify([{ "pin": "$cooMrdGatewayUid$" }]),
            headers: {
                "host": "lop-proxy.jd.com",
                "jexpress-report-time": Date.now().toString(),
                "accept": "application/json, text/plain, */*",
                "accept-encoding": "gzip",
                "lop-dn": "jingcai.jd.com",
                "user-agent": this.UA,
                "cookie": this.Cookie,
                "x-requested-with": "XMLHttpRequest",
                "version": "1.0.0",
                "appparams": "{\"appid\":158,\"ticket_type\":\"m\"}",
                "referer": "https://jingcai-h5.jd.com/",
                "origin": "https://jingcai-h5.jd.com",
                "content-type": "application/json;charset=utf-8",
            }
        }
        const {data} = await this.$.post(options)
        if (data.code === 1) {
            this.beanCount = data.content.jdBean;
        }
    }

    async jingxiang(){
        try{
            const data = await this.commonRequestByH5st("pg_channel_page_data", {"v":"16.3","paramData":{"token":"a243ca12-6642-4754-bc5e-0ff012681710","lid":"Gv8zAj0mnx9iiLgIWfwBEA==","priceChannel":2,"device":0},"argMap":{"channel":"APP","upstreamChannel":"jxz","taskEncId":""}}, "6d239", "vipChannelHome", {
                'referer': 'https://huiyuan.m.jd.com/',
                'origin': 'https://huiyuan.m.jd.com',
                'x-referer-page': 'https://huiyuan.m.jd.com/'
            },"https://api.m.jd.com/client.action")
            // console.log(data)
            const datas = data.data.floorInfoList;
            // console.log(datas)
            this.nickName = datas[1].floorData.userInfo.showName
            this.levelName = datas[1].floorData.userInfo.vipGradeName
            this.beanCount = datas[5].floorData.shoppingBeansParam.currentBeanNum
            this.JingXiang = datas[1].floorData.userInfo.score
        }catch (e) {
            console.log("京享值查询 ",e)
        }
    }

    async getJingBeanBalanceDetail1(page){
        const options = {
            "url": `https://bean.m.jd.com/beanDetail/detail.json?page=${page}`,
            "body": `body=${encodeURIComponent(JSON.stringify({ "pageSize": "20", "page": page.toString() }))}&appid=ld`,
            "headers": {
                'User-Agent': "Mozilla/5.0 (Linux; Android 12; SM-G9880) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36 EdgA/106.0.1370.47",
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': this.Cookie,
            }
        }
        try{
            const {data} = await this.$.post(options)
            return data
        }catch (e) {
            console.log("京豆收入支出查询 ",e)
        }
    }

    async getJingBeanBalanceDetail(page){
        try{
            return await this.commonRequestBySign("getJingBeanBalanceDetail", {
                "pageSize": "20",
                "page": page.toString()
            })
        }catch (e) {
            console.log("京豆收入支出查询 ",e)
        }
    }

    async bean(){
        //前一天的0:0:0时间戳
        const tm = parseInt((Date.now() + 28800000) / 86400000) * 86400000 - 28800000 - (24 * 60 * 60 * 1000);
        // 今天0:0:0时间戳
        const tm1 = parseInt((Date.now() + 28800000) / 86400000) * 86400000 - 28800000;
        let page = 1,
            t = 0,
            yesterdayArr = [],
            todayArr = [];
        const testB = await this.getJingBeanBalanceDetail1(page);
        if (testB && testB.jingDetailList && testB.jingDetailList.length > 0) {
            do {
                let response = await this.getJingBeanBalanceDetail1(page);
                if (response && response.code == 0) {
                    page++;
                    let detailList = response.jingDetailList;
                    if (detailList && detailList.length > 0) {
                        for (let item of detailList) {
                            const date = item.date.replace(/-/g, '/') + "+08:00";
                            if (new Date(date).getTime() >= tm1 && (!item['eventMassage'].includes("退还") && !item['eventMassage'].includes("物流") && !item['eventMassage'].includes('扣赠'))) {
                                todayArr.push(item);
                            } else if (tm <= new Date(date).getTime() && new Date(date).getTime() < tm1 && (!item['eventMassage'].includes("退还") && !item['eventMassage'].includes("物流") && !item['eventMassage'].includes('扣赠'))) {
                                //昨日的
                                yesterdayArr.push(item);
                            } else if (tm > new Date(date).getTime()) {
                                //前天的
                                t = 1;
                                break;
                            }
                        }
                    } else {
                        t = 1;
                    }
                } else if (response && response.code === "3") {
                    console.log(`cookie已过期，或者填写不规范，跳出`)
                    t = 1;
                } else {
                    console.log(`未知情况：${JSON.stringify(response)}`);
                    console.log(`未知情况，跳出`)
                    t = 1;
                }
            } while (t === 0);
        } else {
            do {
                let response = await this.getJingBeanBalanceDetail(page);
                if (response && response.code === "0") {
                    page++;
                    let detailList = response.detailList;
                    if (detailList && detailList.length > 0) {
                        for (let item of detailList) {
                            const date = item.date.replace(/-/g, '/') + "+08:00";
                            if (new Date(date).getTime() >= tm1 && (!item['eventMassage'].includes("退还") && !item['eventMassage'].includes("物流") && !item['eventMassage'].includes('扣赠'))) {
                                todayArr.push(item);
                            } else if (tm <= new Date(date).getTime() && new Date(date).getTime() < tm1 && (!item['eventMassage'].includes("退还") && !item['eventMassage'].includes("物流") && !item['eventMassage'].includes('扣赠'))) {
                                //昨日的
                                yesterdayArr.push(item);
                            } else if (tm > new Date(date).getTime()) {
                                //前天的
                                t = 1;
                                break;
                            }
                        }
                    } else {
                        t = 1;
                    }
                } else if (response && response.code === "3") {
                    console.log(`cookie已过期，或者填写不规范，跳出`)
                    t = 1;
                } else {
                    console.log(`未知情况：${JSON.stringify(response)}`);
                    console.log(`未知情况，跳出`)
                    t = 1;
                }
            } while (t === 0);
        }
        for (let item of yesterdayArr) {
            if (Number(item.amount) > 0) {
                this.yesterdayIncomeBean += Number(item.amount);
            } else if (Number(item.amount) < 0) {
                this.yesterdayOutcomeBean += Number(item.amount);
            }
        }
        for (let item of todayArr) {
            if (Number(item.amount) > 0) {
                this.todayIncomeBean += Number(item.amount);
            } else if (Number(item.amount) < 0) {
                this.todayOutcomeBean += Number(item.amount);
            }
        }
        this.todayOutcomeBean = -this.todayOutcomeBean;
        this.yesterdayOutcomeBean = -this.yesterdayOutcomeBean;
    }

    async jdFarm(){
        try{
            const farm = await Promise.allSettled([
                this.commonRequestByH5st("taskInitForFarm",{"version":26,"channel":1,"babelChannel":"522","lat":"0","lng":"0"},"fcb5a","signed_wh5",{
                    "origin": "https://carry.m.jd.com",
                    "referer": "https://carry.m.jd.com/",
                    "x-referer-page": "https://carry.m.jd.com/babelDiy/Zeus/3KSjXqQabiTuD1cJ28QskrpWoBKT/index.html",
                }),
                this.commonRequestByH5st("initForFarm",{"babelChannel":"522","version":26,"channel":1,"lat":"0","lng":"0"},"8a2af","signed_wh5",{
                    "origin": "https://carry.m.jd.com",
                    "referer": "https://carry.m.jd.com/",
                    "x-referer-page": "https://carry.m.jd.com/babelDiy/Zeus/3KSjXqQabiTuD1cJ28QskrpWoBKT/index.html",
                })
            ])
            const taskInitForFarm = farm[0].status === "fulfilled" ? farm[0].value : null;
            const initForFarm = farm[1].status === "fulfilled" ? farm[1].value : null;
            let JDwaterEveryDayT = 0;
            if (taskInitForFarm){
                JDwaterEveryDayT = taskInitForFarm.totalWaterTaskInit.totalWaterTaskTimes;
            }
            if (initForFarm){
                if (initForFarm.farmUserPro) {
                    this.JdFarmProdName = initForFarm.farmUserPro.name;
                    this.JdtreeEnergy = initForFarm.farmUserPro.treeEnergy;
                    this.JdtreeTotalEnergy = initForFarm.farmUserPro.treeTotalEnergy;
                    this.TotalEnergy = initForFarm.farmUserPro.totalEnergy
                    this.treeState = initForFarm.treeState;
                    const waterTotalT = (initForFarm.farmUserPro.treeTotalEnergy - initForFarm.farmUserPro.treeEnergy - initForFarm.farmUserPro.totalEnergy) / 10; //一共还需浇多少次水
                    const waterD = Math.ceil(waterTotalT / JDwaterEveryDayT);
                    this.JdwaterTotalT = waterTotalT;
                    this.JdwaterD = waterD;
                }
            }
        }catch (e) {
            console.log("东东农场 ",e)
        }

    }

    async jdFarmNew(){
        try{
            const data = await this.commonRequestByH5st("farm_home",{"version": 7},"c57f6","signed_wh5",{
                'x-referer-page': 'https://h5.m.jd.com/pb/015686010/Bc9WX7MpCW7nW9QjZ5N3fFeJXMH/index.html',
                'origin': 'https://h5.m.jd.com',
                'referer': 'https://h5.m.jd.com/',
                'x-rp-client': 'h5_1.0.0',
                'request-from': 'native',
            })
            // console.log(data)
            if (data.data && data.data.result && data.data.result.skuName){
                if (data.data.result.treeCurrentState===0){
                    this.newFarminfo = `${data.data.result.skuName} 种植中,种植进度：${data.data.result.treeFullStage}/5(${data.data.result.currentProcess}%)${data.data.result.waterTips}`
                }
            }else {
                if (data.data.result.treeFullStage===0){
                    this.newFarminfo = `水果未种植`
                }else {
                    throw new Error(JSON.stringify(data))
                }
            }
            this.newFarmWater = data.data.result.bottleWater
        }catch (e) {
            console.log("新农场 ", e)
        }
    }

    async redPack(){
        try{
            const data = await this.commonRequestBySign("myhongbao_getUsableHongBaoList",{"activityArea":"-1","activityType":"1","appId":"appHongBao","appToken":"apphongbao_token","applicantErp":"-1","childActiveName":"-1","childActivityId":"-1","childActivityTime":"-1","childActivityUrl":"-1","country":"cn","eid":"-1","extend":"-1","fp":"-1","isRvc":"-1","jda":"-1","openId":"-1","orgType":"2","organization":"JD","pageClickKey":"-1","platform":"1","platformId":"appHongBao","platformToken":"apphongbao_token","shshshfp":"-1","shshshfpa":"-1","shshshfpb":"-1"})
            let jxRed = 0,
                jsRed = 0,
                jdRed = 0,
                jdhRed = 0,
                jdwxRed = 0,
                jdGeneralRed = 0,
                jxRedExpire = 0,
                jsRedExpire = 0,
                jdRedExpire = 0,
                jdhRedExpire = 0,
                jdwxRedExpire = 0,
                jdGeneralRedExpire = 0
            let t = new Date();
            t.setDate(t.getDate() + 1);
            t.setHours(0, 0, 0, 0);
            t = parseInt((t - 1) / 1000) * 1000;
            console.log(t)
            for (let vo of data.hongBaoList || []) {
                // console.log(vo)
                if (vo.orgLimitStr) {
                    if (vo.orgLimitStr.includes("京喜") && !vo.orgLimitStr.includes("特价")) {
                        jxRed += parseFloat(vo.balance)
                        if (vo['endTime'] === t) {
                            jxRedExpire += parseFloat(vo.balance)
                        }
                        continue;
                    } else if (vo.orgLimitStr.includes("购物小程序")) {
                        jdwxRed += parseFloat(vo.balance)
                        if (vo['endTime'] === t) {
                            jdwxRedExpire += parseFloat(vo.balance)
                        }
                        continue;
                    } else if (vo.orgLimitStr.includes("京东商城")) {
                        jdRed += parseFloat(vo.balance)
                        if (vo['endTime'] === t) {
                            jdRedExpire += parseFloat(vo.balance)
                        }
                        continue;
                    } else if (vo.orgLimitStr.includes("极速") || vo.orgLimitStr.includes("京东特价") || vo.orgLimitStr.includes("京喜特价")) {
                        jsRed += parseFloat(vo.balance)
                        if (vo['endTime'] === t) {
                            jsRedExpire += parseFloat(vo.balance)
                        }
                        continue;
                    } else if (vo.orgLimitStr && vo.orgLimitStr.includes("京东健康")) {
                        jdhRed += parseFloat(vo.balance)
                        if (vo['endTime'] === t) {
                            jdhRedExpire += parseFloat(vo.balance)
                        }
                        continue;
                    }
                }
                jdGeneralRed += parseFloat(vo.balance)
                if (vo['endTime'] === t) {
                    jdGeneralRedExpire += parseFloat(vo.balance)
                }
            }
            const balance = (jxRed + jsRed + jdRed + jdhRed + jdwxRed + jdGeneralRed).toFixed(2);
            jxRed = jxRed.toFixed(2);
            jsRed = jsRed.toFixed(2);
            jdRed = jdRed.toFixed(2);
            jdhRed = jdhRed.toFixed(2);
            jdwxRed = jdwxRed.toFixed(2);
            jdGeneralRed = jdGeneralRed.toFixed(2);
            const expiredBalance = (jxRedExpire + jsRedExpire + jdRedExpire + jdhRedExpire + jdwxRedExpire + jdGeneralRedExpire).toFixed(2);
            this.redPackmsg += `【红包总额】${balance}(总过期${expiredBalance})元 \n`;
            if (jxRed > 0) {
                if (jxRedExpire > 0)
                    this.redPackmsg += `【京喜红包】${jxRed}(将过期${jxRedExpire.toFixed(2)})元 \n`;
                else
                    this.redPackmsg += `【京喜红包】${jxRed}元 \n`;
            }
            if (jsRed > 0) {
                if (jsRedExpire > 0)
                    this.redPackmsg += `【京东特价】${jsRed}(将过期${jsRedExpire.toFixed(2)})元(原极速版) \n`;
                else
                    this.redPackmsg += `【京东特价】${jsRed}元(原极速版) \n`;
            }
            if (jdRed > 0) {
                if (jdRedExpire > 0)
                    this.redPackmsg += `【京东红包】${jdRed}(将过期${jdRedExpire.toFixed(2)})元 \n`;
                else
                    this.redPackmsg += `【京东红包】${jdRed}元 \n`;
            }
            if (jdhRed > 0) {
                if (jdhRedExpire > 0)
                    this.redPackmsg += `【健康红包】${jdhRed}(将过期${jdhRedExpire.toFixed(2)})元 \n`;
                else
                    this.redPackmsg += `【健康红包】${jdhRed}元 \n`;
            }
            if (jdwxRed > 0) {
                if (jdwxRedExpire > 0)
                    this.redPackmsg += `【微信小程序】${jdwxRed}(将过期${jdwxRedExpire.toFixed(2)})元 \n`;
                else
                    this.redPackmsg += `【微信小程序】${jdwxRed}元 \n`;
            }
            if (jdGeneralRed > 0) {
                if (jdGeneralRedExpire > 0)
                    this.redPackmsg += `【全平台通用】${jdGeneralRed}(将过期${jdGeneralRedExpire.toFixed(2)})元 \n`;
                else
                    this.redPackmsg += `【全平台通用】${jdGeneralRed}元 \n`;
            }
        }catch (e) {
            console.log("红包 ", e)
        }
    }

    async eCard(){
        try{
            const data = await this.commonRequestByH5st("queryGiftCardCountStatusCom",{"queryList":"b,i,d,g,a"},"42e80","mygiftcard",{
                'x-referer-page': 'https://mygiftcard.jd.com/giftcardForM.html',
                'origin': 'https://mygiftcard.jd.com',
                'referer': 'https://mygiftcard.jd.com/',
            })
            if (data.code === 'success'){
                let useable = data.data.g[1].num;
                if (parseInt(useable)>0) {
                    this.eCardInfo = '共' + useable + '张E卡,合计' + data.data.a + 'R';
                }
            }else {
                throw new Error(JSON.stringify(data))
            }
        }catch (e) {
            console.log("E卡",e)
        }
    }

    async hfJifen(){
        const t = new Date().getTime()
        const encstr = CryptoJS.MD5(t + "e9c398ffcb2d4824b4d0a703e38yffdd").toString()
        const options = {
            url: `https://api.m.jd.com/api?functionId=DATAWALLET_USER_SIGN_INFO`,
            headers: {
                'cookie': this.Cookie,
                'user-agent': this.UA,
                'referer': 'https://prodev.m.jd.com/mall/active/eEcYM32eezJB7YX4SBihziJCiGV/index.html',
                'content-type': 'application/x-www-form-urlencoded',
            },
            data: qs.stringify({
                'appid':'h5-sep',
                'body':JSON.stringify({"t":t,"encStr":encstr}),
                'client':'m',
                'clientVersion':'6.0.0'
            })
        }
        const {data} = await this.$.post(options)
        if (data.code === 200) {
            this.hfjifen = data.data.balanceNum;
        }
    }

    async _page(page,selected=1){
        try{
            return await this.commonRequestByH5st("try_MyTrials", {"page": page, "selected": selected}, "6d63a", "newtry",{
                'origin': 'https://prodev.m.jd.com',
                'referer': 'https://prodev.m.jd.com/'
            })
        }catch (e) {
            console.log("试用相关",e)
        }
    }

    async trialCount(){

        const results = await Promise.allSettled([
            this._page(1),
            this._page(5),
            this._page(9),
        ])
        const result1 = results[0].value;
        const result5 = results[1].value;
        const result9 = results[2].value;
        if (result1.success) {
            let tc1 = result1.data.list.length
            if (tc1 === 12) {
                if (result5.success) {
                    let tc5 = result5.data.list.length
                    if (tc5 === 12) {
                        if (result9.success) {
                            let tc9 = result9.data.list.length
                            if (tc9 === 12) {
                                this.jdtrycount = "大于108"
                            } else if (tc9 !== 0 && tc9 < 12) {
                                this.jdtrycount = "" + (96 + tc9)
                            } else {
                                this.jdtrycount = "大于60,小于96"
                            }
                        }
                    } else if (tc5 !== 0 && tc5 < 12) {
                        this.jdtrycount = "" + (48 + tc5)
                    } else {
                        this.jdtrycount = "大于12,小于48"
                    }
                }
            } else if (tc1 !== 0 && tc1 < 12) {
                this.jdtrycount = "" + tc1
            } else {
                this.jdtrycount = "小于等于0"
            }
        }
    }

    async trialWaitdraw(){
        const data = await this._page(1,2);
        if (data.success === true) {
            let drawlist = data.data.list
            let draw = 0;
            if (drawlist.length !== 0) {
                for (let i = 0; i < drawlist.length; i++) {
                    if (drawlist[i].tryButtonList != null) {
                        if (drawlist[i].tryButtonList.length === 2) {
                            if (drawlist[i].tryButtonList[0].id <= 2) {
                                draw++
                                this.waitdrawname += drawlist[i].trialName
                            }
                        }
                    }
                }
                this.waitdrawcount = "" + draw
            } else {
                this.waitdrawcount = "0"
            }
        }
    }

    async plantBean(){
        try{
            const data = await this.commonRequestByH5st("plantBeanIndex",{"channel":"wojinghd","monitor_source":"plant_m_plant_index","monitor_refer":"","version":"9.2.4.5"},"d246a","signed_wh5",{
                'referer': 'https://plantearth.m.jd.com/',
            })
            let list = data.data.roundList
            this.planlastbean = list[0].awardBeans
            this.planlastgrowth = list[0].growth
            this.plangrowth = list[1].growth
            this.plandateDesc = list[1].dateDesc
        }catch (e) {
            console.log("种豆得豆 ",e)
        }
    }

    async superMarket(){
        try{
            const data = await this.commonRequestByH5st("atop_channel_marketCard_cardInfo",{"babelChannel":"ttt9","isJdApp":"1","isWx":"0"},"35fa0","jd-super-market",{
                'x-referer-page': 'https://pro.m.jd.com/mall/active/3KehY4eAj3D1iLzFB7p5pb68qXkT/index.html',
                'origin': 'https://pro.m.jd.com',
                'referer': 'https://pro.m.jd.com/mall/active/3KehY4eAj3D1iLzFB7p5pb68qXkT/index.html?babelChannel=ttt9&showhead=no&hideBack=1&forceCurrentView=1&spmTabbar=1&hideAnchorBottomTab=1&topNavStyle=1&navh=49&stath=29&tttparams=7jnhteyJhZGRyZXNzSWQiOjUwOTI1ODI4MjIsImRMYXQiOjAsImRMbmciOjAsImdMYXQiOiI0MS43MjYzNDYiLCJnTG5nIjoiMTIzLjQ5NzU1NyIsImdwc19hcmVhIjoiMF8wXzBfMCIsImxhdCI6MCwibG5nIjowLCJtb2RlbCI6IlJlZG1pIEs1MCBVbHRyYSIsInBvc0xhdCI6IjQxLjcyNjM0NiIsInBvc0xuZyI6IjEyMy40OTc1NTciLCJwcnN0YXRlIjoiMCIsInVlbXBzIjoiMC0wLTIiLCJ1bl9hcmVhIjoiOF81NjBfNTA4MjZfMTI5MjIxIn50%3D',
            },"https://api.m.jd.com/atop_channel_marketCard_cardInfo")
            if (data.success) {
                const data1 = data.data && data.data.floorData && data.data.floorData.items
                if (data1) {
                    const balance = data1[0].marketCardVO.balance
                    const expirDes = data1[0].marketCardVO.expirationGiftAmountDes
                    this.supperMarket += `账户余额${balance}${expirDes?"，"+expirDes:""}`
                }
            }
        }catch (e) {
            console.log("京东超市卡",e)
        }
    }

    async newFarmAwards(){
        try{
            const data = await this.commonRequestByH5st("farm_award_detail",{"version":3,"type":1},"c57f6","signed_wh5",{
                'referer': 'https://h5.m.jd.com/'
            })
            if (data.code===0){
                const awards = data.data.result.plantAwards||[];
                for (const award of awards) {
                    // console.log(award)
                    if (award.awardStatus===1){
                        this.farmAwardsNew += `【新农场奖励】${award.skuName}-->${award.plantCompleteTip},${award.exchangeRemind}\n`
                    }
                }
            }
        }catch (e) {
            console.log("新农场奖励",e)
        }

    }

    async wanyiwan(){
        try {
            const data = await this.commonRequestByH5st("wanyiwan_exchange_page",{"showShortcut":false,"version":7},"afec7","signed_wh5",{
                'x-referer-page': 'https://pro.m.jd.com/mall/active/3aydrBPrN7xsUGwj31PK3UhkHAqA/index.html',
                'origin': 'https://pro.m.jd.com',
                'referer': 'https://pro.m.jd.com/mall/active/3aydrBPrN7xsUGwj31PK3UhkHAqA/index.html?babelChannel=ttt1&jwebprog=0&hybrid_err_view=1&transparent=1&commontitle=no&has_native=0&navh=49&stath=29&tttparams=Wi1Ee2CleyJhZGRyZXNzSWQiOjUwOTI1ODI4MjIsImRMYXQiOjAsImRMbmciOjAsImdMYXQiOiI0MS43MzA4MTUiLCJnTG5nIjoiMTIzLjUwNDYyNSIsImdwc19hcmVhIjoiMF8wXzBfMCIsImxhdCI6MCwibG5nIjowLCJtb2RlbCI6IlJlZG1pIEs1MCBVbHRyYSIsInBvc0xhdCI6IjQxLjczMDgxNSIsInBvc0xuZyI6IjEyMy41MDQ2MjUiLCJwcnN0YXRlIjoiMCIsInVlbXBzIjoiMC0wLTAiLCJ1bl9hcmVhIjoiOF81NjBfNTA4MjZfMTI5MjIxIn80%3D',
                'x-rp-client': 'h5_1.0.0',
                'request-from': 'native',
            })
            // console.log(data)
            if (data.code===0){
                this.wanyiwanP = data.data.result.score
            }
        }catch (e) {
            console.log("玩一玩",e)
        }
    }

    async wangBei(){
        function WbSign(body){
            const signKey = "c4491f13dce9c71f";
            const i = []
            for (const value of Object.keys(body).sort()) {
                i.push(body[value])
            }
            const j = i.join("")
            const timestamp = Date.now().toString();
            const r = "".concat(signKey).concat(j).concat(timestamp);
            const sign = CryptoJS.MD5(r).toString();
            body.timestamp = timestamp
            body.sign = sign
            body.signKey = signKey
            return body
        }
        try{
            const data = await this.commonRequestByH5st("arvr_queryInteractiveRewardInfo",WbSign({
                "pageSize": 10,
                "currentPage": 1,
                "projectId": "1764671",
                "projectKey": "2nym8aW7jNKRbmxXLdbb75m3ebSH",
                "sourceCode": 2,
                "needExchangeRestScore": 1
            }),"84692","commonActivity",{
                'x-referer-page': 'https://pro.m.jd.com/mall/active/472hYWPS9d6GP7xtJzsWscXepKZf/index.html',
                'origin': 'https://pro.m.jd.com',
                'referer': 'https://pro.m.jd.com/mall/active/472hYWPS9d6GP7xtJzsWscXepKZf/index.html?babelChannel=ttt1&hideAnchorBottomTab=1&topNavStyle=1&navh=49&stath=29&tttparams=',
                'x-rp-client': 'h5_1.0.0',
                'request-from': 'native',
            })
            if (data.msg==="success"){
                const scoreInfo = data.scoreInfoMap
                this.wangBeiTotal = scoreInfo.total;
                this.wangBeiUsable = scoreInfo.usable;
                this.wangBeiUsed = scoreInfo.used;
            }else {
                throw new Error(JSON.stringify(data))
            }
        }catch (e) {
            console.log("超市汪贝",e)
        }
    }

    async jdh(){
        const options = {
            url:`https://api.m.jd.com/api?appid=jdh-middle&functionId=jdh_bm_queryAwardAndScore&t=${Date.now()}`,
            headers: {
                'cookie': this.Cookie,
                'user-agent': this.UA,
                "Connection": "keep-alive",
                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'x-requested-with': 'com.jingdong.app.mall',
                'referer': 'https://jdhm.jd.com/',
                'origin': 'https://jdhm.jd.com'
            },
            body: qs.stringify({
                body:JSON.stringify({"appKey":"231282000001","appId":"1EFRYwg","channel":"jdapp","activityId":8542,"taskIdList":["520953","520954","520955","674815","841731","674816","674814"],"awardType":2,"imei":"JHNFCKDL"})
            }),
            httpsAgent: new Agent({
                ciphers: "TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256"
            })
        }
        try{
            const data = await this.$.post(options)
            const res = data.data
            if (res.code===0){
                this.jdhEng = res.data.energyValue
            }else {
                throw new Error(JSON.stringify(res))
            }
        }catch (e) {
            console.log("健康能量",e)
        }

    }

    async miniSheng(){
        try {
            const data = await this.commonRequestByH5st("miniTask_hbChannelPage",{"source":"task","businessSource":"cjs"},"60d61","hot_channel",{
                'x-referer-page': '/pages/marketing/entry_task/index',
                'referer': 'https://servicewechat.com/wx91d27dbf599dff74/770/page-frame.html',
                'x-referer-package': 'wx91d27dbf599dff74',
                'wqreferer': 'http://wq.jd.com/wxapp/pages/marketing/entry_task/index'
            })
            console.log(data)
            if (data.subCode===0){
                this.shengB = data.data.point
            }else{
                throw new Error(JSON.stringify(data))
            }
        }catch (e) {
            console.log("省钱币",e)
        }
    }
};
(async () => {
    await checkDependency()
    const check = await checkConfig();
    if (!check) {
        notifyMasters("Y_查询-->配参不完整，请填写所有带有*的配参");
        await setContinue();
        return
    }
    const imType = await getImtype();
    console.log(check);
    if (check.proxy==="true") {
        if (check.proxyip) {
            useProxy = true;
            proxyip = check.proxyip
            proxyport = parseInt(check.proxyport)
        }else{
            notifyMasters("Y_查询-->您启用了代理请求，请配置代理池ip和端口");
            return
        }
    }
    queryList = {
        jingxiang: check.jingxiang==="true",
        isPlus: check.plus==="true",
        // plusScores: check.plus==="true",
        userBean: check.jingdou==="true",
        bean: check.jingdou==="true",
        eCard: check.eka==="true",
        superMarket: check.chaoshika==="true",
        wangBei: check.wangbei==="true",
        hfJifen:check.huafeijifen==="true",
        wanyiwan:check.wanyiwan==="true",
        jdh:check.jdh==="true",
        miniSheng:check.shengqianbi==="true",
        plantBean:check.zhongdou==="true",
        jdFarm:check.nongchang==="true",
        jdFarmNew:check.xinnongchang==="true",
        newFarmAwards:check.xinnongchang==="true",
        trialCount:check.shiyong==="true",
        trialWaitdraw:check.shiyong==="true",
        beanGuoqi:check.linqi==="true",
        redPack:check.hongbao==="true",
    }
    if (imType === "rt") {
        const rtParams = await getRouterParams();
        const Cookie = rtParams.cookie;
        const token = rtParams.token;
        const type = rtParams.type;
        if (token.toString() !== check.usertoken.toString()) {
            reply("错误的token")
            return
        }
        if (type.toString() !== 0..toString() && type.toString() !== 1..toString()) {
            reply("type错误")
            return
        }
        if (!await checkCk(Cookie)) {
            reply(check.invalid)
            return
        }
        if (type.toString() === 0..toString()) {
            const queryInstance = new Query(Cookie);
            try{
                const nickname = await bucketGet("Y_nickCache", decodeURIComponent(Cookie.match(/pt_pin=(.*?);/)[1]))
                queryInstance.nickName = nickname
            }catch(e){
                console.log(e)
            }
            const res = await queryInstance.beanDetail();
            if (queryInstance.nickName) {
                try{
                    await bucketSet("Y_nickCache", decodeURIComponent(Cookie.match(/pt_pin=(.*?);/)[1]), queryInstance.nickName)
                }catch(e){
                    console.log(e)
                }
            }
            reply(res)
        } else {
            const queryInstance = new Query(Cookie);
            try{
                const nickname = await bucketGet("Y_nickCache", decodeURIComponent(Cookie.match(/pt_pin=(.*?);/)[1]))
                queryInstance.nickName = nickname
            }catch(e){
                console.log(e)
            }
            const res = await queryInstance.jdQuery();
            if (queryInstance.nickName) {
                try{
                    await bucketSet("Y_nickCache", decodeURIComponent(Cookie.match(/pt_pin=(.*?);/)[1]), queryInstance.nickName)
                }catch(e){
                    console.log(e)
                }
            }
            reply(res)
        }
        // reply(Cookie + token + type)
        return
    }
    // 构造触发关键词数组
    const beanDetailRule = check.detail.replaceAll("，", ",").split(",").filter(item => item !== "");
    const queryInfoRule = check.info.replaceAll("，", ",").split(",").filter(item => item !== "");
    // 获取发送的消息内容
    const context = await getMessage();
    if (!beanDetailRule.includes(context) && !queryInfoRule.includes(context)) {
        await setContinue();
        return
    }
    const userId = await getUserID();
    const jds = await bucketKeys("pin" + imType.toUpperCase(), userId);
    const cookieArr = [];
    if (jds.length === 0) {
        reply(check.notice)
        return
    }
    let qinglongs = [];
    if (check.qlnames) {
        qinglongs = await findQinglongByName(check.qlnames.replaceAll("，", ",").split(",").filter(item => item !== ""))
    }else{
        qinglongs = await findQinglong(check.qlname.replaceAll("，", ",").split(",").filter(item => item !== ""));
    }
    if (jds.length !== 1 && check.queryall !== "true") {
        const nickList = [];
        for (const jdpin of jds) {
            nickList.push(bucketGet("Y_nickCache", decodeURIComponent(jdpin)));
        }
        const nikeNames = await Promise.allSettled(nickList)
        let pinStr = `请选择要查询的账号\n[0] 查询全部`
        for (let i = 0; i < jds.length; i++) {
            const element = jds[i];
            pinStr += `\n[${(i + 1)}] ${decodeURIComponent(element)}`
            if (check.usecachenick==="true"&&nikeNames[i].status === "fulfilled"&& nikeNames[i].value&& nikeNames[i].value !== decodeURIComponent(element)) {
                pinStr += `(${nikeNames[i].value})`
            }
        }
        reply(pinStr)
        let inputIndex = "";
        try {
            inputIndex = await listen(30000)
        } catch (error) {
            inputIndex = "";
        }
        if (isNaN(parseInt(inputIndex)) || parseInt(inputIndex) < 0 || parseInt(inputIndex) > jds.length) {
            await reply("输入错误，退出程序");
            return
        } else if (parseInt(inputIndex) === 0) {
            for (const jd of jds) {
                const userCk = await findCookie(jd, check.qlonly === "true", qinglongs);
                if (!userCk) {
                    await reply(`未找到${decodeURIComponent(jd)}对应的Cookie`)
                    continue
                }
                const ck = "pt_key=" + userCk.PtKey + ";pt_pin=" + userCk.ID + ";"
                cookieArr.push(ck)
            }
        } else {
            let index = parseInt(inputIndex);
            const choosePin = jds[index - 1];
            const userCk = await findCookie(choosePin, check.qlonly === "true", qinglongs);
            if (!userCk) {
                await reply(`未找到${decodeURIComponent(choosePin)}对应的Cookie`)
                return
            }
            const ck = "pt_key=" + userCk.PtKey + ";pt_pin=" + userCk.ID + ";"
            cookieArr.push(ck)
        }
    } else {
        for (const jd of jds) {
            const userCk = await findCookie(jd, check.qlonly === "true", qinglongs);
            if (!userCk) {
                await reply(`未找到${decodeURIComponent(jd)}对应的Cookie`)
                continue
            }
            const ck = "pt_key=" + userCk.PtKey + ";pt_pin=" + userCk.ID + ";"
            cookieArr.push(ck)
        }
    }
    if (beanDetailRule.includes(context)) {
        for (const cookie of cookieArr) {
            const isValid = await checkCk(cookie);
            if (!isValid) {
                reply(`账号【${decodeURIComponent(cookie.match(/pt_pin=(.*?);/)[1])}】Cookie过期`)
                continue
            }
            reply(`开始查询【${decodeURIComponent(cookie.match(/pt_pin=(.*?);/)[1])}】`)
            const queryInstance = new Query(cookie);
            try{
                const nickname = await bucketGet("Y_nickCache", decodeURIComponent(cookie.match(/pt_pin=(.*?);/)[1]))
                queryInstance.nickName = nickname
            }catch(e){
                console.log(e)
            }
            const res = await queryInstance.beanDetail();
            if (queryInstance.nickName) {
                try{
                    await bucketSet("Y_nickCache", decodeURIComponent(cookie.match(/pt_pin=(.*?);/)[1]), queryInstance.nickName)
                }catch(e){
                    console.log(e)
                }
            }
            reply(res)
        }
    } else {
        for (const cookie of cookieArr) {
            const isValid = await checkCk(cookie);
            if (!isValid) {
                reply(`账号【${decodeURIComponent(cookie.match(/pt_pin=(.*?);/)[1])}】Cookie过期`)
                continue
            }
            reply(`开始查询【${decodeURIComponent(cookie.match(/pt_pin=(.*?);/)[1])}】`)
            const queryInstance = new Query(cookie);
            try{
                const nickname = await bucketGet("Y_nickCache", decodeURIComponent(cookie.match(/pt_pin=(.*?);/)[1]))
                queryInstance.nickName = nickname
            }catch(e){
                console.log(e)
            }
            const res = await queryInstance.jdQuery();
            if (queryInstance.nickName) {
                try{
                    await bucketSet("Y_nickCache", decodeURIComponent(cookie.match(/pt_pin=(.*?);/)[1]), queryInstance.nickName)
                }catch(e){
                    console.log(e)
                }
            }
            reply(res)
        }
    }
})()

// 寻找Cookie
async function findCookie(pin, onlyql, qls = []) {
    async function findBucket() {
        // 返回string
        const bktCookie = await bucketGet("jdNotify", encodeURIComponent(decodeURIComponent(pin)))
        if (bktCookie.length === 0) {
            return false;
        }
        return JSON.parse(bktCookie);
    }

    async function findQl() {
        for (const ql of qls) {
            let res = await ql.ApiQL("envs", `?searchValue=JD_COOKIE&t=${Date.now()}`, "get")
            let allEnvs = res.data
            for (const qlenv of allEnvs) {
                let vpin = decodeURIComponent(qlenv.value.match(/pt_pin=(.*?);/)[1])
                if (vpin === decodeURIComponent(pin)) {
                    const key = qlenv.value.match(/pt_key=(.*?);/)[1];
                    return {
                        PtKey: key,
                        ID: encodeURIComponent(vpin)
                    }
                }
            }
        }
        return false
    }
    if (!onlyql) {
        const bktRes = await findBucket();
        if (bktRes) {
            return bktRes
        }
    }
    return await findQl()
}

// 查找青龙面板
async function findQinglong(ids = []) {
    const qlArr = [];
    if (ids.length > 0) {
        for (const id of ids) {
            try {
                const userQinglong = JSON.parse(await bucketGet("qls", id))
                if (userQinglong) {
                    qlArr.push(new Qinglong(userQinglong.host, userQinglong.client_id, userQinglong.client_secret))
                }
            } catch (error) {
                console.log("findQinglong-->", error);
            }
        }
        return qlArr;
    }
    const userAllQinglong = await bucketAll("qls");
    for (const key in userAllQinglong) {
        if (Object.hasOwnProperty.call(userAllQinglong, key)) {
            try {
                const element = JSON.parse(userAllQinglong[key]);
                if (element.default) {
                    qlArr.push(new Qinglong(element.host, element.client_id, element.client_secret))
                }
            } catch (error) {
                console.log("findQinglong-->", error);
            }

        }
    }
    return qlArr;
}

async function findQinglongByName(names=[]) {
    const qlArr = [];
    const userAllQinglong = await bucketAll("qls");
    for (const key in userAllQinglong) {
        const value = userAllQinglong[key];
        const element = JSON.parse(value);
        const name = element.name
        if (names.includes(name)){
            qlArr.push(new Qinglong(element.host, element.client_id, element.client_secret))
        }
    }
    return qlArr;
}

// 检测Ck有效性
async function checkCk(cookie) {
    let check1 = await totalBean(cookie)
    if (check1) {
        return true
    } else {
        let check2 = await isLoginByX1a0He(cookie)
        if (check2) {
            return true
        } else {
            return false
        }
    }
}

async function totalBean(cookie) {
    const options = {
        url: "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion",
        headers: {
            Cookie: cookie,
            "User-Agent": "jdapp;iPhone;9.4.4;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "Accept-Language": "zh-cn",
            "Referer": "https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&",
        },
        method: "get",
    }
    let res = await req(options)
    if (res) {
        try {
            let data = res
            if (data['retcode'] === "1001") {
                console.log("Cookie失效")
                return false
            }
            if (data['retcode'] === "0" && data.data && data.data.hasOwnProperty("userInfo")) {
                return true
            } else {
                return false
            }
        } catch (e) {
            console.log(e)
            return false
        }
    } else {
        return false
    }
}

async function isLoginByX1a0He(cookie) {
    const options = {
        url: 'https://plogin.m.jd.com/cgi-bin/ml/islogin',
        headers: {
            "Cookie": cookie,
            "referer": "https://h5.m.jd.com/",
            "User-Agent": "jdapp;iPhone;10.1.2;15.0;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        },
        method: "get",
    }
    let res = await req(options)
    if (res) {
        let data = res
        if (data.islogin === "1") {
            console.log("Cookie有效");
            return true
        } else if (data.islogin === "0") {
            console.log("Cookie无效");
            return false
        } else {
            return false
        }
    } else {
        return false
    }
}

// 检查配参
async function checkConfig() {
    let { detail, info, invalid, notice, qlname, qlnames,queryall, usecachenick, usertoken, qlonly,proxy,proxyip,proxyport,jingxiang,jingdou,eka,chaoshika,wangbei,huafeijifen,wanyiwan,jdh,shengqianbi,zhongdou,nongchang,xinnongchang,shiyong,linqi,hongbao } = await bucketAll("Y_" + bucketN);
    if (!detail || !info || !invalid || !notice || !usertoken) {
        return false
    }
    if (!qlname) {
        qlname = ""
    }
    if (!qlnames) {
        qlnames = ""
    }
    return {
        detail, info, invalid, notice, qlname,qlnames, queryall,usecachenick, usertoken, qlonly,proxy,proxyip,proxyport,jingxiang,jingdou,eka,chaoshika,wangbei,huafeijifen,wanyiwan,jdh,shengqianbi,zhongdou,nongchang,xinnongchang,shiyong,linqi,hongbao
    }
}

// 用于适配旧版本的自定义bucketAll
async function mybucketAll(bucket) {
    // 获取所有的key value
    const allKeys = await bucketAllKeys(bucket);
    const bucketKv = await Promise.all(allKeys.map(async (key) => {
        const value = await bucketGet(bucket, key)
        return {
            [key]: value
        }
    }))
    return Object.assign({}, ...bucketKv)
}

async function checkDependency() {
    let deps = ["axios", "crypto-js","qs"];
    for (const dep of deps) {
        let testRes = testDependency(dep)
        if (!testRes) {
            await notifyMasters(`缺少${dep}尝试安装`)
            let installRes = installDependency(dep)
            if (installRes) {
                await notifyMasters(`${dep}安装成功`)
            } else {
                await notifyMasters(`${dep}可能安装失败，请尝试手动安装`)
            }
        }
    }
}

// 检测依赖安装情况
function testDependency(Dependency) {
    try {
        if (Dependency.includes("@")) {
            Dependency = Dependency.match(/(.*?)@/)[1]
        }
        console.log(Dependency);
        require(Dependency)
        return true
    } catch (e) {
        return false
    }
}

// 安装依赖
function installDependency(Dependency) {
    const { spawnSync } = require('child_process')
    try {
        let installRes = spawnSync("npm", ["install", Dependency, "--legacy-peer-deps","--registry=https://registry.npmmirror.com"])
        console.log(Buffer.from(installRes.stdout).toString("utf-8"));
        if (Buffer.from(installRes.stdout).toString("utf-8").includes("ERR!")) {
            return false
        }

        return true
    } catch (e) {
        console.log(e);
        return false
    }
}

// 请求
async function req(options) {
    const config = {
        url: options.url,//地址
        headers: options.headers ? options.headers : undefined,
        method: options.method ? options.method : "get",//网络请求方法get,post,put,delete
        data: options.body ? options.body : "",
        timeout: 30000//单位为毫秒ms，也可以都小写timeout
    }
    try {
        let res = await axios(config)
        return res.data
    } catch (error) {
        console.log(error);
        return false
    }
}