//[pin:true]
//[disable:false]
// [rule: ^(.*)农场$] 
// [cron: 59 8,14,18,23 * * *]
//[icon: https://img2.baidu.com/it/u=1715024503,3570115563&fm=253&fmt=auto&app=138&f=JPEG?w=256&h=256]图标链接地址，支持http和https
//[tile: 农场管理]要与文件名相同，也可以不加，上传aut云时会自动将文件名设置为此头注
//[author: specter]作者,可以自定义，不定义的话，上传时会增加为aut云注册的用户名,收费插件一定要填写aut云账号
//[version: 4.3.9] 版本格式：1.0.0，不定义的话，上传时会自动增加此头注，默认为1.0.0 
//[class: 工具类]建议从工具类、查询类、娱乐类、餐饮类、影音类、生活类、图片类、游戏类等中选择，也可自定义
//[platform: qq,wx,tg]适用的平台 qq\wx\tg\wxmp之间选择，中间用英文逗号隔开
//[public: true] 是否公开发布？值为true 或 false，不定义的话，上传aut云时会自动设置为true
//[price: 3.0] 上架价格
//[service: 2607401955]售后联系方式，service不完整，将不会审核上架
//[description: 新旧农场管理付费满助力,附赠成熟和未种植一对一通知,控制账号是否浇水。<br>更新日志（更新插件后需拉取最新库，手动禁用“新农场CK顺序助力”，启用并修改定时“新农场助力码助力”脚本。新农场进度不同步的自己添加青龙变量export FRUIT_NOTIFY=true）。可在插件设置自己设置执行定时，根据执行定时同步农场和发送成熟通知，定时23:59必须有!）<br>命令如下：查询农场、授权农场、删除授权农场、打赏农场、管理农场、统计农场、清理过期农场、同步农场、浇水农场。<br>购买前请先看教程，仅支持最新6dy库，详细教程：https://docs.qq.com/doc/DTlpuUFlHV0JYU09y] 使用方法尽量写具体

var tongzi = "farm";
let userId = GetUserID();
var nickname = param(1);
let firstpeizhi = bucketGet(tongzi, "farmpin");
if (firstpeizhi == "false" || firstpeizhi == "") {
    bucketSet(tongzi, "farmpin", "[]");
}
let newfirstpeizhi = bucketGet(tongzi, "newfarmpin");
if (newfirstpeizhi == "false" || newfirstpeizhi == "") {
    bucketSet(tongzi, "newfarmpin", "[]");
}
let newRepo = bucketGet(tongzi, "newRepo") || "[]";
if (newRepo == "false" || newRepo == "") {
    bucketSet(tongzi, "newRepo", "[]");
}
//更新newRepo缓存
newRepo = JSON.parse(newRepo);
if (newRepo[0] == '6dylan6_jdpro_jd_farm_help_new') {
    newRepo[0] = '6dylan6_jdpro_jd_farmnew_code_help';
    bucketSet(tongzi, "newRepo", JSON.stringify(newRepo));
}
var farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
var isAdmin = isAdmin();
var imType = ImType();
var qltokens = '';
var groupCode = bucketGet(tongzi, "groupCode");

var version = call("version")()["sn"];
Debug(version)
var QLS = null
if (version > '2.6.5') {
    QLS = [];
    const array = bucketKeys('qls');
    if (array && array.length > 0) {
        for (const item of array) {
            let data = bucketGet('qls', item)
            QLS.push(JSON.parse(data));
        }
    } else {
        var QLS = bucketGet("qinglong", "QLS");
        QLS = JSON.parse(QLS)
    }
} else {
    var QLS = bucketGet("qinglong", "QLS");
    QLS = JSON.parse(QLS)
}
// Debug(QLS)
if (QLS.length == 0) {
    notifyMasters("获取容器出错,请在奥特曼后台-系统管理-插件权限中允许本插件访问qinglong数据")
}

function main() {
    var ispeizhi = bucketGet(tongzi, "IsPeiZhi");
    if (ispeizhi == "false" || ispeizhi == "") {    //是否第一次使用
        if (isAdmin) {
            sendText("第一次使用本插件，请稍等正在初始化配置");
            ChuShiPeiZhi();
        } else {
            sendText("当前插件未初始化配置，请联系管理员");
        }
    } else {
        SelectFarmItem();
    }
}

function ChuShiPeiZhi() {
    var IsWanCheng = "";
    if (IsPzShouQuan()) {
        if (PZShouQuan()) {
            if (PzQingLong()) {
                if (PzIsUseShouQuan()) {
                    sendText("插件初始化配置完成，如需修改，请发送管理农场。");
                    bucketSet(tongzi, "IsPeiZhi", "1");
                    bucketSet(tongzi, "IsUserUseDaShang", "true");
                } else {
                    IsWanCheng = false;
                }
            } else {
                IsWanCheng = false;
            }
        } else {
            IsWanCheng = false;
        }
    } else {
        if (PzQingLong()) {
            bucketSet(tongzi, "IsShouQuanTrue", "false");
            sendText("插件初始化配置完成，未配置授权系统，如需修改，请发送管理农场。");
            bucketSet(tongzi, "IsPeiZhi", "1");
            bucketSet(tongzi, "IsUserUseDaShang", "true");
        } else {
            IsWanCheng = false;
        }
    }
    if (IsWanCheng == false || IsWanCheng == "") {
        DeletePeiZhi();
    }
}

