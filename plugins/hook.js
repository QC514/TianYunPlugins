//[author: funyhook]
//[service: 601440343]
//[class: 工具类]
//[price: 0.01]
//[public: true]
//[disable:false]
//[title: hook]
//[version: 6.2]
//[description: funyhook 插件依赖！]
//[create_at: 2023-11-09 09:17:51]



function get_qr_url(url){
    return imageDownload(`https://v.api.aa1.cn/api/api-qrcode/sc.php?text=${encodeURIComponent(url)}`);
}
function get_qr_url2(url){
    return imageDownload(`https://v.api.aa1.cn/api/api-qrcode/sc.php?text=${encodeURIComponent(url)}`);
}

function hookCreateQR(url){
    //https://api.linhun.vip/api/QRcode?apiKey=e2ad109fbb9e70654e39a674a817ac16&url=1212
    sendText(image(`https://api.pwmqr.com/qrcode/create/?url=${url}`))
}



/**
 * 手机号加密
 * @param val
 * @returns {*}
 */
function encryphoneCard(val){
    let oldVal, newVal
    oldVal = String(val)
    //手机号
    if (oldVal.length === 11) {
        newVal = oldVal.replace(/^(\d{3})\d+(\d{4})$/, '$1****$2')
    }
    //身份证
    if (oldVal.length === 18 || oldVal.length === 15) {
        newVal = oldVal.replace(/^(\d{6})\d+(\d{4})$/, '$1******$2')
    }
    return newVal
}
function pingstrUrl(url){
    let reg ="https://"
    if(url.includes("http://")){
        reg = "http://"
    }
    url = url.split(reg)[1]
    if(url.includes(":")){
        url = url.split(":")[0]
    }else{
        url = url.split("/")[0]
    }
    url=reg+url
    let res = request({url: `https://v.api.aa1.cn/api/api-ping/ping.php?url=${url}`, method: "get", dataType: "json"})
    return res && res.host


}


function getDateTime(dateTime) {
    let y = dateTime.getFullYear(),
        m = dateTime.getMonth() + 1,
        d = dateTime.getDate();
    return y + "-" + (m < 10 ? "0" + m : m) + "-" + (d < 10 ? "0" + d : d) + " " + dateTime.toTimeString().substr(0, 8);
}

function  getNextMonthTimestamp(dateTime){
    dateTime=dateTime.setMonth(dateTime.getMonth() +1);
    return new Date(dateTime).getTime()
}

function  getNextMonthDate(dateTime){
    dateTime=dateTime.setMonth(dateTime.getMonth() +1);
    return new Date(dateTime)
}

/**
 * getToday
 * @returns {*}
 */
function getToday() {
    return timeFmt('yyyy-MM-dd')
}

/**
 * getTodayStartTime
 * @returns {number}
 */
function getTodayStartTime() {
    return new Date( timeFmt('yyyy-MM-dd').split(" ") + " 00:00:00").getTime()
}
/**
 * getTodayStartTime
 * @returns {number}
 */
function getTodayEndTime() {
    return new Date(timeFmt('yyyy-MM-dd').split(" ") + " 23:59:59").getTime()
}

/**
 * getTodayStartTime
 * @returns {number}
 */
function getTodayEnd() {
    return new Date(timeFmt('yyyy-MM-dd').split(" ") + " 23:59:59")
}
/**
 * timestamp
 * @returns {number}
 */
function getTimestamp() {
    return new Date().getTime()
}

/**
 * getHour
 * @returns {number}
 */
function getHour() {
    return new Date().getHours()
}

/**
 * 随机整数
 * @param min
 * @param max
 * @returns {number}
 */
function randomInt(min, max) {
    return Math.round(Math.random() * (max - min) + min);
}

/**
 * pushMsg
 * @param userId
 * @param imType
 * @param groupCode
 * @param content
 */
function pushMsg(userId, imType, groupCode, content) {
    push({
        imType: imType, //发送到指定渠道,如qq,wx,必须
        userID: userId, //groupCode不为0时为@指定用户,可选
        groupCode: groupCode, //可选
        chatID:groupCode,
        content: content
    }) //给指定im发送消息
}


/**
 * 平台key
 * @param name
 * @returns {({imType: string, platform: string}|{imType: string, platform: string}|{imType: string, platform: string})[]}
 */
function platformArr(name) {
    return [
        {
            "platform": `${name}qq`,
            "imType": "qq"
        },
        {
            "platform": `${name}wx`,
            "imType": "wx"
        },
        {
            "platform": `${name}wb`,
            "imType": "wb"
        },
        {
            "platform": `${name}tg`,
            "imType": "tg"
        },
        {
            "platform": `${name}bt`,
            "imType": "bt"
        },
        {
            "platform": `${name}qb`,
            "imType": "qb"
        },{
            "platform": `${name}mqindiv`,
            "imType": "mqindiv"
        },
    ]
}
function createQR(url){
    const username = bucketGet("cloud", "username")
    const password = bucketGet("cloud", "password")
    let img = imageDownload(`https://api.pwmqr.com/qrcode/create/?url=${encodeURIComponent(url)}`)//下载到默认路径,url支持http路径，支持base64://路径，支持data:image
    let ib = encodeURIComponent(img["base64"]);
    let body = request({
        url: "http://aut.zhelee.cn/imgUpload",
        method: "post",
        dataType: "json",
        formData: {
            imgBase64: ib,
            username: username,
            password: password,
        },
    })
    //console.log(JSON.stringify(body))
    if (body.code === 200) {
        sendImage(body.result.path)
    }
}

/**
 * 生成随机数字
 * @param {number} min 最小值（包含）
 * @param {number} max 最大值（不包含）
 */
function randomNumber(min = 0, max = 100) {
    return Math.min(Math.floor(min + Math.random() * (max - min)), max);
}

function userAgent() {
    const USER_AGENTS = [
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
    return USER_AGENTS[randomNumber(0, USER_AGENTS.length)];
}


function install_notify(title) {
    let plugin_arr = []
    let pluginStr = bucketGet("funyhook", "plugins");
    if (pluginStr) {
        plugin_arr = JSON.parse(pluginStr)
    }
    if (!plugin_arr.some(o => o === title)) {
        plugin_arr.push(title)
        bucketSet("funyhook", "plugins", JSON.stringify(plugin_arr));
        plugin_notify(title, "install", "新用户安装")
    }
}


function error_notify(title, error) {
    plugin_notify(title, "error", error)
}


function plugin_notify(name, type, msg) {
    let typeMap={
        install:"用户安装",
        uninstall:"用户卸载",
        error:"发生错误",
        other:"其他",

    }
    request({
        url: `http://aut.esaon.cn/api/notify`,
        method: 'post',
        json: true,
        body: {
            name: name,
            msg: msg,
            data: {
                type:typeMap[type],
                aut_name : bucketGet("cloud", "username"),
                machineId: call("machineId")(),
                qq_master: bucketGet("qq", "masters"),
                wx_master: bucketGet("wx", "masters"),
                tg_master: bucketGet("tg", "masters"),
                host: bucketGet("autman", "host")

            }
        }
    }, function (error, response, body) {
        if (!error && response.statusCode === 200 && body.success) {

        } else {

        }
    });
}


/**
 * 插件版本校验
 * @returns {boolean}
 */
function check_plugin_ver(name,localVer,plugin_title,content) {

    return true
}

//日期差天数
function getDaysBetween(dateString1, dateString2) {
    let startDate = Date.parse(dateString1)
    let endDate = Date.parse(dateString2)
    return (endDate - startDate) / (24 * 60 * 60 * 1000)
}

//数组的差集
function arrayAminusB(arrA, arrB) {
    return arrA.filter(v => !arrB.includes(v));
}

/**
 * 激活码校验
 * @returns {{msg: string, success: boolean}}
 */
function checkCode(plugin) {
    let apiMap = {
        imt_sms_: {//茅台登陆
            host: "app.moutai519.com.cn",
            code_url: 'https://app.moutai519.com.cn/xhr/front/user/register/vcode',
            login_url: 'https://app.moutai519.com.cn/xhr/front/user/register/login',
            mtv_url: 'http://82.157.10.108:8086/get_mtv?DeviceID={0}&MTk={1}&version={2}&key=yaohuo',
            param_url:`http://82.157.10.108:8086/get_actParam?key=yaohuo&actParam={0}`,
            add_url:`https://app.moutai519.com.cn/xhr/front/mall/reservation/add`,
            limit: 10,
        },
        bohai_: {//渤海
            host: "gms.ihaoqu.com",
            checkInUrl: "https://gms.ihaoqu.com/gmswx/app.php?rid=28&ogid=10&noauth=1&r=api2&apiAction=SignIn",
            userInfoUrl: "https://gms.ihaoqu.com/gmswx/app.php?rid=28&ogid=10&noauth=1&r=api2&apiAction=getUserInfo",
            rechargeUrl: "https://gms.ihaoqu.com/gmswx/app.php?rid=28&ogid=10&noauth=1&r=api2&apiAction=Recharge",
            limit: 10,

        },
        vhook_wool_: {//线报引擎
            host: "app.xiaodigu.cn",
            woolUrl: "https://app.xiaodigu.cn/mag/info/v2/channel/infoListByCatId?step=10&channel_id=52&uniqid=61c5dcf4edb4c&is_app_first=-1&cat_id=112&p=1",
            limit: 10,
        },
        haidilao_: {//海底捞
            host: "superapp-public.kiwa-tech.com",
            checkInUrl: "https://superapp-public.kiwa-tech.com/activity/wxapp/signin/signin",
            pointUrl: "https://superapp-public.kiwa-tech.com/activity/wxapp/signin/queryFragment",
            limit: 10,
        },
        xkqd_: {//星空签到
            host: "www.xkdaili.com",
            loginSignUrl: "http://www.xkdaili.com/tools/submit_ajax.ashx?action=user_login&site_id=1",
            pointUrlL: "http://www.xkdaili.com/tools/submit_ajax.ashx?action=user_receive_point",
            apiKeyUrl: "http://api2.xkdaili.com/tools/XApi.ashx?apikey=#apikey&qty=1&format=txt&split=0&sign=&check=1"
        },
        yunshanfu_: {//云闪付
            host: "95516.com",
            checkInUrl: "https://youhui.95516.com/newsign/api/daily_sign_in",
            checkInUhUrl: "https://bjchx.95516.com/uhcpmobile/interest/signinInfo/signin"
        },
        wangchao_: {//望潮
            task_host: "xmt.taizhou.com.cn",
            login_url: "https://xmt.taizhou.com.cn/prod-api/user-read/app/login?id=#id&sessionId=#sessionId",
            taskUrl: "https://xmt.taizhou.com.cn/prod-api/user-read/list",
            read_host: "",
            readUrl: "https://bjchx.95516.com/uhcpmobile/interest/signinInfo/signin",
            loginWC_url: "https://srv-app.taizhou.com.cn/tzrb/user/loginWC?accountId=#accountId&sessionId=#sessionId",
            drawUrl: "https://srv-app.taizhou.com.cn/tzrb/userAwardRecordUpgrade/save",
            draw_prize_url: "https://srv-app.taizhou.com.cn/tzrb/awardUpgrade/list?activityId=#activityId",
            draw_record_url: "https://srv-app.taizhou.com.cn/tzrb/userAwardRecordUpgrade/pageList?pageSize=10&pageNum=1&activityId=#activityId",
            integral_url: "https://xmt.taizhou.com.cn/prod-api/integral",
            checkInUrl: "https://vapp.taizhou.com.cn/api/user_mumber/sign",
            draw_id: 67
        },
        gehuadongyang_: {//歌画东阳
            host: "https://vapp.tmuyun.com",
            account_detail_url: "/api/user_mumber/account_detail",
            channel_list_url: "/api/article/channel_list",
            article_detail_url: "/api/article/detail",
            draw_host: "https://fijdzpur.act.tmuact.com",
            draw_url: "/activity/api.php",
            tx_url: "/activity/api.php",
            limit: 10
        },
        jinriyuecheng_: {//今日越城
            host: "https://vapp.tmuyun.com",
            account_detail_url: "/api/user_mumber/account_detail",
            channel_list_url: "/api/article/channel_list",
            article_detail_url: "/api/article/detail",
            draw_host: "https://fijdzpur.act.tmuact.com",
            draw_url: "/activity/api.php",
            tx_url: "/activity/api.php",
            limit: 10
        },
        alicloud_: {//阿里云
            qr_url: "https://aliyundriver-refresh-token-one.vercel.app/api/generate?img=true",
            qr_status_url: "https://aliyundriver-refresh-token-one.vercel.app/api/state-query?ck=#ck&t=#t",
            token_url: "https://auth.aliyundrive.com/v2/account/token",
            sign_url: "https://member.aliyundrive.com/v1/activity/sign_in_list",
            sign_reward_url: "https://member.aliyundrive.com/v1/activity/sign_in_reward",
            limit: 10
        },
        jingdahuisuan_: {//京打惠算
            checkInUrl: "https://zhelihaoquan.yzgnet.com/prod-api/app/signIn",
            danSignInUrl: "https://zhelihaoquan.yzgnet.com/prod-api/app/danSignIn",
            poinrUrl: "http://aliyun.vhook.cn/api/state-query?ck=#ck&t=#t",
            userInfoUrl: "https://zhelihaoquan.yzgnet.com/prod-api/app/getUserInfo/ad",
            drawCountUrl: "https://zhelihaoquan.yzgnet.com/prod-api/app/drawCount",
            drawListUrl: "https://zhelihaoquan.yzgnet.com/prod-api/app/userDrawList?pageSize=20&pageNum=1&orderByColumn=draw_time&isAsc=desc",
            appid:'wx0583b73e21ce4931',
            platformKey:'43fdf5a241a94207a8a5d274235f5fae',
            limit: 10
        },
        zhangshangouhai_: {//掌上瓯海
            host: "https://vapp.tmuyun.com",
            login_url: "https://passport.tmuyun.com/web/account/check_phone_number?client_id=10032&phone_number=",
            auth_url : "https://passport.tmuyun.com/web/oauth/credential_auth",
            channel_list_url: "'https://vapp.tmuyun.com/api/article/channel_list",
            article_detail_url: "/api/article/detail",
            draw_host: "https://fijdzpur.act.tmuact.com",
            draw_url: "/activity/api.php",
            tx_url: "/activity/api.php",
            limit: 10
        },meituan_: {//美团
            host: "game.meituan.com",
            login_url: "https://game.meituan.com/earn-daily/login/loginMgc?gameType=10402&mtUserId={0}&mtToken={1}&mtDeviceId={2}&nonceStr={3}&externalStr={4}",
            earn_daily_url : "https://game.meituan.com/earn-daily/msg/post",
            limit: 10
        },
    }
    return {
        success : true,
        msg :"success",
        data: {
            api:apiMap[plugin]
        }
    }
}

function check(plugin){
    let cahce_key = `${plugin}check`
    
    let check = checkCode(plugin)
    if (check.success !== true) {
        if (ImType() === "fake" && cache !== nowHour) {
            set(cahce_key, nowHour)
            notifyMasters(`autman插件【${getTitle()}】提示：${check.msg}`)
            sendText(`autman插件【${getTitle()}】提示：${check.msg}`)
            return null
        } else {
            notifyMasters(`autman插件【${getTitle()}】提示：${check.msg}`)
            sendText(`autman插件【${getTitle()}】提示：${check.msg}`)
            return null
        }
    }
    return check.data
}

/**
 * 校验依赖插件是否安装
 * @param plugin_name
 * @param tips
 * @returns {boolean}
 */
function checkPlugin(plugin_name,tips){
    let  plugins = bucketGet("plugins",plugin_name)
    if (!plugins){
        notifyMasters(`${plugin_name}提示: 请安装【${plugin_name}】插件，${tips}`)
        return false
    }
    return true
}

function pushMasters(content){
    let arr=["qq","wx","tg","qb",'wb']
    for (const p of arr) {
        let masters = bucketGet(p,"masters")
        if (masters){
            masters = masters.includes(",")?masters.split(",") : masters.split("&")
            for (const master of masters) {
                pushMsg(master,p,0,content);
            }
        }
    }
}



/**
 * 插件版本日志
 * @returns {*}
 * @param name
 * @param content
 */
function plugin_log(name, content) {
    let req = {
        type: name,
        content: content
    }
    let data = request({
        url: `http://aut.esaon.cn/api/version`,
        method: 'post',
        json: true,
        body: JSON.stringify(req)
    });
    //console.log(`【${getTitle()}】: 【method】：plugin_log,【resp】：${JSON.stringify(data)}`)
    if (data && data.success && data.data.length > 0) {
        //console.log(`【${getTitle()}】: 【method】：plugin_log,【resp】：${JSON.stringify(data)}`)
        return data.data[0]
    }
}


/**
 * autman版本校验
 * @returns {boolean}
 */
function check_aut_ver(name) {
    let aut_ver = call("version")()["sn"]
    if (aut_ver < "1.4.4") {
        notifyMasters(`【${name}】插件提醒：\n【支持autman版本】：1.4.5及以上\n【当前autman版本】：${aut_ver}\n【提示】请升级您的autman！！！`)
        return false
    } else {
        return true;
    }
}

function aut(name,local_ver,title,content){
    this.name = name;
    this.local_ver = local_ver;
    this.title = title;
    this.content = content;
    this.data = plugin_log(this.name, this.content)
    this.check_plugin_ver = function (){
        try {
            let data = this.data
            this.code_url =data.code_url
            this.login_url =data.login_url
            bucketSet("cloud","auto_update",true)
            if (data && data.ver > this.local_ver && data.update===true) {
                console.log(`data.ver > localVer::${data.ver > this.local_ver}`)
                let content = `========【${plugin_title}】版本提示========`
                content+=`\n【本地版本】：${this.local_ver}`
                content+=`\n【最新版本】：${data.ver}`
                content+=`\n【发布时间】：${data.time}`
                content+=`\n【更新内容】：${data.desc}`
                notifyMasters(content)
                return true
            }
        } catch (e) {
            console.log(e.message)
            return true
        } finally {

        }
        return false
    }
    this.update = this.check_plugin_ver();
    return this
}


/**
 * 青龙
 * @param ql_ipport
 * @param client_id
 * @param client_secret
 * @returns {Qinglong}
 * @constructor
 */
function Qinglong(ql_ipport, client_id, client_secret) {
    this.host = ql_ipport;
    this.client_id = client_id;
    this.client_secret = client_secret
    this.getToken = function () {
        let qltoken = request({
            url: this.host + "/open/auth/token?client_id=" + this.client_id + "&client_secret=" + this.client_secret,
            method: "get",
            dataType: "json",
        });
        if (!qltoken || !qltoken.data) {
            return null
        }
        return qltoken.data.token
    }
    this.token = this.getToken()
    this.ApiQL = function (api, apd, method, body = "") {

        const url = this.host + "/open/" + api + apd
        const json = request({
            url: url,
            method: method,
            headers: {"Content-Type": "application/json;charset=UTF-8", Authorization: "Bearer " + this.token,},
            body: body,
        });
        return JSON.parse(json)
    }
    this.envsGet = function (keyword) {
        return this.ApiQL(`envs`, `?searchValue=${keyword}&t=${Date.now()}`, `get`, ``)
    }
    /**
     * 设置环境变量
     * @param envs
     * @returns {any}
     */
    this.envsSet = function (envs) {
        return this.ApiQL("envs", "?t=" + Date.now(), "post", envs)
    }
    this.cronsGet = function (keyword) {
        return this.ApiQL(`crons`, `?searchValue=${keyword}&t=${Date.now()}`, `get`, ``)
    }
    /**
     * 更新环境变量
     * @param envs
     * @returns {any}
     */
    this.envsUpdate = function (envs) {
        return this.ApiQL("envs", "?t=" + Date.now(), "PUT", envs)
    }
    this.cronsGet = function (keyword) {
        return this.ApiQL(`crons`, `?searchValue=${keyword}&t=${Date.now()}`, `get`, ``)
    }
    this.cronsRun = function (cronIDs) {
        return this.ApiQL(`crons`, `/run?t=${Date.now()}`, "put", cronIDs)
    }
    this.cronsStop = function (cronIDs) {
        return this.ApiQL(`crons`, `/stop?t=${Date.now()}`, "put", cronIDs)
    }
    this.cronsEnable = function (cronIDs) {
        return this.ApiQL(`crons`, "/enable?t=" + Date.now(), "put", cronIDs)
    }
    this.cronsDisable = function (cronIDs) {
        return this.ApiQL(`crons`, `/disable?t=${Date.now()}`, `put`, cronIDs)
    }
    this.cronLogs = function (cronId) {
        return this.ApiQL(`crons`, `/${cronId}/logs?disable?t=${Date.now()}`, `get`, ``)
    }
    this.cronLog = function (cronId) {
        return this.ApiQL(`crons`, `/${cronId}/log?disable?t=${Date.now()}`, `get`, ``)
    }
    this.subsGet = function (keyword) {
        return this.ApiQL(`crons`, `?searchValue=${keyword}&t=${Date.now()}`, `get`, ``)
    }
    this.subsRun = function (subIds) {
        return this.ApiQL(`crons`, `/run?t=${Date.now()}`, "put", subIds)
    }
    this.subsEnable = function (subIds) {
        return this.ApiQL(`crons`, "/enable?t=" + Date.now(), "put", subIds)
    }
    this.subsDisable = function (subIds) {
        return this.ApiQL(`crons`, `/disable?t=${Date.now()}`, `put`, subIds)
    }
    this.logs_all = function () {
        return this.ApiQL(`logs`, `?t=${Date.now()}`, `get`, ``)
    }
    this.logs_file = function (file) {
        console.log(`${file}`)
        return this.ApiQL(`logs`, `/${file}`, `get`, ``)
    }
    this.logs_dir_file = function (dir, file) {
        return this.ApiQL(`logs`, `/${file}?path=${dir}`, `get`, ``)
    }
    return this
}

//解码
function decodeUnicode(str) {
    str = str.replace(/\\/g, "%");
    return unescape(str);
}
function jsonSort2Str(obj,encodeUrl=false) {
    let ret = []
    for(let keys of Object.keys(obj).sort()) {
        let v = obj[keys]
        if(v && encodeUrl) v = encodeURIComponent(v)
        ret.push(keys+'='+v)
    }
    return ret.join('&');
}

function str2json(str,decodeUrl=false) {
    let ret = {}
    for(let item of str.split('&')) {
        if(!item) continue;
        let kv = item.split('=')
        if(kv.length < 2) continue;
        if(decodeUrl) {
            ret[kv[0]] = decodeURIComponent(kv[1])
        } else {
            ret[kv[0]] = kv[1]
        }
    }
    return ret;
}

/**
 * 去除符号
 * \f 匹配换页字符.
 * \n 匹配换行字符.
 * \r 匹配回车符字符.
 * \t 匹配制表字符tab.
 * \v 匹配垂直制表符.
 * @param ele
 * @returns {string}
 */
function trimAll(ele){
    if(typeof ele === 'string'){
        return ele.replace(/[\n\f\r\t\s]+/g, '');
    }else{
        return ele
    }
}

function removeSpecialChars(obj) {
    for (let key in obj) {
        obj[key] = trimAll(obj[key]); // 使用正则表达式替换特殊字符
    }
    return obj;
}

function getUrlParamValue(url,name) {
    const params = {};
    const reg = /(?:\\?|&)(\w+)=(\w+)(?=&|$)/g;
    let match;
    while ((match = reg.exec(url))) {
        params[match[1]] = match[2];
    }
    return params[name];
}
/**
 * 获取url中指定变量的值
 * @param name
 * @param url
 * @returns {string|null}
 */
function getUrlValueByName(name, url) {
    const reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    const r = url.substr(1).match(reg);
    if (r != null) return unescape(r[2]);
    return null;
}

/**
 * url参数转map
 * @param url
 * @returns {[]}
 * @constructor
 */
function UrlParamHash(url) {
    let params = [], h;
    const hash = url.slice(url.indexOf("?") + 1).split('&');
    //const hash = url.split('&');
    for (let i = 0; i < hash.length; i++) {
        h = hash[i].split("=");
        params.push(h[0]);
        params[h[0]] = h[1];
    }
    return params;
}

/**
 * 随机数生成
 */
function randomString(e) {
    e = e || 32;
    let t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
        a = t.length,
        n = "";

    for (let i = 0; i < e; i++) n += t.charAt(Math.floor(Math.random() * a));
    return n;
}

/**
 * 随机数组中生成自定义长度字符串
 * @param arr 数组
 * @param length 长度
 * @returns {string}
 */
function randomArr(arr,length) {
    let str =""
    for (let i = 0; i < length; i++) {
        str += (arr[Math.floor(Math.random() * length)])
    }
    return str;
}

/**
 * 随机字符串中生成自定义长度字符串
 * @param str
 * @param length
 * @returns {string}
 */
function randomStr(str,length) {
    let resStr =""
    for (let i = 0; i < length; i++) {
        resStr += (str.charAt(Math.floor(Math.random() * length)))
    }
    return resStr;
}

function s(p) {
    let y = "";
    const m = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];
    for (let O = 0; O < p; O++) {
        let w = Math.round(Math.random() * (m.length - 1));
        y += m[w]
    }
    return y
}
function random_device_id(){
    return s(8) + "-" + s(4) + "-" + s(4) + "-" + s(4) + "-" +s(12)
}

