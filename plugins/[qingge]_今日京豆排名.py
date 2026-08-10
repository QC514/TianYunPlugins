//[disable:false]

//[rule:^(今日排名|昨日排名|京豆排名|个人排名|京豆统计|豆豆统计)$]
//[title: 今日京豆排名]
//[author: qingge]
//[class: 工具类]
//[public: true]
//[icon: http://www.icosky.com/icon/png/System/Boomy/Group+of+users.png]
//[price: 3.88]
//[version: 1.3.2]
//[admin: false]
//[platform: qq,wx,tg,wb,qb]
//[priority: 9999999999]
//[service: 97393412]
//[description: 支持容器内所有CK进行排名查询,个人名下账号排名查询<br/>兼容最新版本奥特曼,需要给[qinglong数据]权限<br/>10-29,增加个人京豆排行榜<br/>新增容器内京豆总收益以及个人名下总收益<br/>新增推送指定个人渠道推送<br/>11-14 修复多个同渠道群组 内容被叠加<br/>11-19 修复过滤PIN无效<br/>8-1 新增查询个人名下京豆总数，总额<br/>8-4 对个人排名中增加查豆豆总数开关合并输出]
// [param: {"required":true,"key":"who_tong.jcql","placeholder":"容器名称","name":"青龙名称","desc":"获取名方法:奥特曼后台-容器管理--对接容器--名称"}]
// [param: {"required":true,"key":"who_tong.h5st_api","placeholder":"http://110.40.165.213:39000","name":"自建H5接口","desc":"填写你搭建好的地址：http://110.40.165.213:39000"}]
//[param: {"spliter":true}]
// [param: {"required":true,"key":"who_tong.pm_qn","placeholder":"","name":"排名前N位","desc":"例如前10,则填10"}]
// [param: {"required":false,"key":"who_tong.jd_jrzs","bool":true,"placeholder":"false","name":"查总京豆","desc":"默认不开启,开启后发个人排名时会含用户名下总京豆一并查"}]
// [param: {"required":true,"key":"who_tong.jd_guolv","placeholder":"","name":"过滤PIN","desc":"填你需要过滤的pin,用,逗号分割"}]
// [param: {"required":true,"key":"who_tong.jd_tsqd","placeholder":"","name":"群组通知渠道","desc":"wb:123456,qq:45678,使用小写,逗号分开多渠道"}]
// [param: {"required":true,"key":"who_tong.jd_grqd","placeholder":"","name":"个人推送","desc":"qq:45678,使用小写,逗号分开,只能支持一个"}]
// [param: {"required":false,"key":"otto.who_sq","bool":true,"placeholder":"false","name":"授权控制","desc":"暂时没有作用"}]

const content = GetContent();
const imType = ImType();

let checkJS = false;
let container = null;
let containerEnv = [];

let host_api = "";
let nc_ua = "";
let h5_ver = "";

const state = {
    zrjd: 0, // 昨日总收益京豆
    jrjd: 0, // 今日总收益京豆
    zsjdtj: 0, // 京豆总数统计
    rankList: [] // 排行列表
};

const config = getConfig();

try {
    importJs("qinglong.js");
    importJs("who-hs.js");
} catch (err) {
    checkJS = true;
}

function getConfig() {
    return {
        qlName: bucketGet("who_tong", "jcql") || "",
        h5stApi: bucketGet("who_tong", "h5st_api") || "",
        topN: Number(bucketGet("who_tong", "pm_qn") || 10),
        needTotalBean: String(bucketGet("who_tong", "jd_jrzs")) === "true",
        filterPins: parseFilterPins(bucketGet("who_tong", "jd_guolv") || ""),
        groupPushChannels: bucketGet("who_tong", "jd_tsqd") || "",
        personalPush: bucketGet("who_tong", "jd_grqd") || "",
        jdGrkg: String(bucketGet("who_tong", "jd_grkg")) === "true",
        authSwitch: get("who_sq")
    };
}

function parseFilterPins(text) {
    if (!text) return [];
    return text
        .split(",")
        .map(item => item.trim())
        .filter(Boolean);
}

function resetState() {
    state.zrjd = 0;
    state.jrjd = 0;
    state.zsjdtj = 0;
    state.rankList = [];
}