function PZShouQuan() {
    try {
        const messages = [
            "请在60秒内告知我旧版付费农场账号最大总数,输入纯数字(输入“q”随时退出会话。)",
            "请在60秒内告知我新版付费农场账号最大总数,输入纯数字(输入“q”随时退出会话。)",
            "请在60秒内告知我用户旧版农场续费价格x元/30天,输入x(x只能为整数,输入“q”随时退出会话。)",
            "请在60秒内告知我用户新版农场续费价格x元/30天,输入x(x只能为整数,输入“q”随时退出会话。)",
            "请在60秒内告知我给用户发送的赞赏码图片地址 (必须为奥特曼挂着的微信机器人的赞赏码，输入“q”随时退出会话。)"
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

        const shouquan = {
            "MaxAccounts": answers[0],
            "NewMaxAccounts": answers[1],
            "SumAtTimePrice": answers[2],
            "NewSumAtTimePrice": answers[3],
            "Images": answers[4]
        };

        sendText("配置成功，确保您已成功配置微信机器人，否则自助授权系统将失效。");
        bucketSet(tongzi, "MoRenShouQuan", JSON.stringify(shouquan));
        return true;
    } catch {
        sendText("配置授权系统出现问题，请检查并重新配置！");
        return false;
    }
}

function IsPzShouQuan() {
    sendText("请在60秒内告知我是否配置授权系统true/false(输入“q”随时退出会话。)");
    var msg2 = ChuShiShuRu();
    if (msg2) {
        if (msg2 == true || msg2 == "true") {
            return true;
        } else {
            return false;
        }
    } else {
        return
    }
}

function DeletePeiZhi() {
    bucketSet(tongzi, "peizhi", "false");
    bucketSet(tongzi, "IsShouQuanTrue", "false");
    bucketSet(tongzi, "IsUserUseDaShang", "false");
    DeletPzQingLong();
}

function PzIsUseShouQuan() {
    sendText("是否开启用户自助授权功能？ true/false (输入“q”随时退出会话。)");
    var msg = ChuShiShuRu();
    if (msg) {
        var IsShouQuanTrue = msg;
        if (IsShouQuanTrue == "true" || IsShouQuanTrue == "false") {
            bucketSet(tongzi, "IsShouQuanTrue", IsShouQuanTrue);
            return true;
        }
        else {
            sendText("输入错误，默认关闭用户自助授权功能！");
            bucketSet(tongzi, "IsShouQuanTrue", "false");
            return true
        }
    } else {
        return
    }
}

function PzQingLong() {
    sendText("请输入是否由autMan管理农场助力码？  true/false (输入“q”随时退出会话。)");
    var msg = ChuShiShuRu();
    if (msg == 'false') {
        DeletPzQingLong();
        return true
    }

    var pzqlstr = "请选择农场助力容器：\n0.全部容器";
    let farmQLS = [];
    QLS.forEach((item, index) => {
        pzqlstr = pzqlstr + "\n" + (index + 1) + "." + item.name;
        farmQLS.push(item.name);
    })
    pzqlstr = pzqlstr + '\n如果要选择其中几个,可以用英文逗号分割开,例(1,2)';
    sendText(pzqlstr);
    var msg = ShuRu();
    if (msg == "0") {
        farmQLS = farmQLS;
    } else {
        msg = msg.split(',');
        farmQLS = msg.map(item => farmQLS[item - 1]);
    }
    farmQLS = farmQLS.join(',');
    bucketSet('farm', 'QLS', farmQLS);
    if (chooserepo()) {
        if (newchooserepo()) {
            sendText('正在检索青龙数据。。。')
            isupqlenv();
            sendText('配置青龙成功，需要填写所有账号的助力码，助力顺序默认根据授权时间排序，更多设置请发送"管理农场"查看');
        }
    }
    return true
}

function chooserepo() {
    var pzqlstr = "请选择你使用的旧版农场助力脚本仓库：\n1.6dy库\n2.我修改过脚本名字，输入自定义脚本名（仅支持6dy库）\n3.我修改过脚本名字或有多个助力脚本（仅支持6dy库）";
    sendText(pzqlstr);
    var msg = ShuRu();
    const repo = ['6dylan6_jdpro_jd_farm_help', '6dylan6_jdpro_jd_fruit'];
    let relrepo = [];
    if (msg == 'false') {
        return false
    } else if (msg == '2') {
        sendText('请输入你修改过的旧版农场助力脚本命令，例：task 6dylan6_jdpro/jd_farm_help.js');
        var msg1 = ShuRu();
        if (msg1) {
            relrepo.push(msg1.replace(/^task\s(.+)\.js$/, '$1').replace('/', '_'));
        } else {
            sendText('输入错误，已退出');
            return false
        }
        sendText('请输入你修改过的旧版农场任务脚本命令，例：task 6dylan6_jdpro/jd_fruit.js');
        var msg2 = ShuRu();
        if (msg2) {
            relrepo.push(msg2.replace(/^task\s(.+)\.js$/, '$1').replace('/', '_'));
        } else {
            sendText('输入错误，已退出');
            return false
        }
    } else if (msg == '3') {
        sendText('请输入你修改过的旧版农场助力脚本命令，例：task 6dylan6_jdpro/jd_farm_help.js');
        var isstop = true;
        var strrepo = '';
        while (isstop) {
            sendText('请输入一条旧版农场助力脚本执行命令，如果没了请输入false');
            var msg1 = ShuRu();
            if (msg1 === 'false') {
                isstop = false;
                if (strrepo.length == 0) {
                    sendText('错误，请至少输入一条，已退出');
                    return false
                }
                strrepo = strrepo.replace(/,$/, '');
                relrepo.push(strrepo);
            } else if (msg1 != false) {
                strrepo = strrepo + msg1.replace(/^task\s(.+)\.js$/, '$1').replace('/', '_') + ',';
            } else {
                sendText('输入错误，已退出');
                return false
            }
        }
        sendText('请输入你修改过的旧版农场日常任务脚本命令，例：task 6dylan6_jdpro/jd_fruit.js');
        var isstop = true;
        var strrepo = '';
        while (isstop) {
            sendText('请输入一条旧版农场日常任务脚本执行命令，如果没了请输入false');
            var msg1 = ShuRu();
            if (msg1 === 'false') {
                isstop = false;
                if (strrepo.length == 0) {
                    sendText('错误，请至少输入一条，已退出');
                    return false
                }
                strrepo = strrepo.replace(/,$/, '');
                relrepo.push(strrepo);
            } else if (msg1 != false) {
                strrepo = strrepo + msg1.replace(/^task\s(.+)\.js$/, '$1').replace('/', '_') + ',';
            } else {
                sendText('输入错误，已退出');
                return false
            }
        }
    } else {
        relrepo = repo;
    }
    bucketSet('farm', 'Repo', JSON.stringify(relrepo));
    return true
}

function newchooserepo() {
    var pzqlstr = "请选择你使用的新版农场助力脚本仓库：\n1.6dy库\n2.我修改过脚本名字，输入自定义脚本名（仅支持6dy库）\n3.我修改过脚本名字或有多个助力脚本（仅支持6dy库）";
    sendText(pzqlstr);
    var msg = ShuRu();
    const repo = ['6dylan6_jdpro/jd_farmnew_code_help', '6dylan6_jdpro_jd_fruit_new'];
    let relrepo = [];
    if (msg == 'false') {
        return false
    } else if (msg == '2') {
        sendText('请输入你修改过的新版农场助力脚本命令，例：task 6dylan6_jdpro/jd_farm_help_new.js');
        var msg1 = ShuRu();
        if (msg1) {
            relrepo.push(msg1.replace(/^task\s(.+)\.js$/, '$1').replace('/', '_'));
        } else {
            sendText('输入错误，已退出');
            return false
        }
        sendText('请输入你修改过的新版农场任务脚本命令，例：task 6dylan6_jdpro/jd_fruit_new.js');
        var msg2 = ShuRu();
        if (msg2) {
            relrepo.push(msg2.replace(/^task\s(.+)\.js$/, '$1').replace('/', '_'));
        } else {
            sendText('输入错误，已退出');
            return false
        }
    } else if (msg == '3') {
        sendText('请输入你修改过的新版农场助力脚本命令，例：task 6dylan6_jdpro/jd_farm_help_new.js');
        var isstop = true;
        var strrepo = '';
        while (isstop) {
            sendText('请输入一条新版农场助力脚本执行命令，如果没了请输入false');
            var msg1 = ShuRu();
            if (msg1 === 'false') {
                isstop = false;
                if (strrepo.length == 0) {
                    sendText('错误，请至少输入一条，已退出');
                    return false
                }
                strrepo = strrepo.replace(/,$/, '');
                relrepo.push(strrepo);
            } else if (msg1 != false) {
                strrepo = strrepo + msg1.replace(/^task\s(.+)\.js$/, '$1').replace('/', '_') + ',';
            } else {
                sendText('输入错误，已退出');
                return false
            }
        }
        sendText('请输入你修改过的新版农场日常任务脚本命令，例：task 6dylan6_jdpro/jd_fruit_new.js');
        var isstop = true;
        var strrepo = '';
        while (isstop) {
            sendText('请输入一条新版农场日常任务脚本执行命令，如果没了请输入false');
            var msg1 = ShuRu();
            if (msg1 === 'false') {
                isstop = false;
                if (strrepo.length == 0) {
                    sendText('错误，请至少输入一条，已退出');
                    return false
                }
                strrepo = strrepo.replace(/,$/, '');
                relrepo.push(strrepo);
            } else if (msg1 != false) {
                strrepo = strrepo + msg1.replace(/^task\s(.+)\.js$/, '$1').replace('/', '_') + ',';
            } else {
                sendText('输入错误，已退出');
                return false
            }
        }
    } else {
        relrepo = repo;
    }
    bucketSet('farm', 'newRepo', JSON.stringify(relrepo));
    return true
}

function DeletPzQingLong() {
    bucketSet(tongzi, "QLS", "");
}

function GetHelpCode(cookie) {
    let shareCoderesult = false;
    try {
        request({
            url: `https://api.m.jd.com/client.action?functionId=initForFarm&body=body=%7B%22babelChannel%22%3A%22121%22%2C%22sid%22%3A%22%2C%22un_area%22%3A%22%22%2C%22version%22%3A19%2C%22channel%22%3A1%2C%22lat%22%3A%22%2C%22lng%22%3A%22%7D&appid=wh5&timestamp=${Date.now()}&client=android&clientVersion=11.4.4`,
            method: "get",
            headers: {
                "User-Agent": UserAgents(),
                "cookie": cookie,
                "origin": "https://carry.m.jd.com",
                "referer": "https://carry.m.jd.com/",
            },
            "timeOut": 10000,
        }, function (error, response, header, body) {
            Debug(body);
            try {
                if (error) {
                    notifyMasters('\n东东农场: API查询请求失败 ‼️‼️');
                    Debug(JSON.stringify(error));
                    notifyMasters('联网获取异常，请等待下次获取或者发送"管理农场",手动添加助力码，需要保证所有账号都有助力码，防止统计出错');
                    return false
                } else {
                    if (safeGet(body)) {
                        body = JSON.parse(body);
                        if (body.code == '0') {
                            notifyMasters('获取成功，助力码为' + body.farmUserPro.shareCode);
                            shareCoderesult = body.farmUserPro.shareCode;
                        } else {
                            notifyMasters('联网获取异常，请等待下次获取或者发送"管理农场",手动添加助力码，需要保证所有账号都有助力码，防止统计出错');
                            return false
                        }
                    } else {
                        return false
                    }
                }
            } catch (e) {
                Debug(e, response);
            }
        })
    } catch (err) { Debug(err) }
    return shareCoderesult
}


function safeGet(data) {
    try {
        if (typeof JSON.parse(data) == "object") {
            return true;
        }
    } catch (e) {
        Debug(e);
        notifyMasters(`京东服务器访问数据为空，请检查自身设备网络情况`);
        return false;
    }
}

function upqlenv() {
    // let farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    // if (bucketGet(tongzi, 'IsClean') === 'true') {
    //     const newarr = farmfull.filter(item => item.days !== 0);
    //     if (newarr.length !== farmfull.length) {
    //         bucketSet(tongzi, "farmpin", JSON.stringify(newarr));
    //         notifyMasters(`共删除${farmfull.length - newarr.length}个剩余天数为0的授权`);
    //     }
    // }
    // farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    // var IsSort = bucketGet("farm", "IsSort");
    // if (IsSort === 'descending') {
    //     notifyMasters('当前模式：剩余天数最多排前面');
    //     farmfull.sort((a, b) => b.days - a.days);
    // } else if (IsSort === 'ascending') {
    //     notifyMasters('当前模式：剩余天数最少排前面');
    //     farmfull.sort((a, b) => a.days - b.days);
    // }
    // bucketSet(tongzi, "farmpin", JSON.stringify(farmfull));
    // let checklogin = false;
    // bucketGet(tongzi, 'NoLoginOutSync') === 'true' ? checklogin = true : checklogin = false;
    // farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    // for (let item of farmfull) {
    //     if (typeof item.shareCode == 'undefined' || item.shareCode.length !== 32) {
    //         loggethelpcode();
    //         break
    //     }
    // }
    // farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    // if (bucketGet(tongzi, 'NoLoginOutSync') == 'true') {
    //     farmfull.forEach(item => {
    //         try {
    //             item.userpin = decodeURIComponent(item.userpin);
    //             let jnStr = bucketGet("jdNotify", encodeURIComponent(item.userpin));
    //             let jn = JSON.parse(jnStr);
    //             let cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";";
    //             item.isLogin = isLogin(cookie);
    //         } catch (e) {
    //             notifyMasters(e);
    //             notifyMasters(item.userpin + '获取出错，请检查jdNotify桶子是否有这个pin');
    //         }
    //     })
    // }
    // bucketSet(tongzi, "farmpin", JSON.stringify(farmfull));
    // checklogin == true ? notifyMasters('当前模式：付费账号ck过期不助力') : notifyMasters('当前模式：付费账号ck过期也助力');
    // let autmancode = farmfull
    //     .filter(item => {
    //         if (checklogin == true) {
    //             return item.days != 0 && item.shareCode && item.isLogin && !item.isfulled
    //         } else {
    //             return item.days != 0 && item.shareCode && !item.isfulled
    //         }
    //     })
    //     .map(item => item.shareCode).filter(item => item != 'false')
    // const autmancodelength = autmancode.length;
    // autmancode = autmancode.join('&');
    // if (autmancode == '') {
    //     autmancode = 'false';
    // }
    // var QLSName = bucketGet("farm", "QLS");
    // QLSName = QLSName.split(',')
    // if (QLSName == "" || QLSName == null) {
    //     notifyMasters("未配置青龙相关信息，请发送管理农场配置。");
    //     return;
    // }
    // for (let i = 0; i < QLSName.length; i++) {
    //     if (i > 0 && i % 3 == 0) {
    //         Debug(`第${i / 3 + 1}个青龙`);
    //         sleep(3000);
    //     }
    //     // let QLS = bucketGet("qinglong", "QLS");
    //     // QLS = JSON.parse(QLS);
    //     let ql;
    //     for (const item of QLS) {
    //         if (item.name == QLSName[i]) {
    //             ql = { host: item.host, client_id: item.client_id, client_secret: item.client_secret };
    //         }
    //     }
    //     var id = SelectQLSIsIndexOfAccount(ql, 'FRUITCODES');
    //     try {
    //         if (id != 0) {
    //             var qlupdatebody = qlupdate(autmancode, id, ql, 'FRUITCODES');
    //             var qlupdatebodyjson = JSON.parse(qlupdatebody);
    //             if (qlupdatebodyjson.code == "200") {
    //                 notifyMasters(`${QLSName[i]}更新旧版农场助力码成功，此次发送${autmancodelength}个助力码`);
    //             } else {
    //                 notifyMasters("更新失败，请联系管理员。");
    //             }
    //             //执行更新
    //         } else if (id == false || id == "false") {
    //             //否则用当前容器进行记录
    //             qltoken(ql.host, ql.client_id, ql.client_secret);
    //             var qlinsertbody = qlinsert(autmancode, ql, 'FRUITCODES');
    //             var qlinsertbodyjson = JSON.parse(qlinsertbody);
    //             if (qlinsertbodyjson.code == "200") {
    //                 notifyMasters(`${QLSName[i]}更新旧版农场助力码成功，此次发送${autmancodelength}个助力码`);
    //             } else {
    //                 notifyMasters(`${QLSName[i]}更新旧版农场助力码失败，请检查青龙配置`);
    //             }
    //         }
    //     } catch (e) {
    //         notifyMasters(e);
    //         notifyMasters(`${QLSName[i]}更新旧版农场助力码失败，请检查青龙配置`);
    //     }
    //     var IsShare = bucketGet("farm", "IsShare");
    //     if (IsShare === 'true') {
    //         notifyMasters('当前模式：多余助力分给免费账号');
    //     } else {
    //         notifyMasters('当前模式：多余助力不分给免费账号');
    //     }
    //     if (IsShare == 'true' && id != 0 && autmancode == 'false') {
    //         Debug('禁用FRUITCODES');
    //         qlalldisabled(ql.host, [id]);
    //     } else {
    //         Debug('启用FRUITCODES');
    //         qlenable(ql.host, [id]);
    //     }
    // }
    newupqlenv()
}

function newupqlenv() {
    let farmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
    if (bucketGet(tongzi, 'IsClean') === 'true') {
        const newarr = farmfull.filter(item => item.days !== 0);
        if (newarr.length !== farmfull.length) {
            bucketSet(tongzi, "newfarmpin", JSON.stringify(newarr));
            notifyMasters(`共删除${farmfull.length - newarr.length}个剩余天数为0的授权`);
        }
    }
    farmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
    var IsSort = bucketGet("farm", "IsSort");
    if (IsSort === 'descending') {
        sendText('当前模式：剩余天数最多排前面')
        farmfull.sort((a, b) => b.days - a.days);
    } else if (IsSort === 'ascending') {
        sendText('当前模式：剩余天数最少排前面')
        farmfull.sort((a, b) => a.days - b.days);
    }
    bucketSet(tongzi, "newfarmpin", JSON.stringify(farmfull));
    let checklogin = false;
    bucketGet(tongzi, 'NoLoginOutSync') === 'true' ? checklogin = true : checklogin = false;
    farmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"))
    for (let item of farmfull) {
        // Debug(item.shareCode + 'item.shareCode')
        // Debug(typeof item.shareCode)
        if (typeof item.shareCode == 'undefined' || item.shareCode.length < 6) {
            newloggethelpcode();
            break
        }
    }
    farmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
    if (bucketGet(tongzi, 'NoLoginOutSync') == 'true') {
        farmfull.forEach(item => {
            try {
                item.userpin = decodeURIComponent(item.userpin);
                let jnStr = bucketGet("jdNotify", encodeURIComponent(item.userpin));
                let jn = JSON.parse(jnStr);
                let cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";";
                item.isLogin = isLogin(cookie);
            } catch (e) {
                notifyMasters(e);
                notifyMasters(item.userpin + '获取出错，请检查jdNotify桶子是否有这个pin');
            }
        })
    }
    bucketSet(tongzi, "newfarmpin", JSON.stringify(farmfull));
    checklogin == true ? sendText('当前模式：付费账号ck过期不助力') : sendText('当前模式：付费账号ck过期也助力')
    let autmancode = farmfull
        .filter(item => {
            if (checklogin == true) {
                return item.days != 0 && item.shareCode && item.isLogin && !item.isfulled
            } else {
                return item.days != 0 && item.shareCode && !item.isfulled
            }
        })
        .map(item => item.shareCode).filter(item => item != 'false')
    const autmancodelength = autmancode.length;
    autmancode = autmancode.join('&');
    if (autmancode == '') {
        autmancode = 'false';
    }
    var QLSName = bucketGet("farm", "QLS");
    QLSName = QLSName.split(',');
    if (QLSName == "" || QLSName == null) {
        notifyMasters("未配置青龙相关信息，请发送管理农场配置。");
        return;
    }
    for (let i = 0; i < QLSName.length; i++) {
        if (i > 0 && i % 3 == 0) {
            Debug(`第${i / 3 + 1}个青龙`);
            sleep(3000);
        }
        // let QLS = bucketGet("qinglong", "QLS");
        // QLS = JSON.parse(QLS);
        let ql;
        for (item of QLS) {
            if (item.name == QLSName[i]) {
                ql = { host: item.host, client_id: item.client_id, client_secret: item.client_secret };
            }
        }
        var id = SelectQLSIsIndexOfAccount(ql, 'NEWFRUITCODES');
        try {
            if (id != 0) {
                var qlupdatebody = qlupdate(autmancode, id, ql, 'NEWFRUITCODES');
                var qlupdatebodyjson = JSON.parse(qlupdatebody);
                if (qlupdatebodyjson.code == "200") {
                    notifyMasters(`${QLSName[i]}更新新版农场助力码成功，此次发送${autmancodelength}个助力码`);
                } else {
                    notifyMasters(qlupdatebody)
                    notifyMasters("更新失败，请联系管理员。");
                }
                //执行更新
            } else if (id == false || id == "false") {
                //否则用当前容器进行记录
                qltoken(ql.host, ql.client_id, ql.client_secret);
                var qlinsertbody = qlinsert(autmancode, ql, 'NEWFRUITCODES');
                var qlinsertbodyjson = JSON.parse(qlinsertbody);
                if (qlinsertbodyjson.code == "200") {
                    notifyMasters(`${QLSName[i]}更新新版农场助力码成功，此次发送${autmancodelength}个助力码`);
                } else {
                    notifyMasters(`${QLSName[i]}更新新版农场助力码失败，请检查青龙配置`);
                }
            }
        } catch (e) {
            notifyMasters(e);
            notifyMasters(`${QLSName[i]}更新新版农场助力码失败，请检查青龙配置`);
        }
        var IsShare = bucketGet("farm", "IsShare");
        if (IsShare == 'true' && id != 0 && autmancode == 'false') {
            Debug('禁用NEWFRUITCODES');
            qlalldisabled(ql.host, [id]);
        } else {
            Debug('启用NEWFRUITCODES');
            qlenable(ql.host, [id]);
        }
    }
}

function isupqlenv() {
    var QLSName = bucketGet("farm", "QLS");
    QLSName = QLSName.split(',');
    if (QLSName == "" || QLSName == null) {
        return false
    } else {
        let currentDate = new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString().slice(0, 10);
        let ResetDate = bucketGet("farm", "ResetDate");
        if (ResetDate && ResetDate != currentDate) {
            chongzhi();
        }
        bucketSet('farm', 'ResetDate', currentDate);
        totalfulled();
        upqlenv();
    }
}


function SelectQLSIsIndexOfAccount(QLS, envname) {
    try {
        // 获取令牌
        qltoken(QLS.host, QLS.client_id, QLS.client_secret);
        
        // 查询环境数据
        const qlselectbody = qlselect(QLS.host, 'envs', envname);
        const qlckjson = JSON.parse(qlselectbody);
        Debug(qlselectbody);
        
        // 查找匹配项
        const match = qlckjson.data.find(({ remarks, name }) => remarks === envname || name === envname);
        
        // 返回匹配项的ID或0
        return match ? match.id || match._id : 0;
        
    } catch (e) {
        Debug(e);
        return 0;
    }
}

function qltoken(qldizhi, qlclient_id, qlclient_secret) {
    try {
        var body = request({
            url: qldizhi + "/open/auth/token?client_id=" + qlclient_id + "&client_secret=" + qlclient_secret,
            method: "get",
        });
        var fhtoken = JSON.parse(body);
        qltokens = fhtoken.data.token;
    } catch (e) {
        qltokens = '';
    }
}

function qlselect(host, category, envname) {
    // Debug(`${host}/open/${category}?searchValue=${envname}`)
    try {
        var body = request({
            url: `${host}/open/${category}?searchValue=${envname}`,
            method: "get",
            headers: {
                "Authorization": "Bearer " + qltokens,
            }
        });
        return body;
    } catch (e) {
        Debug(e)
    }
}


function qlupdate(ck, id, QLS, envname) {
    var body = request({
        url: QLS.host + "/open/envs",
        method: "put",
        body: Object.assign(typeof id === "number" ? {
            "id": id
        } : {
            "_id": id
        }, {
            "name": envname,
            "value": ck,
            "remarks": envname,
        }),
        headers: {
            "Authorization": "Bearer " + qltokens,
        }
    });
    return body;
}

function qlinsert(ck, QLS, envname) {
    var body = request({
        url: QLS.host + "/open/envs",
        method: "post",
        body: [{
            "name": envname,
            "value": ck,
            "remarks": envname,
        }],
        headers: {
            "Authorization": "Bearer " + qltokens,
        }
    });
    return body;
}

function qldelete(id, QLS) {
    if (id == false) {
        return
    }
    var body = request({
        url: QLS.host + "/open/envs",
        method: "delete",
        body: [id],
        headers: {
            "Authorization": "Bearer " + qltokens,
        }
    });
    Debug(body);
    return body;
}

function SelectFarmItem() {
    if (nickname == "查询") {
        chaxun(userId);
    } else if (nickname == "授权") {
        if (isAdmin) {
            adminshouquan();
        } else {
            sendText("此为管理员指令！");
        }
    } else if (nickname == "统计") {
        if (isAdmin) {
            stats();
        } else {
            sendText("此为管理员指令！");
        }
    } else if (nickname == "管理") {
        if (isAdmin) {
            guanli();
        } else {
            sendText("此为管理员指令！");
        }
    } else if (nickname == '打赏') {
        var IfShouQuans = IfShouQuan();
        if (IfShouQuans == true || IfShouQuans == "true") {
            // sendText("请输入你的选择的【数字】：\n1.打赏旧版农场\n2.打赏新版农场");
            var MoRenShouQuan = bucketGet(tongzi, "MoRenShouQuan");
            MoRenShouQuan = JSON.parse(MoRenShouQuan);
            var SumUserAccountNumPrice = MoRenShouQuan.SumAtTimePrice;
            var MaxAccounts = MoRenShouQuan.MaxAccounts;
            let tongzikey = '';
            // let msg = ShuRu();
            // if (msg && msg - 1 == 0) {
            //     tongzikey = "farmpin";
            //     SumUserAccountNumPrice = MoRenShouQuan.SumAtTimePrice;
            //     MaxAccounts = MoRenShouQuan.MaxAccounts;
            // } else if (msg && msg - 1 == 1) {
                tongzikey = "newfarmpin";
                if (MoRenShouQuan.NewSumAtTimePrice) {
                    SumUserAccountNumPrice = MoRenShouQuan.NewSumAtTimePrice;
                }
                if (MoRenShouQuan.NewMaxAccounts) {
                    MaxAccounts = MoRenShouQuan.NewMaxAccounts;
                }
            // } else {
            //     sendText("输入错误，已退出");
            //     return
            // }
            sendText("请在以下选项选择您要续费的项目：\n1.新增授权账号\n2.续费授权时间");
            var XuanZe = ShuRu();

            farmfull = JSON.parse(bucketGet(tongzi, tongzikey));
            if (XuanZe == '1') {
                if (MaxAccounts <= farmfull.length) {
                    sendText(`车位已满，暂时不可上车`);
                } else {
                    let chooseid = listpin(userId);
                    if (!chooseid) {
                        sendText('输入错误，已退出！');
                        return
                    }
                    var PlayAccountNum = AccountPlayWX(SumUserAccountNumPrice, chooseid.length);
                    Debug(PlayAccountNum);
                    if (PlayAccountNum > 0) {
                        notifyMasters(`用户${userId}打赏了${PlayAccountNum}`);

                        var shuruNum = PlayAccountNum / SumUserAccountNumPrice / chooseid.length * 30;
                        chooseid.forEach(item => {
                            CaoZuoShouQuan(userId, item, shuruNum, tongzikey);
                        })
                        isupqlenv();
                    } else {
                        sendText("打赏金额异常，已退出");
                    }
                }
            } else if (XuanZe == '2') {
                let chooseid = listpin(userId);
                if (!chooseid) {
                    sendText('输入错误，已退出！');
                    return
                }
                var PlayAccountNum = AccountPlayWX(SumUserAccountNumPrice, chooseid.length);
                Debug(PlayAccountNum);
                if (PlayAccountNum > 0) {
                    notifyMasters(`用户${userId}打赏了${PlayAccountNum}`);

                    var shuruNum = PlayAccountNum / SumUserAccountNumPrice / chooseid.length * 30;
                    chooseid.forEach(item => {
                        CaoZuoShouQuan(userId, item, shuruNum, tongzikey);
                    })
                    isupqlenv();
                } else {
                    sendText("打赏金额异常，已退出");
                }
            } else {
                sendText("输入错误，已退出");
                return
            }
        } else {
            sendText("未开启授权系统，请联系管理员。");
        }
    } else if (nickname == '释放打赏') {
        if (isAdmin) {
            bucketSet(tongzi, "IsUserUseDaShang", "true");
            sendText("已释放，用户可以正常打赏了");
        } else {
            sendText("此为管理员指令！");
        }
    } else if (nickname == '删除授权') {
        if (isAdmin) {
            deleteshouquan();
        } else {
            sendText("此为管理员指令！");
        }
    } else if (nickname == '同步') {
        if (isAdmin) {
            var QLSName = bucketGet("farm", "QLS");
            QLSName = QLSName.split(',');
            if (QLSName == "" || QLSName == null) {
                notifyMasters("未配置青龙相关信息，请发送管理农场配置。");
                return;
            } else {
                isupqlenv();
            }
        } else {
            sendText("此为管理员指令！");
        }
    } else if (nickname == '清理过期') {
        if (isAdmin) {
            farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
            const newarr = farmfull.filter(item => item.days !== 0);
            bucketSet(tongzi, "farmpin", JSON.stringify(newarr));
            sendText(`共删除${farmfull.length - newarr.length}个剩余天数为0的授权`);
        } else {
            sendText("此为管理员指令！");
        }
    } else if (nickname == '重置') {
        if (isAdmin) {
            sendText('此操作将会把所有账号改为未助力，是否继续？（输入y/n）');
            var msg = ShuRu();
            if (msg == 'y') {
                let farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
                farmfull.forEach(item => {
                    item.isfulled = 0;
                });
                bucketSet(tongzi, "farmpin", JSON.stringify(farmfull));
                let newfarmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
                newfarmfull.forEach(item => {
                    item.isfulled = 0;
                });
                bucketSet(tongzi, "newfarmpin", JSON.stringify(newfarmfull));
                const tomorrowDate = new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString().slice(0, 10);
                bucketSet('farm', 'ResetDate', tomorrowDate);
                sendText('已把所有账号改为未助力！');
            } else {
                sendText('已退出。');
            }
        } else {
            sendText("此为管理员指令！");
        }
    } else if (nickname == '浇水') {
        var waterscript = bucketGet(tongzi, "WaterScript");
        if (isAdmin) {
            if (waterscript == "" || waterscript == null) {
                sendText('请输入你的农场任务脚本命令(只能写一个)，例：task 6dylan6_jdpro/jd_fruit.js');
                var msg2 = ShuRu();
                if (msg2) {
                    let script = msg2.replace(/^task\s(.+)\.js$/, '$1') + '.js';
                    bucketSet('farm', 'WaterScript', script);
                    sendText('配置成功');
                } else {
                    sendText('输入错误，已退出');
                }
                return;
            }
            runwater();
            return
        } else if (waterscript == "" || waterscript == null) {
            sendText('此功能未配置，请联系管理员');
            notifyMasters('未配置浇水农场，请发送"浇水农场"配置。');
            return;
        } else {
            runwater();
        }
    } else if (nickname == '测试') {
        if (isAdmin) {
            ceshi();
        } else {
            sendText("此为管理员指令！");
        }
    } else if (!GetContent()) {
        let now = new Date();
        let tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
        let diff = tomorrow - now;
        Debug(diff);
        // 判断差值是否小于3分钟（180000毫秒）
        if (diff < 180000) {
            totalfulled();
            // newtotalfulled()
            chongzhi();
        } else {
            var QLSName = bucketGet("farm", "QLS");
            QLSName = QLSName.split(',');
            if (QLSName == "" || QLSName == null) {
                return false
            } else {
                var IsOnlyPay = bucketGet("farm", "IsOnlyPay");
                if (IsOnlyPay === 'true') {
                    notifyMasters("定时执行农场任务开始");
                    var farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
                    let paypin = farmfull.map(item => encodeURIComponent(item.userpin));
                    Debug(paypin);
                    ImmediateWater(paypin, false);
                    sleep(6000);
                    var newWaterScript = bucketGet(tongzi, "newWaterScript");
                    if (newWaterScript == "" || newWaterScript == null) {
                        notifyMasters('新版农场只跑付费账号未配置，请发送“管理农场”选择14，进行配置');
                    } else {
                        var newfarmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
                        let newpaypin = newfarmfull.map(item => encodeURIComponent(item.userpin));
                        Debug(newpaypin);
                        newImmediateWater(newpaypin, false);
                    }
                }
                notifyMasters("定时同步农场开始");
                isupqlenv();
            }
        }
    }
}

function runwater() {
    let currentpin = [];
    var farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    farmfull.forEach(item => {
        if (item.userid == userId) currentpin.push(item.userpin);
    })
    currentpin = currentpin.map(item => encodeURIComponent(item));

    var NoWaterPin = bucketGet("farm", "NoWaterPin");
    NoWaterPin = NoWaterPin === '' ? [] : NoWaterPin.split('&');

    var msg1 = listpin(userId);
    if (msg1 == false) {
        return
    }
    sendText('选中的账号是否要浇水？\n1.开启浇水\n2.关闭浇水');
    var msg2 = ShuRu();
    if (msg2 === '1') {
        const commonElements = currentpin.filter(item => msg1.includes(item));
        sendText('请选择浇水方式：\n1.后续一直浇水\n2.仅本次浇水，后续不浇水(仅限付费账号)');
        var msg3 = ShuRu();
        if (msg3 == '1') {
            NoWaterPin = NoWaterPin.filter(item => !msg1.includes(item));
            sendText('修改成功');
        } else if (msg3 == '2') {
            ImmediateWater(commonElements, true);
        }
    } else if (msg2 === '2') {
        NoWaterPin = [...new Set(NoWaterPin.concat(msg1))];
        sendText('修改成功');
    }

    // if (NoWaterPin.length !== 0) {
    const NoWaterPinLength = NoWaterPin.length;
    // NoWaterPin = NoWaterPin.map(item => encodeURIComponent(item));

    var iswater = bucketGet("farm", "IsWater");
    if (NoWaterPin.length !== 0 && iswater == 'NO_WATER') {
        var QLSName = bucketGet("farm", "QLS");
        QLSName = QLSName.split(',');
        if (QLSName == "" || QLSName == null) {
            notifyMasters("未配置青龙相关信息，请发送管理农场配置。");
            return;
        }
        for (let i = 0; i < QLSName.length; i++) {
            if (i > 0 && i % 3 == 0) {
                Debug(`第${i / 3 + 1}个青龙`);
                sleep(3000);
            }
            // let QLS = bucketGet("qinglong", "QLS");
            // QLS = JSON.parse(QLS);
            let ql;
            for (const item of QLS) {
                if (item.name == QLSName[i]) {
                    ql = { host: item.host, client_id: item.client_id, client_secret: item.client_secret };
                    var id = SelectQLSIsIndexOfAccount(ql, 'NO_WATER');
                    qldelete(id, ql);
                }
            }
        }
        bucketSet("farm", "IsWater", 'true');
    }

    NoWaterPin = NoWaterPin.join('&');
    var QLSName = bucketGet("farm", "QLS");
    QLSName = QLSName.split(',');
    if (QLSName == "" || QLSName == null) {
        notifyMasters("未配置青龙相关信息，请发送管理农场配置。");
        return;
    }
    for (let i = 0; i < QLSName.length; i++) {
        if (i > 0 && i % 3 == 0) {
            Debug(`第${i / 3 + 1}个青龙`);
            sleep(3000);
        }
        // let QLS = bucketGet("qinglong", "QLS");
        // QLS = JSON.parse(QLS);
        let ql;
        for (const item of QLS) {
            if (item.name == QLSName[i]) {
                ql = { host: item.host, client_id: item.client_id, client_secret: item.client_secret };
            }
        }
        var id = SelectQLSIsIndexOfAccount(ql, 'FRUIT_PIN');
        if (NoWaterPin.length == 0 && id != 0) {
            qldelete(id, ql);
            notifyMasters(`${QLSName[i]}删除所有不浇水pin成功，建议重启青龙`);
        } else {
            try {
                if (id != 0) {
                    var qlupdatebody = qlupdate(NoWaterPin, id, ql, 'FRUIT_PIN');
                    var qlupdatebodyjson = JSON.parse(qlupdatebody);
                    if (qlupdatebodyjson.code == "200") {
                        notifyMasters(`${QLSName[i]}更新不浇水pin成功，此次发送${NoWaterPinLength}个pin`);
                    } else {
                        notifyMasters("更新失败，请联系管理员。");
                    }
                    //执行更新
                } else if (id == false || id == "false") {
                    //否则用当前容器进行记录
                    qltoken(ql.host, ql.client_id, ql.client_secret);
                    var qlinsertbody = qlinsert(NoWaterPin, ql, 'FRUIT_PIN');
                    var qlinsertbodyjson = JSON.parse(qlinsertbody);
                    if (qlinsertbodyjson.code == "200") {
                        notifyMasters(`${QLSName[i]}更新不浇水pin成功，此次发送${NoWaterPinLength}个pin`);
                    } else {
                        notifyMasters(`${QLSName[i]}更新不浇水pin失败，请检查青龙配置`);
                    }
                }
            } catch (e) {
                notifyMasters(e);
                notifyMasters(`${QLSName[i]}更新不浇水pin失败，请检查青龙配置`);
            }
        }
    }
    // }

    bucketSet(tongzi, "NoWaterPin", NoWaterPin);
}

function ImmediateWater(ckpin, tag) {
    // var isrunning = bucketGet(tongzi, "IsRunning");
    // if (isrunning === 'true') {
    //     sendText('别人正在操作，请过一会再试')
    //     return
    // }
    // ckpin = ckpin.map(item => encodeURIComponent(item));
    Debug(ckpin)
    var QLSName = bucketGet(tongzi, "QLS");
    QLSName = QLSName.split(',');
    if (QLSName == "" || QLSName == null) {
        notifyMasters("未配置青龙相关信息。");
        return;
    }
    var waterscript = bucketGet(tongzi, "WaterScript");
    // let repo = JSON.parse(bucketGet(tongzi, "Repo"))
    // let statename = repo[1].split(',')

    let alreadyid = [];
    for (let i = 0; i < QLSName.length; i++) {
        if (i > 0 && i % 3 == 0) {
            Debug(`第${i / 3 + 1}个青龙`);
            sleep(3000);
        }
        // let QLS = bucketGet("qinglong", "QLS");
        // QLS = JSON.parse(QLS);
        let ql;
        for (let item of QLS) {
            if (item.name == QLSName[i]) {
                ql = { host: item.host, client_id: item.client_id, client_secret: item.client_secret };
            }
        }
        var qlck = SelectQLSCK(ql, 'JD_COOKIE');

        var cronid = SelectQLSCron(ql, waterscript);
        let tongzipin = ckpin;
        try {
            if (cronid.length !== 0) {
                let disabledck = qlck.filter(item => item.status == 1).map(item => item.id);
                let allckid = qlck.map(item => item.id);
                let enableckid = allckid.filter(item => !disabledck.includes(item));
                let currentckid = qlck.filter(item => tongzipin.includes(item.ckpin) && !alreadyid.includes(item.ckpin)).map(item => item.id);
                let thisalreadyid = qlck.filter(item => tongzipin.includes(item.ckpin)).map(item => item.ckpin);
                alreadyid = alreadyid.concat(thisalreadyid);
                if (currentckid.length == 0) {
                    break
                }
                let subArrays = [currentckid];
                // for (let i = 0; i < currentckid.length; i += 10) {
                //     let subArray = currentckid.slice(i, i + 10);
                //     subArrays.push(subArray);
                // }
                // Debug(subArrays)
                sendText(`总共需要运行${tongzipin.length}个账号`);
                let currentckindex = 0;
                for (let item2 of subArrays) {
                    // bucketSet(tongzi, "IsRunning", 'true');
                    // Debug(item2)
                    let otherckid = qlck.filter(item => !item2.includes(item.id)).map(item => item.id);
                    var id = SelectQLSIsIndexOfAccount(ql, 'FRUIT_PIN');
                    if (tag && id != 0) {
                        qlalldisabled(ql.host, [id]);
                        var iswater = bucketGet("farm", "IsWater");
                        if (iswater == 'NO_WATER' || iswater == 'DO_TEN_WATER_AGAIN') {
                            var iswaterid = SelectQLSIsIndexOfAccount(ql, iswater);
                            if (id != 0) qlalldisabled(ql.host, [iswaterid]);
                        }
                    }
                    qlalldisabled(ql.host, otherckid);
                    qlcronrun(ql.host, cronid);
                    sendText('检索中...');
                    sleep(4500);
                    tag ? sendText(`旧农场本次运行${item2.length}个账号`) : notifyMasters(`旧农场本次运行${item2.length}个账号`);
                    sleep(4500);
                    qlenable(ql.host, enableckid);
                    if (tag) {
                        if (id != 0) {
                            qlenable(ql.host, [id]);
                        }
                        var iswater = bucketGet("farm", "IsWater");
                        if (iswater == 'NO_WATER' || iswater == 'DO_TEN_WATER_AGAIN') {
                            var iswaterid = SelectQLSIsIndexOfAccount(ql, iswater);
                            if (id != 0) {
                                qlenable(ql.host, [iswaterid]);
                            }
                        }
                        currentckindex = checkprogress(ql.host, cronid[0], currentckindex);
                    }
                }
            } else if (cronid) {
                sendText('别人正在操作，请过一会再试');
            } else if (qlck) {
                notifyMasters(`${QLSName[i]}获取任务出错`);
                // bucketSet(tongzi, "IsRunning", 'false');
            }
        } catch (e) {
            notifyMasters(e);
            notifyMasters(`${QLSName[i]}出错`);
            // qlenable(QLS.host, enableckid)
            // bucketSet(tongzi, "IsRunning", 'false');
        }
    }
}

function newImmediateWater(ckpin, tag) {
    Debug(ckpin);
    var QLSName = bucketGet(tongzi, "QLS");
    QLSName = QLSName.split(',');
    if (QLSName == "" || QLSName == null) {
        notifyMasters("未配置青龙相关信息。");
        return;
    }
    var waterscript = bucketGet(tongzi, "newWaterScript");
    // let repo = JSON.parse(bucketGet(tongzi, "Repo"))
    // let statename = repo[1].split(',')

    let alreadyid = [];
    for (let i = 0; i < QLSName.length; i++) {
        if (i > 0 && i % 3 == 0) {
            Debug(`第${i / 3 + 1}个青龙`);
            sleep(3000);
        }
        // let QLS = bucketGet("qinglong", "QLS");
        // QLS = JSON.parse(QLS);
        let ql;
        for (let item of QLS) {
            if (item.name == QLSName[i]) {
                ql = { host: item.host, client_id: item.client_id, client_secret: item.client_secret };
            }
        }
        var qlck = SelectQLSCK(ql, 'JD_COOKIE');

        var cronid = SelectQLSCron(ql, waterscript);
        let tongzipin = ckpin;
        try {
            if (cronid.length !== 0) {
                let disabledck = qlck.filter(item => item.status == 1).map(item => item.id);
                let allckid = qlck.map(item => item.id);
                let enableckid = allckid.filter(item => !disabledck.includes(item));
                let currentckid = qlck.filter(item => tongzipin.includes(item.ckpin) && !alreadyid.includes(item.ckpin)).map(item => item.id);
                let thisalreadyid = qlck.filter(item => tongzipin.includes(item.ckpin)).map(item => item.ckpin);
                alreadyid = alreadyid.concat(thisalreadyid);
                if (currentckid.length == 0) {
                    break
                }
                let subArrays = [currentckid];
                sendText(`总共需要运行${tongzipin.length}个账号`);
                for (let item2 of subArrays) {
                    let otherckid = qlck.filter(item => !item2.includes(item.id)).map(item => item.id);
                    qlalldisabled(ql.host, otherckid);
                    qlcronrun(ql.host, cronid);
                    sendText('检索中...');
                    sleep(4500);
                    tag ? sendText(`新农场本次运行${item2.length}个账号`) : notifyMasters(`新农场本次运行${item2.length}个账号`);
                    sleep(4500);
                    qlenable(ql.host, enableckid);
                }
            } else if (cronid) {
                sendText('别人正在操作，请过一会再试');
            } else if (qlck) {
                notifyMasters(`${QLSName[i]}获取任务出错`);
                // bucketSet(tongzi, "IsRunning", 'false');
            }
        } catch (e) {
            notifyMasters(e);
            notifyMasters(`${QLSName[i]}出错`);
            // qlenable(QLS.host, enableckid)
            // bucketSet(tongzi, "IsRunning", 'false');
        }
    }
}

function SelectQLSCK(QLS, envname) {
    var IsTrueAccount = 0;
    try {
        qltoken(QLS.host, QLS.client_id, QLS.client_secret);
        var qlselectbody = qlselect(QLS.host, 'envs', envname);
        var qlckjson = JSON.parse(qlselectbody);
        let qlck = [];
        if (qlckjson && qlckjson.data != "") {
            for (var key in qlckjson.data) {
                if (qlckjson.data[key].name == envname) {
                    IsTrueAccount++;
                    let qlckid = qlckjson.data[key].id || qlckjson.data[key]._id;
                    let ckpin = qlckjson.data[key].value.match(/pt_pin=([^;]+)/)?.[1] || '';
                    qlck.push({
                        id: qlckid,
                        status: qlckjson.data[key].status,
                        ckpin: ckpin
                    })
                }
            }
            return qlck
        }
        if (IsTrueAccount == 0) {
            return false
        }
    } catch (e) {
        Debug(e);
        return false
    }
}

function checkprogress(host, cronid, currentckindex) {
    // let logtime = qllogs(host, '6dylan6_jdpro_jd_comment.js')
    let currentlog = [];
    let alreadylog = [];
    let currentsend = [];
    let isdone = false;
    while (!isdone) {
        currentlog = cronlog(host, cronid);
        if (arraysAreEqual(currentlog, alreadylog)) {
            sleep(6000);
        }
        currentsend = currentlog.slice(alreadylog.length, currentlog.length);
        // Debug(currentsend)
        for (let i of currentsend) {
            if (!i.includes('执行结束...')) {
                if (i.includes('【京东账号')) {
                    // const pin = i.match(/【京东账号\d+】(.+?)\*/)[1];
                    // sendText(`账号${++currentckindex}【${pin}】`)
                    sendText(i.replace(/-/g, ''));
                } else {
                    sendText(i)
                }
                sleep(2000);
            } else {
                sendText('浇水完成！');
                isdone = true;
                // bucketSet(tongzi, "IsRunning", 'false');
                return currentckindex
            }
        }
        alreadylog = currentlog;
    }
    return currentckindex
}

function cronlog(host, cronid) {
    var body = request({
        url: `${host}/open/crons/${cronid}/log?t=${Date.now()}`,
        method: "GET",
        headers: {
            "Authorization": "Bearer " + qltokens,
        }
    });
    // Debug(body)
    let totalarr = JSON.parse(body);
    // Debug(totalarr)
    totalarr = totalarr.data.split('\n');
    totalarr = totalarr.filter(item => {
        // Debug(item)
        let cleanlog = item.includes('【京东账号')
            || item.includes('已可领取')
            // || (item.includes('浇水') && !item.includes('export'))
            || item.includes('水果名称')
            || item.includes('已兑换水果')
            || item.includes('今日共浇水')
            || item.includes('剩余水滴')
            || item.includes('水果进度')
            || item.includes('预测')
            || item.includes('执行结束...')
        return cleanlog
    })
    return totalarr
}

function arraysAreEqual(array1, array2) {
    if (array1.length !== array2.length) {
        return false;
    }
    return array1.every((element, index) => element === array2[index]);
}

function SelectQLSCron(QLS, envname) {
    Debug(envname);
    var IsTrueAccount = 0;
    try {
        // qltoken(QLS.host, QLS.client_id, QLS.client_secret)
        var qlselectbody = qlselect(QLS.host, 'crons', envname);
        // Debug('SelectQLSCron()' + qlselectbody)
        var qlckjson = JSON.parse(qlselectbody);
        let cronid = [];
        if (qlckjson && qlckjson.data != "") {
            if (qlckjson.data.data) {
                for (let key in qlckjson.data.data) {
                    if (qlckjson.data.data[key].status == 0) {
                        return []
                    }
                    if (qlckjson.data.data[key].command.includes(`task ${envname}`)) {
                        IsTrueAccount++;
                        cronid.push(qlckjson.data.data[key].id);
                        return cronid
                    }
                }
            } else {
                for (let item of qlckjson.data) {
                    if (item.status == 0) {
                        return []
                    }
                    if (item.command.includes(`task ${envname}`)) {
                        IsTrueAccount++;
                        item.id ? cronid.push(item.id) : cronid.push(item['_id']);
                        return cronid
                    }
                }
            }
        }
        if (IsTrueAccount == 0) {
            return false
        }
    } catch (e) {
        Debug(e)
        return false
    }
}

function qlalldisabled(host, ckid) {
    var body = request({
        url: host + "/open/envs/disable",
        method: "put",
        headers: {
            "Authorization": "Bearer " + qltokens,
        },
        body: ckid
    });
    Debug('qlalldisabled()' + body);
}

function qlcronrun(host, cronid) {
    Debug(cronid);
    var body = request({
        url: host + "/open/crons/run",
        method: "put",
        headers: {
            "Authorization": "Bearer " + qltokens,
        },
        body: cronid
    });
    Debug('qlcronrun()' + body);
}

function qlenable(host, ckid) {
    var body = request({
        url: host + "/open/envs/enable",
        method: "put",
        headers: {
            "Authorization": "Bearer " + qltokens,
        },
        body: ckid
    });
    Debug('qlenable()' + body);
}

function totalfulled() {
    // var QLSName = bucketGet("farm", "QLS");
    // let repo = bucketGet(tongzi, "Repo");
    // QLSName = QLSName.split(',');
    // if (QLSName == "" || QLSName == null) {
    //     notifyMasters("未配置青龙容器相关信息，请发送“管理农场”，修改青龙配置。");
    //     return;
    // } else if (repo == "" || repo == null) {
    //     notifyMasters("未配置青龙旧版脚本仓库相关信息，请发送“管理农场”，修改青龙配置。");
    //     return;
    // }
    // let fullpin = [];
    // let water = [];
    // for (let i = 0; i < QLSName.length; i++) {
    //     if (i > 0 && i % 3 == 0) {
    //         Debug(`第${i / 3 + 1}个青龙`);
    //         sleep(3000);
    //     }
    //     // let QLS = bucketGet("qinglong", "QLS");
    //     // QLS = JSON.parse(QLS);
    //     let ql;
    //     for (const item of QLS) {
    //         if (item.name == QLSName[i]) {
    //             ql = { host: item.host, client_id: item.client_id, client_secret: item.client_secret };
    //         }
    //     }
    //     qltoken(ql.host, ql.client_id, ql.client_secret);
    //     fullpin = fullpin.concat(qllogstofull(ql.host));
    //     water = water.concat(getstate(ql.host));
    // }
    // fullpin = [...new Set(fullpin)];
    // Debug(JSON.stringify(fullpin));

    // let latestWater = {};
    // for (let i = 0; i < water.length; i++) {
    //     const item = water[i];
    //     const pin = item.pin;
    //     const time = item.time;

    //     if (item.progress !== undefined) {
    //         if (latestWater[pin] === undefined || time > latestWater[pin].time) {
    //             latestWater[pin] = { time, item };
    //         }
    //     }
    // }
    // let truewater = Object.values(latestWater).map((entry) => entry.item);

    // let farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    // farmfull.forEach(item => {
    //     for (let item2 of truewater) {
    //         if (item2.pin == item.userpin) {
    //             item.progress = item2.progress;
    //         }
    //     }
    // })
    // Debug(JSON.stringify(truewater));
    // truewater.forEach(item => {
    //     if (item.progress == '100%' && bucketGet("farm", "IsNotify") == 'true') {
    //         const pinfrom = ["qq", 'qb', 'wx', 'wb', 'fake'];
    //         for (let item3 of pinfrom) {
    //             try {
    //                 if (bucketGet(`pin${item3.toUpperCase()}`, item.pin)) {
    //                     Debug(bucketGet(`pin${item3.toUpperCase()}`, item.pin));
    //                     push(
    //                         {
    //                             imType: item3,
    //                             userID: bucketGet(`pin${item3.toUpperCase()}`, item.pin),
    //                             groupCode: groupCode,
    //                             content: `【首页-我的-东东农场-左上角“回旧版”】\n【账号】${item.pin}\n【提醒】旧版农场水果进度100%，已可领取`,
    //                         }
    //                     )
    //                     // break
    //                 }
    //             } catch (e) {
    //                 Debug(e);
    //             }
    //         }
    //     } else if (item.progress == '0%' && bucketGet("farm", "IsNotify") == 'true') {
    //         const pinfrom = ["qq", 'qb', 'wx', 'wb', 'fake']
    //         for (let item3 of pinfrom) {
    //             try {
    //                 if (bucketGet(`pin${item3.toUpperCase()}`, item.pin)) {
    //                     Debug(bucketGet(`pin${item3.toUpperCase()}`, item.pin))
    //                     push(
    //                         {
    //                             imType: item3,
    //                             userID: bucketGet(`pin${item3.toUpperCase()}`, item.pin),
    //                             groupCode: groupCode,
    //                             content: `【首页-我的-东东农场-左上角“回旧版”】\n【账号】${item.pin}\n【提醒】旧版农场您忘了种植新的水果`,
    //                         }
    //                     )
    //                     // break
    //                 }
    //             } catch (e) {
    //                 Debug(e);
    //             }
    //         }
    //     }
    //     for (let item2 of farmfull) {
    //         if (item.pin == item2.userpin) {
    //             if (item2.progress) {
    //                 item2.progress = item.progress;
    //             }
    //             if (item.currentwater) {
    //                 item2.water = item.currentwater;
    //             }
    //             break
    //         }
    //     }
    // })
    // bucketSet(tongzi, "farmpin", JSON.stringify(farmfull));
    // changeisfull(fullpin, "farmpin");
    newtotalfulled();
}

function newtotalfulled() {
    var QLSName = bucketGet("farm", "QLS");
    let repo = JSON.parse(bucketGet(tongzi, "newRepo"));
    QLSName = QLSName.split(',');
    if (QLSName == "" || QLSName == null) {
        notifyMasters("未配置青龙容器相关信息，请发送“管理农场”，修改青龙配置。");
        return;
    } else if (repo == "" || repo == null || repo.length == 0) {
        notifyMasters("未配置青龙新版脚本仓库相关信息，请发送“管理农场”，修改青龙配置。");
        return;
    }
    let fullpin = [];
    let water = [];
    for (let i = 0; i < QLSName.length; i++) {
        if (i > 0 && i % 3 == 0) {
            Debug(`第${i / 3 + 1}个青龙`);
            sleep(3000);
        }
        // let QLS = bucketGet("qinglong", "QLS");
        // QLS = JSON.parse(QLS);
        let ql;
        for (const item of QLS) {
            if (item.name == QLSName[i]) {
                ql = { host: item.host, client_id: item.client_id, client_secret: item.client_secret };
            }
        }
        qltoken(ql.host, ql.client_id, ql.client_secret);
        fullpin = fullpin.concat(newqllogstofull(ql.host));
        water = water.concat(newgetstate(ql.host));
    }
    fullpin = [...new Set(fullpin)];
    Debug(JSON.stringify(fullpin));

    let latestWater = {};
    for (let i = 0; i < water.length; i++) {
        const item = water[i];
        const pin = item.pin;
        const time = item.time;

        if (item.progress !== undefined) {
            if (latestWater[pin] === undefined || time > latestWater[pin].time) {
                latestWater[pin] = { time, item };
            }
        }
    }
    let truewater = Object.values(latestWater).map((entry) => entry.item);

    let farmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
    farmfull.forEach(item => {
        for (let item2 of truewater) {
            if (item2.pin == item.userpin) {
                item.progress = item2.progress;
            }
        }
    })
    // Debug(JSON.stringify(truewater));
    truewater.forEach(item => {
        let progress = item.progress ? item.progress.slice(-4) : 0
        if (progress == '100%' && bucketGet("farm", "IsNotify") == 'true') {
            const pinfrom = ["qq", 'qb', 'wx', 'wb', 'fake']
            for (let item3 of pinfrom) {
                try {
                    if (bucketGet(`pin${item3.toUpperCase()}`, item.pin)) {
                        Debug(bucketGet(`pin${item3.toUpperCase()}`, item.pin))
                        push(
                            {
                                imType: item3,
                                userID: bucketGet(`pin${item3.toUpperCase()}`, item.pin),
                                groupCode: groupCode,
                                content: `【首页-我的-东东农场-左上角“记录”】\n【账号】${item.pin}\n【提醒】新版农场水果进度100%，已可领取`,
                            }
                        )
                        // break
                    }
                } catch (e) {
                    Debug(e)
                }
            }
        } else if (progress == '0%' && bucketGet("farm", "IsNotify") == 'true') {
            const pinfrom = ["qq", 'qb', 'wx', 'wb', 'fake'];
            for (let item3 of pinfrom) {
                try {
                    if (bucketGet(`pin${item3.toUpperCase()}`, item.pin)) {
                        Debug(bucketGet(`pin${item3.toUpperCase()}`, item.pin));
                        push(
                            {
                                imType: item3,
                                userID: bucketGet(`pin${item3.toUpperCase()}`, item.pin),
                                groupCode: groupCode,
                                content: `【首页-我的-东东农场-左上角“记录”】\n【账号】${item.pin}\n【提醒】新版农场您忘了种植新的水果`,
                            }
                        )
                        // break
                    }
                } catch (e) {
                    Debug(e)
                }
            }
        }
        for (let item2 of farmfull) {
            if (item.pin == item2.userpin) {
                if (item2.progress) {
                    item2.progress = item.progress;
                }
                if (item.currentwater) {
                    item2.water = item.currentwater;
                }
                break
            }
        }
    })
    bucketSet(tongzi, "newfarmpin", JSON.stringify(farmfull));
    changeisfull(fullpin, 'newfarmpin');
}

function qllogs(host, logname) {
    let logtime = [];
    try {
        var body = request({
            url: host + "/open/logs?t=" + Date.now(),
            method: "GET",
            headers: {
                "Authorization": "Bearer " + qltokens,
            }
        });
        body = JSON.parse(body);
        let today = new Date();
        let year = today.getFullYear();
        let month = String(today.getMonth() + 1).padStart(2, '0');
        let day = String(today.getDate()).padStart(2, '0');

        let formattedDate = `${year}-${month}-${day}`;
        if (body.dirs) {
            for (let item of body.dirs) {
                if (item.name === logname) {
                    logtime = item.files.filter(item2 => item2.startsWith(formattedDate)).map(item3 => logname + '/' + item3 + '?');
                    Debug(logtime);
                    break;
                }
            }
        } else if (body.data) {
            for (let item of body.data) {
                let optimizedStr = item.title.split('_').slice(0, -1).join('_');
                if (optimizedStr === logname) {
                    item.children.forEach(item2 => {
                        if (item2.title.startsWith(formattedDate)) {
                            logtime.push(`${item2.title}?path=${item2.parent}&`);
                        }
                    })
                    Debug(logtime);
                    break;
                }
            }
        }
        return logtime
    } catch (e) {
        Debug('qllogs()' + e);
        notifyMasters('qllogs()' + e);
        notifyMasters('获取日志出错，请检查插件青龙配置');
        return logtime
    }
}

function qllogstofull(host) {
    let fullpin = [];
    let repo = JSON.parse(bucketGet(tongzi, "Repo"));
    let helpname = repo[0].split(',');
    try {
        let logtime = [];
        for (let jsname of helpname) {
            logtime = logtime.concat(qllogs(host, jsname));
        }
        for (let item of logtime) {
            var body = request({
                url: `${host}/open/logs/${item}t=${Date.now()}`,
                method: "GET",
                headers: {
                    "Authorization": "Bearer " + qltokens,
                }
            });
            let totalarr = JSON.parse(body)
            totalarr = totalarr.data.split('\n');
            totalarr.forEach((item2, index) => {
                if (item2.includes('已满')) {
                    for (let i = index - 1; i > 0; i--) {
                        if (totalarr[i].includes('助力')) {
                            const res = totalarr[i].substring(totalarr[i].length - 32);
                            fullpin.push(res);
                            break
                        }
                    }
                }
            });
        }
        return fullpin
    } catch (e) {
        Debug('qllogstofull' + e);
        sendText('获取今日已助力出错');
        return fullpin
    }
}

function newqllogstofull(host) {
    let fullpin = [];
    let newrepo = JSON.parse(bucketGet(tongzi, "newRepo"));
    let helpname = newrepo[0].split(',');
    try {
        let logtime = [];
        for (let jsname of helpname) {
            logtime = logtime.concat(qllogs(host, jsname));
        }
        for (let item of logtime) {
            var body = request({
                url: `${host}/open/logs/${item}t=${Date.now()}`,
                method: "GET",
                headers: {
                    "Authorization": "Bearer " + qltokens,
                }
            });
            let totalarr = JSON.parse(body);
            totalarr = totalarr.data.split('\n');
            totalarr.forEach((item2, index) => {
                if (item2.includes('已满') || item2.includes('已到助力目标数')) {
                    for (let i = index - 1; i > 0; i--) {
                        if (totalarr[i].includes('去助力:')) {
                            Debug(totalarr[i]);
                            // const regex = /去助力\s*:?\s*([^\s]+)/;
                            // const match = totalarr[i].match(regex);
                            // Debug(match);
                            // const res = match ? match[1] : '';

                            const res = totalarr[i].split(':')[1];
                            Debug(res);
                            if (res) {
                                fullpin.push(res);
                            }
                            break
                        }
                    }
                }
            });
        }
        return fullpin
    } catch (e) {
        Debug('newqllogstofull' + e);
        sendText('获取新农场今日已助力出错' + e);
        return fullpin
    }
}

function getstate(host) {
    let water = [];
    let repo = JSON.parse(bucketGet(tongzi, "Repo"));
    let statename = repo[1].split(',');
    try {
        let logtime = [];
        for (let jsname of statename) {
            logtime = logtime.concat(qllogs(host, jsname));
        }
        for (let item of logtime) {
            var body = request({
                url: `${host}/open/logs/${item}t=${Date.now()}`,
                method: "GET",
                headers: {
                    "Authorization": "Bearer " + qltokens,
                }
            });
            let totalarr = JSON.parse(body);
            let cutt = totalarr.data.split('==============📣系统通知📣==============');
            // Debug(cutt);
            cutt.forEach(cuttitem => {
                let system = cuttitem.split('------------------【京东账号')[0];
                if (!system.includes('【提示】cookie已失效')) {
                    let info = system.split('\n');
                    let waterpin;
                    let waterprogress;
                    let currentwater;
                    let time = item.match(/(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})/)[1];
                    for (const each of Object.values(info)) {
                        if (each == '') {
                            continue;
                        }
                        if (/\【京东账号/.test(each)) {
                            waterpin = /【.+?】(.+)/.exec(each)[1].replace(/\s/g, '');
                        }
                        if (/种植进度/.test(each)) {
                            waterprogress = each.split('】')[1];
                        }
                        if (/水果进度/.test(each)) {
                            waterprogress = /\d+\.\d+%/.exec(each)[0];
                            waterprogress = waterprogress == "100.00%" ? "100%" : waterprogress;
                        }
                        if (/已种成|已可领取/.test(each)) {
                            waterprogress = "100%";
                        }
                        if (/忘了/.test(each)) {
                            waterprogress = "0%";
                        }
                        if (/剩余水滴/.test(each)) {
                            try {
                                currentwater = /\d+/.exec(each)[0];
                            } catch (e) {
                                // console.log(error);
                            }
                        }
                    }
                    water.push({
                        pin: waterpin,
                        progress: waterprogress,
                        currentwater,
                        time
                    });
                }
            });
        }
        water.shift()
        // Debug(JSON.stringify(water));
        return water
    } catch (e) {
        Debug('getstate()' + e);
        sendText('获取水果进度出错:' + e);
        return water
    }
}

