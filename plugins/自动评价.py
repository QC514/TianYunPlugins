//[rule: 自动评价] 
//[icon: https://img1.baidu.com/it/u=1686866660,3343327692&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=501]图标链接地址，支持http和https
//[tile: 自动评价]要与文件名相同，也可以不加，上传aut云时会自动将文件名设置为此头注
//[author: specter]作者,可以自定义，不定义的话，上传时会增加为aut云注册的用户名,收费插件一定要填写aut云账号
//[version: 1.4.8] 版本格式：1.0.0，不定义的话，上传时会自动增加此头注，默认为1.0.0 
//[class: 工具类]建议从工具类、查询类、娱乐类、餐饮类、影音类、生活类、图片类、游戏类等中选择，也可自定义
//[platform: qq,wx,tg]适用的平台 qq\wx\tg\wxmp之间选择，中间用英文逗号隔开
//[public: true] 是否公开发布？值为true 或 false，不定义的话，上传aut云时会自动设置为true
//[price: 0.5] 上架价格
//[service: 2607401955]售后联系方式，service不完整，将不会审核上架
//[description: 自动评价，支持6dy库。<br>配参完成后就可以管理员和普通用户都可以对机器人说自动评价进行使用。插件需要qls和jdNotify权限。<br>指令：自动评价。] 使用方法尽量写具体
//[priority: 99999] 优先级，数字越大表示优先级越高
//[param: {"required":true,"key":"AutoEvaluate.QLS","bool":false,"placeholder":"输入自动评价的容器名称","name":"自动评价容器","desc":"输入自动评价的容器名称，多个容器用英文逗号分割"}]
//[param: {"required":true,"key":"AutoEvaluate.repo","bool":false,"placeholder":"输入自动评价使用的库名称","name":"自动评价使用的库","desc":"输入自动评价使用的库名称可填写以下其中一个：6dy"}]
//[param: {"required":true,"key":"AutoEvaluate.AllEvaluate","bool":true,"placeholder":"管理员可以评价所有人","name":"管理员可以评价所有人","desc":"勾选则管理员可以评价所有人，不勾选则管理员只评价自己"}]
//[param: {"required":true,"key":"AutoEvaluate.banChat","bool":true,"placeholder":"关闭群聊使用","name":"关闭群聊使用","desc":"勾选则关闭群聊使用，不勾选则开启群聊使用"}]
//[param: {"required":true,"key":"AutoEvaluate.banReply","bool":true,"placeholder":"关闭评价过程回复","name":"关闭评价过程回复","desc":"勾选则关闭评价过程回复减少机器人发送消息，不勾选则开启评价过程回复"}]


var tongzi = "AutoEvaluate";
let qltokens = ''
let userId = GetUserID()
var GetImType = GetImType()
var GetContent = GetContent()
var ChatID = GetChatID()//获取当前会话群ID

var version = call("version")()["sn"];
Debug(version)
var QLS = null
const banReply = bucketGet(tongzi, "banReply")
try {
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
} catch (e) {
    notifyMasters(e)
    notifyMasters("获取容器出错,请在奥特曼后台-系统管理-插件权限中允许本插件访问qls数据")
}
// Debug(QLS)
if (QLS.length == 0) {
    notifyMasters("获取容器出错,请在奥特曼后台-系统管理-插件权限中允许本插件访问qls数据")
}

main()