function main() {
    resetState();

    host_api = config.h5stApi || "http://113.45.206.6:3006";

    if (!config.groupPushChannels) {
        notifyMasters("你还没设置推送渠道\n去云插件的-配置 \n里面设置一下");
    }

    if (checkJS) {
        if (isAdmin()) {
            notifyMasters("到群内下载[qinglong.js]上传到plugin/replies的文件内");
        }
        return;
    }

    if (!config.qlName) {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置");
        return;
    }

    Debug(`指定获取青龙容器名称:${config.qlName}`);

    const containerData = qls(config.qlName);
    if (!containerData) {
        notifyMasters("未找到对应的青龙容器，请检查青龙名称是否正确");
        return;
    }

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

    try {
        if (content === "今日排名" || content === "昨日排名" || content === "京豆排名") {
            handleGlobalRank();
        } else if (content === "京豆统计" || content === "豆豆统计") {
            handlePersonalBeanStats();
        } else {
            handlePersonalRank();
        }
    } catch (e) {
        Debug("main error: " + e);
    }
}

function handleGlobalRank() {
    if (!(isAdmin() || imType === "croncmd")) {
        return;
    }

    const cookieObj = getActiveCookies(containerEnv);

    for (let j = 0; j < cookieObj.length; j++) {
        const cookie = cookieObj[j].value;
        const pin = getPin(cookie);

        if (isPinFiltered(pin)) {
            Debug("过滤名单中: " + pin);
            continue;
        }

        sumBean(cookie);
    }

    const msgs = buildGlobalRankMessage();
    pushGroupMessages(msgs.join("\n"));
    pushPersonalMessage(msgs.join("\n"));
}

function handlePersonalBeanStats() {
    const msgs = [];
    msgs.push(`-->个人京豆<-----`);

    const bindPins = getUserBindPins();
    const cookieObj = getAllCookies(containerEnv);
    let count = 0;

    for (let p = 0; p < bindPins.length; p++) {
        for (let j = 0; j < cookieObj.length; j++) {
            const cookie = cookieObj[j].value;
            const pin = getPin(cookie);

            if (cookieObj[j].status !== 0) continue;
            if (bindPins[p] !== pin) continue;

            count++;


            if (needVipCheck(pin)) {
                if (user_vip_jc(pin)) {
                    Debug(decodeURIComponent(pin) + ",还没到期");
                    newUserInfo(cookie, count, msgs);
                } else {
                    get_tx("账号：" + decodeURIComponent(pin) + "\n已经到期，如需继续代挂\n请发送：续费");
                }
            } else {
                newUserInfo(cookie, count, msgs);
            }
        }
    }

    get_tx(msgs.join("\n") + "\n");
}

function handlePersonalRank() {
    const bindPins = getUserBindPins();
    const cookieObj = getAllCookies(containerEnv);

    for (let p = 0; p < bindPins.length; p++) {
        for (let j = 0; j < cookieObj.length; j++) {
            const cookie = cookieObj[j].value;
            const pin = getPin(cookie);

            if (bindPins[p] !== pin) continue;

            if (needVipCheck(pin)) {
                if (user_vip_jc(pin)) {
                    Debug(decodeURIComponent(pin) + ",还没到期");
                    sumBean(cookie);
                } else {
                    get_tx("账号：" + decodeURIComponent(pin) + "\n已经到期，如需继续代挂\n请发送：续费");
                }
            } else {
                sumBean(cookie);
            }
        }
    }

    const msgs = [];
    msgs.push(`--->今日个人京豆排行榜<---`);

    state.rankList.sort((a, b) => b.new - a.new);
    for (let i = 0; i < state.rankList.length; i++) {
        msgs.push(
            `[${i + 1}] ${hideMiddlePart(decodeURIComponent(state.rankList[i].name))}, 今收: ${state.rankList[i].new}, 昨收: ${state.rankList[i].old}`
        );
    }

    msgs.push(`收益:今日京豆:${state.jrjd},昨日京豆:${state.zrjd}`);
    msgs.push(`----------------------`);

    if (config.needTotalBean) {
        let count = 0;
        for (let p = 0; p < bindPins.length; p++) {
            for (let j = 0; j < cookieObj.length; j++) {
                const cookie = cookieObj[j].value;
                const pin = getPin(cookie);

                if (bindPins[p] !== pin) continue;

                count++;

                if (needVipCheck(pin)) {
                    if (user_vip_jc(pin)) {
                        Debug(decodeURIComponent(pin) + ",还没到期");
                        newUserInfo(cookie, count, msgs);
                    } else {
                        get_tx("账号：" + decodeURIComponent(pin) + "\n已经到期，如需继续代挂\n请发送：续费");
                    }
                } else {
                    newUserInfo(cookie, count, msgs);
                }
            }
        }

        msgs.push(`--->京豆总:${state.zsjdtj}豆🐶<---`);
    }

    get_tx(msgs.join("\n"));
}