function newgetstate(host) {
    let water = [];
    let newrepo = JSON.parse(bucketGet(tongzi, "newRepo"));
    let statename = newrepo[1].split(',');
    try {
        let logtime = [];
        for (let jsname of statename) {
            logtime = logtime.concat(qllogs(host, jsname));
        }
        for (let item of logtime) {
            var body = request({
                url: `${host}/open/logs/${item}t=${Date.now()}`,
                method: "GET",
                headers: {
                    "Authorization": "Bearer " + qltokens,
                }
            });
            let totalarr = JSON.parse(body);
            let cutt = totalarr.data.split('==============📣系统通知📣==============');
            cutt.forEach(cuttitem => {
                let system = cuttitem.split('------------------【京东账号')[0];
                if (!system.includes('【提示】cookie已失效')) {
                    let info = system.split('\n');
                    let waterpin;
                    let waterprogress;
                    let currentwater;
                    let time = item.match(/(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})/)[1];
                    for (const each of Object.values(info)) {
                        if (each == '') {
                            continue;
                        }
                        if (/\【京东账号/.test(each)) {
                            waterpin = /【.+?】(.+)/.exec(each)[1].replace(/\s/g, '');
                        }
                        if (/种植进度/.test(each)) {
                            waterprogress = each.split('】')[1];
                            if (waterprogress && waterprogress.includes('undefined')) {
                                waterprogress = undefined
                            }
                        }
                        if (/水果进度/.test(each)) {
                            waterprogress = /\d+\.\d+%/.exec(each)[0];
                            waterprogress = waterprogress == "100.00%" ? "100%" : waterprogress;
                        }
                        if (/已种成|已可领取/.test(each)) {
                            waterprogress = "100%";
                        }
                        if (/忘了/.test(each)) {
                            waterprogress = "0%";
                        }
                        if (/剩余水滴/.test(each)) {
                            try {
                                currentwater = /\d+/.exec(each)[0];
                            } catch (e) {
                                // console.log(error);
                            }
                        }
                    }
                    water.push({
                        pin: waterpin,
                        progress: waterprogress,
                        currentwater,
                        time
                    });
                }
            });
        }
        water.shift()
        Debug(JSON.stringify(water));
        return water
    } catch (e) {
        Debug('newgetstate()' + e);
        sendText('获取水果进度出错:' + e);
        return water
    }
}