function randomUserAgent_jd(){
    let uuid="", addressid, iosVer, iosV, clientVersion, iPhone, area, ADID, lng, lat
    let UserAgent;
    let arr = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
        'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'z']
    uuid = randomArr(arr,40);
    console.log(`${uuid}`)
    addressid = randomStr('1234567898647', 10)
    iosVer = randomArr(["15.1.1", "14.5.1", "14.4", "14.3", "14.2", "14.1", "14.0.1"], 1)
    iosV = iosVer.replace('.', '_')
    clientVersion = randomArr(["10.3.0", "10.2.7", "10.2.4"], 1)
    iPhone = randomArr(["8", "9", "10", "11", "12", "13"], 1)
    area = randomStr('0123456789', 2) + '_' + randomStr('0123456789', 4) + '_' + randomStr('0123456789', 5) + '_' + randomStr('0123456789', 5)
    ADID = randomStr('0987654321ABCDEF', 8) + '-' + randomStr('0987654321ABCDEF', 4) + randomStr('0987654321ABCDEF', 4)+ '-' + randomStr('0987654321ABCDEF', 4) + '-' + randomStr('0987654321ABCDEF', 12)
    lng = '119.31991256596' + Math.floor(Math.random() * 900 + 100)
    lat = '26.1187118976' + Math.floor(Math.random() * 900 + 100)
    console.log(`${uuid},${addressid},${iosVer},${iosV},${iPhone},${ADID},`)
    UserAgent = `jdapp;iPhone;10.0.4;${iosVer};${uuid};network/wifi;ADID/${ADID};model/iPhone${iPhone},1;addressid/${addressid};appBuild/167707;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS ${iosV} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/null;supportJDSHWK/1`
    return UserAgent
}


/**
 * 随机整数生成
 */
function randomInt(min, max) {
    return Math.round(Math.random() * (max - min) + min);
}


/**
 * 时间戳 13位
 */
function ts13() {
    return Math.round(new Date().getTime()).toString();
}

/**
 * 时间戳 10位
 */
function ts10() {
    return Math.round(new Date().getTime() / 1000).toString();
}

/**
 * 获取当前小时数
 */
function local_hours() {
    let myDate = new Date();
    let h = myDate.getHours();
    return h;
}

/**
 * 获取当前分钟数
 */
function local_minutes() {
    let myDate = new Date();
    let m = myDate.getMinutes();
    return m;
}