function buildGlobalRankMessage() {
    const msgs = [];
    msgs.push(`今日京豆收入排行榜`);

    state.rankList.sort((a, b) => b.new - a.new);

    const max = Math.min(config.topN, state.rankList.length);
    for (let i = 0; i < max; i++) {
        msgs.push(
            `[${i + 1}] ${decodeURIComponent(state.rankList[i].name)}, 今收: ${state.rankList[i].new}, 昨收: ${state.rankList[i].old}`
        );
    }

    msgs.push(`所有用户[京豆]总收益:今日京豆:${state.jrjd},昨日京豆:${state.zrjd}`);
    return msgs;
}

function pushGroupMessages(text) {
    if (!config.groupPushChannels) return;

    const qd = config.groupPushChannels.split(",").map(s => s.trim()).filter(Boolean);

    for (let k = 0; k < qd.length; k++) {
        const qdts = qd[k].split(":");
        if (qdts.length < 2) continue;

        push({
            imType: qdts[0],
            userID: "",
            title: "",
            groupCode: qdts[1],
            content: text,
        });
    }
}

function pushPersonalMessage(text) {
    if (!config.personalPush) return;

    const arr = config.personalPush.split(":");
    if (arr.length < 2) return;

    push({
        imType: arr[0],
        userID: arr[1],
        title: "",
        groupCode: "",
        content: text,
    });
}

function getActiveCookies(envs) {
    return envs.filter(function (_data) {
        return _data.name === "JD_COOKIE" && _data.status === 0;
    });
}

function getAllCookies(envs) {
    return envs.filter(function (_data) {
        return _data.name === "JD_COOKIE";
    });
}

function getUserBindPins() {
    return bucketKeys("pin" + imType.toUpperCase(), GetUserID()) || [];
}

function getPin(cookie) {
    const match = cookie.match(/pt_pin=([^;]+)/);
    return match ? match[1] : "";
}

function isPinFiltered(pin) {
    return config.filterPins.includes(pin);
}

function needVipCheck(pin) {
    return config.authSwitch === "true" || config.authSwitch === true;
}

function qls(uid) {
    const allpins = bucketKeys("qls") || [];
    for (let j = 0; j < allpins.length; j++) {
        const ql_a = JSON.parse(bucketGet("qls", String(allpins[j])));
        if (ql_a.name === uid) {
            return ql_a;
        }
    }
    return null;
}

function DateToStr(date) {
    const year = date.getFullYear();
    const month = date.getMonth();
    const day = date.getDate();
    return year + "-" +
        ((month + 1) > 9 ? (month + 1) : "0" + (month + 1)) + "-" +
        (day > 9 ? day : ("0" + day));
}

// 汇总豆豆
function sumBean(cookie) {
    const pin = getPin(cookie);

    try {
        let todayIn = 0;
        let todayOut = 0;
        let yesterIn = 0;
        let yesterOut = 0;

        const curDate = new Date();
        const yesDate = new Date();
        yesDate.setDate(curDate.getDate() - 1);

        const strToday = DateToStr(curDate);
        const strYester = DateToStr(yesDate);

        const MAX_PAGE = 20;

        for (let page = 1; page <= MAX_PAGE; page++) {
            const data = getJingBeanBalanceDetail(cookie, page);
            if (!data) break;

            const jd_data = JSON.parse(data);
            let obj=jd_data.rs?.beanTransactions?.beanTransactionsDetail
            if (!obj || !obj?.transactions || !obj?.transactions.length) break;

            let shouldBreak = false;

            for (let i = 0; i < obj.transactions.length; i++) {
                const item = obj.transactions[i];
                const dateStr = item.transactionTime || "";
                const eventMassage = item.title || "";
                const  amount= parseInt(item.num || 0);
//sendText(amount)
                if (dateStr.slice(0, 10) === strToday) {
                    if (eventMassage.indexOf("退还") === -1 && eventMassage.indexOf("使用") === -1) {
                        if (amount > 0) {
                            todayIn += amount;
                        } else {
                            todayOut += amount;
                        }
                    }
                } else if (dateStr.slice(0, 10) === strYester) {
                    if (eventMassage.indexOf("退还") === -1 && eventMassage.indexOf("使用") === -1) {
                        if (amount > 0) {
                            yesterIn += amount;
                        } else {
                            yesterOut += amount;
                        }
                    }
                } else {
                    shouldBreak = true;
                    break;
                }
            }

            if (shouldBreak) break;
        }

        state.rankList.push({
            name: String(pin),
            new: parseInt(todayIn),
            old: parseInt(yesterIn)
        });

        state.zrjd += parseInt(yesterIn);
        state.jrjd += parseInt(todayIn);
    } catch (err) {
        Debug("sumBean error: " + err);
    }
}