function loggethelpcode(num) {
    var QLSName = bucketGet("farm", "QLS");
    let repo = JSON.parse(bucketGet(tongzi, "Repo"));
    QLSName = QLSName.split(',');
    if (QLSName == "" || QLSName == null) {
        notifyMasters("未配置青龙容器相关信息，请发送“管理农场”，修改青龙配置。");
        return;
    } else if (repo == "" || repo == null) {
        notifyMasters("未配置青龙脚本仓库相关信息，请发送“管理农场”，修改青龙配置。");
        return;
    }
    let farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    let count = null;
    num === 0 ? count = num : count = 1;
    farmfull.forEach(item => {
        if (typeof item.shareCode == 'undefined' || item.shareCode.length !== 32) {
            count++
        }
    })
    if (count === 0) {
        notifyMasters('已全部填写助力码');
        return
    } else if (typeof num != 'undefined') {
        notifyMasters(`有${count}个用户未填写助力码`);
    }
    farmfull.forEach(item => {
        if (typeof item.shareCode == 'undefined' || item.shareCode.length !== 32) {
            let isget = false;
            Debug(item.userpin);
            for (let i = 0; i < QLSName.length; i++) {
                if (i > 0 && i % 3 == 0) {
                    Debug(`第${i / 3 + 1}个青龙`);
                    sleep(3000);
                }
                if (isget) {
                    break
                }
                // let QLS = bucketGet("qinglong", "QLS");
                // QLS = JSON.parse(QLS);
                let ql;
                for (let item4 of QLS) {
                    if (item4.name == QLSName[i]) {
                        ql = { host: item4.host, client_id: item4.client_id, client_secret: item4.client_secret };
                    }
                }
                qltoken(ql.host, ql.client_id, ql.client_secret);
                let repo = JSON.parse(bucketGet(tongzi, "Repo"));
                let statename = repo[1].split(',');
                try {
                    let logtime = [];
                    for (let jsname of statename) {
                        logtime = logtime.concat(qllogs(ql.host, jsname));
                    }
                    for (let item2 of logtime) {
                        Debug(isget);
                        if (isget) {
                            break
                        }
                        var body = request({
                            url: `${ql.host}/open/logs/${item2}t=${Date.now()}`,
                            method: "GET",
                            headers: {
                                "Authorization": "Bearer " + qltokens,
                            }
                        });
                        let totalarr = JSON.parse(body);
                        totalarr = totalarr.data.split('\n');
                        for (let index2 in totalarr) {
                            if (isget) {
                                break
                            }
                            if (totalarr[index2].includes('好友互助码')) {
                                // Debug(totalarr[index2])
                                for (let j = index2 - 1; j > index2 - 8; j--) {
                                    // Debug(totalarr[j])
                                    if (totalarr[j].includes('--【京东账号')) {
                                        let result = totalarr[j].match(/【京东账号\d+】(.+?)---/)[1];
                                        // Debug(result)
                                        if (result == item.userpin) {
                                            item.shareCode = totalarr[index2].substring(totalarr[index2].length - 32);
                                            isget = true;
                                            notifyMasters(`${item.userpin}获取成功\n助力码:${item.shareCode}`);
                                            break
                                        }
                                    }
                                }
                            }
                        }
                    }
                } catch (e) {
                    Debug('loggethelpcode()' + e)
                    sendText('日志获取助力码出错')
                }
            }
            if (!isget) {
                let jnStr = bucketGet("jdNotify", encodeURIComponent(item.userpin));
                if (jnStr) {
                    let jn = JSON.parse(jnStr);
                    let cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";";
                    if (typeof item.shareCode == 'undefined' || item.shareCode.length !== 32) {
                        item.shareCode = 'false';
                        notifyMasters(`${jn.ID}的助力码为空，尝试联网获取`);
                        let result = GetHelpCode(cookie);
                        if (result !== false) {
                            item.shareCode = result;
                            isget = true;
                        }
                    }
                }
            }
        }
    })
    bucketSet(tongzi, "farmpin", JSON.stringify(farmfull));
}

