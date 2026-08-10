//[router: /jd/sign]
//[method: get]
//[method: post]
//[open_source: false]
//[title: JDsignES5版]
//[author: hunyan]
//[class: 工具类]
//[version: 1.0.0]
//[service: qq2946148573]
//[price: 1.81]
//[public:true] 
//[description: 本插件仅作为“JD通用sign”的es5版本，功能与“JD通用sign”完全相同。（已有“JD通用sign”插件的无需安装，且可能会与“JD通用sign”产生冲突）。适合于autMan1.0.9以上,理论适用于m和kr的通用sign，也可以用来自动评价使用。接口地址：http://奥特曼地址:端口/jd/sign，自动评价仅需填写http://奥特曼地址:端口]

main()

function main() {
    const method = getMethod()
    if (method === "get") {
        sender.reply("您的sign正常运行中......")
    } else if (method === "post") {
        const data = getRouterData()
        const params = getRouterParams()
        let body;
        let fn;
        try {
            if (data) {
                const dataobj = typeof data === "string" ? JSON.parse(data) : data
                fn = dataobj.fn
                body = dataobj.body
                if (typeof body === "object") {
                    body = JSON.stringify(body)
                    if (typeof body === "object") {
                        body = JSON.stringify(body)
                    }
                }
            } else if (params) {
                console.log(params);
                fn = params.functionId
                body = params.body
                if (typeof body === "object") {
                    body = JSON.stringify(body)
                    if (typeof body === "object") {
                        body = JSON.stringify(body)
                    }
                }
            } else {
                sender.reply({
                    code: 403,
                    message: "请求参数有误"
                })
                return
            }
        } catch (e) {
            sender.reply({
                code: 403,
                message: "请求参数有误"
            })
            return
        }
        console.log(fn)
        console.log(body)
        try {
            const result = get_sign(fn,body)
            sender.reply(result)
        } catch (e) {
            console.log(e);
            sender.reply({
                code: 401,
                message: "出错了",
                data: {
                    fn,
                    body
                }
            })
        }

    } else {
        sender.reply({
            code: 404,
            message: "请求方式有误"
        })
    }
}

function get_sign(functionId, body, client = "android", clientVersion = '12.1.4') {
    console.log(functionId,body);
    const d = JSON.parse(body)
    if (d.hasOwnProperty("eid")) {
        eid = d["eid"]
    } else {
        eid = randomeid()
    }
    const { ep, ts, jduuid, d_brand } = getep()
    const version = [[0, 2], [1, 1], [2, 0]];
    const r1r2 = version[Math.floor(Math.random() * version.length)];
    const r1 = r1r2[0];
    const r2 = r1r2[1];
    const sv = "1" + r1 + r2;
    const all_arg = `functionId=${functionId}&body=${body}&uuid=${jduuid}&client=${client}&clientVersion=${clientVersion}&st=${ts}&sv=${sv}`;
    const by = stringToBytes(all_arg)
    const back_base64 = sign_core(by)
    const sign = call("md5")(back_base64)
    const ext = encodeURIComponent('{"prstate":"0","pvcStu":"1"}');
    const partner = d_brand.toLowerCase();
    const convertUrl = `body=${encodeURIComponent(body)}&clientVersion=${clientVersion}&build=98935&client=${client}&partner=${partner}&sdkVersion=31&lang=zh_CN&harmonyOs=0&networkType=wifi&ext=${ext}&oaid=${jduuid}&eid=${eid}&ef=1&ep=${encodeURIComponent(ep)}&st=${ts}&sign=${sign}&sv=${sv}`;
    console.log(convertUrl);
    const result = {
        code: 200,
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
    return result
}

function stringToBytes(param, ascii) { //该方法只适用于utf-8编码和ascii编码(适用于生成文件),参数为string
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

function bytesToString(params, ascii) { //该方法只适用于utf-8编码和ascii编码,参数为byte数组
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

function base64(params, ascii) { //将byte数组(或字符串)转换成base64
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
    return bytesToString(result);
}

function sign_core(inarg) {
    let key = stringToBytes('80306f4370b39fd5630ad0529f77adb6')
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
    return base64(array)
}

function randomeid() {
    return "eidAaf8081218as20a2GM" + randomstr(20) + "7FnfQYOecyDYLcd0rfzm3Fy2ePY4UJJOeV0Ub840kG8C7lmIqt3DTlc11fB/s4qsAP8gtPTSoxu"
}

function randomstr(num) {
    let string = '';
    let str1 = "abcdefghijklmnopqrstuvwxyz0123456789"
    for (let i = 0; i < num; i++) {
        string += str1.charAt(Math.floor(Math.random() * str1.length));
    }
    return string;
}

function translate(str, str1, str2) {
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

function randomhex(num) {
    let string = '';
    let str1 = "abcdef0123456789"
    for (let i = 0; i < num; i++) {
        string += str1.charAt(Math.floor(Math.random() * str1.length));
    }
    return string;
}

function uuidv1() {
    return `${randomhex(8)}-${randomhex(4)}-${randomhex(4)}-${randomhex(4)}-${randomhex(12)}`
}

function base64Encode(str) {
    return translate(base64(str), "KLMNOPQRSTABCDEFGHIJUVWXYZabcdopqrstuvwxefghijklmnyz0123456789+/", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/")
}

function randomnum(num) {
    let string = '';
    let str1 = "0123456789"
    for (let i = 0; i < num; i++) {
        string += str1.charAt(Math.floor(Math.random() * str1.length));
    }
    return string;
}
function getep() {
    let jduuid = uuidv1().replace(/-/g, '').slice(0, 16)
    let ts = Date.now()
    let area = randomnum(2) + '_' + randomnum(4) + '_' + randomnum(5) + '_' + randomnum(4)
    const d_brand_model = {
        "OPPO": ["PAFM00", "PDEM10", "PDRM00", "PENM00", "PGW110"],
        "Xiaomi": ["23078PND5G", "2211133C", "M1902F1A"],
        "HUAWEI": ["LIO-AL00", "OCE-AN10", "JER-AN20", "RTE-AL00"]
    }
    const d_brand = Object.keys(d_brand_model)[Math.floor(Math.random() * (Object.keys(d_brand_model).length))]
    const d_model = d_brand_model[d_brand][Math.floor(Math.random() * (d_brand_model[d_brand].length))]
    const wifiBssid = `TP_LINK_${randomstr(6)}`
    const osVersion = ["10", "11", "12"][Math.floor(Math.random() * (["10", "11", "12"].length))]
    const screen = ["640x1136", "750x1334", "1080x1920"][Math.floor(Math.random() * (["640x1136", "750x1334", "1080x1920"].length))]
    const ep = JSON.stringify({
        "hdid": "JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=",
        "ts": ts,
        "ridx": -1,
        "cipher": {
            "area": base64Encode(area),
            "d_model": base64Encode(d_model),
            "wifiBssid": base64Encode(wifiBssid),
            "osVersion": base64Encode(osVersion),
            "d_brand": base64Encode(d_brand),
            "screen": base64Encode(screen),
            "uuid": base64Encode(jduuid),
            "aid": base64Encode(jduuid),
            "openudid": base64Encode(jduuid)
        },
        "ciphertype": 5,
        "version": "1.2.0",
        "appname": "com.jingdong.app.mall",
    })
    return { ep, ts, jduuid, d_brand }
}