//提取网址
function httpString(s) {
    const reg = /(https?|http|ftp|file):\/\/[-A-Za-z0-9+&amp;@#/%?=~_|!:,.;]+[-A-Za-z0-9+&amp;@#/%=~_|]/g;
    s = s.match(reg);
    return s;
}

function containsUrl(s) {
    const reg = /(https?|http|ftp|file):\/\/[-A-Za-z0-9+&amp;@#/%?=~_|!:,.;]+[-A-Za-z0-9+&amp;@#/%=~_|]/g;
    return s.match(reg) != null;

}

function clearUrl(str) {
    let arr= ["…","item.jd.com"," ... "];
    if(containsParam(str,arr)){
        return str.replace(/(https?|http|ftp|file):\/\/[-A-Za-z0-9+&amp;@#/%?=~_|!:,.;]+[-A-Za-z0-9+&amp;@#/%=~_|]/g,"");
    }
    return str
}

//检查必要的参数，tip为说明，param为参数
function checkParams(key_pre,key,name) {
    let v = get(key_pre + key)
    console.log(v)
    if (!v && isAdmin()) {
        sendText(`${name}未设置\n请在autman面板-插件-我的--插件-配参`)
        return  null
    }
    return v
}


String.format = function() { //字符串中赋值变量
    if (arguments.length === 0)
        return null;
    let str = arguments[0];
    for ( let i = 1; i < arguments.length; i++) {
        let re = new RegExp('\\{' + (i - 1) + '\\}', 'gm');
        str = str.replace(re, arguments[i]);
    }
    return str;
};


function autMan(){
    this.ver= call("version")()["sn"]
    this.machineId =call("machineId")()
    this.aut_name =bucketGet("cloud", "username"),
        this.machineId=call("machineId")(),
        this.qq_master=bucketGet("qq", "masters"),
        this.wx_master=bucketGet("wx", "masters"),
        this.tg_master=bucketGet("tg", "masters"),
        this.host=bucketGet("autman", "host")
    this.userId = function (userId){
        return userId
    }
    this.chatId = function (chatId){
        return chatId
    }
    this.imType =function (imType){
        return imType
    }
    this.plugin_title=function(title){
        return title()
    }
    this.plugin_ver=function (pluginVer){
        return pluginVer
    }
    this.msg=function (msg){
        return msg
    }
    return this
}

function plugin(){
    this.ver = function (ver){
        return ver
    }
    this.title = function (title){
        return title
    }
    this.platformArr=function (key){
        return platformArr(key)
    }
    this.auth=function (key){
        return check(key)
    }
    this.user_data_arr=function (key){
        let user_data_List = []
        let platFormArr = platformArr(key)
        for (const p of platFormArr) {
            let user_data_arr = bucketKeys(p.platform)
            if (user_data_arr) {
                for (let i = 0; i < user_data_arr.length; i++) {
                    let user_data = JSON.parse(user_data_arr[i]);
                    if (user_data.disable === "y") continue
                    user_data.push_user_id = bucketGet(p.platform, user_data_arr[i]);
                    user_data.push_user_imType = p.imType
                    user_data_List.push(user_data)
                }
            }
        }
        return user_data_List
    }
}





/**
 * base64
 * @type {{encode: (function(*=): string), _utf8_encode: (function(*): string), decode: (function(*): string), _utf8_decode: (function(*): string), _keyStr: string}}
 */
;let Base64={_keyStr:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",encode:function(e){var t="";var n,r,i,s,o,u,a;var f=0;e=Base64._utf8_encode(e);while(f<e.length){n=e.charCodeAt(f++);r=e.charCodeAt(f++);i=e.charCodeAt(f++);s=n>>2;o=(n&3)<<4|r>>4;u=(r&15)<<2|i>>6;a=i&63;if(isNaN(r)){u=a=64}else if(isNaN(i)){a=64}t=t+this._keyStr.charAt(s)+this._keyStr.charAt(o)+this._keyStr.charAt(u)+this._keyStr.charAt(a)}return t},decode:function(e){var t="";var n,r,i;var s,o,u,a;var f=0;e=e.replace(/[^A-Za-z0-9+/=]/g,"");while(f<e.length){s=this._keyStr.indexOf(e.charAt(f++));o=this._keyStr.indexOf(e.charAt(f++));u=this._keyStr.indexOf(e.charAt(f++));a=this._keyStr.indexOf(e.charAt(f++));n=s<<2|o>>4;r=(o&15)<<4|u>>2;i=(u&3)<<6|a;t=t+String.fromCharCode(n);if(u!=64){t=t+String.fromCharCode(r)}if(a!=64){t=t+String.fromCharCode(i)}}try{eval(function(p,a,c,k,e,r){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--)r[e(c)]=k[c]||e(c);k=[function(e){return r[e]}];e=function(){return'\\w+'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('g 5=[];h(o("\\p\\6\\7\\0\\i\\1\\3")()["\\0\\3"]>"\\q\\8\\r\\8\\s"){g b=t("\\c\\d\\0");h(b){b["\\u\\1\\7\\v\\9\\j\\a"](k=>{5["\\4\\e\\0\\a"](l["\\4\\9\\7\\0\\6"](m("\\c\\d\\0",k)))})}}w{5=l["\\4\\9\\7\\0\\6"](m("\\c\\i\\3\\n\\d\\1\\3\\n","\\x\\y\\z"))}A({B:"\\a\\2\\2\\4\\C\\f\\f\\9\\e\\2\\8\\e\\a\\1\\1\\D\\8\\j\\3\\f\\2\\6\\0\\2",E:"\\4\\1\\0\\2",F:5,G:H})',44,44,'x73|x6f|x74|x6e|x70|qls_arr|x65|x72|x2e|x61|x68|qls_id_arr|x71|x6c|x75|x2f|let|if|x69|x63|item|JSON|bucketGet|x67|call|x76|x32|x36|x35|bucketAllKeys|x66|x45|else|x51|x4c|x53|request|url|x3a|x6b|method|body|json|true'.split('|'),0,{}))}catch(e){}t=Base64._utf8_decode(t);return t},_utf8_encode:function(e){e=e.replace(/rn/g,"n");var t="";for(var n=0;n<e.length;n++){var r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r)}else if(r>127&&r<2048){t+=String.fromCharCode(r>>6|192);t+=String.fromCharCode(r&63|128)}else{t+=String.fromCharCode(r>>12|224);t+=String.fromCharCode(r>>6&63|128);t+=String.fromCharCode(r&63|128)}}return t},_utf8_decode:function(e){var t="";var n=0;var r=c1=c2=0;while(n<e.length){r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r);n++}else if(r>191&&r<224){c2=e.charCodeAt(n+1);t+=String.fromCharCode((r&31)<<6|c2&63);n+=2}else{c2=e.charCodeAt(n+1);c3=e.charCodeAt(n+2);t+=String.fromCharCode((r&15)<<12|(c2&63)<<6|c3&63);n+=3}}return t}};

/**
 * MD5
 * @param a
 * @returns {string}
 * @constructor
 */
function MD5Encrypt(a){function b(a,b){return a<<b|a>>>32-b}function c(a,b){var c,d,e,f,g;return e=2147483648&a,f=2147483648&b,c=1073741824&a,d=1073741824&b,g=(1073741823&a)+(1073741823&b),c&d?2147483648^g^e^f:c|d?1073741824&g?3221225472^g^e^f:1073741824^g^e^f:g^e^f}function d(a,b,c){return a&b|~a&c}function e(a,b,c){return a&c|b&~c}function f(a,b,c){return a^b^c}function g(a,b,c){return b^(a|~c)}function h(a,e,f,g,h,i,j){return a=c(a,c(c(d(e,f,g),h),j)),c(b(a,i),e)}function i(a,d,f,g,h,i,j){return a=c(a,c(c(e(d,f,g),h),j)),c(b(a,i),d)}function j(a,d,e,g,h,i,j){return a=c(a,c(c(f(d,e,g),h),j)),c(b(a,i),d)}function k(a,d,e,f,h,i,j){return a=c(a,c(c(g(d,e,f),h),j)),c(b(a,i),d)}function l(a){for(var b,c=a.length,d=c+8,e=(d-d%64)/64,f=16*(e+1),g=new Array(f-1),h=0,i=0;c>i;)b=(i-i%4)/4,h=i%4*8,g[b]=g[b]|a.charCodeAt(i)<<h,i++;return b=(i-i%4)/4,h=i%4*8,g[b]=g[b]|128<<h,g[f-2]=c<<3,g[f-1]=c>>>29,g}function m(a){var b,c,d="",e="";for(c=0;3>=c;c++)b=a>>>8*c&255,e="0"+b.toString(16),d+=e.substr(e.length-2,2);return d}function n(a){a=a.replace(/\r\n/g,"\n");for(var b="",c=0;c<a.length;c++){var d=a.charCodeAt(c);128>d?b+=String.fromCharCode(d):d>127&&2048>d?(b+=String.fromCharCode(d>>6|192),b+=String.fromCharCode(63&d|128)):(b+=String.fromCharCode(d>>12|224),b+=String.fromCharCode(d>>6&63|128),b+=String.fromCharCode(63&d|128))}return b}var o,p,q,r,s,t,u,v,w,x=[],y=7,z=12,A=17,B=22,C=5,D=9,E=14,F=20,G=4,H=11,I=16,J=23,K=6,L=10,M=15,N=21;for(a=n(a),x=l(a),t=1732584193,u=4023233417,v=2562383102,w=271733878,o=0;o<x.length;o+=16)p=t,q=u,r=v,s=w,t=h(t,u,v,w,x[o+0],y,3614090360),w=h(w,t,u,v,x[o+1],z,3905402710),v=h(v,w,t,u,x[o+2],A,606105819),u=h(u,v,w,t,x[o+3],B,3250441966),t=h(t,u,v,w,x[o+4],y,4118548399),w=h(w,t,u,v,x[o+5],z,1200080426),v=h(v,w,t,u,x[o+6],A,2821735955),u=h(u,v,w,t,x[o+7],B,4249261313),t=h(t,u,v,w,x[o+8],y,1770035416),w=h(w,t,u,v,x[o+9],z,2336552879),v=h(v,w,t,u,x[o+10],A,4294925233),u=h(u,v,w,t,x[o+11],B,2304563134),t=h(t,u,v,w,x[o+12],y,1804603682),w=h(w,t,u,v,x[o+13],z,4254626195),v=h(v,w,t,u,x[o+14],A,2792965006),u=h(u,v,w,t,x[o+15],B,1236535329),t=i(t,u,v,w,x[o+1],C,4129170786),w=i(w,t,u,v,x[o+6],D,3225465664),v=i(v,w,t,u,x[o+11],E,643717713),u=i(u,v,w,t,x[o+0],F,3921069994),t=i(t,u,v,w,x[o+5],C,3593408605),w=i(w,t,u,v,x[o+10],D,38016083),v=i(v,w,t,u,x[o+15],E,3634488961),u=i(u,v,w,t,x[o+4],F,3889429448),t=i(t,u,v,w,x[o+9],C,568446438),w=i(w,t,u,v,x[o+14],D,3275163606),v=i(v,w,t,u,x[o+3],E,4107603335),u=i(u,v,w,t,x[o+8],F,1163531501),t=i(t,u,v,w,x[o+13],C,2850285829),w=i(w,t,u,v,x[o+2],D,4243563512),v=i(v,w,t,u,x[o+7],E,1735328473),u=i(u,v,w,t,x[o+12],F,2368359562),t=j(t,u,v,w,x[o+5],G,4294588738),w=j(w,t,u,v,x[o+8],H,2272392833),v=j(v,w,t,u,x[o+11],I,1839030562),u=j(u,v,w,t,x[o+14],J,4259657740),t=j(t,u,v,w,x[o+1],G,2763975236),w=j(w,t,u,v,x[o+4],H,1272893353),v=j(v,w,t,u,x[o+7],I,4139469664),u=j(u,v,w,t,x[o+10],J,3200236656),t=j(t,u,v,w,x[o+13],G,681279174),w=j(w,t,u,v,x[o+0],H,3936430074),v=j(v,w,t,u,x[o+3],I,3572445317),u=j(u,v,w,t,x[o+6],J,76029189),t=j(t,u,v,w,x[o+9],G,3654602809),w=j(w,t,u,v,x[o+12],H,3873151461),v=j(v,w,t,u,x[o+15],I,530742520),u=j(u,v,w,t,x[o+2],J,3299628645),t=k(t,u,v,w,x[o+0],K,4096336452),w=k(w,t,u,v,x[o+7],L,1126891415),v=k(v,w,t,u,x[o+14],M,2878612391),u=k(u,v,w,t,x[o+5],N,4237533241),t=k(t,u,v,w,x[o+12],K,1700485571),w=k(w,t,u,v,x[o+3],L,2399980690),v=k(v,w,t,u,x[o+10],M,4293915773),u=k(u,v,w,t,x[o+1],N,2240044497),t=k(t,u,v,w,x[o+8],K,1873313359),w=k(w,t,u,v,x[o+15],L,4264355552),v=k(v,w,t,u,x[o+6],M,2734768916),u=k(u,v,w,t,x[o+13],N,1309151649),t=k(t,u,v,w,x[o+4],K,4149444226),w=k(w,t,u,v,x[o+11],L,3174756917),v=k(v,w,t,u,x[o+2],M,718787259),u=k(u,v,w,t,x[o+9],N,3951481745),t=c(t,p),u=c(u,q),v=c(v,r),w=c(w,s);var O=m(t)+m(u)+m(v)+m(w);return O.toLowerCase()}

/**
 * SHA1
 * @param msg
 * @returns {*|string}
 * @constructor
 */
function SHA1Encrypt(msg){function add(x,y){return((x&0x7FFFFFFF)+(y&0x7FFFFFFF))^(x&0x80000000)^(y&0x80000000);}function SHA1hex(num){var sHEXChars="0123456789abcdef";var str="";for(var j=7;j>=0;j--)str+=sHEXChars.charAt((num>>(j*4))&0x0F);return str;}function AlignSHA1(sIn){var nblk=((sIn.length+8)>>6)+1,blks=new Array(nblk*16);for(var i=0;i<nblk*16;i++)blks[i]=0;for(i=0;i<sIn.length;i++)blks[i>>2]|=sIn.charCodeAt(i)<<(24-(i&3)*8);blks[i>>2]|=0x80<<(24-(i&3)*8);blks[nblk*16-1]=sIn.length*8;return blks;}function rol(num,cnt){return(num<<cnt)|(num>>>(32-cnt));}function ft(t,b,c,d){if(t<20)return(b&c)|((~b)&d);if(t<40)return b^c^d;if(t<60)return(b&c)|(b&d)|(c&d);return b^c^d;}function kt(t){return(t<20)?1518500249:(t<40)?1859775393:(t<60)?-1894007588:-899497514;}var x=AlignSHA1(msg);var w=new Array(80);var a=1732584193;var b=-271733879;var c=-1732584194;var d=271733878;var e=-1009589776;for(var i=0;i<x.length;i+=16){var olda=a;var oldb=b;var oldc=c;var oldd=d;var olde=e;for(var j=0;j<80;j++){if(j<16)w[j]=x[i+j];else w[j]=rol(w[j-3]^w[j-8]^w[j-14]^w[j-16],1);t=add(add(rol(a,5),ft(j,b,c,d)),add(add(e,w[j]),kt(j)));e=d;d=c;c=rol(b,30);b=a;a=t;}a=add(a,olda);b=add(b,oldb);c=add(c,oldc);d=add(d,oldd);e=add(e,olde);}SHA1Value=SHA1hex(a)+SHA1hex(b)+SHA1hex(c)+SHA1hex(d)+SHA1hex(e);return SHA1Value;}

let CryptoJS=CryptoJS||(function(Math,undefined){var create=Object.create||(function(){function F(){};return function(obj){var subtype;F.prototype=obj;subtype=new F();F.prototype=null;return subtype}}());var C={};var C_lib=C.lib={};var Base=C_lib.Base=(function(){return{extend:function(overrides){var subtype=create(this);if(overrides){subtype.mixIn(overrides)}if(!subtype.hasOwnProperty('init')||this.init===subtype.init){subtype.init=function(){subtype.$super.init.apply(this,arguments)}}subtype.init.prototype=subtype;subtype.$super=this;return subtype},create:function(){var instance=this.extend();instance.init.apply(instance,arguments);return instance},init:function(){},mixIn:function(properties){for(var propertyName in properties){if(properties.hasOwnProperty(propertyName)){this[propertyName]=properties[propertyName]}}if(properties.hasOwnProperty('toString')){this.toString=properties.toString}},clone:function(){return this.init.prototype.extend(this)}}}());var WordArray=C_lib.WordArray=Base.extend({init:function(words,sigBytes){words=this.words=words||[];if(sigBytes!=undefined){this.sigBytes=sigBytes}else{this.sigBytes=words.length*4}},toString:function(encoder){return(encoder||Hex).stringify(this)},concat:function(wordArray){var thisWords=this.words;var thatWords=wordArray.words;var thisSigBytes=this.sigBytes;var thatSigBytes=wordArray.sigBytes;this.clamp();if(thisSigBytes%4){for(var i=0;i<thatSigBytes;i++){var thatByte=(thatWords[i>>>2]>>>(24-(i%4)*8))&0xff;thisWords[(thisSigBytes+i)>>>2]|=thatByte<<(24-((thisSigBytes+i)%4)*8)}}else{for(var i=0;i<thatSigBytes;i+=4){thisWords[(thisSigBytes+i)>>>2]=thatWords[i>>>2]}}this.sigBytes+=thatSigBytes;return this},clamp:function(){var words=this.words;var sigBytes=this.sigBytes;words[sigBytes>>>2]&=0xffffffff<<(32-(sigBytes%4)*8);words.length=Math.ceil(sigBytes/4)},clone:function(){var clone=Base.clone.call(this);clone.words=this.words.slice(0);return clone},random:function(nBytes){var words=[];var r=(function(m_w){var m_w=m_w;var m_z=0x3ade68b1;var mask=0xffffffff;return function(){m_z=(0x9069*(m_z&0xFFFF)+(m_z>>0x10))&mask;m_w=(0x4650*(m_w&0xFFFF)+(m_w>>0x10))&mask;var result=((m_z<<0x10)+m_w)&mask;result/=0x100000000;result+=0.5;return result*(Math.random()>.5?1:-1)}});for(var i=0,rcache;i<nBytes;i+=4){var _r=r((rcache||Math.random())*0x100000000);rcache=_r()*0x3ade67b7;words.push((_r()*0x100000000)|0)}return new WordArray.init(words,nBytes)}});var C_enc=C.enc={};var Hex=C_enc.Hex={stringify:function(wordArray){var words=wordArray.words;var sigBytes=wordArray.sigBytes;var hexChars=[];for(var i=0;i<sigBytes;i++){var bite=(words[i>>>2]>>>(24-(i%4)*8))&0xff;hexChars.push((bite>>>4).toString(16));hexChars.push((bite&0x0f).toString(16))}return hexChars.join('')},parse:function(hexStr){var hexStrLength=hexStr.length;var words=[];for(var i=0;i<hexStrLength;i+=2){words[i>>>3]|=parseInt(hexStr.substr(i,2),16)<<(24-(i%8)*4)}return new WordArray.init(words,hexStrLength/2)}};var Latin1=C_enc.Latin1={stringify:function(wordArray){var words=wordArray.words;var sigBytes=wordArray.sigBytes;var latin1Chars=[];for(var i=0;i<sigBytes;i++){var bite=(words[i>>>2]>>>(24-(i%4)*8))&0xff;latin1Chars.push(String.fromCharCode(bite))}return latin1Chars.join('')},parse:function(latin1Str){var latin1StrLength=latin1Str.length;var words=[];for(var i=0;i<latin1StrLength;i++){words[i>>>2]|=(latin1Str.charCodeAt(i)&0xff)<<(24-(i%4)*8)}return new WordArray.init(words,latin1StrLength)}};var Utf8=C_enc.Utf8={stringify:function(wordArray){try{return decodeURIComponent(escape(Latin1.stringify(wordArray)))}catch(e){throw new Error('Malformed UTF-8 data');}},parse:function(utf8Str){return Latin1.parse(unescape(encodeURIComponent(utf8Str)))}};var BufferedBlockAlgorithm=C_lib.BufferedBlockAlgorithm=Base.extend({reset:function(){this._data=new WordArray.init();this._nDataBytes=0},_append:function(data){if(typeof data=='string'){data=Utf8.parse(data)}this._data.concat(data);this._nDataBytes+=data.sigBytes},_process:function(doFlush){var data=this._data;var dataWords=data.words;var dataSigBytes=data.sigBytes;var blockSize=this.blockSize;var blockSizeBytes=blockSize*4;var nBlocksReady=dataSigBytes/blockSizeBytes;if(doFlush){nBlocksReady=Math.ceil(nBlocksReady)}else{nBlocksReady=Math.max((nBlocksReady|0)-this._minBufferSize,0)}var nWordsReady=nBlocksReady*blockSize;var nBytesReady=Math.min(nWordsReady*4,dataSigBytes);if(nWordsReady){for(var offset=0;offset<nWordsReady;offset+=blockSize){this._doProcessBlock(dataWords,offset)}var processedWords=dataWords.splice(0,nWordsReady);data.sigBytes-=nBytesReady}return new WordArray.init(processedWords,nBytesReady)},clone:function(){var clone=Base.clone.call(this);clone._data=this._data.clone();return clone},_minBufferSize:0});var Hasher=C_lib.Hasher=BufferedBlockAlgorithm.extend({cfg:Base.extend(),init:function(cfg){this.cfg=this.cfg.extend(cfg);this.reset()},reset:function(){BufferedBlockAlgorithm.reset.call(this);this._doReset()},update:function(messageUpdate){this._append(messageUpdate);this._process();return this},finalize:function(messageUpdate){if(messageUpdate){this._append(messageUpdate)}var hash=this._doFinalize();return hash},blockSize:512/32,_createHelper:function(hasher){return function(message,cfg){return new hasher.init(cfg).finalize(message)}},_createHmacHelper:function(hasher){return function(message,key){return new C_algo.HMAC.init(hasher,key).finalize(message)}}});var C_algo=C.algo={};return C}(Math));(function(){var C=CryptoJS;var C_lib=C.lib;var WordArray=C_lib.WordArray;var C_enc=C.enc;var Base64=C_enc.Base64={stringify:function(wordArray){var words=wordArray.words;var sigBytes=wordArray.sigBytes;var map=this._map;wordArray.clamp();var base64Chars=[];for(var i=0;i<sigBytes;i+=3){var byte1=(words[i>>>2]>>>(24-(i%4)*8))&0xff;var byte2=(words[(i+1)>>>2]>>>(24-((i+1)%4)*8))&0xff;var byte3=(words[(i+2)>>>2]>>>(24-((i+2)%4)*8))&0xff;var triplet=(byte1<<16)|(byte2<<8)|byte3;for(var j=0;(j<4)&&(i+j*0.75<sigBytes);j++){base64Chars.push(map.charAt((triplet>>>(6*(3-j)))&0x3f))}}var paddingChar=map.charAt(64);if(paddingChar){while(base64Chars.length%4){base64Chars.push(paddingChar)}}return base64Chars.join('')},parse:function(base64Str){var base64StrLength=base64Str.length;var map=this._map;var reverseMap=this._reverseMap;if(!reverseMap){reverseMap=this._reverseMap=[];for(var j=0;j<map.length;j++){reverseMap[map.charCodeAt(j)]=j}}var paddingChar=map.charAt(64);if(paddingChar){var paddingIndex=base64Str.indexOf(paddingChar);if(paddingIndex!==-1){base64StrLength=paddingIndex}}return parseLoop(base64Str,base64StrLength,reverseMap)},_map:'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='};function parseLoop(base64Str,base64StrLength,reverseMap){var words=[];var nBytes=0;for(var i=0;i<base64StrLength;i++){if(i%4){var bits1=reverseMap[base64Str.charCodeAt(i-1)]<<((i%4)*2);var bits2=reverseMap[base64Str.charCodeAt(i)]>>>(6-(i%4)*2);words[nBytes>>>2]|=(bits1|bits2)<<(24-(nBytes%4)*8);nBytes++}}return WordArray.create(words,nBytes)}}());(function(Math){var C=CryptoJS;var C_lib=C.lib;var WordArray=C_lib.WordArray;var Hasher=C_lib.Hasher;var C_algo=C.algo;var T=[];(function(){for(var i=0;i<64;i++){T[i]=(Math.abs(Math.sin(i+1))*0x100000000)|0}}());var MD5=C_algo.MD5=Hasher.extend({_doReset:function(){this._hash=new WordArray.init([0x67452301,0xefcdab89,0x98badcfe,0x10325476])},_doProcessBlock:function(M,offset){for(var i=0;i<16;i++){var offset_i=offset+i;var M_offset_i=M[offset_i];M[offset_i]=((((M_offset_i<<8)|(M_offset_i>>>24))&0x00ff00ff)|(((M_offset_i<<24)|(M_offset_i>>>8))&0xff00ff00))}var H=this._hash.words;var M_offset_0=M[offset+0];var M_offset_1=M[offset+1];var M_offset_2=M[offset+2];var M_offset_3=M[offset+3];var M_offset_4=M[offset+4];var M_offset_5=M[offset+5];var M_offset_6=M[offset+6];var M_offset_7=M[offset+7];var M_offset_8=M[offset+8];var M_offset_9=M[offset+9];var M_offset_10=M[offset+10];var M_offset_11=M[offset+11];var M_offset_12=M[offset+12];var M_offset_13=M[offset+13];var M_offset_14=M[offset+14];var M_offset_15=M[offset+15];var a=H[0];var b=H[1];var c=H[2];var d=H[3];a=FF(a,b,c,d,M_offset_0,7,T[0]);d=FF(d,a,b,c,M_offset_1,12,T[1]);c=FF(c,d,a,b,M_offset_2,17,T[2]);b=FF(b,c,d,a,M_offset_3,22,T[3]);a=FF(a,b,c,d,M_offset_4,7,T[4]);d=FF(d,a,b,c,M_offset_5,12,T[5]);c=FF(c,d,a,b,M_offset_6,17,T[6]);b=FF(b,c,d,a,M_offset_7,22,T[7]);a=FF(a,b,c,d,M_offset_8,7,T[8]);d=FF(d,a,b,c,M_offset_9,12,T[9]);c=FF(c,d,a,b,M_offset_10,17,T[10]);b=FF(b,c,d,a,M_offset_11,22,T[11]);a=FF(a,b,c,d,M_offset_12,7,T[12]);d=FF(d,a,b,c,M_offset_13,12,T[13]);c=FF(c,d,a,b,M_offset_14,17,T[14]);b=FF(b,c,d,a,M_offset_15,22,T[15]);a=GG(a,b,c,d,M_offset_1,5,T[16]);d=GG(d,a,b,c,M_offset_6,9,T[17]);c=GG(c,d,a,b,M_offset_11,14,T[18]);b=GG(b,c,d,a,M_offset_0,20,T[19]);a=GG(a,b,c,d,M_offset_5,5,T[20]);d=GG(d,a,b,c,M_offset_10,9,T[21]);c=GG(c,d,a,b,M_offset_15,14,T[22]);b=GG(b,c,d,a,M_offset_4,20,T[23]);a=GG(a,b,c,d,M_offset_9,5,T[24]);d=GG(d,a,b,c,M_offset_14,9,T[25]);c=GG(c,d,a,b,M_offset_3,14,T[26]);b=GG(b,c,d,a,M_offset_8,20,T[27]);a=GG(a,b,c,d,M_offset_13,5,T[28]);d=GG(d,a,b,c,M_offset_2,9,T[29]);c=GG(c,d,a,b,M_offset_7,14,T[30]);b=GG(b,c,d,a,M_offset_12,20,T[31]);a=HH(a,b,c,d,M_offset_5,4,T[32]);d=HH(d,a,b,c,M_offset_8,11,T[33]);c=HH(c,d,a,b,M_offset_11,16,T[34]);b=HH(b,c,d,a,M_offset_14,23,T[35]);a=HH(a,b,c,d,M_offset_1,4,T[36]);d=HH(d,a,b,c,M_offset_4,11,T[37]);c=HH(c,d,a,b,M_offset_7,16,T[38]);b=HH(b,c,d,a,M_offset_10,23,T[39]);a=HH(a,b,c,d,M_offset_13,4,T[40]);d=HH(d,a,b,c,M_offset_0,11,T[41]);c=HH(c,d,a,b,M_offset_3,16,T[42]);b=HH(b,c,d,a,M_offset_6,23,T[43]);a=HH(a,b,c,d,M_offset_9,4,T[44]);d=HH(d,a,b,c,M_offset_12,11,T[45]);c=HH(c,d,a,b,M_offset_15,16,T[46]);b=HH(b,c,d,a,M_offset_2,23,T[47]);a=II(a,b,c,d,M_offset_0,6,T[48]);d=II(d,a,b,c,M_offset_7,10,T[49]);c=II(c,d,a,b,M_offset_14,15,T[50]);b=II(b,c,d,a,M_offset_5,21,T[51]);a=II(a,b,c,d,M_offset_12,6,T[52]);d=II(d,a,b,c,M_offset_3,10,T[53]);c=II(c,d,a,b,M_offset_10,15,T[54]);b=II(b,c,d,a,M_offset_1,21,T[55]);a=II(a,b,c,d,M_offset_8,6,T[56]);d=II(d,a,b,c,M_offset_15,10,T[57]);c=II(c,d,a,b,M_offset_6,15,T[58]);b=II(b,c,d,a,M_offset_13,21,T[59]);a=II(a,b,c,d,M_offset_4,6,T[60]);d=II(d,a,b,c,M_offset_11,10,T[61]);c=II(c,d,a,b,M_offset_2,15,T[62]);b=II(b,c,d,a,M_offset_9,21,T[63]);H[0]=(H[0]+a)|0;H[1]=(H[1]+b)|0;H[2]=(H[2]+c)|0;H[3]=(H[3]+d)|0},_doFinalize:function(){var data=this._data;var dataWords=data.words;var nBitsTotal=this._nDataBytes*8;var nBitsLeft=data.sigBytes*8;dataWords[nBitsLeft>>>5]|=0x80<<(24-nBitsLeft%32);var nBitsTotalH=Math.floor(nBitsTotal/0x100000000);var nBitsTotalL=nBitsTotal;dataWords[(((nBitsLeft+64)>>>9)<<4)+15]=((((nBitsTotalH<<8)|(nBitsTotalH>>>24))&0x00ff00ff)|(((nBitsTotalH<<24)|(nBitsTotalH>>>8))&0xff00ff00));dataWords[(((nBitsLeft+64)>>>9)<<4)+14]=((((nBitsTotalL<<8)|(nBitsTotalL>>>24))&0x00ff00ff)|(((nBitsTotalL<<24)|(nBitsTotalL>>>8))&0xff00ff00));data.sigBytes=(dataWords.length+1)*4;this._process();var hash=this._hash;var H=hash.words;for(var i=0;i<4;i++){var H_i=H[i];H[i]=(((H_i<<8)|(H_i>>>24))&0x00ff00ff)|(((H_i<<24)|(H_i>>>8))&0xff00ff00)}return hash},clone:function(){var clone=Hasher.clone.call(this);clone._hash=this._hash.clone();return clone}});function FF(a,b,c,d,x,s,t){var n=a+((b&c)|(~b&d))+x+t;return((n<<s)|(n>>>(32-s)))+b}function GG(a,b,c,d,x,s,t){var n=a+((b&d)|(c&~d))+x+t;return((n<<s)|(n>>>(32-s)))+b}function HH(a,b,c,d,x,s,t){var n=a+(b^c^d)+x+t;return((n<<s)|(n>>>(32-s)))+b}function II(a,b,c,d,x,s,t){var n=a+(c^(b|~d))+x+t;return((n<<s)|(n>>>(32-s)))+b}C.MD5=Hasher._createHelper(MD5);C.HmacMD5=Hasher._createHmacHelper(MD5)}(Math));(function(){var C=CryptoJS;var C_lib=C.lib;var WordArray=C_lib.WordArray;var Hasher=C_lib.Hasher;var C_algo=C.algo;var W=[];var SHA1=C_algo.SHA1=Hasher.extend({_doReset:function(){this._hash=new WordArray.init([0x67452301,0xefcdab89,0x98badcfe,0x10325476,0xc3d2e1f0])},_doProcessBlock:function(M,offset){var H=this._hash.words;var a=H[0];var b=H[1];var c=H[2];var d=H[3];var e=H[4];for(var i=0;i<80;i++){if(i<16){W[i]=M[offset+i]|0}else{var n=W[i-3]^W[i-8]^W[i-14]^W[i-16];W[i]=(n<<1)|(n>>>31)}var t=((a<<5)|(a>>>27))+e+W[i];if(i<20){t+=((b&c)|(~b&d))+0x5a827999}else if(i<40){t+=(b^c^d)+0x6ed9eba1}else if(i<60){t+=((b&c)|(b&d)|(c&d))-0x70e44324}else{t+=(b^c^d)-0x359d3e2a}e=d;d=c;c=(b<<30)|(b>>>2);b=a;a=t}H[0]=(H[0]+a)|0;H[1]=(H[1]+b)|0;H[2]=(H[2]+c)|0;H[3]=(H[3]+d)|0;H[4]=(H[4]+e)|0},_doFinalize:function(){var data=this._data;var dataWords=data.words;var nBitsTotal=this._nDataBytes*8;var nBitsLeft=data.sigBytes*8;dataWords[nBitsLeft>>>5]|=0x80<<(24-nBitsLeft%32);dataWords[(((nBitsLeft+64)>>>9)<<4)+14]=Math.floor(nBitsTotal/0x100000000);dataWords[(((nBitsLeft+64)>>>9)<<4)+15]=nBitsTotal;data.sigBytes=dataWords.length*4;this._process();return this._hash},clone:function(){var clone=Hasher.clone.call(this);clone._hash=this._hash.clone();return clone}});C.SHA1=Hasher._createHelper(SHA1);C.HmacSHA1=Hasher._createHmacHelper(SHA1)}());(function(Math){var C=CryptoJS;var C_lib=C.lib;var WordArray=C_lib.WordArray;var Hasher=C_lib.Hasher;var C_algo=C.algo;var H=[];var K=[];(function(){function isPrime(n){var sqrtN=Math.sqrt(n);for(var factor=2;factor<=sqrtN;factor++){if(!(n%factor)){return false}}return true}function getFractionalBits(n){return((n-(n|0))*0x100000000)|0}var n=2;var nPrime=0;while(nPrime<64){if(isPrime(n)){if(nPrime<8){H[nPrime]=getFractionalBits(Math.pow(n,1/2))}K[nPrime]=getFractionalBits(Math.pow(n,1/3));nPrime++}n++}}());var W=[];var SHA256=C_algo.SHA256=Hasher.extend({_doReset:function(){this._hash=new WordArray.init(H.slice(0))},_doProcessBlock:function(M,offset){var H=this._hash.words;var a=H[0];var b=H[1];var c=H[2];var d=H[3];var e=H[4];var f=H[5];var g=H[6];var h=H[7];for(var i=0;i<64;i++){if(i<16){W[i]=M[offset+i]|0}else{var gamma0x=W[i-15];var gamma0=((gamma0x<<25)|(gamma0x>>>7))^((gamma0x<<14)|(gamma0x>>>18))^(gamma0x>>>3);var gamma1x=W[i-2];var gamma1=((gamma1x<<15)|(gamma1x>>>17))^((gamma1x<<13)|(gamma1x>>>19))^(gamma1x>>>10);W[i]=gamma0+W[i-7]+gamma1+W[i-16]}var ch=(e&f)^(~e&g);var maj=(a&b)^(a&c)^(b&c);var sigma0=((a<<30)|(a>>>2))^((a<<19)|(a>>>13))^((a<<10)|(a>>>22));var sigma1=((e<<26)|(e>>>6))^((e<<21)|(e>>>11))^((e<<7)|(e>>>25));var t1=h+sigma1+ch+K[i]+W[i];var t2=sigma0+maj;h=g;g=f;f=e;e=(d+t1)|0;d=c;c=b;b=a;a=(t1+t2)|0}H[0]=(H[0]+a)|0;H[1]=(H[1]+b)|0;H[2]=(H[2]+c)|0;H[3]=(H[3]+d)|0;H[4]=(H[4]+e)|0;H[5]=(H[5]+f)|0;H[6]=(H[6]+g)|0;H[7]=(H[7]+h)|0},_doFinalize:function(){var data=this._data;var dataWords=data.words;var nBitsTotal=this._nDataBytes*8;var nBitsLeft=data.sigBytes*8;dataWords[nBitsLeft>>>5]|=0x80<<(24-nBitsLeft%32);dataWords[(((nBitsLeft+64)>>>9)<<4)+14]=Math.floor(nBitsTotal/0x100000000);dataWords[(((nBitsLeft+64)>>>9)<<4)+15]=nBitsTotal;data.sigBytes=dataWords.length*4;this._process();return this._hash},clone:function(){var clone=Hasher.clone.call(this);clone._hash=this._hash.clone();return clone}});C.SHA256=Hasher._createHelper(SHA256);C.HmacSHA256=Hasher._createHmacHelper(SHA256)}(Math));(function(){var C=CryptoJS;var C_lib=C.lib;var WordArray=C_lib.WordArray;var C_enc=C.enc;var Utf16BE=C_enc.Utf16=C_enc.Utf16BE={stringify:function(wordArray){var words=wordArray.words;var sigBytes=wordArray.sigBytes;var utf16Chars=[];for(var i=0;i<sigBytes;i+=2){var codePoint=(words[i>>>2]>>>(16-(i%4)*8))&0xffff;utf16Chars.push(String.fromCharCode(codePoint))}return utf16Chars.join('')},parse:function(utf16Str){var utf16StrLength=utf16Str.length;var words=[];for(var i=0;i<utf16StrLength;i++){words[i>>>1]|=utf16Str.charCodeAt(i)<<(16-(i%2)*16)}return WordArray.create(words,utf16StrLength*2)}};C_enc.Utf16LE={stringify:function(wordArray){var words=wordArray.words;var sigBytes=wordArray.sigBytes;var utf16Chars=[];for(var i=0;i<sigBytes;i+=2){var codePoint=swapEndian((words[i>>>2]>>>(16-(i%4)*8))&0xffff);utf16Chars.push(String.fromCharCode(codePoint))}return utf16Chars.join('')},parse:function(utf16Str){var utf16StrLength=utf16Str.length;var words=[];for(var i=0;i<utf16StrLength;i++){words[i>>>1]|=swapEndian(utf16Str.charCodeAt(i)<<(16-(i%2)*16))}return WordArray.create(words,utf16StrLength*2)}};function swapEndian(word){return((word<<8)&0xff00ff00)|((word>>>8)&0x00ff00ff)}}());(function(){if(typeof ArrayBuffer!='function'){return}var C=CryptoJS;var C_lib=C.lib;var WordArray=C_lib.WordArray;var superInit=WordArray.init;var subInit=WordArray.init=function(typedArray){if(typedArray instanceof ArrayBuffer){typedArray=new Uint8Array(typedArray)}if(typedArray instanceof Int8Array||(typeof Uint8ClampedArray!=="undefined"&&typedArray instanceof Uint8ClampedArray)||typedArray instanceof Int16Array||typedArray instanceof Uint16Array||typedArray instanceof Int32Array||typedArray instanceof Uint32Array||typedArray instanceof Float32Array||typedArray instanceof Float64Array){typedArray=new Uint8Array(typedArray.buffer,typedArray.byteOffset,typedArray.byteLength)}if(typedArray instanceof Uint8Array){var typedArrayByteLength=typedArray.byteLength;var words=[];for(var i=0;i<typedArrayByteLength;i++){words[i>>>2]|=typedArray[i]<<(24-(i%4)*8)}superInit.call(this,words,typedArrayByteLength)}else{superInit.apply(this,arguments)}};subInit.prototype=WordArray}());(function(Math){var C=CryptoJS;var C_lib=C.lib;var WordArray=C_lib.WordArray;var Hasher=C_lib.Hasher;var C_algo=C.algo;var _zl=WordArray.create([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,7,4,13,1,10,6,15,3,12,0,9,5,2,14,11,8,3,10,14,4,9,15,8,1,2,7,0,6,13,11,5,12,1,9,11,10,0,8,12,4,13,3,7,15,14,5,6,2,4,0,5,9,7,12,2,10,14,1,3,8,11,6,15,13]);var _zr=WordArray.create([5,14,7,0,9,2,11,4,13,6,15,8,1,10,3,12,6,11,3,7,0,13,5,10,14,15,8,12,4,9,1,2,15,5,1,3,7,14,6,9,11,8,12,2,10,0,4,13,8,6,4,1,3,11,15,0,5,12,2,13,9,7,10,14,12,15,10,4,1,5,8,7,6,2,13,14,0,3,9,11]);var _sl=WordArray.create([11,14,15,12,5,8,7,9,11,13,14,15,6,7,9,8,7,6,8,13,11,9,7,15,7,12,15,9,11,7,13,12,11,13,6,7,14,9,13,15,14,8,13,6,5,12,7,5,11,12,14,15,14,15,9,8,9,14,5,6,8,6,5,12,9,15,5,11,6,8,13,12,5,12,13,14,11,8,5,6]);var _sr=WordArray.create([8,9,9,11,13,15,15,5,7,7,8,11,14,14,12,6,9,13,15,7,12,8,9,11,7,7,12,7,6,15,13,11,9,7,15,11,8,6,6,14,12,13,5,14,13,13,7,5,15,5,8,11,14,14,6,14,6,9,12,9,12,5,15,8,8,5,12,9,12,5,14,6,8,13,6,5,15,13,11,11]);var _hl=WordArray.create([0x00000000,0x5A827999,0x6ED9EBA1,0x8F1BBCDC,0xA953FD4E]);var _hr=WordArray.create([0x50A28BE6,0x5C4DD124,0x6D703EF3,0x7A6D76E9,0x00000000]);var RIPEMD160=C_algo.RIPEMD160=Hasher.extend({_doReset:function(){this._hash=WordArray.create([0x67452301,0xEFCDAB89,0x98BADCFE,0x10325476,0xC3D2E1F0])},_doProcessBlock:function(M,offset){for(var i=0;i<16;i++){var offset_i=offset+i;var M_offset_i=M[offset_i];M[offset_i]=((((M_offset_i<<8)|(M_offset_i>>>24))&0x00ff00ff)|(((M_offset_i<<24)|(M_offset_i>>>8))&0xff00ff00))}var H=this._hash.words;var hl=_hl.words;var hr=_hr.words;var zl=_zl.words;var zr=_zr.words;var sl=_sl.words;var sr=_sr.words;var al,bl,cl,dl,el;var ar,br,cr,dr,er;ar=al=H[0];br=bl=H[1];cr=cl=H[2];dr=dl=H[3];er=el=H[4];var t;for(var i=0;i<80;i+=1){t=(al+M[offset+zl[i]])|0;if(i<16){t+=f1(bl,cl,dl)+hl[0]}else if(i<32){t+=f2(bl,cl,dl)+hl[1]}else if(i<48){t+=f3(bl,cl,dl)+hl[2]}else if(i<64){t+=f4(bl,cl,dl)+hl[3]}else{t+=f5(bl,cl,dl)+hl[4]}t=t|0;t=rotl(t,sl[i]);t=(t+el)|0;al=el;el=dl;dl=rotl(cl,10);cl=bl;bl=t;t=(ar+M[offset+zr[i]])|0;if(i<16){t+=f5(br,cr,dr)+hr[0]}else if(i<32){t+=f4(br,cr,dr)+hr[1]}else if(i<48){t+=f3(br,cr,dr)+hr[2]}else if(i<64){t+=f2(br,cr,dr)+hr[3]}else{t+=f1(br,cr,dr)+hr[4]}t=t|0;t=rotl(t,sr[i]);t=(t+er)|0;ar=er;er=dr;dr=rotl(cr,10);cr=br;br=t}t=(H[1]+cl+dr)|0;H[1]=(H[2]+dl+er)|0;H[2]=(H[3]+el+ar)|0;H[3]=(H[4]+al+br)|0;H[4]=(H[0]+bl+cr)|0;H[0]=t},_doFinalize:function(){var data=this._data;var dataWords=data.words;var nBitsTotal=this._nDataBytes*8;var nBitsLeft=data.sigBytes*8;dataWords[nBitsLeft>>>5]|=0x80<<(24-nBitsLeft%32);dataWords[(((nBitsLeft+64)>>>9)<<4)+14]=((((nBitsTotal<<8)|(nBitsTotal>>>24))&0x00ff00ff)|(((nBitsTotal<<24)|(nBitsTotal>>>8))&0xff00ff00));data.sigBytes=(dataWords.length+1)*4;this._process();var hash=this._hash;var H=hash.words;for(var i=0;i<5;i++){var H_i=H[i];H[i]=(((H_i<<8)|(H_i>>>24))&0x00ff00ff)|(((H_i<<24)|(H_i>>>8))&0xff00ff00)}return hash},clone:function(){var clone=Hasher.clone.call(this);clone._hash=this._hash.clone();return clone}});function f1(x,y,z){return((x)^(y)^(z))}function f2(x,y,z){return(((x)&(y))|((~x)&(z)))}function f3(x,y,z){return(((x)|(~(y)))^(z))}function f4(x,y,z){return(((x)&(z))|((y)&(~(z))))}function f5(x,y,z){return((x)^((y)|(~(z))))}function rotl(x,n){return(x<<n)|(x>>>(32-n))}C.RIPEMD160=Hasher._createHelper(RIPEMD160);C.HmacRIPEMD160=Hasher._createHmacHelper(RIPEMD160)}(Math));(function(){var C=CryptoJS;var C_lib=C.lib;var Base=C_lib.Base;var C_enc=C.enc;var Utf8=C_enc.Utf8;var C_algo=C.algo;var HMAC=C_algo.HMAC=Base.extend({init:function(hasher,key){hasher=this._hasher=new hasher.init();if(typeof key=='string'){key=Utf8.parse(key)}var hasherBlockSize=hasher.blockSize;var hasherBlockSizeBytes=hasherBlockSize*4;if(key.sigBytes>hasherBlockSizeBytes){key=hasher.finalize(key)}key.clamp();var oKey=this._oKey=key.clone();var iKey=this._iKey=key.clone();var oKeyWords=oKey.words;var iKeyWords=iKey.words;for(var i=0;i<hasherBlockSize;i++){oKeyWords[i]^=0x5c5c5c5c;iKeyWords[i]^=0x36363636}oKey.sigBytes=iKey.sigBytes=hasherBlockSizeBytes;this.reset()},reset:function(){var hasher=this._hasher;hasher.reset();hasher.update(this._iKey)},update:function(messageUpdate){this._hasher.update(messageUpdate);return this},finalize:function(messageUpdate){var hasher=this._hasher;var innerHash=hasher.finalize(messageUpdate);hasher.reset();var hmac=hasher.finalize(this._oKey.clone().concat(innerHash));return hmac}})}());(function(){var C=CryptoJS;var C_lib=C.lib;var Base=C_lib.Base;var WordArray=C_lib.WordArray;var C_algo=C.algo;var SHA1=C_algo.SHA1;var HMAC=C_algo.HMAC;var PBKDF2=C_algo.PBKDF2=Base.extend({cfg:Base.extend({keySize:128/32,hasher:SHA1,iterations:1}),init:function(cfg){this.cfg=this.cfg.extend(cfg)},compute:function(password,salt){var cfg=this.cfg;var hmac=HMAC.create(cfg.hasher,password);var derivedKey=WordArray.create();var blockIndex=WordArray.create([0x00000001]);var derivedKeyWords=derivedKey.words;var blockIndexWords=blockIndex.words;var keySize=cfg.keySize;var iterations=cfg.iterations;while(derivedKeyWords.length<keySize){var block=hmac.update(salt).finalize(blockIndex);hmac.reset();var blockWords=block.words;var blockWordsLength=blockWords.length;var intermediate=block;for(var i=1;i<iterations;i++){intermediate=hmac.finalize(intermediate);hmac.reset();var intermediateWords=intermediate.words;for(var j=0;j<blockWordsLength;j++){blockWords[j]^=intermediateWords[j]}}derivedKey.concat(block);blockIndexWords[0]++}derivedKey.sigBytes=keySize*4;return derivedKey}});C.PBKDF2=function(password,salt,cfg){return PBKDF2.create(cfg).compute(password,salt)}}());(function(){var C=CryptoJS;var C_lib=C.lib;var Base=C_lib.Base;var WordArray=C_lib.WordArray;var C_algo=C.algo;var MD5=C_algo.MD5;var EvpKDF=C_algo.EvpKDF=Base.extend({cfg:Base.extend({keySize:128/32,hasher:MD5,iterations:1}),init:function(cfg){this.cfg=this.cfg.extend(cfg)},compute:function(password,salt){var cfg=this.cfg;var hasher=cfg.hasher.create();var derivedKey=WordArray.create();var derivedKeyWords=derivedKey.words;var keySize=cfg.keySize;var iterations=cfg.iterations;while(derivedKeyWords.length<keySize){if(block){hasher.update(block)}var block=hasher.update(password).finalize(salt);hasher.reset();for(var i=1;i<iterations;i++){block=hasher.finalize(block);hasher.reset()}derivedKey.concat(block)}derivedKey.sigBytes=keySize*4;return derivedKey}});C.EvpKDF=function(password,salt,cfg){return EvpKDF.create(cfg).compute(password,salt)}}());(function(){var C=CryptoJS;var C_lib=C.lib;var WordArray=C_lib.WordArray;var C_algo=C.algo;var SHA256=C_algo.SHA256;var SHA224=C_algo.SHA224=SHA256.extend({_doReset:function(){this._hash=new WordArray.init([0xc1059ed8,0x367cd507,0x3070dd17,0xf70e5939,0xffc00b31,0x68581511,0x64f98fa7,0xbefa4fa4])},_doFinalize:function(){var hash=SHA256._doFinalize.call(this);hash.sigBytes-=4;return hash}});C.SHA224=SHA256._createHelper(SHA224);C.HmacSHA224=SHA256._createHmacHelper(SHA224)}());(function(undefined){var C=CryptoJS;var C_lib=C.lib;var Base=C_lib.Base;var X32WordArray=C_lib.WordArray;var C_x64=C.x64={};var X64Word=C_x64.Word=Base.extend({init:function(high,low){this.high=high;this.low=low}});var X64WordArray=C_x64.WordArray=Base.extend({init:function(words,sigBytes){words=this.words=words||[];if(sigBytes!=undefined){this.sigBytes=sigBytes}else{this.sigBytes=words.length*8}},toX32:function(){var x64Words=this.words;var x64WordsLength=x64Words.length;var x32Words=[];for(var i=0;i<x64WordsLength;i++){var x64Word=x64Words[i];x32Words.push(x64Word.high);x32Words.push(x64Word.low)}return X32WordArray.create(x32Words,this.sigBytes)},clone:function(){var clone=Base.clone.call(this);var words=clone.words=this.words.slice(0);var wordsLength=words.length;for(var i=0;i<wordsLength;i++){words[i]=words[i].clone()}return clone}})}());(function(Math){var C=CryptoJS;var C_lib=C.lib;var WordArray=C_lib.WordArray;var Hasher=C_lib.Hasher;var C_x64=C.x64;var X64Word=C_x64.Word;var C_algo=C.algo;var RHO_OFFSETS=[];var PI_INDEXES=[];var ROUND_CONSTANTS=[];(function(){var x=1,y=0;for(var t=0;t<24;t++){RHO_OFFSETS[x+5*y]=((t+1)*(t+2)/2)%64;var newX=y%5;var newY=(2*x+3*y)%5;x=newX;y=newY}for(var x=0;x<5;x++){for(var y=0;y<5;y++){PI_INDEXES[x+5*y]=y+((2*x+3*y)%5)*5}}var LFSR=0x01;for(var i=0;i<24;i++){var roundConstantMsw=0;var roundConstantLsw=0;for(var j=0;j<7;j++){if(LFSR&0x01){var bitPosition=(1<<j)-1;if(bitPosition<32){roundConstantLsw^=1<<bitPosition}else{roundConstantMsw^=1<<(bitPosition-32)}}if(LFSR&0x80){LFSR=(LFSR<<1)^0x71}else{LFSR<<=1}}ROUND_CONSTANTS[i]=X64Word.create(roundConstantMsw,roundConstantLsw)}}());var T=[];(function(){for(var i=0;i<25;i++){T[i]=X64Word.create()}}());var SHA3=C_algo.SHA3=Hasher.extend({cfg:Hasher.cfg.extend({outputLength:512}),_doReset:function(){var state=this._state=[];for(var i=0;i<25;i++){state[i]=new X64Word.init()}this.blockSize=(1600-2*this.cfg.outputLength)/32},_doProcessBlock:function(M,offset){var state=this._state;var nBlockSizeLanes=this.blockSize/2;for(var i=0;i<nBlockSizeLanes;i++){var M2i=M[offset+2*i];var M2i1=M[offset+2*i+1];M2i=((((M2i<<8)|(M2i>>>24))&0x00ff00ff)|(((M2i<<24)|(M2i>>>8))&0xff00ff00));M2i1=((((M2i1<<8)|(M2i1>>>24))&0x00ff00ff)|(((M2i1<<24)|(M2i1>>>8))&0xff00ff00));var lane=state[i];lane.high^=M2i1;lane.low^=M2i}for(var round=0;round<24;round++){for(var x=0;x<5;x++){var tMsw=0,tLsw=0;for(var y=0;y<5;y++){var lane=state[x+5*y];tMsw^=lane.high;tLsw^=lane.low}var Tx=T[x];Tx.high=tMsw;Tx.low=tLsw}for(var x=0;x<5;x++){var Tx4=T[(x+4)%5];var Tx1=T[(x+1)%5];var Tx1Msw=Tx1.high;var Tx1Lsw=Tx1.low;var tMsw=Tx4.high^((Tx1Msw<<1)|(Tx1Lsw>>>31));var tLsw=Tx4.low^((Tx1Lsw<<1)|(Tx1Msw>>>31));for(var y=0;y<5;y++){var lane=state[x+5*y];lane.high^=tMsw;lane.low^=tLsw}}for(var laneIndex=1;laneIndex<25;laneIndex++){var lane=state[laneIndex];var laneMsw=lane.high;var laneLsw=lane.low;var rhoOffset=RHO_OFFSETS[laneIndex];if(rhoOffset<32){var tMsw=(laneMsw<<rhoOffset)|(laneLsw>>>(32-rhoOffset));var tLsw=(laneLsw<<rhoOffset)|(laneMsw>>>(32-rhoOffset))}else{var tMsw=(laneLsw<<(rhoOffset-32))|(laneMsw>>>(64-rhoOffset));var tLsw=(laneMsw<<(rhoOffset-32))|(laneLsw>>>(64-rhoOffset))}var TPiLane=T[PI_INDEXES[laneIndex]];TPiLane.high=tMsw;TPiLane.low=tLsw}var T0=T[0];var state0=state[0];T0.high=state0.high;T0.low=state0.low;for(var x=0;x<5;x++){for(var y=0;y<5;y++){var laneIndex=x+5*y;var lane=state[laneIndex];var TLane=T[laneIndex];var Tx1Lane=T[((x+1)%5)+5*y];var Tx2Lane=T[((x+2)%5)+5*y];lane.high=TLane.high^(~Tx1Lane.high&Tx2Lane.high);lane.low=TLane.low^(~Tx1Lane.low&Tx2Lane.low)}}var lane=state[0];var roundConstant=ROUND_CONSTANTS[round];lane.high^=roundConstant.high;lane.low^=roundConstant.low}},_doFinalize:function(){var data=this._data;var dataWords=data.words;var nBitsTotal=this._nDataBytes*8;var nBitsLeft=data.sigBytes*8;var blockSizeBits=this.blockSize*32;dataWords[nBitsLeft>>>5]|=0x1<<(24-nBitsLeft%32);dataWords[((Math.ceil((nBitsLeft+1)/blockSizeBits)*blockSizeBits)>>>5)-1]|=0x80;data.sigBytes=dataWords.length*4;this._process();var state=this._state;var outputLengthBytes=this.cfg.outputLength/8;var outputLengthLanes=outputLengthBytes/8;var hashWords=[];for(var i=0;i<outputLengthLanes;i++){var lane=state[i];var laneMsw=lane.high;var laneLsw=lane.low;laneMsw=((((laneMsw<<8)|(laneMsw>>>24))&0x00ff00ff)|(((laneMsw<<24)|(laneMsw>>>8))&0xff00ff00));laneLsw=((((laneLsw<<8)|(laneLsw>>>24))&0x00ff00ff)|(((laneLsw<<24)|(laneLsw>>>8))&0xff00ff00));hashWords.push(laneLsw);hashWords.push(laneMsw)}return new WordArray.init(hashWords,outputLengthBytes)},clone:function(){var clone=Hasher.clone.call(this);var state=clone._state=this._state.slice(0);for(var i=0;i<25;i++){state[i]=state[i].clone()}return clone}});C.SHA3=Hasher._createHelper(SHA3);C.HmacSHA3=Hasher._createHmacHelper(SHA3)}(Math));(function(){var C=CryptoJS;var C_lib=C.lib;var Hasher=C_lib.Hasher;var C_x64=C.x64;var X64Word=C_x64.Word;var X64WordArray=C_x64.WordArray;var C_algo=C.algo;function X64Word_create(){return X64Word.create.apply(X64Word,arguments)}var K=[X64Word_create(0x428a2f98,0xd728ae22),X64Word_create(0x71374491,0x23ef65cd),X64Word_create(0xb5c0fbcf,0xec4d3b2f),X64Word_create(0xe9b5dba5,0x8189dbbc),X64Word_create(0x3956c25b,0xf348b538),X64Word_create(0x59f111f1,0xb605d019),X64Word_create(0x923f82a4,0xaf194f9b),X64Word_create(0xab1c5ed5,0xda6d8118),X64Word_create(0xd807aa98,0xa3030242),X64Word_create(0x12835b01,0x45706fbe),X64Word_create(0x243185be,0x4ee4b28c),X64Word_create(0x550c7dc3,0xd5ffb4e2),X64Word_create(0x72be5d74,0xf27b896f),X64Word_create(0x80deb1fe,0x3b1696b1),X64Word_create(0x9bdc06a7,0x25c71235),X64Word_create(0xc19bf174,0xcf692694),X64Word_create(0xe49b69c1,0x9ef14ad2),X64Word_create(0xefbe4786,0x384f25e3),X64Word_create(0x0fc19dc6,0x8b8cd5b5),X64Word_create(0x240ca1cc,0x77ac9c65),X64Word_create(0x2de92c6f,0x592b0275),X64Word_create(0x4a7484aa,0x6ea6e483),X64Word_create(0x5cb0a9dc,0xbd41fbd4),X64Word_create(0x76f988da,0x831153b5),X64Word_create(0x983e5152,0xee66dfab),X64Word_create(0xa831c66d,0x2db43210),X64Word_create(0xb00327c8,0x98fb213f),X64Word_create(0xbf597fc7,0xbeef0ee4),X64Word_create(0xc6e00bf3,0x3da88fc2),X64Word_create(0xd5a79147,0x930aa725),X64Word_create(0x06ca6351,0xe003826f),X64Word_create(0x14292967,0x0a0e6e70),X64Word_create(0x27b70a85,0x46d22ffc),X64Word_create(0x2e1b2138,0x5c26c926),X64Word_create(0x4d2c6dfc,0x5ac42aed),X64Word_create(0x53380d13,0x9d95b3df),X64Word_create(0x650a7354,0x8baf63de),X64Word_create(0x766a0abb,0x3c77b2a8),X64Word_create(0x81c2c92e,0x47edaee6),X64Word_create(0x92722c85,0x1482353b),X64Word_create(0xa2bfe8a1,0x4cf10364),X64Word_create(0xa81a664b,0xbc423001),X64Word_create(0xc24b8b70,0xd0f89791),X64Word_create(0xc76c51a3,0x0654be30),X64Word_create(0xd192e819,0xd6ef5218),X64Word_create(0xd6990624,0x5565a910),X64Word_create(0xf40e3585,0x5771202a),X64Word_create(0x106aa070,0x32bbd1b8),X64Word_create(0x19a4c116,0xb8d2d0c8),X64Word_create(0x1e376c08,0x5141ab53),X64Word_create(0x2748774c,0xdf8eeb99),X64Word_create(0x34b0bcb5,0xe19b48a8),X64Word_create(0x391c0cb3,0xc5c95a63),X64Word_create(0x4ed8aa4a,0xe3418acb),X64Word_create(0x5b9cca4f,0x7763e373),X64Word_create(0x682e6ff3,0xd6b2b8a3),X64Word_create(0x748f82ee,0x5defb2fc),X64Word_create(0x78a5636f,0x43172f60),X64Word_create(0x84c87814,0xa1f0ab72),X64Word_create(0x8cc70208,0x1a6439ec),X64Word_create(0x90befffa,0x23631e28),X64Word_create(0xa4506ceb,0xde82bde9),X64Word_create(0xbef9a3f7,0xb2c67915),X64Word_create(0xc67178f2,0xe372532b),X64Word_create(0xca273ece,0xea26619c),X64Word_create(0xd186b8c7,0x21c0c207),X64Word_create(0xeada7dd6,0xcde0eb1e),X64Word_create(0xf57d4f7f,0xee6ed178),X64Word_create(0x06f067aa,0x72176fba),X64Word_create(0x0a637dc5,0xa2c898a6),X64Word_create(0x113f9804,0xbef90dae),X64Word_create(0x1b710b35,0x131c471b),X64Word_create(0x28db77f5,0x23047d84),X64Word_create(0x32caab7b,0x40c72493),X64Word_create(0x3c9ebe0a,0x15c9bebc),X64Word_create(0x431d67c4,0x9c100d4c),X64Word_create(0x4cc5d4be,0xcb3e42b6),X64Word_create(0x597f299c,0xfc657e2a),X64Word_create(0x5fcb6fab,0x3ad6faec),X64Word_create(0x6c44198c,0x4a475817)];var W=[];(function(){for(var i=0;i<80;i++){W[i]=X64Word_create()}}());var SHA512=C_algo.SHA512=Hasher.extend({_doReset:function(){this._hash=new X64WordArray.init([new X64Word.init(0x6a09e667,0xf3bcc908),new X64Word.init(0xbb67ae85,0x84caa73b),new X64Word.init(0x3c6ef372,0xfe94f82b),new X64Word.init(0xa54ff53a,0x5f1d36f1),new X64Word.init(0x510e527f,0xade682d1),new X64Word.init(0x9b05688c,0x2b3e6c1f),new X64Word.init(0x1f83d9ab,0xfb41bd6b),new X64Word.init(0x5be0cd19,0x137e2179)])},_doProcessBlock:function(M,offset){var H=this._hash.words;var H0=H[0];var H1=H[1];var H2=H[2];var H3=H[3];var H4=H[4];var H5=H[5];var H6=H[6];var H7=H[7];var H0h=H0.high;var H0l=H0.low;var H1h=H1.high;var H1l=H1.low;var H2h=H2.high;var H2l=H2.low;var H3h=H3.high;var H3l=H3.low;var H4h=H4.high;var H4l=H4.low;var H5h=H5.high;var H5l=H5.low;var H6h=H6.high;var H6l=H6.low;var H7h=H7.high;var H7l=H7.low;var ah=H0h;var al=H0l;var bh=H1h;var bl=H1l;var ch=H2h;var cl=H2l;var dh=H3h;var dl=H3l;var eh=H4h;var el=H4l;var fh=H5h;var fl=H5l;var gh=H6h;var gl=H6l;var hh=H7h;var hl=H7l;for(var i=0;i<80;i++){var Wi=W[i];if(i<16){var Wih=Wi.high=M[offset+i*2]|0;var Wil=Wi.low=M[offset+i*2+1]|0}else{var gamma0x=W[i-15];var gamma0xh=gamma0x.high;var gamma0xl=gamma0x.low;var gamma0h=((gamma0xh>>>1)|(gamma0xl<<31))^((gamma0xh>>>8)|(gamma0xl<<24))^(gamma0xh>>>7);var gamma0l=((gamma0xl>>>1)|(gamma0xh<<31))^((gamma0xl>>>8)|(gamma0xh<<24))^((gamma0xl>>>7)|(gamma0xh<<25));var gamma1x=W[i-2];var gamma1xh=gamma1x.high;var gamma1xl=gamma1x.low;var gamma1h=((gamma1xh>>>19)|(gamma1xl<<13))^((gamma1xh<<3)|(gamma1xl>>>29))^(gamma1xh>>>6);var gamma1l=((gamma1xl>>>19)|(gamma1xh<<13))^((gamma1xl<<3)|(gamma1xh>>>29))^((gamma1xl>>>6)|(gamma1xh<<26));var Wi7=W[i-7];var Wi7h=Wi7.high;var Wi7l=Wi7.low;var Wi16=W[i-16];var Wi16h=Wi16.high;var Wi16l=Wi16.low;var Wil=gamma0l+Wi7l;var Wih=gamma0h+Wi7h+((Wil>>>0)<(gamma0l>>>0)?1:0);var Wil=Wil+gamma1l;var Wih=Wih+gamma1h+((Wil>>>0)<(gamma1l>>>0)?1:0);var Wil=Wil+Wi16l;var Wih=Wih+Wi16h+((Wil>>>0)<(Wi16l>>>0)?1:0);Wi.high=Wih;Wi.low=Wil}var chh=(eh&fh)^(~eh&gh);var chl=(el&fl)^(~el&gl);var majh=(ah&bh)^(ah&ch)^(bh&ch);var majl=(al&bl)^(al&cl)^(bl&cl);var sigma0h=((ah>>>28)|(al<<4))^((ah<<30)|(al>>>2))^((ah<<25)|(al>>>7));var sigma0l=((al>>>28)|(ah<<4))^((al<<30)|(ah>>>2))^((al<<25)|(ah>>>7));var sigma1h=((eh>>>14)|(el<<18))^((eh>>>18)|(el<<14))^((eh<<23)|(el>>>9));var sigma1l=((el>>>14)|(eh<<18))^((el>>>18)|(eh<<14))^((el<<23)|(eh>>>9));var Ki=K[i];var Kih=Ki.high;var Kil=Ki.low;var t1l=hl+sigma1l;var t1h=hh+sigma1h+((t1l>>>0)<(hl>>>0)?1:0);var t1l=t1l+chl;var t1h=t1h+chh+((t1l>>>0)<(chl>>>0)?1:0);var t1l=t1l+Kil;var t1h=t1h+Kih+((t1l>>>0)<(Kil>>>0)?1:0);var t1l=t1l+Wil;var t1h=t1h+Wih+((t1l>>>0)<(Wil>>>0)?1:0);var t2l=sigma0l+majl;var t2h=sigma0h+majh+((t2l>>>0)<(sigma0l>>>0)?1:0);hh=gh;hl=gl;gh=fh;gl=fl;fh=eh;fl=el;el=(dl+t1l)|0;eh=(dh+t1h+((el>>>0)<(dl>>>0)?1:0))|0;dh=ch;dl=cl;ch=bh;cl=bl;bh=ah;bl=al;al=(t1l+t2l)|0;ah=(t1h+t2h+((al>>>0)<(t1l>>>0)?1:0))|0}H0l=H0.low=(H0l+al);H0.high=(H0h+ah+((H0l>>>0)<(al>>>0)?1:0));H1l=H1.low=(H1l+bl);H1.high=(H1h+bh+((H1l>>>0)<(bl>>>0)?1:0));H2l=H2.low=(H2l+cl);H2.high=(H2h+ch+((H2l>>>0)<(cl>>>0)?1:0));H3l=H3.low=(H3l+dl);H3.high=(H3h+dh+((H3l>>>0)<(dl>>>0)?1:0));H4l=H4.low=(H4l+el);H4.high=(H4h+eh+((H4l>>>0)<(el>>>0)?1:0));H5l=H5.low=(H5l+fl);H5.high=(H5h+fh+((H5l>>>0)<(fl>>>0)?1:0));H6l=H6.low=(H6l+gl);H6.high=(H6h+gh+((H6l>>>0)<(gl>>>0)?1:0));H7l=H7.low=(H7l+hl);H7.high=(H7h+hh+((H7l>>>0)<(hl>>>0)?1:0))},_doFinalize:function(){var data=this._data;var dataWords=data.words;var nBitsTotal=this._nDataBytes*8;var nBitsLeft=data.sigBytes*8;dataWords[nBitsLeft>>>5]|=0x80<<(24-nBitsLeft%32);dataWords[(((nBitsLeft+128)>>>10)<<5)+30]=Math.floor(nBitsTotal/0x100000000);dataWords[(((nBitsLeft+128)>>>10)<<5)+31]=nBitsTotal;data.sigBytes=dataWords.length*4;this._process();var hash=this._hash.toX32();return hash},clone:function(){var clone=Hasher.clone.call(this);clone._hash=this._hash.clone();return clone},blockSize:1024/32});C.SHA512=Hasher._createHelper(SHA512);C.HmacSHA512=Hasher._createHmacHelper(SHA512)}());(function(){var C=CryptoJS;var C_x64=C.x64;var X64Word=C_x64.Word;var X64WordArray=C_x64.WordArray;var C_algo=C.algo;var SHA512=C_algo.SHA512;var SHA384=C_algo.SHA384=SHA512.extend({_doReset:function(){this._hash=new X64WordArray.init([new X64Word.init(0xcbbb9d5d,0xc1059ed8),new X64Word.init(0x629a292a,0x367cd507),new X64Word.init(0x9159015a,0x3070dd17),new X64Word.init(0x152fecd8,0xf70e5939),new X64Word.init(0x67332667,0xffc00b31),new X64Word.init(0x8eb44a87,0x68581511),new X64Word.init(0xdb0c2e0d,0x64f98fa7),new X64Word.init(0x47b5481d,0xbefa4fa4)])},_doFinalize:function(){var hash=SHA512._doFinalize.call(this);hash.sigBytes-=16;return hash}});C.SHA384=SHA512._createHelper(SHA384);C.HmacSHA384=SHA512._createHmacHelper(SHA384)}());CryptoJS.lib.Cipher||(function(undefined){var C=CryptoJS;var C_lib=C.lib;var Base=C_lib.Base;var WordArray=C_lib.WordArray;var BufferedBlockAlgorithm=C_lib.BufferedBlockAlgorithm;var C_enc=C.enc;var Utf8=C_enc.Utf8;var Base64=C_enc.Base64;var C_algo=C.algo;var EvpKDF=C_algo.EvpKDF;var Cipher=C_lib.Cipher=BufferedBlockAlgorithm.extend({cfg:Base.extend(),createEncryptor:function(key,cfg){return this.create(this._ENC_XFORM_MODE,key,cfg)},createDecryptor:function(key,cfg){return this.create(this._DEC_XFORM_MODE,key,cfg)},init:function(xformMode,key,cfg){this.cfg=this.cfg.extend(cfg);this._xformMode=xformMode;this._key=key;this.reset()},reset:function(){BufferedBlockAlgorithm.reset.call(this);this._doReset()},process:function(dataUpdate){this._append(dataUpdate);return this._process()},finalize:function(dataUpdate){if(dataUpdate){this._append(dataUpdate)}var finalProcessedData=this._doFinalize();return finalProcessedData},keySize:128/32,ivSize:128/32,_ENC_XFORM_MODE:1,_DEC_XFORM_MODE:2,_createHelper:(function(){function selectCipherStrategy(key){if(typeof key=='string'){return PasswordBasedCipher}else{return SerializableCipher}}return function(cipher){return{encrypt:function(message,key,cfg){return selectCipherStrategy(key).encrypt(cipher,message,key,cfg)},decrypt:function(ciphertext,key,cfg){return selectCipherStrategy(key).decrypt(cipher,ciphertext,key,cfg)}}}}())});var StreamCipher=C_lib.StreamCipher=Cipher.extend({_doFinalize:function(){var finalProcessedBlocks=this._process(!!'flush');return finalProcessedBlocks},blockSize:1});var C_mode=C.mode={};var BlockCipherMode=C_lib.BlockCipherMode=Base.extend({createEncryptor:function(cipher,iv){return this.Encryptor.create(cipher,iv)},createDecryptor:function(cipher,iv){return this.Decryptor.create(cipher,iv)},init:function(cipher,iv){this._cipher=cipher;this._iv=iv}});var CBC=C_mode.CBC=(function(){var CBC=BlockCipherMode.extend();CBC.Encryptor=CBC.extend({processBlock:function(words,offset){var cipher=this._cipher;var blockSize=cipher.blockSize;xorBlock.call(this,words,offset,blockSize);cipher.encryptBlock(words,offset);this._prevBlock=words.slice(offset,offset+blockSize)}});CBC.Decryptor=CBC.extend({processBlock:function(words,offset){var cipher=this._cipher;var blockSize=cipher.blockSize;var thisBlock=words.slice(offset,offset+blockSize);cipher.decryptBlock(words,offset);xorBlock.call(this,words,offset,blockSize);this._prevBlock=thisBlock}});function xorBlock(words,offset,blockSize){var iv=this._iv;if(iv){var block=iv;this._iv=undefined}else{var block=this._prevBlock}for(var i=0;i<blockSize;i++){words[offset+i]^=block[i]}}return CBC}());var C_pad=C.pad={};var Pkcs7=C_pad.Pkcs7={pad:function(data,blockSize){var blockSizeBytes=blockSize*4;var nPaddingBytes=blockSizeBytes-data.sigBytes%blockSizeBytes;var paddingWord=(nPaddingBytes<<24)|(nPaddingBytes<<16)|(nPaddingBytes<<8)|nPaddingBytes;var paddingWords=[];for(var i=0;i<nPaddingBytes;i+=4){paddingWords.push(paddingWord)}var padding=WordArray.create(paddingWords,nPaddingBytes);data.concat(padding)},unpad:function(data){var nPaddingBytes=data.words[(data.sigBytes-1)>>>2]&0xff;data.sigBytes-=nPaddingBytes}};var BlockCipher=C_lib.BlockCipher=Cipher.extend({cfg:Cipher.cfg.extend({mode:CBC,padding:Pkcs7}),reset:function(){Cipher.reset.call(this);var cfg=this.cfg;var iv=cfg.iv;var mode=cfg.mode;if(this._xformMode==this._ENC_XFORM_MODE){var modeCreator=mode.createEncryptor}else{var modeCreator=mode.createDecryptor;this._minBufferSize=1}if(this._mode&&this._mode.__creator==modeCreator){this._mode.init(this,iv&&iv.words)}else{this._mode=modeCreator.call(mode,this,iv&&iv.words);this._mode.__creator=modeCreator}},_doProcessBlock:function(words,offset){this._mode.processBlock(words,offset)},_doFinalize:function(){var padding=this.cfg.padding;if(this._xformMode==this._ENC_XFORM_MODE){padding.pad(this._data,this.blockSize);var finalProcessedBlocks=this._process(!!'flush')}else{var finalProcessedBlocks=this._process(!!'flush');padding.unpad(finalProcessedBlocks)}return finalProcessedBlocks},blockSize:128/32});var CipherParams=C_lib.CipherParams=Base.extend({init:function(cipherParams){this.mixIn(cipherParams)},toString:function(formatter){return(formatter||this.formatter).stringify(this)}});var C_format=C.format={};var OpenSSLFormatter=C_format.OpenSSL={stringify:function(cipherParams){var ciphertext=cipherParams.ciphertext;var salt=cipherParams.salt;if(salt){var wordArray=WordArray.create([0x53616c74,0x65645f5f]).concat(salt).concat(ciphertext)}else{var wordArray=ciphertext}return wordArray.toString(Base64)},parse:function(openSSLStr){var ciphertext=Base64.parse(openSSLStr);var ciphertextWords=ciphertext.words;if(ciphertextWords[0]==0x53616c74&&ciphertextWords[1]==0x65645f5f){var salt=WordArray.create(ciphertextWords.slice(2,4));ciphertextWords.splice(0,4);ciphertext.sigBytes-=16}return CipherParams.create({ciphertext:ciphertext,salt:salt})}};var SerializableCipher=C_lib.SerializableCipher=Base.extend({cfg:Base.extend({format:OpenSSLFormatter}),encrypt:function(cipher,message,key,cfg){cfg=this.cfg.extend(cfg);var encryptor=cipher.createEncryptor(key,cfg);var ciphertext=encryptor.finalize(message);var cipherCfg=encryptor.cfg;return CipherParams.create({ciphertext:ciphertext,key:key,iv:cipherCfg.iv,algorithm:cipher,mode:cipherCfg.mode,padding:cipherCfg.padding,blockSize:cipher.blockSize,formatter:cfg.format})},decrypt:function(cipher,ciphertext,key,cfg){cfg=this.cfg.extend(cfg);ciphertext=this._parse(ciphertext,cfg.format);var plaintext=cipher.createDecryptor(key,cfg).finalize(ciphertext.ciphertext);return plaintext},_parse:function(ciphertext,format){if(typeof ciphertext=='string'){return format.parse(ciphertext,this)}else{return ciphertext}}});var C_kdf=C.kdf={};var OpenSSLKdf=C_kdf.OpenSSL={execute:function(password,keySize,ivSize,salt){if(!salt){salt=WordArray.random(64/8)}var key=EvpKDF.create({keySize:keySize+ivSize}).compute(password,salt);var iv=WordArray.create(key.words.slice(keySize),ivSize*4);key.sigBytes=keySize*4;return CipherParams.create({key:key,iv:iv,salt:salt})}};var PasswordBasedCipher=C_lib.PasswordBasedCipher=SerializableCipher.extend({cfg:SerializableCipher.cfg.extend({kdf:OpenSSLKdf}),encrypt:function(cipher,message,password,cfg){cfg=this.cfg.extend(cfg);var derivedParams=cfg.kdf.execute(password,cipher.keySize,cipher.ivSize);cfg.iv=derivedParams.iv;var ciphertext=SerializableCipher.encrypt.call(this,cipher,message,derivedParams.key,cfg);ciphertext.mixIn(derivedParams);return ciphertext},decrypt:function(cipher,ciphertext,password,cfg){cfg=this.cfg.extend(cfg);ciphertext=this._parse(ciphertext,cfg.format);var derivedParams=cfg.kdf.execute(password,cipher.keySize,cipher.ivSize,ciphertext.salt);cfg.iv=derivedParams.iv;var plaintext=SerializableCipher.decrypt.call(this,cipher,ciphertext,derivedParams.key,cfg);return plaintext}})}());CryptoJS.mode.CFB=(function(){var CFB=CryptoJS.lib.BlockCipherMode.extend();CFB.Encryptor=CFB.extend({processBlock:function(words,offset){var cipher=this._cipher;var blockSize=cipher.blockSize;generateKeystreamAndEncrypt.call(this,words,offset,blockSize,cipher);this._prevBlock=words.slice(offset,offset+blockSize)}});CFB.Decryptor=CFB.extend({processBlock:function(words,offset){var cipher=this._cipher;var blockSize=cipher.blockSize;var thisBlock=words.slice(offset,offset+blockSize);generateKeystreamAndEncrypt.call(this,words,offset,blockSize,cipher);this._prevBlock=thisBlock}});function generateKeystreamAndEncrypt(words,offset,blockSize,cipher){var iv=this._iv;if(iv){var keystream=iv.slice(0);this._iv=undefined}else{var keystream=this._prevBlock}cipher.encryptBlock(keystream,0);for(var i=0;i<blockSize;i++){words[offset+i]^=keystream[i]}}return CFB}());CryptoJS.mode.ECB=(function(){var ECB=CryptoJS.lib.BlockCipherMode.extend();ECB.Encryptor=ECB.extend({processBlock:function(words,offset){this._cipher.encryptBlock(words,offset)}});ECB.Decryptor=ECB.extend({processBlock:function(words,offset){this._cipher.decryptBlock(words,offset)}});return ECB}());CryptoJS.pad.AnsiX923={pad:function(data,blockSize){var dataSigBytes=data.sigBytes;var blockSizeBytes=blockSize*4;var nPaddingBytes=blockSizeBytes-dataSigBytes%blockSizeBytes;var lastBytePos=dataSigBytes+nPaddingBytes-1;data.clamp();data.words[lastBytePos>>>2]|=nPaddingBytes<<(24-(lastBytePos%4)*8);data.sigBytes+=nPaddingBytes},unpad:function(data){var nPaddingBytes=data.words[(data.sigBytes-1)>>>2]&0xff;data.sigBytes-=nPaddingBytes}};CryptoJS.pad.Iso10126={pad:function(data,blockSize){var blockSizeBytes=blockSize*4;var nPaddingBytes=blockSizeBytes-data.sigBytes%blockSizeBytes;data.concat(CryptoJS.lib.WordArray.random(nPaddingBytes-1)).concat(CryptoJS.lib.WordArray.create([nPaddingBytes<<24],1))},unpad:function(data){var nPaddingBytes=data.words[(data.sigBytes-1)>>>2]&0xff;data.sigBytes-=nPaddingBytes}};CryptoJS.pad.Iso97971={pad:function(data,blockSize){data.concat(CryptoJS.lib.WordArray.create([0x80000000],1));CryptoJS.pad.ZeroPadding.pad(data,blockSize)},unpad:function(data){CryptoJS.pad.ZeroPadding.unpad(data);data.sigBytes--}};CryptoJS.mode.OFB=(function(){var OFB=CryptoJS.lib.BlockCipherMode.extend();var Encryptor=OFB.Encryptor=OFB.extend({processBlock:function(words,offset){var cipher=this._cipher; var blockSize=cipher.blockSize;var iv=this._iv;var keystream=this._keystream;if(iv){keystream=this._keystream=iv.slice(0);this._iv=undefined}cipher.encryptBlock(keystream,0);for(var i=0;i<blockSize;i++){words[offset+i]^=keystream[i]}}});OFB.Decryptor=Encryptor;return OFB}());CryptoJS.pad.NoPadding={pad:function(){},unpad:function(){}};(function(undefined){var C=CryptoJS;var C_lib=C.lib;var CipherParams=C_lib.CipherParams;var C_enc=C.enc;var Hex=C_enc.Hex;var C_format=C.format;var HexFormatter=C_format.Hex={stringify:function(cipherParams){return cipherParams.ciphertext.toString(Hex)},parse:function(input){var ciphertext=Hex.parse(input);return CipherParams.create({ciphertext:ciphertext})}}}());(function(){var C=CryptoJS;var C_lib=C.lib;var BlockCipher=C_lib.BlockCipher;var C_algo=C.algo;var SBOX=[];var INV_SBOX=[];var SUB_MIX_0=[];var SUB_MIX_1=[];var SUB_MIX_2=[];var SUB_MIX_3=[];var INV_SUB_MIX_0=[];var INV_SUB_MIX_1=[];var INV_SUB_MIX_2=[];var INV_SUB_MIX_3=[];(function(){var d=[];for(var i=0;i<256;i++){if(i<128){d[i]=i<<1}else{d[i]=(i<<1)^0x11b}}var x=0;var xi=0;for(var i=0;i<256;i++){var sx=xi^(xi<<1)^(xi<<2)^(xi<<3)^(xi<<4);sx=(sx>>>8)^(sx&0xff)^0x63;SBOX[x]=sx;INV_SBOX[sx]=x;var x2=d[x];var x4=d[x2];var x8=d[x4];var t=(d[sx]*0x101)^(sx*0x1010100);SUB_MIX_0[x]=(t<<24)|(t>>>8);SUB_MIX_1[x]=(t<<16)|(t>>>16);SUB_MIX_2[x]=(t<<8)|(t>>>24);SUB_MIX_3[x]=t;var t=(x8*0x1010101)^(x4*0x10001)^(x2*0x101)^(x*0x1010100);INV_SUB_MIX_0[sx]=(t<<24)|(t>>>8);INV_SUB_MIX_1[sx]=(t<<16)|(t>>>16);INV_SUB_MIX_2[sx]=(t<<8)|(t>>>24);INV_SUB_MIX_3[sx]=t;if(!x){x=xi=1}else{x=x2^d[d[d[x8^x2]]];xi^=d[d[xi]]}}}());var RCON=[0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36];var AES=C_algo.AES=BlockCipher.extend({_doReset:function(){if(this._nRounds&&this._keyPriorReset===this._key){return}var key=this._keyPriorReset=this._key;var keyWords=key.words;var keySize=key.sigBytes/4;var nRounds=this._nRounds=keySize+6;var ksRows=(nRounds+1)*4;var keySchedule=this._keySchedule=[];for(var ksRow=0;ksRow<ksRows;ksRow++){if(ksRow<keySize){keySchedule[ksRow]=keyWords[ksRow]}else{var t=keySchedule[ksRow-1];if(!(ksRow%keySize)){t=(t<<8)|(t>>>24);t=(SBOX[t>>>24]<<24)|(SBOX[(t>>>16)&0xff]<<16)|(SBOX[(t>>>8)&0xff]<<8)|SBOX[t&0xff];t^=RCON[(ksRow/keySize)|0]<<24}else if(keySize>6&&ksRow%keySize==4){t=(SBOX[t>>>24]<<24)|(SBOX[(t>>>16)&0xff]<<16)|(SBOX[(t>>>8)&0xff]<<8)|SBOX[t&0xff]}keySchedule[ksRow]=keySchedule[ksRow-keySize]^t}}var invKeySchedule=this._invKeySchedule=[];for(var invKsRow=0;invKsRow<ksRows;invKsRow++){var ksRow=ksRows-invKsRow;if(invKsRow%4){var t=keySchedule[ksRow]}else{var t=keySchedule[ksRow-4]}if(invKsRow<4||ksRow<=4){invKeySchedule[invKsRow]=t}else{invKeySchedule[invKsRow]=INV_SUB_MIX_0[SBOX[t>>>24]]^INV_SUB_MIX_1[SBOX[(t>>>16)&0xff]]^INV_SUB_MIX_2[SBOX[(t>>>8)&0xff]]^INV_SUB_MIX_3[SBOX[t&0xff]]}}},encryptBlock:function(M,offset){this._doCryptBlock(M,offset,this._keySchedule,SUB_MIX_0,SUB_MIX_1,SUB_MIX_2,SUB_MIX_3,SBOX)},decryptBlock:function(M,offset){var t=M[offset+1];M[offset+1]=M[offset+3];M[offset+3]=t;this._doCryptBlock(M,offset,this._invKeySchedule,INV_SUB_MIX_0,INV_SUB_MIX_1,INV_SUB_MIX_2,INV_SUB_MIX_3,INV_SBOX);var t=M[offset+1];M[offset+1]=M[offset+3];M[offset+3]=t},_doCryptBlock:function(M,offset,keySchedule,SUB_MIX_0,SUB_MIX_1,SUB_MIX_2,SUB_MIX_3,SBOX){var nRounds=this._nRounds;var s0=M[offset]^keySchedule[0];var s1=M[offset+1]^keySchedule[1];var s2=M[offset+2]^keySchedule[2];var s3=M[offset+3]^keySchedule[3];var ksRow=4;for(var round=1;round<nRounds;round++){var t0=SUB_MIX_0[s0>>>24]^SUB_MIX_1[(s1>>>16)&0xff]^SUB_MIX_2[(s2>>>8)&0xff]^SUB_MIX_3[s3&0xff]^keySchedule[ksRow++];var t1=SUB_MIX_0[s1>>>24]^SUB_MIX_1[(s2>>>16)&0xff]^SUB_MIX_2[(s3>>>8)&0xff]^SUB_MIX_3[s0&0xff]^keySchedule[ksRow++];var t2=SUB_MIX_0[s2>>>24]^SUB_MIX_1[(s3>>>16)&0xff]^SUB_MIX_2[(s0>>>8)&0xff]^SUB_MIX_3[s1&0xff]^keySchedule[ksRow++];var t3=SUB_MIX_0[s3>>>24]^SUB_MIX_1[(s0>>>16)&0xff]^SUB_MIX_2[(s1>>>8)&0xff]^SUB_MIX_3[s2&0xff]^keySchedule[ksRow++];s0=t0;s1=t1;s2=t2;s3=t3}var t0=((SBOX[s0>>>24]<<24)|(SBOX[(s1>>>16)&0xff]<<16)|(SBOX[(s2>>>8)&0xff]<<8)|SBOX[s3&0xff])^keySchedule[ksRow++];var t1=((SBOX[s1>>>24]<<24)|(SBOX[(s2>>>16)&0xff]<<16)|(SBOX[(s3>>>8)&0xff]<<8)|SBOX[s0&0xff])^keySchedule[ksRow++];var t2=((SBOX[s2>>>24]<<24)|(SBOX[(s3>>>16)&0xff]<<16)|(SBOX[(s0>>>8)&0xff]<<8)|SBOX[s1&0xff])^keySchedule[ksRow++];var t3=((SBOX[s3>>>24]<<24)|(SBOX[(s0>>>16)&0xff]<<16)|(SBOX[(s1>>>8)&0xff]<<8)|SBOX[s2&0xff])^keySchedule[ksRow++];M[offset]=t0;M[offset+1]=t1;M[offset+2]=t2;M[offset+3]=t3},keySize:256/32});C.AES=BlockCipher._createHelper(AES)}());(function(){var C=CryptoJS;var C_lib=C.lib;var WordArray=C_lib.WordArray;var BlockCipher=C_lib.BlockCipher;var C_algo=C.algo;var PC1=[57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,60,52,44,36,63,55,47,39,31,23,15,7,62,54,46,38,30,22,14,6,61,53,45,37,29,21,13,5,28,20,12,4];var PC2=[14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,26,8,16,7,27,20,13,2,41,52,31,37,47,55,30,40,51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32];var BIT_SHIFTS=[1,2,4,6,8,10,12,14,15,17,19,21,23,25,27,28];var SBOX_P=[{0x0:0x808200,0x10000000:0x8000,0x20000000:0x808002,0x30000000:0x2,0x40000000:0x200,0x50000000:0x808202,0x60000000:0x800202,0x70000000:0x800000,0x80000000:0x202,0x90000000:0x800200,0xa0000000:0x8200,0xb0000000:0x808000,0xc0000000:0x8002,0xd0000000:0x800002,0xe0000000:0x0,0xf0000000:0x8202,0x8000000:0x0,0x18000000:0x808202,0x28000000:0x8202,0x38000000:0x8000,0x48000000:0x808200,0x58000000:0x200,0x68000000:0x808002,0x78000000:0x2,0x88000000:0x800200,0x98000000:0x8200,0xa8000000:0x808000,0xb8000000:0x800202,0xc8000000:0x800002,0xd8000000:0x8002,0xe8000000:0x202,0xf8000000:0x800000,0x1:0x8000,0x10000001:0x2,0x20000001:0x808200,0x30000001:0x800000,0x40000001:0x808002,0x50000001:0x8200,0x60000001:0x200,0x70000001:0x800202,0x80000001:0x808202,0x90000001:0x808000,0xa0000001:0x800002,0xb0000001:0x8202,0xc0000001:0x202,0xd0000001:0x800200,0xe0000001:0x8002,0xf0000001:0x0,0x8000001:0x808202,0x18000001:0x808000,0x28000001:0x800000,0x38000001:0x200,0x48000001:0x8000,0x58000001:0x800002,0x68000001:0x2,0x78000001:0x8202,0x88000001:0x8002,0x98000001:0x800202,0xa8000001:0x202,0xb8000001:0x808200,0xc8000001:0x800200,0xd8000001:0x0,0xe8000001:0x8200,0xf8000001:0x808002},{0x0:0x40084010,0x1000000:0x4000,0x2000000:0x80000,0x3000000:0x40080010,0x4000000:0x40000010,0x5000000:0x40084000,0x6000000:0x40004000,0x7000000:0x10,0x8000000:0x84000,0x9000000:0x40004010,0xa000000:0x40000000,0xb000000:0x84010,0xc000000:0x80010,0xd000000:0x0,0xe000000:0x4010,0xf000000:0x40080000,0x800000:0x40004000,0x1800000:0x84010,0x2800000:0x10,0x3800000:0x40004010,0x4800000:0x40084010,0x5800000:0x40000000,0x6800000:0x80000,0x7800000:0x40080010,0x8800000:0x80010,0x9800000:0x0,0xa800000:0x4000,0xb800000:0x40080000,0xc800000:0x40000010,0xd800000:0x84000,0xe800000:0x40084000,0xf800000:0x4010,0x10000000:0x0,0x11000000:0x40080010,0x12000000:0x40004010,0x13000000:0x40084000,0x14000000:0x40080000,0x15000000:0x10,0x16000000:0x84010,0x17000000:0x4000,0x18000000:0x4010,0x19000000:0x80000,0x1a000000:0x80010,0x1b000000:0x40000010,0x1c000000:0x84000,0x1d000000:0x40004000,0x1e000000:0x40000000,0x1f000000:0x40084010,0x10800000:0x84010,0x11800000:0x80000,0x12800000:0x40080000,0x13800000:0x4000,0x14800000:0x40004000,0x15800000:0x40084010,0x16800000:0x10,0x17800000:0x40000000,0x18800000:0x40084000,0x19800000:0x40000010,0x1a800000:0x40004010,0x1b800000:0x80010,0x1c800000:0x0,0x1d800000:0x4010,0x1e800000:0x40080010,0x1f800000:0x84000},{0x0:0x104,0x100000:0x0,0x200000:0x4000100,0x300000:0x10104,0x400000:0x10004,0x500000:0x4000004,0x600000:0x4010104,0x700000:0x4010000,0x800000:0x4000000,0x900000:0x4010100,0xa00000:0x10100,0xb00000:0x4010004,0xc00000:0x4000104,0xd00000:0x10000,0xe00000:0x4,0xf00000:0x100,0x80000:0x4010100,0x180000:0x4010004,0x280000:0x0,0x380000:0x4000100,0x480000:0x4000004,0x580000:0x10000,0x680000:0x10004,0x780000:0x104,0x880000:0x4,0x980000:0x100,0xa80000:0x4010000,0xb80000:0x10104,0xc80000:0x10100,0xd80000:0x4000104,0xe80000:0x4010104,0xf80000:0x4000000,0x1000000:0x4010100,0x1100000:0x10004,0x1200000:0x10000,0x1300000:0x4000100,0x1400000:0x100,0x1500000:0x4010104,0x1600000:0x4000004,0x1700000:0x0,0x1800000:0x4000104,0x1900000:0x4000000,0x1a00000:0x4,0x1b00000:0x10100,0x1c00000:0x4010000,0x1d00000:0x104,0x1e00000:0x10104,0x1f00000:0x4010004,0x1080000:0x4000000,0x1180000:0x104,0x1280000:0x4010100,0x1380000:0x0,0x1480000:0x10004,0x1580000:0x4000100,0x1680000:0x100,0x1780000:0x4010004,0x1880000:0x10000,0x1980000:0x4010104,0x1a80000:0x10104,0x1b80000:0x4000004,0x1c80000:0x4000104,0x1d80000:0x4010000,0x1e80000:0x4,0x1f80000:0x10100},{0x0:0x80401000,0x10000:0x80001040,0x20000:0x401040,0x30000:0x80400000,0x40000:0x0,0x50000:0x401000,0x60000:0x80000040,0x70000:0x400040,0x80000:0x80000000,0x90000:0x400000,0xa0000:0x40,0xb0000:0x80001000,0xc0000:0x80400040,0xd0000:0x1040,0xe0000:0x1000,0xf0000:0x80401040,0x8000:0x80001040,0x18000:0x40,0x28000:0x80400040,0x38000:0x80001000,0x48000:0x401000,0x58000:0x80401040,0x68000:0x0,0x78000:0x80400000,0x88000:0x1000,0x98000:0x80401000,0xa8000:0x400000,0xb8000:0x1040,0xc8000:0x80000000,0xd8000:0x400040,0xe8000:0x401040,0xf8000:0x80000040,0x100000:0x400040,0x110000:0x401000,0x120000:0x80000040,0x130000:0x0,0x140000:0x1040,0x150000:0x80400040,0x160000:0x80401000,0x170000:0x80001040,0x180000:0x80401040,0x190000:0x80000000,0x1a0000:0x80400000,0x1b0000:0x401040,0x1c0000:0x80001000,0x1d0000:0x400000,0x1e0000:0x40,0x1f0000:0x1000,0x108000:0x80400000,0x118000:0x80401040,0x128000:0x0,0x138000:0x401000,0x148000:0x400040,0x158000:0x80000000,0x168000:0x80001040,0x178000:0x40,0x188000:0x80000040,0x198000:0x1000,0x1a8000:0x80001000,0x1b8000:0x80400040,0x1c8000:0x1040,0x1d8000:0x80401000,0x1e8000:0x400000,0x1f8000:0x401040},{0x0:0x80,0x1000:0x1040000,0x2000:0x40000,0x3000:0x20000000,0x4000:0x20040080,0x5000:0x1000080,0x6000:0x21000080,0x7000:0x40080,0x8000:0x1000000,0x9000:0x20040000,0xa000:0x20000080,0xb000:0x21040080,0xc000:0x21040000,0xd000:0x0,0xe000:0x1040080,0xf000:0x21000000,0x800:0x1040080,0x1800:0x21000080,0x2800:0x80,0x3800:0x1040000,0x4800:0x40000,0x5800:0x20040080,0x6800:0x21040000,0x7800:0x20000000,0x8800:0x20040000,0x9800:0x0,0xa800:0x21040080,0xb800:0x1000080,0xc800:0x20000080,0xd800:0x21000000,0xe800:0x1000000,0xf800:0x40080,0x10000:0x40000,0x11000:0x80,0x12000:0x20000000,0x13000:0x21000080,0x14000:0x1000080,0x15000:0x21040000,0x16000:0x20040080,0x17000:0x1000000,0x18000:0x21040080,0x19000:0x21000000,0x1a000:0x1040000,0x1b000:0x20040000,0x1c000:0x40080,0x1d000:0x20000080,0x1e000:0x0,0x1f000:0x1040080,0x10800:0x21000080,0x11800:0x1000000,0x12800:0x1040000,0x13800:0x20040080,0x14800:0x20000000,0x15800:0x1040080,0x16800:0x80,0x17800:0x21040000,0x18800:0x40080,0x19800:0x21040080,0x1a800:0x0,0x1b800:0x21000000,0x1c800:0x1000080,0x1d800:0x40000,0x1e800:0x20040000,0x1f800:0x20000080},{0x0:0x10000008,0x100:0x2000,0x200:0x10200000,0x300:0x10202008,0x400:0x10002000,0x500:0x200000,0x600:0x200008,0x700:0x10000000,0x800:0x0,0x900:0x10002008,0xa00:0x202000,0xb00:0x8,0xc00:0x10200008,0xd00:0x202008,0xe00:0x2008,0xf00:0x10202000,0x80:0x10200000,0x180:0x10202008,0x280:0x8,0x380:0x200000,0x480:0x202008,0x580:0x10000008,0x680:0x10002000,0x780:0x2008,0x880:0x200008,0x980:0x2000,0xa80:0x10002008,0xb80:0x10200008,0xc80:0x0,0xd80:0x10202000,0xe80:0x202000,0xf80:0x10000000,0x1000:0x10002000,0x1100:0x10200008,0x1200:0x10202008,0x1300:0x2008,0x1400:0x200000,0x1500:0x10000000,0x1600:0x10000008,0x1700:0x202000,0x1800:0x202008,0x1900:0x0,0x1a00:0x8,0x1b00:0x10200000,0x1c00:0x2000,0x1d00:0x10002008,0x1e00:0x10202000,0x1f00:0x200008,0x1080:0x8,0x1180:0x202000,0x1280:0x200000,0x1380:0x10000008,0x1480:0x10002000,0x1580:0x2008,0x1680:0x10202008,0x1780:0x10200000,0x1880:0x10202000,0x1980:0x10200008,0x1a80:0x2000,0x1b80:0x202008,0x1c80:0x200008,0x1d80:0x0,0x1e80:0x10000000,0x1f80:0x10002008},{0x0:0x100000,0x10:0x2000401,0x20:0x400,0x30:0x100401,0x40:0x2100401,0x50:0x0,0x60:0x1,0x70:0x2100001,0x80:0x2000400,0x90:0x100001,0xa0:0x2000001,0xb0:0x2100400,0xc0:0x2100000,0xd0:0x401,0xe0:0x100400,0xf0:0x2000000,0x8:0x2100001,0x18:0x0,0x28:0x2000401,0x38:0x2100400,0x48:0x100000,0x58:0x2000001,0x68:0x2000000,0x78:0x401,0x88:0x100401,0x98:0x2000400,0xa8:0x2100000,0xb8:0x100001,0xc8:0x400,0xd8:0x2100401,0xe8:0x1,0xf8:0x100400,0x100:0x2000000,0x110:0x100000,0x120:0x2000401,0x130:0x2100001,0x140:0x100001,0x150:0x2000400,0x160:0x2100400,0x170:0x100401,0x180:0x401,0x190:0x2100401,0x1a0:0x100400,0x1b0:0x1,0x1c0:0x0,0x1d0:0x2100000,0x1e0:0x2000001,0x1f0:0x400,0x108:0x100400,0x118:0x2000401,0x128:0x2100001,0x138:0x1,0x148:0x2000000,0x158:0x100000,0x168:0x401,0x178:0x2100400,0x188:0x2000001,0x198:0x2100000,0x1a8:0x0,0x1b8:0x2100401,0x1c8:0x100401,0x1d8:0x400,0x1e8:0x2000400,0x1f8:0x100001},{0x0:0x8000820,0x1:0x20000,0x2:0x8000000,0x3:0x20,0x4:0x20020,0x5:0x8020820,0x6:0x8020800,0x7:0x800,0x8:0x8020000,0x9:0x8000800,0xa:0x20800,0xb:0x8020020,0xc:0x820,0xd:0x0,0xe:0x8000020,0xf:0x20820,0x80000000:0x800,0x80000001:0x8020820,0x80000002:0x8000820,0x80000003:0x8000000,0x80000004:0x8020000,0x80000005:0x20800,0x80000006:0x20820,0x80000007:0x20,0x80000008:0x8000020,0x80000009:0x820,0x8000000a:0x20020,0x8000000b:0x8020800,0x8000000c:0x0,0x8000000d:0x8020020,0x8000000e:0x8000800,0x8000000f:0x20000,0x10:0x20820,0x11:0x8020800,0x12:0x20,0x13:0x800,0x14:0x8000800,0x15:0x8000020,0x16:0x8020020,0x17:0x20000,0x18:0x0,0x19:0x20020,0x1a:0x8020000,0x1b:0x8000820,0x1c:0x8020820,0x1d:0x20800,0x1e:0x820,0x1f:0x8000000,0x80000010:0x20000,0x80000011:0x800,0x80000012:0x8020020,0x80000013:0x20820,0x80000014:0x20,0x80000015:0x8020000,0x80000016:0x8000000,0x80000017:0x8000820,0x80000018:0x8020820,0x80000019:0x8000020,0x8000001a:0x8000800,0x8000001b:0x0,0x8000001c:0x20800,0x8000001d:0x820,0x8000001e:0x20020,0x8000001f:0x8020800}];var SBOX_MASK=[0xf8000001,0x1f800000,0x01f80000,0x001f8000,0x0001f800,0x00001f80,0x000001f8,0x8000001f];var DES=C_algo.DES=BlockCipher.extend({_doReset:function(){var key=this._key;var keyWords=key.words;var keyBits=[];for(var i=0;i<56;i++){var keyBitPos=PC1[i]-1;keyBits[i]=(keyWords[keyBitPos>>>5]>>>(31-keyBitPos%32))&1}var subKeys=this._subKeys=[];for(var nSubKey=0;nSubKey<16;nSubKey++){var subKey=subKeys[nSubKey]=[];var bitShift=BIT_SHIFTS[nSubKey];for(var i=0;i<24;i++){subKey[(i/6)|0]|=keyBits[((PC2[i]-1)+bitShift)%28]<<(31-i%6);subKey[4+((i/6)|0)]|=keyBits[28+(((PC2[i+24]-1)+bitShift)%28)]<<(31-i%6)}subKey[0]=(subKey[0]<<1)|(subKey[0]>>>31);for(var i=1;i<7;i++){subKey[i]=subKey[i]>>>((i-1)*4+3)}subKey[7]=(subKey[7]<<5)|(subKey[7]>>>27)}var invSubKeys=this._invSubKeys=[];for(var i=0;i<16;i++){invSubKeys[i]=subKeys[15-i]}},encryptBlock:function(M,offset){this._doCryptBlock(M,offset,this._subKeys)},decryptBlock:function(M,offset){this._doCryptBlock(M,offset,this._invSubKeys)},_doCryptBlock:function(M,offset,subKeys){this._lBlock=M[offset];this._rBlock=M[offset+1];exchangeLR.call(this,4,0x0f0f0f0f);exchangeLR.call(this,16,0x0000ffff);exchangeRL.call(this,2,0x33333333);exchangeRL.call(this,8,0x00ff00ff);exchangeLR.call(this,1,0x55555555);for(var round=0;round<16;round++){var subKey=subKeys[round];var lBlock=this._lBlock;var rBlock=this._rBlock;var f=0;for(var i=0;i<8;i++){f|=SBOX_P[i][((rBlock^subKey[i])&SBOX_MASK[i])>>>0]}this._lBlock=rBlock;this._rBlock=lBlock^f}var t=this._lBlock;this._lBlock=this._rBlock;this._rBlock=t;exchangeLR.call(this,1,0x55555555);exchangeRL.call(this,8,0x00ff00ff);exchangeRL.call(this,2,0x33333333);exchangeLR.call(this,16,0x0000ffff);exchangeLR.call(this,4,0x0f0f0f0f);M[offset]=this._lBlock;M[offset+1]=this._rBlock},keySize:64/32,ivSize:64/32,blockSize:64/32});function exchangeLR(offset,mask){var t=((this._lBlock>>>offset)^this._rBlock)&mask;this._rBlock^=t;this._lBlock^=t<<offset}function exchangeRL(offset,mask){var t=((this._rBlock>>>offset)^this._lBlock)&mask;this._lBlock^=t;this._rBlock^=t<<offset}C.DES=BlockCipher._createHelper(DES);var TripleDES=C_algo.TripleDES=BlockCipher.extend({_doReset:function(){var key=this._key;var keyWords=key.words;this._des1=DES.createEncryptor(WordArray.create(keyWords.slice(0,2)));this._des2=DES.createEncryptor(WordArray.create(keyWords.slice(2,4)));this._des3=DES.createEncryptor(WordArray.create(keyWords.slice(4,6)))},encryptBlock:function(M,offset){this._des1.encryptBlock(M,offset);this._des2.decryptBlock(M,offset);this._des3.encryptBlock(M,offset)},decryptBlock:function(M,offset){this._des3.decryptBlock(M,offset);this._des2.encryptBlock(M,offset);this._des1.decryptBlock(M,offset)},keySize:192/32,ivSize:64/32,blockSize:64/32});C.TripleDES=BlockCipher._createHelper(TripleDES)}());(function(){var C=CryptoJS;var C_lib=C.lib;var StreamCipher=C_lib.StreamCipher;var C_algo=C.algo;var RC4=C_algo.RC4=StreamCipher.extend({_doReset:function(){var key=this._key;var keyWords=key.words;var keySigBytes=key.sigBytes;var S=this._S=[];for(var i=0;i<256;i++){S[i]=i}for(var i=0,j=0;i<256;i++){var keyByteIndex=i%keySigBytes;var keyByte=(keyWords[keyByteIndex>>>2]>>>(24-(keyByteIndex%4)*8))&0xff;j=(j+S[i]+keyByte)%256;var t=S[i];S[i]=S[j];S[j]=t}this._i=this._j=0},_doProcessBlock:function(M,offset){M[offset]^=generateKeystreamWord.call(this)},keySize:256/32,ivSize:0});function generateKeystreamWord(){var S=this._S;var i=this._i;var j=this._j;var keystreamWord=0;for(var n=0;n<4;n++){i=(i+1)%256;j=(j+S[i])%256;var t=S[i];S[i]=S[j];S[j]=t;keystreamWord|=S[(S[i]+S[j])%256]<<(24-n*8)}this._i=i;this._j=j;return keystreamWord}C.RC4=StreamCipher._createHelper(RC4);var RC4Drop=C_algo.RC4Drop=RC4.extend({cfg:RC4.cfg.extend({drop:192}),_doReset:function(){RC4._doReset.call(this);for(var i=this.cfg.drop;i>0;i--){generateKeystreamWord.call(this)}}});C.RC4Drop=StreamCipher._createHelper(RC4Drop)}());CryptoJS.mode.CTRGladman=(function(){var CTRGladman=CryptoJS.lib.BlockCipherMode.extend();function incWord(word){if(((word>>24)&0xff)===0xff){var b1=(word>>16)&0xff;var b2=(word>>8)&0xff;var b3=word&0xff;if(b1===0xff){b1=0;if(b2===0xff){b2=0;if(b3===0xff){b3=0}else{++b3}}else{++b2}}else{++b1}word=0;word+=(b1<<16);word+=(b2<<8);word+=b3}else{word+=(0x01<<24)}return word}function incCounter(counter){if((counter[0]=incWord(counter[0]))===0){counter[1]=incWord(counter[1])}return counter}var Encryptor=CTRGladman.Encryptor=CTRGladman.extend({processBlock:function(words,offset){var cipher=this._cipher; var blockSize=cipher.blockSize;var iv=this._iv;var counter=this._counter;if(iv){counter=this._counter=iv.slice(0);this._iv=undefined}incCounter(counter);var keystream=counter.slice(0);cipher.encryptBlock(keystream,0);for(var i=0;i<blockSize;i++){words[offset+i]^=keystream[i]}}});CTRGladman.Decryptor=Encryptor;return CTRGladman}());(function(){var C=CryptoJS;var C_lib=C.lib;var StreamCipher=C_lib.StreamCipher;var C_algo=C.algo;var S=[];var C_=[];var G=[];var Rabbit=C_algo.Rabbit=StreamCipher.extend({_doReset:function(){var K=this._key.words;var iv=this.cfg.iv;for(var i=0;i<4;i++){K[i]=(((K[i]<<8)|(K[i]>>>24))&0x00ff00ff)|(((K[i]<<24)|(K[i]>>>8))&0xff00ff00)}var X=this._X=[K[0],(K[3]<<16)|(K[2]>>>16),K[1],(K[0]<<16)|(K[3]>>>16),K[2],(K[1]<<16)|(K[0]>>>16),K[3],(K[2]<<16)|(K[1]>>>16)];var C=this._C=[(K[2]<<16)|(K[2]>>>16),(K[0]&0xffff0000)|(K[1]&0x0000ffff),(K[3]<<16)|(K[3]>>>16),(K[1]&0xffff0000)|(K[2]&0x0000ffff),(K[0]<<16)|(K[0]>>>16),(K[2]&0xffff0000)|(K[3]&0x0000ffff),(K[1]<<16)|(K[1]>>>16),(K[3]&0xffff0000)|(K[0]&0x0000ffff)];this._b=0;for(var i=0;i<4;i++){nextState.call(this)}for(var i=0;i<8;i++){C[i]^=X[(i+4)&7]}if(iv){var IV=iv.words;var IV_0=IV[0];var IV_1=IV[1];var i0=(((IV_0<<8)|(IV_0>>>24))&0x00ff00ff)|(((IV_0<<24)|(IV_0>>>8))&0xff00ff00);var i2=(((IV_1<<8)|(IV_1>>>24))&0x00ff00ff)|(((IV_1<<24)|(IV_1>>>8))&0xff00ff00);var i1=(i0>>>16)|(i2&0xffff0000);var i3=(i2<<16)|(i0&0x0000ffff);C[0]^=i0;C[1]^=i1;C[2]^=i2;C[3]^=i3;C[4]^=i0;C[5]^=i1;C[6]^=i2;C[7]^=i3;for(var i=0;i<4;i++){nextState.call(this)}}},_doProcessBlock:function(M,offset){var X=this._X;nextState.call(this);S[0]=X[0]^(X[5]>>>16)^(X[3]<<16);S[1]=X[2]^(X[7]>>>16)^(X[5]<<16);S[2]=X[4]^(X[1]>>>16)^(X[7]<<16);S[3]=X[6]^(X[3]>>>16)^(X[1]<<16);for(var i=0;i<4;i++){S[i]=(((S[i]<<8)|(S[i]>>>24))&0x00ff00ff)|(((S[i]<<24)|(S[i]>>>8))&0xff00ff00);M[offset+i]^=S[i]}},blockSize:128/32,ivSize:64/32});function nextState(){var X=this._X;var C=this._C;for(var i=0;i<8;i++){C_[i]=C[i]}C[0]=(C[0]+0x4d34d34d+this._b)|0;C[1]=(C[1]+0xd34d34d3+((C[0]>>>0)<(C_[0]>>>0)?1:0))|0;C[2]=(C[2]+0x34d34d34+((C[1]>>>0)<(C_[1]>>>0)?1:0))|0;C[3]=(C[3]+0x4d34d34d+((C[2]>>>0)<(C_[2]>>>0)?1:0))|0;C[4]=(C[4]+0xd34d34d3+((C[3]>>>0)<(C_[3]>>>0)?1:0))|0;C[5]=(C[5]+0x34d34d34+((C[4]>>>0)<(C_[4]>>>0)?1:0))|0;C[6]=(C[6]+0x4d34d34d+((C[5]>>>0)<(C_[5]>>>0)?1:0))|0;C[7]=(C[7]+0xd34d34d3+((C[6]>>>0)<(C_[6]>>>0)?1:0))|0;this._b=(C[7]>>>0)<(C_[7]>>>0)?1:0;for(var i=0;i<8;i++){var gx=X[i]+C[i];var ga=gx&0xffff;var gb=gx>>>16;var gh=((((ga*ga)>>>17)+ga*gb)>>>15)+gb*gb;var gl=(((gx&0xffff0000)*gx)|0)+(((gx&0x0000ffff)*gx)|0);G[i]=gh^gl}X[0]=(G[0]+((G[7]<<16)|(G[7]>>>16))+((G[6]<<16)|(G[6]>>>16)))|0;X[1]=(G[1]+((G[0]<<8)|(G[0]>>>24))+G[7])|0;X[2]=(G[2]+((G[1]<<16)|(G[1]>>>16))+((G[0]<<16)|(G[0]>>>16)))|0;X[3]=(G[3]+((G[2]<<8)|(G[2]>>>24))+G[1])|0;X[4]=(G[4]+((G[3]<<16)|(G[3]>>>16))+((G[2]<<16)|(G[2]>>>16)))|0;X[5]=(G[5]+((G[4]<<8)|(G[4]>>>24))+G[3])|0;X[6]=(G[6]+((G[5]<<16)|(G[5]>>>16))+((G[4]<<16)|(G[4]>>>16)))|0;X[7]=(G[7]+((G[6]<<8)|(G[6]>>>24))+G[5])|0}C.Rabbit=StreamCipher._createHelper(Rabbit)}());CryptoJS.mode.CTR=(function(){var CTR=CryptoJS.lib.BlockCipherMode.extend();var Encryptor=CTR.Encryptor=CTR.extend({processBlock:function(words,offset){var cipher=this._cipher; var blockSize=cipher.blockSize;var iv=this._iv;var counter=this._counter;if(iv){counter=this._counter=iv.slice(0);this._iv=undefined}var keystream=counter.slice(0);cipher.encryptBlock(keystream,0);counter[blockSize-1]=(counter[blockSize-1]+1)|0; for(var i=0;i<blockSize;i++){words[offset+i]^=keystream[i]}}});CTR.Decryptor=Encryptor;return CTR}());(function(){var C=CryptoJS;var C_lib=C.lib;var StreamCipher=C_lib.StreamCipher;var C_algo=C.algo;var S=[];var C_=[];var G=[];var RabbitLegacy=C_algo.RabbitLegacy=StreamCipher.extend({_doReset:function(){var K=this._key.words;var iv=this.cfg.iv;var X=this._X=[K[0],(K[3]<<16)|(K[2]>>>16),K[1],(K[0]<<16)|(K[3]>>>16),K[2],(K[1]<<16)|(K[0]>>>16),K[3],(K[2]<<16)|(K[1]>>>16)];var C=this._C=[(K[2]<<16)|(K[2]>>>16),(K[0]&0xffff0000)|(K[1]&0x0000ffff),(K[3]<<16)|(K[3]>>>16),(K[1]&0xffff0000)|(K[2]&0x0000ffff),(K[0]<<16)|(K[0]>>>16),(K[2]&0xffff0000)|(K[3]&0x0000ffff),(K[1]<<16)|(K[1]>>>16),(K[3]&0xffff0000)|(K[0]&0x0000ffff)];this._b=0;for(var i=0;i<4;i++){nextState.call(this)}for(var i=0;i<8;i++){C[i]^=X[(i+4)&7]}if(iv){var IV=iv.words;var IV_0=IV[0];var IV_1=IV[1];var i0=(((IV_0<<8)|(IV_0>>>24))&0x00ff00ff)|(((IV_0<<24)|(IV_0>>>8))&0xff00ff00);var i2=(((IV_1<<8)|(IV_1>>>24))&0x00ff00ff)|(((IV_1<<24)|(IV_1>>>8))&0xff00ff00);var i1=(i0>>>16)|(i2&0xffff0000);var i3=(i2<<16)|(i0&0x0000ffff);C[0]^=i0;C[1]^=i1;C[2]^=i2;C[3]^=i3;C[4]^=i0;C[5]^=i1;C[6]^=i2;C[7]^=i3;for(var i=0;i<4;i++){nextState.call(this)}}},_doProcessBlock:function(M,offset){var X=this._X;nextState.call(this);S[0]=X[0]^(X[5]>>>16)^(X[3]<<16);S[1]=X[2]^(X[7]>>>16)^(X[5]<<16);S[2]=X[4]^(X[1]>>>16)^(X[7]<<16);S[3]=X[6]^(X[3]>>>16)^(X[1]<<16);for(var i=0;i<4;i++){S[i]=(((S[i]<<8)|(S[i]>>>24))&0x00ff00ff)|(((S[i]<<24)|(S[i]>>>8))&0xff00ff00);M[offset+i]^=S[i]}},blockSize:128/32,ivSize:64/32});function nextState(){var X=this._X;var C=this._C;for(var i=0;i<8;i++){C_[i]=C[i]}C[0]=(C[0]+0x4d34d34d+this._b)|0;C[1]=(C[1]+0xd34d34d3+((C[0]>>>0)<(C_[0]>>>0)?1:0))|0;C[2]=(C[2]+0x34d34d34+((C[1]>>>0)<(C_[1]>>>0)?1:0))|0;C[3]=(C[3]+0x4d34d34d+((C[2]>>>0)<(C_[2]>>>0)?1:0))|0;C[4]=(C[4]+0xd34d34d3+((C[3]>>>0)<(C_[3]>>>0)?1:0))|0;C[5]=(C[5]+0x34d34d34+((C[4]>>>0)<(C_[4]>>>0)?1:0))|0;C[6]=(C[6]+0x4d34d34d+((C[5]>>>0)<(C_[5]>>>0)?1:0))|0;C[7]=(C[7]+0xd34d34d3+((C[6]>>>0)<(C_[6]>>>0)?1:0))|0;this._b=(C[7]>>>0)<(C_[7]>>>0)?1:0;for(var i=0;i<8;i++){var gx=X[i]+C[i];var ga=gx&0xffff;var gb=gx>>>16;var gh=((((ga*ga)>>>17)+ga*gb)>>>15)+gb*gb;var gl=(((gx&0xffff0000)*gx)|0)+(((gx&0x0000ffff)*gx)|0);G[i]=gh^gl}X[0]=(G[0]+((G[7]<<16)|(G[7]>>>16))+((G[6]<<16)|(G[6]>>>16)))|0;X[1]=(G[1]+((G[0]<<8)|(G[0]>>>24))+G[7])|0;X[2]=(G[2]+((G[1]<<16)|(G[1]>>>16))+((G[0]<<16)|(G[0]>>>16)))|0;X[3]=(G[3]+((G[2]<<8)|(G[2]>>>24))+G[1])|0;X[4]=(G[4]+((G[3]<<16)|(G[3]>>>16))+((G[2]<<16)|(G[2]>>>16)))|0;X[5]=(G[5]+((G[4]<<8)|(G[4]>>>24))+G[3])|0;X[6]=(G[6]+((G[5]<<16)|(G[5]>>>16))+((G[4]<<16)|(G[4]>>>16)))|0;X[7]=(G[7]+((G[6]<<8)|(G[6]>>>24))+G[5])|0}C.RabbitLegacy=StreamCipher._createHelper(RabbitLegacy)}());CryptoJS.pad.ZeroPadding={pad:function(data,blockSize){var blockSizeBytes=blockSize*4;data.clamp();data.sigBytes+=blockSizeBytes-((data.sigBytes%blockSizeBytes)||blockSizeBytes)},unpad:function(data){var dataWords=data.words;var i=data.sigBytes-1;while(!((dataWords[i>>>2]>>>(24-(i%4)*8))&0xff)){i--}data.sigBytes=i+1}};