function newloggethelpcode(num) {
    var QLSName = bucketGet("farm", "QLS");
    let repo = JSON.parse(bucketGet(tongzi, "newRepo"));
    QLSName = QLSName.split(',');
    if (QLSName == "" || QLSName == null) {
        notifyMasters("未配置青龙容器相关信息，请发送“管理农场”，修改青龙配置。");
        return;
    } else if (repo == "" || repo == null) {
        notifyMasters("未配置青龙新版脚本仓库相关信息，请发送“管理农场”，修改青龙配置。");
        return;
    }
    let farmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
    let count = null;
    num === 0 ? count = num : count = 1;
    farmfull.forEach(item => {
        // Debug(typeof item.shareCode)
        // Debug(item.shareCode.length)
        if (typeof item.shareCode == 'undefined' || item.shareCode.length < 6) {
            count++
        }
    })
    if (count === 0) {
        notifyMasters('已全部填写助力码');
        return
    } else if (typeof num != 'undefined') {
        notifyMasters(`有${count}个用户未填写助力码`);
    }
    farmfull.forEach(item => {
        if (typeof item.shareCode == 'undefined' || item.shareCode.length < 6) {
            let isget = false;
            Debug(item.userpin);
            for (let i = 0; i < QLSName.length; i++) {
                if (i > 0 && i % 3 == 0) {
                    Debug(`第${i / 3 + 1}个青龙`);
                    sleep(3000);
                }
                if (isget) {
                    break
                }
                // let QLS = bucketGet("qinglong", "QLS");
                // QLS = JSON.parse(QLS);
                let ql;
                for (let item4 of QLS) {
                    if (item4.name == QLSName[i]) {
                        ql = { host: item4.host, client_id: item4.client_id, client_secret: item4.client_secret };
                    }
                }
                qltoken(ql.host, ql.client_id, ql.client_secret);
                let newrepo = JSON.parse(bucketGet(tongzi, "newRepo"));
                let statename = newrepo[1].split(',');
                try {
                    let logtime = [];
                    for (let jsname of statename) {
                        logtime = logtime.concat(qllogs(ql.host, jsname));
                    }
                    for (let item2 of logtime) {
                        Debug(isget);
                        if (isget) {
                            break
                        }
                        var body = request({
                            url: `${ql.host}/open/logs/${item2}t=${Date.now()}`,
                            method: "GET",
                            headers: {
                                "Authorization": "Bearer " + qltokens,
                            }
                        });
                        let totalarr = JSON.parse(body);
                        totalarr = totalarr.data.split('\n');
                        for (let index2 in totalarr) {
                            if (isget) {
                                break
                            }
                            if (totalarr[index2].includes('新农场任务好友互助码')) {
                                // Debug(totalarr[index2])
                                // for (let j = index2 - 1; j > index2 - 8; j--) {
                                // Debug(totalarr[j])
                                // if (totalarr[j].includes('--【京东账号')) {
                                // let result = totalarr[j].match(/【京东账号\d+】(.+?)---/)[1];
                                const regex = /账号\（([^）]+)\）/;
                                const match = totalarr[index2].match(regex);
                                const accountId = match ? match[1] : null;
                                // Debug(result)
                                if (accountId == item.userpin) {
                                    const regex = /互助码】(.+)$/;
                                    const match = totalarr[index2].match(regex);
                                    item.shareCode = match ? match[1] : null;
                                    isget = true;
                                    notifyMasters(`${item.userpin}获取成功\n助力码:${item.shareCode}`);
                                    break
                                }
                                // }
                                // }
                            }
                        }
                    }
                } catch (e) {
                    Debug('newloggethelpcode()' + e);
                    sendText('日志获取助力码出错');
                }
            }
            if (!isget) {
                // let jnStr = bucketGet("jdNotify", encodeURIComponent(item.userpin))
                // let jn = JSON.parse(jnStr)
                // let cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                if (typeof item.shareCode == 'undefined' || item.shareCode.length < 6) {
                    // item.shareCode = 'false'
                    // notifyMasters(`${jn.ID}的助力码为空，尝试联网获取`)
                    // let result = GetHelpCode(cookie)
                    // if (result !== false) {
                    //     item.shareCode = result
                    //     isget = true
                    // }
                    notifyMasters(`${item.userpin}未获取到助力码，请去新版农场日志中手动搜索`);
                }
            }
        }
    })
    bucketSet(tongzi, "newfarmpin", JSON.stringify(farmfull));
}