function main() {
    if (bucketGet(tongzi, "banChat") == 'true' && ChatID) {
        sendText("请私聊我使用自动评价")
        return
    }

    Debug(GetContent)
    // if (isAdmin() && GetContent == '管理自动评价') {
    //     qlcontainer()
    //     return
    // } else if (isAdmin() && GetContent == '释放自动评价') {
    //     bucketSet(tongzi, "IsRunning", 'false');
    //     sendText('操作成功。')
    //     return
    // }
    // var isrunning = bucketGet(tongzi, "IsRunning");
    // if (isrunning === 'true') {
    //     sendText('别人正在操作，请过一会再试')
    //     return
    // }
    var QLSName = bucketGet(tongzi, "QLS");
    QLSName = QLSName.split(',')
    if (QLSName == "" || QLSName == null) {
        notifyMasters("自动评价插件未配参青龙相关信息。")
        return;
    }

    let alreadypin = []
    for (let i = 0; i < QLSName.length; i++) {
        let currentQLS = null
        for (item of QLS) {
            if (item.name == QLSName[i]) {
                currentQLS = { host: item.host, client_id: item.client_id, client_secret: item.client_secret }
            }
        }
        var qlck = SelectQLSCK(currentQLS, 'JD_COOKIE')
        let repo = bucketGet(tongzi, "repo") || '6dy';
        let script = ''
        if (repo == '6dy') {
            script = '6dylan6_jdpro/jd_AutoEval.js'
        } else if (repo == 'MR') {
            script = 'HT944_MR_main/jd_comment_run.py'
        }
        Debug(script)
        // var cronid = SelectQLSCron(QLS, '6dylan6_jdpro/jd_AutoEval.js')
        // var cronid = SelectQLSCron(QLS, 'HT944_MR_main/jd_comment_run.py')
        var cronid = SelectQLSCron(currentQLS, script)
        let tongzipin = gettongzipin(qlck)
        if (tongzipin.length == 0) {
            return
        }
        sendText(`总共需要运行${tongzipin.length}个账号`)

        try {
            Debug(cronid + '这是cronid')
            if (cronid !== false && cronid.length > 0) {
                if (!tongzipin) {
                    Debug('没有可用的京东账号')
                    return
                }
                Debug(`正在检查容器 ${QLSName[i]} 的账号`)
                let currentckid = qlck.filter(item => tongzipin.includes(item.ckpin) && !alreadypin.includes(item.ckpin)).map(item => item.id)
                Debug(`容器 ${QLSName[i]} 找到待评价账号数: ${currentckid.length}`)
                if (currentckid.length == 0) {
                    continue
                }
                let disabledck = qlck.filter(item => item.status == 1).map(item => item.id)
                let allckid = qlck.map(item => item.id)
                let enableckid = allckid.filter(item => !disabledck.includes(item))
                let thisalreadypin = qlck.filter(item => tongzipin.includes(item.ckpin)).map(item => item.ckpin)
                alreadypin = alreadypin.concat(thisalreadypin)

                let subArrays = []
                if (script == '6dylan6_jdpro/jd_AutoEval.js' || script == '6dylan6_jdpro_main/jd_AutoEval.js') {
                    for (let i = 0; i < currentckid.length; i += 20) {
                        let subArray = currentckid.slice(i, i + 20);
                        subArrays.push(subArray);
                    }
                } else if (script == 'HT944_MR_main/jd_comment_run.py' || script == 'HT944_MR/jd_comment_run_main.py') {
                    subArrays.push(currentckid)
                }
                Debug(subArrays)
                let currentckindex = 0
                for (let item2 of subArrays) {
                    bucketSet(tongzi, "IsRunning", 'true');
                    // Debug(item2)
                    let otherckid = qlck.filter(item => !item2.includes(item.id)).map(item => item.id);
                    qlalldisabled(currentQLS.host, otherckid);
                    qlcronrun(currentQLS.host, cronid);
                    sendText('检索中...');
                    sleep(4500);
                    sendText(`本次运行${item2.length}个账号`);
                    sleep(4500);
                    qlenable(currentQLS.host, enableckid);
                    currentckindex = checkprogress(currentQLS.host, cronid[0], currentckindex);
                }
            } else if (cronid) {
                sendText('别人正在操作，请过一会再试')
            } else if (qlck) {
                Debug(`${QLSName[i]}获取脚本出错，请搜索青龙是否有${script}脚本`)
                notifyMasters(`${QLSName[i]}获取脚本出错，请搜索青龙是否有${script}脚本`)
                bucketSet(tongzi, "IsRunning", 'false');
            }
        } catch (e) {
            notifyMasters(e);
            notifyMasters(`自动评价${QLSName[i]}容器出错`)
            sendText("自动评价出错，请稍后再试")
            // qlenable(QLS.host, enableckid)
            bucketSet(tongzi, "IsRunning", 'false');
        }
    }
}