// 获取豆豆明细
function getJingBeanBalanceDetail(cookie, page) {
    try {
        const body = encodeURIComponent(JSON.stringify({ pageSize: "20", pageNo: String(page),"scene":"beanTransactions","type":"0" }));
        return request({
            url: "https://api.m.jd.com/api?functionId=bff_rightsCenter_bean&scene=beanTransactions",
            body: "appid=plus_business&functionId=bff_rightsCenter_bean&body=" + body + "&loginType=2",
          method: "post",
            headers: {
                "User-Agent": UserAgents(),
                "Content-Type": "application/x-www-form-urlencoded",
                "origin":"https://pro.m.jd.com",
                "Cookie": cookie,
            },
            timeout: 10000,
        });
    } catch (e) {
        Debug("getJingBeanBalanceDetail error: " + e);
        return null;
    }
}

// 检测到期时间
function user_vip_jc(ID) {
    const user = bucketGet("who_user_vip", ID);
    if (user === "") {
        return false;
    } else {
        let time = Date.parse(new Date());
        time = parseInt(time / 1000);
        if (user <= time) {
            return false;
        } else {
            return true;
        }
    }
}


function ncaua(data) {
    for (let k = 0; k < 5; k++) {
        const body = request({
            url: `${host_api}/UA`,
            method: "post",
            body: data,
            headers: {
                "Content-Type": "application/json",
            },
            dataType: "json",
            timeOut: 8000
        });

        if (body && body.code === 200 && body.data) {
            nc_ua = body.data;
            const ucxa = nc_ua.split(";");
            h5_ver = ucxa[2] || "";
            return true;
        }
    }
    return false;
}

function hideMiddlePart(str, startLength = 5, endLength = 5) {
    if (!str || str.length <= startLength + endLength) {
        return str;
    }
    const hiddenPart = `***`;
    return str.substring(0, startLength) + hiddenPart + str.substring(str.length - endLength);
}

// 账号信息
function newUserInfo(cook, lend, msgs) {
    const str = getPin(cook);
    const pin = decodeURIComponent(str);

    for (let k = 0; k < 1; k++) {
        const data = request({
            url: "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion",
            method: "get",
            headers: {
                cookie: cook,
                Accept: "application/json, text/plain",
                "Content-Type": "application/json;charset=UTF-8",
                "User-Agent": UserAgents()
            },
            dataType: "json",
            timeOut: 8000
        });

        if (data && data.msg === "success") {
            msgs.push(`[${lend}] ${hideMiddlePart(pin)},总数 ${data.data.assetInfo.beanNum} 豆`);
            state.zsjdtj += parseInt(data.data.assetInfo.beanNum || 0);
            return true;
        } else {
            msgs.push(`[${lend}] ${hideMiddlePart(pin)},已失效,重新登录`);
        }
    }

    return false;
}

var USER_AGENTS = [
    "jdltapp;iPad;3.7.0;14.4;network/wifi;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;2346663656561603-4353564623932316;network/wifi;model/ONEPLUS A5010;addressid/0;aid/2dfceea045ed292a;oaid/;osVer/29;appBuild/1436;psn/BS6Y9SAiw0IpJ4ro7rjSOkCRZTgR3z2K|10;psq/5;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/10.5;jdv/;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/oppo;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ONEPLUS A5010 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.1;59d6ae6e8387bd09fe046d5b8918ead51614e80a;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone12,1;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/;pv/1.26;apprpd/;ref/JDLTSubMainPageViewController;psq/0;ads/;psn/59d6ae6e8387bd09fe046d5b8918ead51614e80a|3;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.1;Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;13.5;22d679c006bf9c087abf362cf1d2e0020ebb8798;network/wifi;ADID/10857A57-DDF8-4A0D-A548-7B8F43AC77EE;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone12,1;addressid/2378947694;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/15.7;apprpd/Allowance_Registered;ref/JDLTTaskCenterViewController;psq/6;ads/;psn/22d679c006bf9c087abf362cf1d2e0020ebb8798|22;jdv/0|kong|t_1000170135|tuiguang|notset|1614153044558|1614153044;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;2616935633265383-5333463636261326;network/UNKNOWN;model/M2007J3SC;addressid/1840745247;aid/ba9e3b5853dccb1b;oaid/371d8af7dd71e8d5;osVer/29;appBuild/1436;psn/t7JmxZUXGkimd4f9Jdul2jEeuYLwxPrm|8;psq/6;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/5.6;jdv/;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/xiaomi;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 10; M2007J3SC Build/QKQ1.200419.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045135 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;network/wifi;Mozilla/5.0 (Linux; Android 10; Redmi Note 7 Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.4;network/3g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1"
];

function UserAgents() {
    return USER_AGENTS[parseInt(Math.random() * USER_AGENTS.length)];
}

main();