function changeisfull(fullpin, tongzikey) {
    let notfull = 0;
    let count = 0;
    let farmfull = JSON.parse(bucketGet(tongzi, tongzikey));
    Debug('开始通过助力码判断');
    if (fullpin.length != 0) {
        fullpin.forEach(item1 => {
            farmfull.forEach(item2 => {
                if (item2.shareCode == item1.trim()) {
                    if (item2.isfulled == 0 && item2.days != 0) {
                        item2.isfulled = 1;
                        item2.days = item2.days - 1;
                        count++;
                    } else if (item2.days == 0) {
                        notifyMasters(item2.userpin + '助力已到期！' + item2.userid);
                    }
                }
            })
        });
    }
    farmfull.forEach(item => {
        if (item.isfulled == 0) {
            notfull++
        }
    })
    let newfarmfull = JSON.stringify(farmfull);
    bucketSet(tongzi, tongzikey, newfarmfull);
    if (tongzikey == 'farmpin') {
        notifyMasters('旧版农场检查完毕，此次助力完成' + count + '人,' + "今日剩余" + notfull + "人未助力");
    } else {
        notifyMasters('新版农场检查完毕，此次助力完成' + count + '人,' + "今日剩余" + notfull + "人未助力");
    }
}


function deleteshouquan() {
    sendText('警告，你正在执行删除授权');
    // sendText("请输入你的选择的【数字】：\n1.删除旧版农场\n2.删除新版农场");
    // let msg = ShuRu();
    // let tongzikey = "farmpin";
    // if (msg - 1 == 1) {
        tongzikey = "newfarmpin";
    // }
    sendText('检测当前对话渠道为' + imType + "，仅可删除授权" + imType + "用户");
    sendText('请告知我要删除授权的' + imType + '账号，若不清楚可让用户给机器人发送myuid');
    let msg1 = ShuRu();
    if (msg1) {
        sendText('警告，你正在执行删除授权');
        sendText("请选择要删除授权账号:" + msg1 + " 的账号pt_pin");
        var msg2 = listpin(msg1);
        msg2.forEach(item => {
            if (item) {
                var farmfull = JSON.parse(bucketGet(tongzi, tongzikey));
                for (let i in farmfull) {
                    if (farmfull[i].userpin == decodeURIComponent(item) || farmfull[i].userpin == item) {
                        farmfull.splice(i, 1);
                        sendText('已删除' + item + '的授权');
                        bucketSet(tongzi, tongzikey, JSON.stringify(farmfull));
                        return
                    }
                }
                sendText('未找到此账号，请手动去数据桶删除')
            }
        })
    }
}

function guanli() {
    sendText("农场管理菜单\n1.删除所有配置(慎用)\n2.修改青龙配置，脚本配置\n3.开启/关闭用户自助打赏功能\n4.修改账号总数、打赏配置\n5.手动添加账号助力码\n6.自动添加账号助力码\n7.选择群聊推送还是私聊推送\n8.每日是否通知付费农场ck失效的人\n9.是否开启ck过期的账户不同步助力码\n10.手动调整授权账号位置\n11.是否开启农场成熟通知\n12.是否关闭农场浇水\n13.是否开启助力天数为0自动删除\n14.是否开启仅付费账号跑农场任务\n15.是否开启多余助力分给免费账号\n16.自定义未付费用户查询农场提示语\n发送“q”退出当前会话。");
    var num = input(60000);
    if (num == '1') {
        DeletePeiZhi();
        sendText("操作成功。");
    } else if (num == '2') {
        PzQingLong();
    } else if (num == '3') {
        PzIsUseShouQuan();
        sendText("操作成功。");
    } else if (num == '4') {
        var IfShouQuans = IfShouQuan();
        if (IfShouQuans == true || IfShouQuans == "true") {
            if (PZShouQuan()) {
                sendText("操作成功。");
            }
        } else {
            sendText("未开启用户自助授权功能，无法操作");
        }
    } else if (num == '5') {
        var QLSName = bucketGet("farm", "QLS");
        QLSName = QLSName.split(',')
        if (QLSName == "" || QLSName == null) {
            notifyMasters("未配置青龙相关信息，请发送管理农场配置。");
            return;
        } else {
            if (AddshareCode()) {
                newAddshareCode();
            }
        }
    } else if (num == '6') {
        var QLSName = bucketGet("farm", "QLS");
        QLSName = QLSName.split(',');
        if (QLSName == "" || QLSName == null) {
            notifyMasters("未配置青龙相关信息，请发送管理农场配置。");
            return;
        } else {
            // AIAddshareCode()
            loggethelpcode(0);
            newloggethelpcode(0);
        }
    } else if (num == '7') {
        var QLSName = bucketGet("farm", "QLS");
        QLSName = QLSName.split(',');
        if (QLSName == "" || QLSName == null) {
            notifyMasters("未配置青龙相关信息，请发送管理农场配置。");
            return;
        } else {
            sendText('请在60秒内告知我是否开启群聊推送,输入true/false(输入“q”随时退出会话。)');
            var msg = ShuRu();
            if (msg == 'true') {
                sendText('请在60秒内告知我推送的群id,不知道可退出后发送groupCode(输入“q”随时退出会话。)');
                var msg2 = ShuRu();
                bucketSet(tongzi, 'groupCode', msg2.trim());
            } else {
                bucketSet(tongzi, 'groupCode', '');
            }
            sendText("操作成功。");
        }
    } else if (num == '8') {
        var CheckLogin = bucketGet("farm", "CheckLogin");
        if (CheckLogin === 'true') {
            sendText('当前模式：开启通知付费农场ck失效');
        } else {
            sendText('当前模式：关闭通知付费农场ck失效');
        }
        sendText("请输入你的选择的【数字】：\n1.开启通知付费农场ck失效\n2.关闭通知付费农场ck失效");
        var msg = ShuRu();
        if (msg && msg - 1 == 0) {
            bucketSet(tongzi, 'CheckLogin', 'true');
        } else {
            bucketSet(tongzi, 'CheckLogin', 'false');
        }
        sendText("操作成功。");
    } else if (num == '9') {
        var QLSName = bucketGet("farm", "QLS");
        QLSName = QLSName.split(',');
        if (QLSName == "" || QLSName == null) {
            notifyMasters("未配置青龙相关信息，请发送管理农场配置。");
            return;
        } else {
            var NoLoginOutSync = bucketGet("farm", "NoLoginOutSync");
            if (NoLoginOutSync === 'true') {
                sendText('当前模式：ck过期不助力');
            } else {
                sendText('当前模式：ck过期也助力');
            }
            sendText("请输入你的选择的【数字】：\n1.ck过期不助力\n2.ck过期也助力");
            var msg = ShuRu();
            if (msg && msg - 1 == 0) {
                bucketSet(tongzi, 'NoLoginOutSync', 'true');
            } else {
                bucketSet(tongzi, 'NoLoginOutSync', 'false');
            }
            isupqlenv();
        }
        sendText("操作成功。");
    } else if (num == '10') {
        sendText('请选择下列中的一项:\n1.剩余天数最多排前面\n2.剩余天数最少排前面\n3.改变其中一个账户的位置');
        var IsSort = bucketGet("farm", "IsSort");
        if (IsSort === 'descending') {
            sendText('当前模式：剩余天数最多排前面');
        } else if (IsSort === 'ascending') {
            sendText('当前模式：剩余天数最少排前面');
        }
        var farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
        var newfarmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
        var choose = ShuRu();
        if (choose == '1') {
            farmfull.sort((a, b) => b.days - a.days);
            bucketSet(tongzi, "farmpin", JSON.stringify(farmfull));
            newfarmfull.sort((a, b) => b.days - a.days);
            bucketSet(tongzi, "newfarmpin", JSON.stringify(newfarmfull));
            bucketSet(tongzi, "IsSort", "descending");
        } else if (choose == '2') {
            farmfull.sort((a, b) => a.days - b.days);
            bucketSet(tongzi, "farmpin", JSON.stringify(farmfull));
            newfarmfull.sort((a, b) => a.days - b.days);
            bucketSet(tongzi, "newfarmpin", JSON.stringify(newfarmfull));
            bucketSet(tongzi, "IsSort", "ascending");
        } else if (choose == '3') {
            sendText("请输入你的选择的【数字】：\n1.调整旧版农场\n2.调整新版农场");
            let truefarmfull = null;
            let tongzikey = null;
            let msg1 = ShuRu();
            if (msg1 && msg1 - 1 == 0) {
                tongzikey = "farmpin";
                truefarmfull = farmfull;
            } else if (msg1 && msg1 - 1 == 1) {
                tongzikey = "newfarmpin";
                truefarmfull = newfarmfull;
            } else {
                sendText("已退出");
                return
            }
            var sendstr = '请选择下列账号中的一个:';
            var count = 0;
            truefarmfull.forEach((item, index) => {
                sendstr = sendstr + `\n${index + 1}.用户:${item.userid}\n账户名称:${item.userpin}\n剩余天数:${item.days}`;
                count++
                if (count % 40 == 0) {
                    sendText(sendstr);
                    sendstr = '';
                }
            })
            sendText(sendstr);
            var msg = ShuRu();
            if (msg) {
                sendText(`请输入你想把${truefarmfull[msg - 1].userpin}放在第几个,输入纯数字`);
                var msg2 = ShuRu();
                if (msg2) {
                    const itemToMove = truefarmfull[msg - 1];
                    truefarmfull.splice(msg - 1, 1);
                    truefarmfull.splice(msg2 - 1, 0, itemToMove);
                    bucketSet(tongzi, tongzikey, JSON.stringify(truefarmfull));
                } else {
                    sendText("已退出");
                    return
                }
            } else {
                sendText("已退出");
                return
            }
        } else {
            return
        }
        isupqlenv();
        sendText("操作成功。");
    } else if (num == '11') {
        var isnotify = bucketGet("farm", "IsNotify");
        if (isnotify === 'true') {
            sendText('当前模式：开启成熟通知');
        } else {
            sendText('当前模式：关闭成熟通知');
        }
        sendText("请输入你的选择的【数字】：\n1.开启成熟通知\n2.关闭成熟通知");
        var msg = ShuRu();
        if (msg && msg - 1 == 0) {
            bucketSet(tongzi, 'IsNotify', 'true');
            sendText("已开启，本功能只能作用于插件设置的青龙容器，随着插件执行定时，自动通知农场可领取的用户");
        } else {
            bucketSet(tongzi, 'IsNotify', 'false');
            sendText('已关闭农场成熟通知');
        }
        sendText("操作成功。");
    } else if (num == '12') {
        var iswater = bucketGet("farm", "IsWater");
        if (iswater == 'NO_WATER') {
            sendText('当前模式：完全不浇水，浇水任务不做了');
        } else if (iswater == 'DO_TEN_WATER_AGAIN') {
            sendText('当前模式：攒水滴只浇10次水，完成每日浇水任务');
        } else {
            sendText('当前模式：正常浇水，每天保留100滴');
        }
        sendText("请输入你的选择的【数字】：\n0.正常浇水，每天保留100滴\n1.完全不浇水，浇水任务不做了\n2.攒水滴只浇10次水，完成每日浇水任务");
        var msg = ShuRu();
        if (msg) {
            choosewater(msg);
            sendText("操作成功。");
        } else {
            sendText("超时，已退出。");
        }
    } else if (num == '13') {
        var isclean = bucketGet("farm", "IsClean");
        if (isclean === 'true') {
            sendText('当前模式：开启自动清理');
        } else {
            sendText('当前模式：关闭自动清理');
        }
        sendText("请输入你的选择的【数字】：\n1.开启自动清理\n2.关闭自动清理");
        var msg = ShuRu();
        if (msg && msg - 1 == 0) {
            bucketSet(tongzi, 'IsClean', 'true');
        } else {
            bucketSet(tongzi, 'IsClean', 'false');
        }
        sendText("操作成功。");
    } else if (num == '14') {
        var waterscript = bucketGet(tongzi, "WaterScript");
        if (waterscript == "" || waterscript == null) {
            sendText('请输入你的农场任务脚本命令(只能写一个)，例：task 6dylan6_jdpro/jd_fruit.js');
            var msg2 = ShuRu();
            if (msg2) {
                let script = msg2.replace(/^task\s(.+)\.js$/, '$1') + '.js';
                bucketSet('farm', 'WaterScript', script);
                sendText('配置成功');
            } else {
                sendText('输入错误，已退出');
                return;
            }
        }
        var IsOnlyPay = bucketGet("farm", "IsOnlyPay");
        if (IsOnlyPay === 'true') {
            sendText('当前模式：只有付费账号跑农场任务');
        } else {
            sendText('当前模式：所有人都可以跑农场任务');
        }
        sendText("请输入你的选择的【数字】：\n1.只有付费账号跑农场任务\n2.所有人都可以跑农场任务");
        var msg = ShuRu();
        if (msg && msg - 1 == 0) {
            var waterscript = bucketGet(tongzi, "WaterScript");
            if (waterscript == "" || waterscript == null) {
                sendText('请输入你的旧版农场任务脚本命令(只能写一个)，例：task 6dylan6_jdpro/jd_fruit.js');
                var msg2 = ShuRu();
                if (msg2) {
                    let script = msg2.replace(/^task\s(.+)\.js$/, '$1') + '.js';
                    bucketSet('farm', 'WaterScript', script);
                    sendText('配置成功');
                } else {
                    sendText('输入错误，已退出');
                    return;
                }
            }
            var newWaterScript = bucketGet(tongzi, "newWaterScript");
            if (newWaterScript == "" || newWaterScript == null) {
                sendText('请输入你的新版农场任务脚本命令(只能写一个)，例：task 6dylan6_jdpro/jd_fruit_new.js');
                var msg2 = ShuRu();
                if (msg2) {
                    let script = msg2.replace(/^task\s(.+)\.js$/, '$1') + '.js';
                    bucketSet('farm', 'newWaterScript', script);
                    sendText('配置成功');
                } else {
                    sendText('输入错误，已退出');
                    return;
                }
            }
            bucketSet(tongzi, 'IsOnlyPay', 'true');
            sendText("选择此模式请禁用青龙容器中新旧农场日常任务，后续将根据农场管理插件的执行定时，执行农场任务");
        } else if (msg - 1 == 1) {
            bucketSet(tongzi, 'IsOnlyPay', 'false');
        }
        sendText("操作成功。");
    } else if (num == '15') {
        var IsShare = bucketGet("farm", "IsShare");
        if (IsShare === 'true') {
            sendText('当前模式：多余助力分给免费账号');
        } else {
            sendText('当前模式：多余助力不分给免费账号');
        }
        sendText("请输入你的选择的【数字】：\n1.分给免费账号\n2.不分给免费账号");
        var msg = ShuRu();
        if (msg && msg - 1 == 0) {
            bucketSet(tongzi, 'IsShare', 'true');
        } else {
            bucketSet(tongzi, 'IsShare', 'false');
        }
        sendText("操作成功。");
    } else if (num == '16') {
        var TipText = bucketGet("farm", "TipText");
        if (TipText) {
            sendText('当前提示语：' + TipText);
        } else {
            sendText('当前提示语：优先级不足，吃随机助力');
        }
        sendText("请输入想要展示的提示语");
        var msg = ShuRu();
        if (msg) {
            bucketSet(tongzi, 'TipText', msg);
            sendText("操作成功。");
        } else {
            sendText("未做修改。");
        }
    } else if (num == "q" || num == "Q") {
        sendText("已退出。");
    } else {
        sendText("输入错误，已退出。");
    }
}