function gettongzipin(qlck) {
    let tongzipin = []
    var AllEvaluate = bucketGet(tongzi, "AllEvaluate");
    if (AllEvaluate === 'true' && isAdmin()) {
        tongzipin = qlck.filter(item => item.status === 0).map(item => item.ckpin)
    } else {
        //媒介
        let imType = ImType()
        //绑定的京东账号
        let jds = bucketKeys("pin" + imType.toUpperCase(), userId)
        // Debug(jds)
        if (jds.length == 0) {
            sendText("没有与你绑定的账号，请对我说：“登陆”")
            return []
        } else {
            // jdsIndex = []
            // for (i = 0; i < jds.length; i++) {
            //     jnStr = bucketGet("jdNotify", jds[i])
            //     if (jnStr) {
            //         // Debug(jnStr)
            //         jn = JSON.parse(jnStr)
            //         tongzipin.push(jn.ID)
            //     }
            // }
            tongzipin = jds
        }
    }
    Debug(tongzipin)
    return tongzipin
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

function qltoken(qldizhi, qlclient_id, qlclient_secret) {
    try {
        var body = request({
            url: qldizhi + "/open/auth/token?client_id=" + qlclient_id + "&client_secret=" + qlclient_secret,
            method: "get",
        });
        Debug('qltokens为' + body)
        var fhtoken = JSON.parse(body);
        qltokens = fhtoken.data.token;
    } catch (e) {
        Debug(e)
        qltokens = ''
    }
}

function getQlckjson(QLS, envname) {
    var qlselectbody = qlselect(QLS.host, 'crons', envname); // 尝试获取原始环境名对应脚本
    Debug('Cron()' + qlselectbody)
    var qlckjson = JSON.parse(qlselectbody);

    // 检查数据是否为空，如果为空则尝试获取备用脚本
    if (!qlckjson || qlckjson.data == "") {
        var fallbackEnvName;
        if (envname == '6dylan6_jdpro/jd_AutoEval.js') {
            fallbackEnvName = '6dylan6_jdpro_main/jd_AutoEval.js';
        } else if (envname == 'HT944_MR_main/jd_comment_run.py') {
            fallbackEnvName = 'HT944_MR/jd_comment_run.py';
        }

        if (fallbackEnvName) {
            qlselectbody = qlselect(QLS.host, 'crons', fallbackEnvName);
            Debug('Cron()' + qlselectbody)
            qlckjson = JSON.parse(qlselectbody);
        }
    }

    return qlckjson;
}

function SelectQLSCron(QLS, envname) {
    try {
        const qlckjson = getQlckjson(QLS, envname);

        if (!qlckjson || !qlckjson.data) {
            return false;
        }

        // 处理两种可能的数据结构
        const items = qlckjson.data.data || qlckjson.data;

        // 检查是否有正在运行的任务
        const hasRunningTask = Array.isArray(items) && items.some(item => item.status === 0);
        if (hasRunningTask) {
            Debug(`${QLS.host}青龙的自动评价脚本正在运行，请稍后再试`)
            return [];
        }

        // 查找匹配的任务
        for (const item of items) {
            if (item.command?.includes(`task ${envname}`)) {
                // 返回包含任务ID的数组
                return [item.id || item._id];
            }
        }

        return false; // 未找到匹配的任务

    } catch (e) {
        Debug(e);
        return false;
    }
}

function SelectQLSCK(QLS, envname) {
    try {
        // 获取 token
        qltoken(QLS.host, QLS.client_id, QLS.client_secret);

        // 获取环境变量数据
        const qlselectbody = qlselect(QLS.host, 'envs', envname);
        const qlckjson = JSON.parse(qlselectbody);

        // 检查数据有效性
        if (!qlckjson?.data) {
            Debug('获取环境变量数据失败');
            return false;
        }

        // 提取符合条件的环境变量
        const qlck = qlckjson.data
            .filter(item => item.name === envname)
            .map(item => ({
                id: item.id || item._id,
                status: item.status,
                ckpin: item.value.match(/pt_pin=([^;]+)/)?.[1] || ''
            }));

        // 检查是否找到任何匹配项
        return qlck.length > 0 ? qlck : false;

    } catch (e) {
        Debug(`SelectQLSCK 执行出错: ${e}`);
        return false;
    }
}


function qlselect(host, category, envname) {
    Debug(`${host}/open/${category}?searchValue=${envname}`)
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

function qlalldisabled(host, ckid) {
    var body = request({
        url: host + "/open/envs/disable",
        method: "put",
        headers: {
            "Authorization": "Bearer " + qltokens,
        },
        body: ckid
    });
    Debug('qlalldisabled()' + body)
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
    Debug('qlenable()' + body)
}

function qlcronrun(host, cronid) {
    Debug(cronid)
    var body = request({
        url: host + "/open/crons/run",
        method: "put",
        headers: {
            "Authorization": "Bearer " + qltokens,
        },
        body: cronid
    });
    Debug('qlcronrun()' + body)
}

function qllogs(host, logname) {
    let logtime = ''
    try {
        var body = request({
            url: host + "/open/logs?t=" + Date.now(),
            method: "GET",
            headers: {
                "Authorization": "Bearer " + qltokens,
            }
        });
        body = JSON.parse(body)
        if (body.dirs) {
            for (let item of body.dirs) {
                if (item.name === logname) {
                    logtime = logname + '/' + item.files[0] + '?'
                    Debug(logtime)
                    break;
                }
            }
        } else if (body.data) {
            for (let item of body.data) {
                if (item.title.includes(logname)) {
                    logtime = `${item.children[0].title}?path=${item.children[0].parent}&`
                    Debug(logtime)
                    break;
                }
            }
        }
        return logtime
    } catch (e) {
        Debug('qllogs()' + e)
        sendText('qllogs()' + e)
        sendText('获取日志出错，请检查插件青龙配置')
        return logtime
    }
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
    let totalarr = JSON.parse(body)
    totalarr = totalarr.data.split('\n')
    totalarr = totalarr.filter(item => {
        let cleanlog = item.includes('【京东账号')
            || item.includes('cookie已失效')
            || item.includes('待评价')
            || item.includes('等待')
            || item.includes('去评价')
            || item.includes('发布成功')
            || item.includes('执行结束...')
        return cleanlog
    })
    return totalarr
}

function checkprogress(host, cronid, currentckindex) {
    // let logtime = qllogs(host, '6dylan6_jdpro_jd_comment.js')
    let currentlog = []
    let alreadylog = []
    let currentsend = []
    let isdone = false
    let sendindex = 0
    while (!isdone) {
        currentlog = cronlog(host, cronid)
        if (arraysAreEqual(currentlog, alreadylog)) {
            sleep(5000)
        }
        currentsend = currentlog.slice(alreadylog.length, currentlog.length)
        for (let i of currentsend) {
            if (!i.includes('执行结束...')) {
                if (banReply == 'true') {
                    continue
                }
                if (i.includes('京东账号')) {
                    const pin = i.match(/开始【京东账号\d+】(.+?)\*/)[1];
                    sendText(`账号${++currentckindex}【${pin}】`)
                } else if (ChatID) {
                    if (i.includes('待评价')) {
                        sendText(i)
                        sendindex = 0
                    } else if (i.includes('去评价')) {
                        sendText('去评价 ' + ++sendindex)
                    } else {
                        sendText(i)
                    }
                } else {
                    sendText(i)
                }
                sleep(2000)
            } else {
                sendText('自动评价完成！')
                isdone = true
                bucketSet(tongzi, "IsRunning", 'false');
                return currentckindex
            }
        }
        alreadylog = currentlog
    }
    return currentckindex
}

function arraysAreEqual(array1, array2) {
    if (array1.length !== array2.length) {
        return false;
    }
    return array1.every((element, index) => element === array2[index]);
}