function choosewater(choose) {
    var QLSName = bucketGet("farm", "QLS");
    QLSName = QLSName.split(',');
    if (QLSName == "" || QLSName == null) {
        notifyMasters("未配置青龙相关信息，请发送管理农场配置。");
        return;
    }
    for (let i = 0; i < QLSName.length; i++) {
        if (i > 0 && i % 3 == 0) {
            Debug(`第${i / 3 + 1}个青龙`);
            sleep(3000);
        }
        // let QLS = bucketGet("qinglong", "QLS");
        // QLS = JSON.parse(QLS);
        let ql;
        for (item of QLS) {
            if (item.name == QLSName[i]) {
                ql = { host: item.host, client_id: item.client_id, client_secret: item.client_secret };
            }
        }
        if (choose == '0') {
            var id = SelectQLSIsIndexOfAccount(ql, 'NO_WATER');
            qldelete(id, ql);
            id = SelectQLSIsIndexOfAccount(ql, 'DO_TEN_WATER_AGAIN');
            qldelete(id, ql);
            bucketSet("farm", "IsWater", 'true');
        } else if (choose == '1') {
            var id = SelectQLSIsIndexOfAccount(ql, 'DO_TEN_WATER_AGAIN');
            qldelete(id, ql);
            qlinsert('true', ql, 'NO_WATER');
            bucketSet("farm", "IsWater", 'NO_WATER');
        } else if (choose == '2') {
            var id = SelectQLSIsIndexOfAccount(ql, 'NO_WATER');
            qldelete(id, ql);
            qlinsert('true', ql, 'DO_TEN_WATER_AGAIN');
            bucketSet("farm", "IsWater", 'DO_TEN_WATER_AGAIN');
        }
    }
}

function AIAddshareCode() {
    sendText(`此功能可智能识别faker、kr库的东东农场内部水滴互助脚本日志，请按照以下格式手动复制日志发给我（不要删除换行，日志中包含数据异常也能识别）\n【京东账号2（jd_fd88ff）的东东农场内部水滴互助好友互助码】

c97be5b2e2bc289089edac97e8a4e48c
    
【京东账号3（jd_31cd5）的东东农场内部水滴互助好友互助码】
    
e37d14242d4ba855adbb72c042bb2aca`)
    var str = ShuRu();
    str = str.split("\n");
    Debug(str);
    let arr = [];
    var obj = {};
    var istrue = false;
    var iserro = false;
    str.forEach((item, index) => {
        if (index == 0 && !item.includes('京东账号')) {
            sendText('格式错误，请严格对照示例');
            istrue = true;
        }
        iserro = false;
        if (item.includes('数据异常') || item.includes('尝试联网')) {
            iserro = true;
        }
        if (item.includes('京东账号') && !iserro) {
            obj = {};
            var regex = /京东账号\d+\（(.+?)\）/;
            obj.userpin = item.match(regex)[1];
        } else if (!iserro) {
            obj.shareCode = item;
            arr.push(obj);
        }
    });
    if (istrue) {
        arr = [];
    }
    let count = 0;
    var farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    arr.forEach(item1 => {
        farmfull.forEach(item2 => {
            if (item1.userpin == item2.userpin && !item2.shareCode) {
                item2.shareCode = item1.shareCode;
                count++
            }
        })
    })
    bucketSet(tongzi, "farmpin", JSON.stringify(farmfull));
    sendText(`识别成功，此次添加了${count}个助力码`);
}

function AddshareCode() {
    var farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    var sendstr = '（旧版农场）请选择下列账号中的一个:';
    var count = 0;
    var noshareCodearr = [];
    farmfull.forEach((item, index) => {
        if (typeof item.shareCode == 'undefined' || item.shareCode.length !== 32) {
            sendstr = sendstr + `\n${++count}.${item.userpin}\n助力码:${item.shareCode}`;
            noshareCodearr.push(index);
            if (count % 40 == 0) {
                sendText(sendstr);
                sendstr = '';
            }
        }
    })
    if (count == 0) {
        sendstr = '旧版农场已全部填写助力码';
        sendText(sendstr);
        return true
    }
    sendText(sendstr);
    var msg = ShuRu();
    if (msg) {
        sendText(`请输入${farmfull[noshareCodearr[msg - 1]].userpin}的助力码`);
        var msg2 = ShuRu();
        if (msg2) {
            farmfull[noshareCodearr[msg - 1]].shareCode = msg2.trim();
            bucketSet(tongzi, "farmpin", JSON.stringify(farmfull));
            sendText(`${farmfull[noshareCodearr[msg - 1]].userpin}助力码更新成功`);
            return true
        }
    }
}

function newAddshareCode() {
    var farmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
    var sendstr = '（新版农场）请选择下列账号中的一个:';
    var count = 0;
    var noshareCodearr = [];
    farmfull.forEach((item, index) => {
        if (typeof item.shareCode == 'undefined' || item.shareCode.length < 6) {
            sendstr = sendstr + `\n${++count}.${item.userpin}\n助力码:${item.shareCode}`;
            noshareCodearr.push(index);
            if (count % 40 == 0) {
                sendText(sendstr);
                sendstr = '';
            }
        }
    })
    if (count == 0) {
        sendstr = '新版农场已全部填写助力码';
        sendText(sendstr);
        return
    }
    sendText(sendstr);
    var msg = ShuRu();
    if (msg) {
        sendText(`请输入${farmfull[noshareCodearr[msg - 1]].userpin}的助力码`);
        var msg2 = ShuRu();
        if (msg2) {
            farmfull[noshareCodearr[msg - 1]].shareCode = msg2.trim();
            bucketSet(tongzi, "newfarmpin", JSON.stringify(farmfull));
            sendText(`${farmfull[noshareCodearr[msg - 1]].userpin}助力码更新成功`);
        }
    }
}

function AccountPlayWX(SumUserAccountNumPrice, length) {
    // var isuse = IsUserUseDaShang()
    let is = atWaitPay();
    if (!is) {
        // bucketSet(tongzi, "IsUserUseDaShang", "false");
        var PlayText = bucketGet(tongzi, "MoRenShouQuan");
        var ss = JSON.parse(PlayText);
        sendText(`农场每日满助力，扫码打赏${SumUserAccountNumPrice * length}元，${length}个账号剩余时间加30天(只能打赏${SumUserAccountNumPrice * length}的倍数！)`);
        sendText('请在120秒内完成打赏，超时将退出');
        sendImage(ss.Images);
        let data = waitPay(120000, "q");
        Debug(JSON.stringify(data));
        if (data == "timeout") {
            sendText("超时，已退出");
            // bucketSet(tongzi, "IsUserUseDaShang", "true");
        } else {
            // bucketSet(tongzi, "IsUserUseDaShang", "true");
            var money = data.money;
            Debug(money);

            if (money % SumUserAccountNumPrice === 0) {
                return money
            } else {
                sendText('打赏金额不是倍数！')
                return 0
            }
        }
    } else {
        sendText("你先等一会哈，别人正在打赏中。");
    }
}

function IsUserUseDaShang() {
    var use = bucketGet(tongzi, "IsUserUseDaShang");
    if (use == "false") {
        return false;
    } else {
        return true;
    }
}

function IfShouQuan() {
    var IfShouQuan = bucketGet(tongzi, "IsShouQuanTrue");
    if (IfShouQuan == "" || IfShouQuan == null) {
        return false;
    } else {
        return IfShouQuan;
    }
}

function chaxun(userid) {
    var farmpin = JSON.parse(bucketGet(tongzi, "farmpin"));
    var newfarmpin = JSON.parse(bucketGet(tongzi, "newfarmpin"));
    var NoWaterPin = bucketGet("farm", "NoWaterPin").split('&');
    var checkLogin = bucketGet(tongzi, 'NoLoginOutSync')
    let isin = 0;

    const updateLogin = (obj) => {
        obj.userpin = decodeURIComponent(obj.userpin);
        let jnStr = bucketGet("jdNotify", encodeURIComponent(obj.userpin));
        if (jnStr) {
            let jn = JSON.parse(jnStr);
            let cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";";
            obj.isLogin = isLogin(cookie);
        }
        return obj
    }

    let matchedObjects = farmpin.filter(obj => obj.userid === userid);
    let newmatchedObjects = newfarmpin.filter(obj => obj.userid === userid);
    let allobjects = {}
    matchedObjects.forEach(item => {
        allobjects[item.userpin] = {
            "旧": item
        }
        const newday = newmatchedObjects.find(item2 => item2.userpin == item.userpin);
        if (newday) {
            allobjects[item.userpin]["新"] = newday
            newmatchedObjects = newmatchedObjects.filter(obj => obj !== newday);
        }
    })
    newmatchedObjects.forEach(item => {
        allobjects[item.userpin] = {
            "新": item
        }
    })

    const status = (item, type, today) => {
        if (item.days == 0) {
            today.push(`${type}农场助力已到期！请及时续费！`);
            notifyMasters(`${item.userpin}'${type}版农场助力已到期\n用户ID：${item.userpin}`);
        } else {
            today.push(`${type}农场：${item.days}天`);
        }
        if (typeof item.progress != 'undefined') {
            today.push(`水果进度：${item.progress}`);
        }
        if (typeof item.water != 'undefined') {
            today.push(`剩余水滴：${item.water}g`);
        }
        item.isfulled == 0 ? today.push(`${type}版助力：❌队列中`) : today.push(`${type}版助力：✅已完成`);
    }

    for (let key in allobjects) {
        Debug(key);
        let today = [`账户名称：${key}`];
        let already = false;
        let isLogin;

        for (let type in allobjects[key]) {
            if (checkLogin == 'true' && already == false) {
                allobjects[key][type] = updateLogin(allobjects[key][type]);
                isLogin = allobjects[key][type].isLogin;
                already = true;
            }
            status(allobjects[key][type], type, today);
        }

        const nowater = NoWaterPin.includes(key);
        nowater ? today.push('浇水状态：关闭浇水') : today.push('浇水状态：开启浇水');
        if (isLogin != undefined) {
            isLogin ? today.push('账号状态：✅正常助力') : today.push('账号状态：❌账号已过期-不助力');
        }
        sendText(today.join('\n'));
        isin++
    }

    if (isin == 0) {
        var TipText = bucketGet("farm", "TipText") || "优先级不足，吃随机助力";
        sendText(TipText);
    }
    bucketSet(tongzi, "farmpin", JSON.stringify(farmpin));
    bucketSet(tongzi, "newfarmpin", JSON.stringify(newfarmpin));
}

function adminshouquan() {
    sendText('检测当前对话渠道为' + imType + "，仅可授权" + imType + "用户");
    // sendText("请输入你的选择的【数字】：\n1.授权旧版农场\n2.授权新版农场");
    let tongzikey = '';
    let msg = ShuRu();
    // if (msg && msg - 1 == 0) {
    //     tongzikey = "farmpin";
    // } else {
        tongzikey = "newfarmpin";
    // }
    sendText('请告知我需要授权的' + imType + '账号，若不清楚可让用户发送myuid');
    let msg1 = ShuRu();
    if (msg1) {
        sendText("请选择要授权账号:" + msg1 + " 的账号pt_pin");
        var msg2 = listpin(msg1);
        if (msg2) {
            sendText("请告知我要增加的授权天数。");
            var msg3 = ShuRu();
            if (msg3) {
                msg2.forEach(item => {
                    CaoZuoShouQuan(msg1, item, msg3, tongzikey);
                })
                isupqlenv();
            }
        }
    }
}

function ChuShiShuRu() {
    var msg = input(60000);
    if (msg == null || msg == "") {
        sendText("超时，60秒内未回复，退出。");
        return false
    } else if (msg == "q" || msg == "Q") {
        sendText("已退出会话。");
        return false
    } else {
        return msg;
    }
}

function ShuRu() {
    var msg = input(60000, 6000);
    if (msg == null) {
        sendText("超时，60秒内未回复，取消本次配置。");
        return false;
    } else if (msg == "q" || msg == "Q") {
        sendText("已退出会话");
        return false
    } else {
        return msg;
    }
}

function CaoZuoShouQuan(shuruqq, shuruNum, shuruday, tongzikey) {
    var IsShouQaun = bucketGet(tongzi, tongzikey);
    var ss = JSON.parse(IsShouQaun);
    var sss = JSON.stringify(ss);
    sss = String(sss);
    shuruday = parseInt(shuruday);
    if (sss.indexOf(decodeURIComponent(shuruNum)) >= 0) {
        for (item of ss) {
            if (encodeURIComponent(item.userpin) == shuruNum) {
                item.userid = shuruqq;
                item.days += shuruday;
                sendText(`授权账号：${shuruqq}\n授权pin：${item.userpin}\n剩余天数：${item.days}天`);
                bucketSet(tongzi, tongzikey, JSON.stringify(ss));
                return
            }
        }
    }
    else {
        sendText("系统中未查询到该账号相关授权信息，已为您自动添加");
        var person = { "userid": shuruqq, "userpin": decodeURIComponent(shuruNum), "days": shuruday, "isfulled": 0, "imType": imType };
        ss.push(person);
        sendText(`授权账号：${shuruqq}\n授权pin：${decodeURIComponent(shuruNum)}\n剩余天数：${shuruday}天`);
        bucketSet(tongzi, tongzikey, JSON.stringify(ss));
        return
    }
}

function stats() {
    let count = 0;
    let notfull = 0;
    let noshareCode = 0;
    let farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    var QLSName = bucketGet("farm", "QLS");
    QLSName = QLSName.split(',');
    let sendstr = '';
    farmfull.forEach(item => {
        item.isfulled == 0 ? notfull++ : count++;
        if (QLSName == "" || QLSName == null) {
            sendstr = sendstr;
        } else {
            if (!item.shareCode) {
                noshareCode++;
            }
        }
    })
    sendstr = `旧版总数：${farmfull.length}\n今日已助力：${count}\n今日未助力：${notfull}\n`;
    if (noshareCode != 0) {
        sendstr = sendstr + `您已开启autman管理农场助力码，目前有${noshareCode}个号未填写助力码，请发送"管理农场"，手动添加助力码`;
    }
    sendText(sendstr);
    count = 0;
    notfull = 0;
    noshareCode = 0;
    sendstr = '';
    farmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
    farmfull.forEach(item => {
        item.isfulled == 0 ? notfull++ : count++;
        if (QLSName == "" || QLSName == null) {
            sendstr = sendstr;
        } else {
            if (!item.shareCode) {
                noshareCode++;
            }
        }
    })
    sendstr = `新版总数：${farmfull.length}\n今日已助力：${count}\n今日未助力：${notfull}\n`;
    if (noshareCode != 0) {
        sendstr = sendstr + `您已开启autman管理农场助力码，目前有${noshareCode}个号未填写助力码，请发送"管理农场"，手动添加助力码`;
    }
    sendText(sendstr);
    check("统计");
}

function chongzhi() {
    let farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    farmfull.forEach(item => {
        item.isfulled = 0;
    });
    bucketSet(tongzi, "farmpin", JSON.stringify(farmfull));
    let newfarmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
    newfarmfull.forEach(item => {
        item.isfulled = 0;
    });
    bucketSet(tongzi, "newfarmpin", JSON.stringify(newfarmfull));
    const tomorrowDate = new Date(Date.now() + 32 * 60 * 60 * 1000).toISOString().slice(0, 10);
    bucketSet('farm', 'ResetDate', tomorrowDate);
    check("重置");
}

function check(status) {
    let str = '';
    let renewstr = '';
    let farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
    farmfull.forEach(item => {
        if (item.days <= 2) {
            str += `\n旧版${item.userid}：`;
            str += `\n${item.userpin}--${item.days}天`;
            str += "\n-----------------------------------";
            if (IfShouQuan()) {
                renewstr = '请对我说"打赏农场"自助续费，或及时联系群主续费';
            } else {
                renewstr = '请及时联系群主续费';
            }
            if (status != "统计") {
                push(
                    {
                        imType: item.imType || 'qq',
                        userID: item.userid,
                        groupCode: groupCode,
                        content: item.userpin + '旧版农场助力天数剩余' + item.days + '天！' + renewstr,
                    }
                )
            }
        }
    });
    let newfarmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
    newfarmfull.forEach(item => {
        if (item.days <= 2) {
            str += `\n新版${item.userid}：`;
            str += `\n${item.userpin}--${item.days}天`;
            str += "\n-----------------------------------";
            if (IfShouQuan()) {
                renewstr = '请对我说"打赏农场"自助续费，或及时联系群主续费';
            } else {
                renewstr = '请及时联系群主续费';
            }
            if (status != "统计") {
                push(
                    {
                        imType: item.imType || 'qq',
                        userID: item.userid,
                        groupCode: groupCode,
                        content: item.userpin + '新版农场助力天数剩余' + item.days + '天！' + renewstr,
                    }
                )
            }
        }
    });
    if (status == "重置") {
        try {
            checkislogin();
            if (bucketGet(tongzi, 'NoLoginOutSync') == 'true') {
                farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
                farmfull = farmfull.filter(item => !item.isLogin);
                str += `\n旧版农场付费ck失效总数:${farmfull.length}`;
                newfarmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
                newfarmfull = newfarmfull.filter(item => !item.isLogin);
                str += `\n新版农场付费ck失效总数:${newfarmfull.length}`;
            }
            notifyMasters('助力状态重置完成，已通知剩余天数不足3天的账号:' + str);
        } catch (e) {
            Debug(e);
        }
        upqlenv();
    } else if (status == "统计") {
        if (bucketGet(tongzi, 'NoLoginOutSync') == 'true') {
            farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
            farmfull = farmfull.filter(item => !item.isLogin);
            str += `\n旧版农场付费ck失效总数:${farmfull.length}`;
            newfarmfull = JSON.parse(bucketGet(tongzi, "newfarmpin"));
            newfarmfull = newfarmfull.filter(item => !item.isLogin);
            str += `\n新版农场付费ck失效总数:${newfarmfull.length}`;
        }
        notifyMasters('剩余天数不足3天的账号:' + str);
    }
}

function checkislogin() {
    var ischecklogin = bucketGet(tongzi, 'CheckLogin');
    if (ischecklogin == "" || ischecklogin == null || ischecklogin == 'false') {
        return;
    }
    farmfull.forEach(item => {
        let jnStr = bucketGet("jdNotify", encodeURIComponent(item.userpin));
        let jn = JSON.parse(jnStr);
        let cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";";
        let result = isLogin(cookie);
        if (!result) {
            notifyMasters(`付费农场账户${jn.ID}ck已失效，已通知`);
            push(
                {
                    imType: item.imType || 'qq',
                    userID: item.userid,
                    groupCode: groupCode,
                    content: '付费农场账户' + item.userpin + '的ck已失效,请及时更新避免消耗剩余天数！',
                }
            )
        }
        sleep(2000);
    })
}

function isLogin(cookie) {
    let ckislogin = true;
    request({
        url: 'https://plogin.m.jd.com/cgi-bin/ml/islogin',
        method: "get",
        headers: {
            "User-Agent": "jdltapp;iPad;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPad7,5;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.14;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/3;ads/;psn/956c074c769cd2eeab2e36fca24ad4c9e469751a|8;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "cookie": cookie,
            "referer": "https://h5.m.jd.com/",
        },
        "timeOut": 10000,
    }, function (error, response, header, body) {
        // Debug(body)
        try {
            if (body) {
                body = JSON.parse(body);
                if (body.islogin === "0") {
                    ckislogin = false;
                }
            }
        } catch (e) {
            Debug(e);
        }
    })
    return ckislogin
}

function listpin(msg1) {
    try {
        //检查版本
        version = call("version")()["sn"];
        Debug("系统版本：" + version);
        if (version < "0.9.5") {
            sendText("当前autMan版本为" + version + "，本插件仅支持0.9.5及以上。");
            return
        }

        //媒介
        imType = ImType();
        //用户id
        const userId = msg1;
        //绑定的京东账号
        const jds = bucketKeys("pin" + imType.toUpperCase(), userId);
        Debug(`pin${imType.toUpperCase()}：${userId}的京东账号：`);
        let farmfull = JSON.parse(bucketGet(tongzi, "farmpin"));
        let newfarmpin = JSON.parse(bucketGet(tongzi, "newfarmpin"));
        let cookiepin = [];
        Debug(jds);
        if (jds.length == 0) {
            sendText("没有与你绑定的账号，请对我说：“登陆”");
            return false
        } else {
            jdsIndex = [];
            var NoWaterPin = bucketGet("farm", "NoWaterPin");
            NoWaterPin = NoWaterPin.split('&');
            for (i = 0; i < jds.length; i++) {
                jnStr = bucketGet("jdNotify", jds[i]);

                Debug(jds[i])
                const farmItem = farmfull.find(item => item.userpin == decodeURIComponent(jds[i]));
                const newfarmItem = newfarmpin.find(item => item.userpin == decodeURIComponent(jds[i]));
                const iswater = NoWaterPin.find(item => item == jds[i]);

                let jdsdays = farmItem ? `旧农场:${farmItem.days}天` : '旧农场:未授权';
                jdsdays += newfarmItem ? `\n新农场:${newfarmItem.days}天` : '\n新农场:未授权';
                jdsdays += iswater ? '\n浇水状态:关闭浇水' : '\n浇水状态:开启浇水';
                if (jnStr) {
                    jn = JSON.parse(jnStr);
                    cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";";
                    jdsIndex[i] = (i + 1) + getnickname(cookie) + "\npt_pin=" + jds[i] + '\n' + jdsdays + "\n-----------------------------------";
                } else {
                    Debug(`jdNotify桶子中没有${jds[i]}`);
                    jdsIndex[i] = (i + 1) + ".pt_pin=" + jds[i] + '\n' + jdsdays + "\n-----------------------------------";
                }
            }
            sendText("请选择下列账号(输入纯数字，如果要选择其中几个请用英文逗号连接)：\n0.全部\n" + jdsIndex.join("\\n"));
            let index = input(30000);
            if (index) {
                if (parseInt(index) == 0) {
                    for (k = 0; k < jds.length; k++) {
                        cookiepin.push(jds[k]);
                    }
                    Debug(cookiepin);
                    return cookiepin
                } else if (index == 'q' || index == 'Q') {
                    sendText("退出");
                    return false
                } else {
                    let i = index.split(',');
                    i.forEach(item => {
                        if (item < jds.length + 1) {
                            cookiepin.push(jds[item - 1]);
                        }
                    })
                    Debug(cookiepin)
                    if (cookiepin.length == 0 || !cookiepin.every(value => value)) {
                        sendText("请选择正确的账号，已退出");
                        return false
                    }
                    return cookiepin
                }
            } else {
                sendText("退出");
                return false
            }
        }
    } catch (err) {
        Debug(err)
    }
}

function getnickname(cookie) {
    let str = "";
    request({
        url: "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion",
        method: "Get",
        headers: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42",
            "Accept-Language": "zh-cn",
            "Referer": "https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&",
            "Cookie": cookie,
            "Accept": "*/*",
            "Host": "me-api.jd.com",
            "Connection": "keep-alive"
        }
    }, function (error, response, header, body) {
        try {
            let obj = JSON.parse(body);
            if (obj['retcode'] === "0" && obj.data && obj.data.hasOwnProperty("userInfo")) {
                str = ".账户昵称:" + obj.data.userInfo.baseInfo.nickname;
            } else if (obj['retcode'] === "1001") {
                str = ".账号已过期";
            } else {
                str = ".未查询到昵称";
            }
        } catch (e) {
            str = ".未查询到昵称";
            Debug(e);
        }
    })
    return str
}

main();

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
];
function UserAgents() {
    return USER_AGENTS[parseInt(Math.random() * USER_AGENTS.length)]
}
