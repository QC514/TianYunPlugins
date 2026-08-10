//[disable:false]
//[title: BBK账密登录]
//[rule:^(BBK版本|socksout|socksret|socks导入)$]
//[rule:^帐密(刷新|停止)$]
//[rule:^账密(刷新|停止)$]
//[rule:^(登陆|登录|短信登录|短信登陆|更新账号)$]
//[rule:^(全部账密|abc|enen|黑名单|全部黑名单|账密)刷新$]
//[author: qingge] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]
//[public: true] 
//[icon: http://www.icosky.com/icon/png/System/Boomy/Group+of+users.png]
//[price: 8.8] 
//[version: 1.0.0] 
//[admin: false] 
//[platform: qq,wx,tg,wb,qb]
//[priority: 9999999999]
//[service: 97393412]
//[description: 数据适配作者[specter]的数据,登陆成功后CK交给奥特曼内部同步到容器,需要搭建接口,需要(qls))权限<br/>增加群组使用开关<br/> 接入BBK  wskey短信登录，需要测试，有使用的人可联系我配合修复]
// [param: {"required":true,"key":"who_tong.bbk_qly","placeholder":"容器名称","name":"源青龙名称","desc":"获取名方法:奥特曼后台-容器管理--对接容器--名称"}]
// [param: {"required":true,"key":"who_tong.bbk_jk","placeholder":"BBK自建接口地址","name":"BBK.接口","desc":"http://192.168.3.154:5081,后面不要带/，BBK提供的docker接口填到这里"}]
// [param: {"required":true,"key":"who_tong.bbk_wskey_dxjk","placeholder":"BBK自建短信接口地址","name":"BBK.接口","desc":"http://192.168.3.154:5084,后面不要带/，BBK提供的docker接口填到这里"}]
// [param: {"required":true,"key":"who_tong.bbk_miyao","placeholder":"","name":"第三方短信接口密钥","desc":"不知道默认空即可"}]
// [param: {"required":false,"key":"who_tong.bbk_dx_kga1","bool":true,"placeholder":"false","name":"显示是否可用1","desc":"默认显示可用，bbk需要自己是否打勾"}]
// [param: {"required":false,"key":"who_tong.bbk_dx_kga2","bool":true,"placeholder":"false","name":"显示是否可用2","desc":"默认显示可用，bbk需要自己是否打勾"}]
// [param: {"required":false,"key":"who_tong.bbk_dx_kga3","bool":true,"placeholder":"false","name":"显示是否可用3","desc":"默认显示可用"}]
// [param: {"required":false,"key":"who_tong.bbk_dx_kga4","bool":true,"placeholder":"false","name":"显示是否可用4","desc":"默认显示可用"}]

// [param: {"spliter":true}]
// [param: {"required":false,"key":"who_tong.bbk_zhongjian","bool":true,"placeholder":"false","name":"使用中间页","desc":"默认不使用,使用中间页需要安装【xiaoqing】订阅的【BBK账密中间页】进行调用CK"}]
// [param: {"required":true,"key":"who_tong.bbk_token","placeholder":"","name":"BBK的token","desc":"用于加白,不填则不会自动更换白名单"}]
// [param: {"required":true,"key":"who_tong.bbk_gwip","placeholder":"","name":"BBK容器公网IP","desc":"如果你BBK容器部署在公网IP上请你填写,你的公网IP，用于加白,本奥特曼同个宽带内则留空"}]
// [param: {"required":true,"key":"who_tong.bbk_oldip","placeholder":"","name":"当前IP白名单","desc":"如果你是宽带这里忽略,不要更改这里的IP数据,如果填写了BBK token会自动根据当前白名单进行更换"}]
// [param: {"required":false,"key":"who_tong.pro_hmd","bool":true,"placeholder":"false","name":"过滤黑名单","desc":"默认不开启,需要开启过滤黑名单则需打勾,开启后则不会删除,配合：验证的次数"}]
// [param: {"spliter":true}]
// [param: {"required":true,"key":"who_tong.bbk_ckyc","placeholder":"","name":"检测更新延迟","desc":"填写数字，以秒为单位"}]
// [param: {"required":true,"key":"who_tong.bbk_hmdckyc","placeholder":"","name":"黑名单刷新延迟","desc":"填写数字，以秒为单位"}]
// [param: {"required":false,"key":"who_tong.bbk_add_tuisong","bool":true,"placeholder":"false","name":"刷新链接","desc":"默认不开启,开启则在刷新时推送【验证链接】给用户"}]
// [param: {"required":false,"key":"who_tong.bbk_pinck","bool":true,"placeholder":"false","name":"隐藏PIN","desc":"默认不开启,开启则隐藏PIN中间部分"}]
// [param: {"required":true,"key":"who_tong.bbk_yhm_ismin","placeholder":"","name":"验证群组推送用户","desc":"出现验证时一并推送至指定群组，群组ID,例如：wx:1564654654,qq:1564654654"}]
// [param: {"required":true,"key":"who_tong.bbk_ismin","placeholder":"","name":"安全验证通知群组","desc":"出现验证/密码错误等等情况推送到指定群组,渠道:群组ID,例如：wx:1564654654,qq:1564654654"}]
// [param: {"spliter":true}]
// [param: {"required":false,"key":"who_tong.bbk_pay","bool":true,"placeholder":"false","name":"是否收费","desc":"默认不开启,开启则按登录次数收费,需要配合(积分管理))"}]
// [param: {"required":true,"key":"who_tong.bbk_Charging","placeholder":"","name":"每次扣积分","desc":"每次扣取多少积分。例如:10"}]
// [param: {"required":true,"key":"who_tong.bbk_pay_name","placeholder":"","name":"积分不足引导","desc":"例如：请你先发送：积分充值"}]
// [param: {"spliter":true}]
// [param: {"required":false,"key":"who_tong.bbk_socks_ms","bool":true,"placeholder":"false","name":"使用模式","desc":"打开则开启顺序使用,默认不使用,说明:2个方式的socks5存储的位置不一样"}]

// [param: {"spliter":true}]
// [param: {"required":false,"key":"who_tong.bbk_mmzm","bool":true,"placeholder":"false","name":"密码错误","desc":"打开则删除账密数据,默认不开启"}]
// [param: {"required":false,"key":"who_tong.bbk_aqzm","bool":true,"placeholder":"false","name":"短信/语音","desc":"打开则到设定次数后删除账密数据,默认不开启"}]
// [param: {"required":true,"key":"who_tong.bbk_zmdel","placeholder":"","name":"安全验证","desc":"提示多少次后未更新  删除/拉黑    账密数据,输入数字。例如:10"}]
// [param: {"required":true,"key":"who_tong.bbk_tsy","placeholder":"","name":"登录成功后提示语","desc":"例如:登录成功!"}]
// [param: {"required":false,"key":"who_tong.bbk_usertz","bool":true,"placeholder":"false","name":"更新成功通知","desc":"打开则禁止推送更新成功的信息给用户"}]
// [param: {"required":true,"key":"who_tong.bbk_tzqd","placeholder":"","name":"通知渠道","desc":"wb,qq"}]
// [param: {"required":false,"key":"who_tong.bbk_glytz","bool":true,"placeholder":"false","name":"登录通知管理员","desc":"打开则会通知管理员登录提醒"}]
// [param: {"required":false,"key":"who_tong.bbk_qzkg","bool":true,"placeholder":"false","name":"群组开启","desc":"打开则禁止在群组内使用：账密登录,默认不开启"}]
// [param: {"required":true,"key":"who_tong.bbk_sxqd","placeholder":"","name":"失效提示","desc":"该账号已经失效，如需继续挂京豆请发送：登录"}]
// [param: {"required":true,"key":"who_tong.bbk_aqyz","placeholder":"","name":"安全验证引导语","desc":"请你点击上方链接过一下验证后在发送:账密登陆"}]
// [param: {"required":true,"key":"who_tong.bbk_jksb","placeholder":"","name":"接口访问失败","desc":"例如：登陆失败,请重新发送:账密登陆,留空则啥都不发送"}]
// [param: {"required":true,"key":"who_tong.bbk_dxzdynr","placeholder":"","name":"短信尾部自定义","desc":"默认：目前账密稳定，推送使用：账密登录"}]
// [param: {"required":false,"key":"who_tong.qx_kg","bool":true,"placeholder":"false","name":"不懂莫乱开","desc":"自用功能"}]
// [param: {"required":true,"key":"who_tong.bbk_xkip","placeholder":"","name":"ip代理api地址","desc":",这里只有短信需要用到,目前测试就品赞的3分钟的IP可用,只行对IP加白名单：115.28.82.74"}]
// [param: {"required":true,"key":"who_tong.bbk_rlyz","placeholder":"","name"人脸登录尾部自定义","desc":"默认：目前账密稳定，推送使用：账密登录"}]
let userId = GetUserID();//获取用户ID
var GetContent = GetContent()
var imType = ImType()
var checkJS = false
var bbk_yhm_ismin = bucketGet("who_tong", "bbk_yhm_ismin")//青龙
var bbk_xkip = bucketGet("who_tong", "bbk_xkip")//青龙
var ismin = bucketGet("who_tong", "bbk_ismin")//青龙
var zhongjianye = bucketGet("who_tong", "bbk_zhongjian")//中间页
var zmqly = bucketGet("who_tong", "bbk_qly")//青龙
var bbk_glytz = bucketGet("who_tong", "bbk_glytz")//管理员通知
var bbk_jk = bucketGet("who_tong", "bbk_jk")//BBK接口地址
var bbk_wskey_dxjk = bucketGet("who_tong", "bbk_wskey_dxjk")//BBK接口短信地址
var bbk_tsy = bucketGet("who_tong", "bbk_tsy")//登录成功后提示
var stxs = bucketGet("who_tong", "bbk_tzqd")//通知渠道
var jcsx = bucketGet("who_tong", "bbk_sxqd")//通知渠道
var bbk_qzkg = bucketGet("who_tong", "bbk_qzkg")//通知渠道
var bbk_aqyz = bucketGet("who_tong", "bbk_aqyz")//安全验证通知
var bbk_aqzm = bucketGet("who_tong", "bbk_aqzm")//安全验证账密删除数据
var bbk_usertz = bucketGet("who_tong", "bbk_usertz")//更新成功的通知开关
var mmcw = bucketGet("who_tong", "bbk_mmzm")//模式选择
var bbk_delck = bucketGet("who_tong", "bbk_delck")//模式选择
var bbk_ckyc = parseInt(bucketGet("who_tong", "bbk_ckyc"))
var bbk_hmdckyc = parseInt(bucketGet("who_tong", "bbk_hmdckyc"))


var bbk_socks_ms = bucketGet("who_tong", "bbk_socks_ms")//限制同时登陆


var bbk_jksb = bucketGet("who_tong", "bbk_jksb")
var bbk_add_tuisong = bucketGet("who_tong", "bbk_add_tuisong")
var bbk_zmdel = parseInt(bucketGet("who_tong", "bbk_zmdel"))//通知多少次后未更新删除
var bbk_pinck = bucketGet("who_tong", "bbk_pinck")
//----------------------------
var pro_hmd = bucketGet("who_tong", "pro_hmd")//开启过滤黑名单
var vkey = bucketGet("who_tong", "bbk_miyao")
var bbk_rlyz = bucketGet("who_tong", "bbk_rlyz")

var bbk_dx_kga1 = bucketGet("who_tong", "bbk_dx_kga1")
var bbk_dx_kga2 = bucketGet("who_tong", "bbk_dx_kga2")
var bbk_dx_kga3 = bucketGet("who_tong", "bbk_dx_kga3")
var bbk_dx_kga4 = bucketGet("who_tong", "bbk_dx_kga4")

//------------------------------
var bbk_pay = bucketGet("who_tong", "bbk_pay")//是否开启收费
var bbk_Charging = bucketGet("who_tong", "bbk_Charging")//单次扣多少积分
var zd_jfts = bucketGet("who_tong", "bbk_pay_name")//单次扣多少积分
var bbk_zdh = bucketGet("who_tong", "bbk_zdhua")//是否开启收费
//----------------------------
var cookie = ""
var login = false
var ck_pin = "", IP = ""
var PIN_HB = []//合并过期PIN
var loginA = {}
var encryptedPwd = "", bbk_add_yz = false, qt_name = "", uid = ""
var cuowu = false
//----------------------------
var cg = 0//登录成功
var dx = 0//出现短信
var sb = 0//其他原因
var zs = 0//总数量
var yx = 0//有效账号
var ysx = 0//失效数量
var qtbl = 0//不是账密
var mmtj = 0//密码统计
var rltj = 0//人脸统计
var pftj = 0//频繁统计
var hmdtj = 0//黑名单统计
var hmd_kg = false//黑名单开关
let containerEnv = [];
// 存储常量配置（独立命名空间不变）
const DATA_NS = "who_socks5";          // 原始数据存储命名空间
const POS_NS = "socks5_position";  // 位置标记独立存储命名空间
const POS_KEY = "current_pos";  // 位置标记的Key
const SOCKS5_NS = "who_socks5"; // socks5 数据存储命名空间
try {
    importJs("qinglong.js");
    importJs("CryptoJS.js");
    importJs("who-hs.js");
} catch (err) {
    checkJS = true
}
const config = getConfig();

function getConfig() {
    return {
        qlName: bucketGet("who_tong", "bbk_qly") || ""
    };
}
let text_bbk = `关于BBK的使用说明：
独享容器的情况下:
不需要同步多容器CK[调用青龙]里面需要留空
如果你需要同步多容器CK，需要配置[调用青龙]和BBK容器内的青龙一致
如果你只需要[调用青龙]的CK同步多容器,那么不要打勾[是否删除CK]

-------------
黑名单说明：
1.针对指令：【账密刷新】【全部账密刷新】支持黑名单过滤条件
2.黑名单指令：【黑名单刷新】【全部黑名单刷新】
3.开启黑名单过滤后,则不会删除黑名单账密数据
------------
8.26更新说明：
1.获取实时CK进行检测刷新[降低重复刷新]
2.优化黑名单显示数量浮动
3.存储当前IP白名单,IP变更后会使用当前IP与最新IP进行更换,类似代理IP的加白模式
4.如果需要自动更换。需要填写你当前使用的IP,否则IP变时指定IP进行更换
9.11更新说明:
1.修复最新人脸的问题
11.24更新说明:
  1.增加socks5顺序使用模式
12.5 更新说明：
  1.增加批量导入socks5,仅支持万安格式
  2.导入socks5指令【socks导入】
  3.查询socks5的总数据：【socksout】
  4.重置使用socks5位置：【socksret】
  5.购买socks地址【推荐】：https://user.benfuip.com/main/register?aff=xiaoqing20
  6.购买【特价独享1M】【T节点】地区任意选，推荐不要选IP太少的，最少100+以上的，购买后并把IP刷成【前面三段一致的】
  `
function mian() {
    if (checkJS) {
        if (isAdmin()) notifyMasters("到群内下载[qinglong.js和CryptoJS.js]上传到plugin/replies的文件内");
        return;
    }
    Debug(`指定获取青龙容器名称:${zmqly}`);
    if (!zmqly) {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置");
        return;
    }
    let containeta = qls(zmqly);
    let container, containerEnv;
    for (let qx = 0; qx < 5; qx++) {
        try {
            container = Qinglong(containeta.host, containeta.client_id, containeta.client_secret);
            containerEnv = container.ApiQL("envs", "", "get", "").data;
            break;
        } catch (e) {
            notifyMasters(`【BBK账密登录】链接容器【${zmqly}】失败，请检查配置是否正确或网络是否正常`);
            return;
        }
    }
    let cookieObj = containerEnv.filter(_data => _data.name == "JD_COOKIE");
    cookieObj.forEach(obj => {
        let pina = obj.value.match(/(?<=pt_pin=)[^;]+/g);
        let pin_ck = bucketGet("AutoJdck", pina);
        if (!pin_ck) return;

        zs++;
        // 黑名单过滤逻辑合并
        if (pro_hmd == "true" || pro_hmd == true) {
            var zm_hmd = bucketGet("who_pro_hmd", pina)
            if (zm_hmd != "") {
                hmdtj++
                //console.log(`黑名单:${pina}`)
                if (hmd_kg == false) {
                    // console.log(`普通刷新时跳过黑名单`)
                    return; // 普通刷新时跳过黑名单
                }
                // console.log(`黑名单刷新时继续处理`)
                // 
            }
        }
        pin_ck = JSON.parse(pin_ck);

        let jnStr = bucketGet("jdNotify", pina);
        let jn;
        if (jnStr && isJsonString(jnStr)) {
            jn = JSON.parse(jnStr);
            var cookie = `pt_key=${jn.PtKey};pt_pin=${jn.ID};`;
        } else {
            //Debug(`jdNotify数据异常，pina=${pina}，jnStr=${jnStr}`);
            //notifyMasters(`jdNotify数据异常，pina=${pina}，请检查是否权限不足或重新给予权限`);
            //return; // 跳过本次
            var cookie = obj.value
        }

        if (jdck(cookie)) {
            //Debug("该用户处于CK有效,跳过刷新+" + decodeURIComponent(pina));
            yx = yx + 1
        } else {
            Debug("该用户CK失效\n" + decodeURIComponent(pina) + "\n" + getStatMsg());

            ysx++
            pwdLoginApi(pina, pin_ck.account, pin_ck.password, false);
            if (login) {
                handleLoginSuccess(pina);
                login = false;
            }

            if (cuowu) {
                notifyMasters(decodeURIComponent(pina) + ",BBK-IP黑了,退出任务");
                // 退出当前forEach循环：通过抛出异常
                throw new Error("BBK-IP黑了,退出任务");
            }

            if (hmd_kg == true) {
                if (bbk_hmdckyc == "") {
                    sleep(bbk_ckyc * 1000);
                } else {
                    sleep(bbk_hmdckyc * 1000);
                }

            } else {
                sleep(bbk_ckyc * 1000);
            }


        }
        let text = bucketGet("who_tong", "bbk_tingzhi")
        if (text == "true") {
            bucketSet("who_tong", "bbk_tingzhi")
            bucketSet("who_tong", "bbk_jincheng")
            notifyMasters("开启强制退出刷新")
            throw new Error("开启强制退出刷新");
        }
    });
    notifyMasters(getStatMsg());
    let lineArr = PIN_HB.join('\n').split('\n').filter(line => line.trim() !== '');
    let lineCount = lineArr.length;
    //    notifyMasters(`总共有 ${lineCount} 个黑名单账号`);

    // 每35行分割推送
    for (let i = 0; i < lineArr.length; i += 35) {
        let part = lineArr.slice(i, i + 35).join('\n');
        notifyMasters(part);
        pushToGroups(part)
    }
}
function abcmian() {
    if (checkJS) {
        if (isAdmin()) notifyMasters("到群内下载[qinglong.js和CryptoJS.js]上传到plugin/replies的文件内");
        return;
    }
    Debug(`指定获取青龙容器名称:${zmqly}`);
    if (!zmqly) {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置");
        return;
    }
    let containeta = qls(zmqly);
    let container, containerEnv;
    for (let qx = 0; qx < 5; qx++) {
        try {
            container = Qinglong(containeta.host, containeta.client_id, containeta.client_secret);
            containerEnv = container.ApiQL("envs", "", "get", "").data;
            break;
        } catch (e) {
            notifyMasters(`【BBK账密登录】链接容器【${zmqly}】失败，请检查配置是否正确或网络是否正常`);
            return;
        }
    }
    let cookieObj = containerEnv.filter(_data => _data.name == "JD_COOKIE");
    cookieObj.forEach(obj => {
        let pina = obj.value.match(/(?<=pt_pin=)[^;]+/g);
        let pin_ck = bucketGet("AutoJdck", pina);
        if (!pin_ck) return;
        zs++;
        // 黑名单过滤逻辑合并
        if (pro_hmd == "true" || pro_hmd == true) {
            var zm_hmd = bucketGet("who_pro_hmd", pina)
            if (zm_hmd != "") {
                hmdtj++
                console.log(`黑名单:${pina}`)
                quchong(`黑名单:${pina}`, pina)
                if (hmd_kg == false) {
                    console.log(`普通刷新时跳过黑名单`)
                    return; // 普通刷新时跳过黑名单
                }

            }
            ysx++
        }
        console.log("该用户CK失效\n" + decodeURIComponent(pina));
    });
    notifyMasters(getStatMsg());
    let lineArr = PIN_HB.join('\n').split('\n').filter(line => line.trim() !== '');
    let lineCount = lineArr.length;
    //    notifyMasters(`总共有 ${lineCount} 个黑名单账号`);

    // 每35行分割推送
    for (let i = 0; i < lineArr.length; i += 35) {
        let part = lineArr.slice(i, i + 35).join('\n');
        notifyMasters(part);
        pushToGroups(part)
    }
}
// 辅助函数：处理登录成功后的CK同步
function handleLoginSuccess(pina) {
    if (zhongjianye == "true") {
        Debug("使用中间页");
        for (let j = 0; j < 3; j++) {
            let qljs = bucketGet("A_zm_ck", pina);
            if (qljs) {
                bucketSet("A_zm_ck", pina);
                breakIn(qljs);
                break;
            }
            sleep(3000);
        }
    } else {
        let qljs = bucketGet("who_tong", "bbk_qljson");
        if (qljs) subCKToXZ(pina);
    }
}

// 辅助函数：统计信息
function getStatMsg() {
    let mode = hmd_kg ? "【黑名单刷新】" : "【普通刷新】";
    return `${mode}：刷新数据:
总账密数-->${zs}
有效数量-->${yx}
失效数量-->${ysx}
---------------
黑名单数量-->${hmdtj}
成功数量-->${cg}
---------------
验证数量-->${dx}
人脸数量-->${rltj}
密错数量-->${mmtj}
频繁数量-->${pftj}
---------------
其他数量-->${sb}`;
}
//分割
// 优化后的分割函数：每35行分割为一段
function fenge(txt) {
    const lines = txt.split('\n').filter(line => line.trim() !== '');
    const textArr = [];
    for (let i = 0; i < lines.length; i += 50) {
        textArr.push(lines.slice(i, i + 50).join('\n'));
    }
    return textArr;
}


// 辅助函数：推送到指定群组
function pushToGroups(content) {
    if (!ismin) return;
    ismin.split(",").forEach(item => {
        let [imType, groupCode] = item.split(":");
        push({
            imType,
            userID: "",
            title: "",
            groupCode,
            content
        });
    });
}


function qbmian() {

    Debug(`指定获取青龙容器名称:${zmqly}`)
    if (zmqly) {
        // ql_a = qls(ql_name)
    } else {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置")
    }
    let containeta = qls(zmqly)
    let container = ""
    let containerEnv = ""
    let pin_ck = ""
    let bbk_yz = false
    try {
        container = Qinglong(containeta.host, containeta.client_id, containeta.client_secret)
        containerEnv = container.ApiQL("envs", "", "get", "").data

    } catch (e) {
        notifyMasters("【BBK账密登录】链接容器【" + zmqly + "】失败，请检查配置是否正确或网络是否正常")
        return
    }


    let elmckUserIdArr = bucketKeys("AutoJdck")

    for (let k = 0; k < elmckUserIdArr.length; k++) {
        pin_ck = bucketGet("AutoJdck", elmckUserIdArr[k])
        // get_tx(elmckUserIdArr[k] + "------")
        let st = 0
        let cookieObj = containerEnv.filter(function (_data) {
            return _data.name == "JD_COOKIE" && _data.value.indexOf(elmckUserIdArr[k]) != -1
        });
        if (cookieObj.length == 0) {
            // get_tx("青龙内未找到该CK:" + elmckUserIdArr[k])
            if (pin_ck.indexOf("account") != -1) {
                pin_ck = JSON.parse(pin_ck)
                //存在account，是账密数据
                //get_tx("存在account，是账密数据"+pin_ck)
                ysx++
                pwdLoginApi(elmckUserIdArr[k], pin_ck.account, pin_ck.password)
                //调用青龙
                if (login) {
                    if (zhongjianye == "true") {
                        for (let j = 0; j < 3; j++) {

                            let qljs = bucketGet("A_zm_ck", elmckUserIdArr[k])
                            if (qljs == "") {

                            } else {
                                bucketSet("A_zm_ck", elmckUserIdArr[k])
                                breakIn(qljs)
                                j = 9
                            }
                            sleep(2000)
                        }

                    } else {

                        let qljs = bucketGet("who_tong", "bbk_qljson")
                        if (qljs == "") {
                            //不获取CK
                        } else {
                            //获取CK
                            subCKToXZ(elmckUserIdArr[k])
                        }
                    }
                    login = false
                }
            } else {
                qtbl = qtbl + 1
            }
        } else {
            pin_ck = JSON.parse(pin_ck)
            //get_tx("找到找到该PIN：" + cookieObj[0].value)
            let jc_ck = jdck(cookieObj[0].value)

            if (jc_ck) {
                Debug("该用户处于CK有效,跳过刷新+" + decodeURIComponent(elmckUserIdArr[k]))
                yx = yx + 1
            } else {
                Debug("该用户CK失效\n" + decodeURIComponent(elmckUserIdArr[k]))
                if (hmd_kg == false) {
                    if (pro_hmd == "true" || pro_hmd == true) {
                        //开启过滤黑名单
                        var zm_hmd = bucketGet("who_pro_hmd", elmckUserIdArr[k])
                        if (zm_hmd == "") {

                        } else {
                            console.log(`黑名单:${elmckUserIdArr[k]}`)
                            hmdtj = hmdtj + 1
                            continue
                        }
                    }
                } else {
                    hmdtj = hmdtj + 1
                    if (pro_hmd == "true" || pro_hmd == true) {
                        //开启过滤黑名单
                        var zm_hmd = bucketGet("who_pro_hmd", elmckUserIdArr[k])
                        if (zm_hmd == "") {
                            continue
                        } else {
                            console.log(`黑名单:${elmckUserIdArr[k]}`)


                        }
                    }
                }
                ysx++
                pwdLoginApi(elmckUserIdArr[k], pin_ck.account, pin_ck.password)
                //调用青龙
                if (login) {
                    if (zhongjianye == "true") {
                        Debug("使用中间页")
                        for (let j = 0; j < 3; j++) {

                            let qljs = bucketGet("A_zm_ck", elmckUserIdArr[k])
                            if (qljs == "") {

                            } else {
                                bucketSet("A_zm_ck", elmckUserIdArr[k])
                                breakIn(qljs)
                                j = 9
                            }
                            sleep(2000)
                        }

                    } else {
                        let qljs = bucketGet("who_tong", "bbk_qljson")
                        if (qljs == "") {
                            //不获取CK
                        } else {
                            //获取CK
                            subCKToXZ(elmckUserIdArr[k])
                        }
                    }
                    login = false
                }
            }

        }
        if (cuowu == true) {
            notifyMasters(decodeURIComponent(pina) + ",BBK-IP黑了,退出任务")
            k == 99999999
            //return
        }
    }

    notifyMasters(`JD账密刷新数据:
总账密数-->${zs}
有效数量-->${yx}
失效数量-->${ysx}
---------------
黑名单数量-->${hmdtj}
成功数量-->${cg}
---------------
验证数量-->${dx}
人脸数量-->${rltj}
密错数量-->${mmtj}
频繁数量-->${pftj}
---------------
其他数量-->${sb}`)
    let yhm = ""
    for (let i = 0; i < PIN_HB.length; i++) {
        yhm += `${PIN_HB[i]}\n`
        if (i % 20 === 0) {
            notifyMasters(yhm)
            if (ismin == "") {
            } else {
                var jd_grqd = ismin.split(",")
                for (let k = 0; k < jd_grqd.length; k++) {
                    let grqd = jd_grqd[k].split(":")
                    push({
                        imType: grqd[0],
                        userID: "",
                        title: "",
                        groupCode: grqd[1],
                        content: yhm,
                    });
                }
            }
            yhm = ""
        }
    }
    if (ismin == "") {
    } else {
        var jd_grqd = ismin.split(",")
        for (let k = 0; k < jd_grqd.length; k++) {
            let grqd = jd_grqd[k].split(":")
            push({
                imType: grqd[0],
                userID: "",
                title: "",
                groupCode: grqd[1],
                content: yhm,
            });
        }
    }
    notifyMasters(yhm)

}
function enensx() {

    Debug(`指定获取青龙容器名称:${zmqly}`)
    if (zmqly) {
        // ql_a = qls(ql_name)
    } else {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置")
    }
    let containeta = qls(zmqly)
    let container = ""
    let containerEnv = ""
    let pin_ck = ""
    let bbk_yz = false
    try {
        container = Qinglong(containeta.host, containeta.client_id, containeta.client_secret)
        containerEnv = container.ApiQL("envs", "", "get", "").data

    } catch (e) {
        notifyMasters("【BBK账密登录】链接容器【" + zmqly + "】失败，请检查配置是否正确或网络是否正常")
        return
    }


    let elmckUserIdArr = bucketKeys("AutoJdck")

    for (let k = 0; k < elmckUserIdArr.length; k++) {
        pin_ck = bucketGet("AutoJdck", elmckUserIdArr[k])
        // get_tx(elmckUserIdArr[k] + "------")
        let st = 0
        let cookieObj = containerEnv.filter(function (_data) {
            return _data.name == "JD_COOKIE" && _data.value.indexOf(elmckUserIdArr[k]) != -1
        });
        if (cookieObj.length == 0) {
            //get_tx("青龙内未找到该CK:" + elmckUserIdArr[k])
            if (pin_ck.indexOf("account") != -1) {
                pin_ck = JSON.parse(pin_ck)
                //存在account，是账密数据
                //get_tx("存在account，是账密数据"+pin_ck)
                ysx++

                pwdLoginApi(elmckUserIdArr[k], pin_ck.account, pin_ck.password)
                //调用青龙
                if (login) {
                    if (zhongjianye == "true") {
                        for (let j = 0; j < 3; j++) {

                            let qljs = bucketGet("A_zm_ck", elmckUserIdArr[k])
                            if (qljs == "") {

                            } else {
                                bucketSet("A_zm_ck", elmckUserIdArr[k])
                                breakIn(qljs)
                                j = 9
                            }
                            sleep(2000)
                        }

                    } else {

                        let qljs = bucketGet("who_tong", "bbk_qljson")
                        if (qljs == "") {
                            //不获取CK
                        } else {
                            //获取CK
                            subCKToXZ(elmckUserIdArr[k])
                        }
                    }
                    login = false
                }
            } else {
                qtbl = qtbl + 1
            }
        } else {
            jd_enen(cookieObj[0].value)
            pin_ck = JSON.parse(pin_ck)
            pwdLoginApi(elmckUserIdArr[k], pin_ck.account, pin_ck.password)
            //调用青龙
            if (login) {
                if (zhongjianye == "true") {
                    Debug("使用中间页")
                    for (let j = 0; j < 3; j++) {

                        let qljs = bucketGet("A_zm_ck", elmckUserIdArr[k])
                        if (qljs == "") {

                        } else {
                            bucketSet("A_zm_ck", elmckUserIdArr[k])
                            breakIn(qljs)
                            j = 9
                        }
                        sleep(2000)
                    }

                } else {
                    let qljs = bucketGet("who_tong", "bbk_qljson")
                    if (qljs == "") {
                        //不获取CK
                    } else {
                        //获取CK
                        subCKToXZ(elmckUserIdArr[k])
                    }
                }
                login = false
            }
            //get_tx("找到找到该PIN：" + cookieObj[0].value)


        }
        if (cuowu == true) {
            notifyMasters(decodeURIComponent(pina) + ",BBK-IP黑了,退出任务")
            k == 99999999
            //return
        }
    }

    notifyMasters(`JD账密刷新数据:
总账密数-->${zs}
有效数量-->${yx}
---------------
失效数量-->${ysx}
成功数量-->${cg}
失败数量-->${dx}
---------------
人脸数量-->${rltj}
密错数量-->${mmtj}
频繁数量-->${pftj}
其他数量-->${sb}`)

}
function phone(mobile) {
    return mobile.slice(0, 3) + '***' + mobile.slice(7)
}
function pwdLoginApi(PIN, username, password) {
    if (bbk_socks_ms == "true") {
        // console.warn(`bbk_socks:${bbk_socks},bbk_socks_ms:${bbk_socks_ms},${socks_ipxx}`)
        socks5proxy = socks_mian("socks5-get", username)
    }
    let bbk_cs = 0
    for (let i = 0; i < 3; i++) {
        if (bbk_socks_ms == "true") {

            var obj = {
                username: username,
                password: password,
                socks5proxy: socks5proxy
            }
        } else {
            var obj = {
                username: username,
                password: password
            }
        }
        var qd = stxs.split(",")
        body = request({
            method: "post",
            url: `${bbk_jk}/xcx/pwdLoginApi`,
            body: JSON.stringify(sign(obj)),
            headers: {
                "Content-Type": "application/json; charset=utf-8"
            },
            dataType: "json",
            timeOut: 80000
        })
        if (body) {

            Debug("账密登录情况：" + JSON.stringify(body) + "-" + body.msg)
            if (body.msg == "登录失败:账号或密码不正确" || body.msg == "账号或密码不正确") {
                i = 5
                breakIn(`CK删除+${PIN}`);
                get_tx(`账号->${decodeURIComponent(PIN)}\n-->${body.msg}`)
                if (mmcw == "true") {
                    bucketSet("AutoJdck", PIN)
                    bucketSet("AutoJdpin", PIN)
                    bucketSet("who_pro_hmd", PIN)


                }
                if (bbk_socks_ms == "true") {
                } else {
                    huifucs(socks5)
                }
                mmtj = mmtj + 1
                if (GetContent == "账密登录" || GetContent == "账密登陆" || GetContent == "帐密登陆" || GetContent == "帐密登陆" || GetContent == "登录" || GetContent == "登陆") {
                } else {
                    for (let k = 0; k < qd.length; k++) {
                        bind = bucketGet("pin" + qd[k].toUpperCase(), PIN)
                        TXfs_tuisong(qd[k], bind, `===JD账号->账密更新失败===
东东账号->${decodeURIComponent(PIN)}
登录失败->${body.msg}`)
                    }
                    return
                }
            }
            if (body.msg == "访问服务器出错" || body.msg == "check1请求失败,请重新触发登录验证" || body.msg == "页面已超时，请返回重试" || body.msg == "sid请求失败,请重新触发登录验证" || body.msg == "API请求Timeout失败，请检查网路重试" || body.msg == "refresh验证失败,请重新触发登录验证" || body.msg == "sid请求失败,登录错误,请重试" || body.msg == "执行错误了哦" || body.msg == "请求没有返回数据" || body.msg == "服务器链接失败了哦" || body.msg == "请重新触发登录验证" || body.msg == "接收内容为空") {

                if (body.msg == "API请求Timeout失败，请检查网路重试") {
                    notifyMasters(socks5proxy + "--IP请求超时")
                    console.log(socks5proxy + "--IP请求超时--" + username)
                }


                // dx = dx + 1

                bbk_cs++
                if (bbk_cs > 3) {
                    get_tx(`账号->${decodeURIComponent(PIN)}\n--->登陆失败,重新发送：账密登录`)
                    quchong(decodeURIComponent(PIN) + ",原因:" + body.msg, decodeURIComponent(PIN))
                    i = 5
                } else {
                    sleep(2000)
                }
                continue
            }
            if (body.msg == "API请求Timeout失败，请检查网路重试") {
                notifyMasters(`发现该代理超时过大${socks5proxy},有可能失效,及时更换`)
                if (bbk_socks_ms == "true") {
                    socks5proxy = socks_mian("socks5-get", username)
                    console.log(socks5proxy + "---" + username)
                }
                bbk_cs++
                if (bbk_cs > 3) {
                    quchong(decodeURIComponent(PIN) + ",原因:" + body.msg, decodeURIComponent(PIN))
                    return
                }

                continue
            }
            if (body.code == 128 || body.msg == "为了账号安全需要" || body.msg == "您的账号存在风险，为了账号安全需要短信/语音验证，是否继续？" || body.msg == "需要验证" || body.msg == "登录失败:您的账号存在安全风险，为了您的资产及隐私安全，请电话联系京东客服（950618)") {
                i = 5
                breakIn(`账密添加+${PIN}`);
                //get_tx("出现安全验证？")
                bucketSet("Auto_IP", username)
                dx = dx + 1
                //出现安全验证
                if (bbk_aqzm == "true") {
                    var pin_del = bucketGet("AutoJdpin", PIN)
                    if (pin_del == "") {
                        pin_del = 0
                        bucketSet("AutoJdpin", PIN, 1)
                    } else {
                        if (parseInt(pin_del) >= bbk_zmdel) {
                            console.log("该账号已达到设定次数," + decodeURIComponent(PIN))
                            if (pro_hmd == "true") {
                                //开启过滤黑名单
                                bucketSet("who_pro_hmd", PIN, PIN)
                            } else {
                                notifyMasters(PIN + "该账密数据已达到设定次数未过验证,删除掉,并重置")
                                bucketDel("AutoJdck", PIN)
                                bucketDel("AutoJdpin", PIN)
                            }
                        } else {
                            bucketSet("AutoJdpin", PIN, parseInt(pin_del) + 1)
                        }
                    }
                }
                quchong(`${decodeURIComponent(PIN)},原因:验证码`, decodeURIComponent(PIN))
                if (GetContent == "账密登录" || GetContent == "账密登陆" || GetContent == "帐密登陆" || GetContent == "帐密登陆" || GetContent == "登录" || GetContent == "登陆") {
                    let w = asse(`账号->${decodeURIComponent(PIN)}\n安全验证,点击链接-->${body.jmp_url}\n-->-->请你点击上方链接过一下.验证后在回复：1`)
                    if (w == "" || w == false || w == "false") {
                        bbk_add_yz = true
                    } else {
                        bbk_add_yz = true
                    }

                } else {

                   /* for (let k = 0; k < qd.length; k++) {
                        bind = bucketGet("pin" + qd[k].toUpperCase(), PIN)
                        if (bind == "") {

                        } else {
                            if (bbk_aqyz == "" || bbk_aqyz == "null") {
                                if (bbk_add_tuisong == "true") {
                                    TXfs_tuisong(qd[k], bind, `===JD账号->账密更新失败===\n东东账号->${decodeURIComponent(PIN)}\n安全验证,点击链接-->${body.jmp_url}\n请你点击上方链接过一下验证后在回复:1`)

                                } else {

                                    TXfs_tuisong(qd[k], bind, `===JD账号->账密更新失败===\n东东账号->${decodeURIComponent(PIN)}\n您的账号更新失败\n请您重新发送:账密登录`)
                                }
                            } else {
                                if (bbk_add_tuisong == "true") {
                                    TXfs_tuisong(qd[k], bind, `===JD账号->账密更新失败===
东东账号->${decodeURIComponent(PIN)}
安全验证,点击链接-->${body.jmp_url}
${bbk_aqyz}`)
                                } else {
                                    TXfs_tuisong(qd[k], bind, `===JD账号->账密更新失败===
东东账号->${decodeURIComponent(PIN)}
失败原因->需要验证码登录
处理方法->您的账号已失效,请您重新登陆
请您重新发送:账密登录`)
                                }
                            }
                        }

                    }*/
                }
                return
            }
            if (body.msg == "操作过于频繁，请24小时后再试，或先使用其他方式登录") {
                i = 5
                get_tx(`账号->${decodeURIComponent(PIN)}\n-->登录失败,请您先使用短信验证码登录`)
                quchong(decodeURIComponent(PIN) + ":登录失败,原因:" + body.msg, decodeURIComponent(PIN))
                sb = sb + 1
                sleep(1000)
                return
            }
            if (body.msg == "强风控账号,登陆失败" || body.msg == "您的账号在当前应用已注销，无法继续使用，如需使用请重新注册新账号") {
                i = 5
                breakIn(`账密添加+${PIN}`);
                get_tx(`账号->${decodeURIComponent(PIN)}\n-->${body.msg}`)
                quchong(decodeURIComponent(PIN) + ":登录失败,原因:" + body.msg, decodeURIComponent(PIN))
                sb = sb + 1
                // sleep(1000)
               if (bbk_aqzm == "true") {
                    var pin_del = bucketGet("AutoJdpin", PIN)
                    if (pin_del == "") {
                        pin_del = 0
                        bucketSet("AutoJdpin", PIN, 1)
                    } else {
                        if (parseInt(pin_del) >= bbk_zmdel) {
                            console.log("该账号已达到设定次数," + decodeURIComponent(PIN))
                            if (pro_hmd == "true") {
                                //开启过滤黑名单
                                bucketSet("who_pro_hmd", PIN, PIN)
                            } else {
                                notifyMasters(PIN + "该账密数据已达到设定次数未过验证,删除掉,并重置")
                                bucketDel("AutoJdck", PIN)
                                bucketDel("AutoJdpin", PIN)
                            }
                        } else {
                            bucketSet("AutoJdpin", PIN, parseInt(pin_del) + 1)
                        }
                    }
                }
                return
            }
            if (body.msg == "验证码服务器链接失败" || body.msg == "验证码验证失败,请重新触发登录验证") {
                i = 5
                get_tx(`账号->${decodeURIComponent(PIN)}\n-->登录失败,请您先使用短信验证码登录`)
                quchong(decodeURIComponent(PIN) + ":登录失败,原因:" + body.msg, decodeURIComponent(PIN))
                sb = sb + 1
                //sleep(12000)
                return
            }
            if (body.code == 200) {
                login = true
                cg = cg + 1
                i = 5
                let pin_del = bucketGet("AutoJdpin", PIN)
                if (pin_del == "") {
                } else {
                    bucketSet("AutoJdpin", PIN)
                }
                //登录成功
                get_tx(`${bbk_tsy}->${body.msg}`)
                // 假设这是你的原始字符串
                let str = body.msg
                let start = str.indexOf('[') + 1;
                // 找到第一个右方括号的位置
                let end = str.indexOf(']');
                // 截取方括号之间的内容
                //ck_pin = encodeURIComponent(str.substring(start, end));
                ck_pin = str.substring(start, end)
                bucketSet("pin" + imType.toUpperCase(), ck_pin, GetUserID())
                bucketSet("who_pro_hmd", ck_pin)
                if (bbk_usertz == "true") {
                    //Debug("禁止推送更新状态给用户")
                } else {
                    if (GetContent == "账密刷新" || GetContent == "B账密刷新") {
                        for (let k = 0; k < qd.length; k++) {
                            bind = bucketGet("pin" + qd[k].toUpperCase(), ck_pin)

                            if (bind == "") {

                            } else {
                                TXfs_tuisong(qd[k], bind, `===JD账号->更新成功===\n东东账号：${ck_pin}`)
                                sleep(1000)
                            }
                        }
                    }
                }
            } else {

                let msg = body.msg
                if (msg.indexOf("非白名单") != -1) {
                    Debug(msg + "出现非白名单")
                    i = 9
                    //cuowu = true
                    var bbk_token = bucketGet("who_tong", "bbk_token")//青龙
                    if (bbk_token == "") {
                        notifyMasters(`账号->${decodeURIComponent(PIN)}\n-->\n请你到插件云配置中设置BBK的token,用于加白`)
                        cuowu = true
                        return
                    } else {
                        notifyMasters("尝试加白IP中...")
                        add_ip(bbk_token)
                        i = 1
                    }
                } else if (msg.indexOf("操作过于频繁证") != -1) {
                    i = 9
                    get_tx(`账号->${decodeURIComponent(PIN)}\n登陆失败原因-->${msg}`)
                    quchong(decodeURIComponent(PIN) + ":" + msg, decodeURIComponent(PIN))
                    pftj = pftj + 1
                    sleep(15000)
                    cuowu = true
                    return
                } else {
                    if (msg.indexOf("为了您的账号安全请到京东商城") != -1 || msg.indexOf("打开京东商城APP重新登录") != -1) {
                        bucketSet("Auto_IP", username)
                        i = 9
                        rltj = rltj + 1
                        if (bbk_aqzm == "true") {
                            var pin_del = bucketGet("AutoJdpin", PIN)
                            if (pin_del == "") {
                                pin_del = 0
                                bucketSet("AutoJdpin", PIN, 1)
                            } else {
                                if (parseInt(pin_del) >= bbk_zmdel) {
                                    console.log("该账号已达到设定次数," + decodeURIComponent(PIN))
                                    if (pro_hmd == "true") {
                                        //开启过滤黑名单
                                        bucketSet("who_pro_hmd", PIN, PIN)
                                    } else {
                                        notifyMasters(PIN + "该账密数据已达到设定次数未过验证,删除掉,并重置")
                                        bucketDel("AutoJdck", PIN)
                                        bucketDel("AutoJdpin", PIN)
                                    }
                                } else {
                                    bucketSet("AutoJdpin", PIN, parseInt(pin_del) + 1)
                                }
                            }
                        }
                        get_tx(`账号->${decodeURIComponent(PIN)}
失败原因->请您先去京东APP上登录
如果登录还是出现这个，
请您使用验证码登录\n再发送:登录`)
                        quchong(`${decodeURIComponent(PIN)},原因:人脸`, decodeURIComponent(PIN))
                        for (let k = 0; k < qd.length; k++) {
                            bind = bucketGet("pin" + qd[k].toUpperCase(), PIN)
                            if (bind == "") {

                            } else {
                                TXfs_tuisong(qd[k], bind, `===JD账号->账密更新失败===
东东账号->${decodeURIComponent(PIN)}
失败原因->失败原因->请您先去京东APP上登录
如果登录还是出现这个，
请您使用验证码登录,\n再发送:登录`)
                            }

                        }
                        return

                    } else {
                        sb = sb + 1
                    }
                    //
                    if (bbk_socks_ms == "true") {
                        socks5proxy = socks_mian("socks5-get", username)
                    }
                    console.info(`账号->${decodeURIComponent(PIN)},原因->${JSON.stringify(body)}`)
                    //其他原因
                    // get_tx(`账号->${decodeURIComponent(PIN)}\n登陆失败.原因->${msg}\n-->${jcsx}`)
                    quchong(`${decodeURIComponent(PIN)}:登录失败..原因:${msg}`, decodeURIComponent(PIN))
                    for (let k = 0; k < qd.length; k++) {
                        bind = bucketGet("pin" + qd[k].toUpperCase(), PIN)
                        if (bind == "") {

                        } else {
                            if (jcsx == "" || jcsx == "null") {
                                if (GetContent == "账密登录" || GetContent == "账密登陆" || GetContent == "帐密登陆" || GetContent == "帐密登陆" || GetContent == "登录" || GetContent == "登陆") {
                                } else {
                                    TXfs_tuisong(qd[k], bind, `===JD账号->账密更新失败===
     东东账号->${decodeURIComponent(PIN)}
     失败原因->${msg}-${body.code}
     请你使用短信登陆一次,指令发送:登陆`)
                                }
                            } else {
                                if (GetContent == "账密登录" || GetContent == "账密登陆" || GetContent == "帐密登陆" || GetContent == "帐密登陆" || GetContent == "登录" || GetContent == "登陆") {
                                } else {
                                    TXfs_tuisong(qd[k], bind, `===JD账号->账密更新失败===\n东东账号->${decodeURIComponent(PIN)}\n失败原因->${msg}-${body.code}\n${jcsx}`)
                                }
                            }
                        }

                    }
                }
            }
        } else {
            if (bbk_jksb == "") {

            } else {
                get_tx(bbk_jksb)
            }
            //notifyMasters("接口挂了,靓仔")
        }
        sleep(8000)
        /*} catch (err) {
            if (bbk_jksb == "") {
     
            } else {
                get_tx(bbk_jksb)
            }
     
            //notifyMasters("接口挂了,靓仔")
        }*/
    }
}
function quchong(text, pin) {
    if (!PIN_HB.some(item => item.includes(pin))) {
        PIN_HB.push(text);
    }
}
function spwdLoginApi(PIN, username, password, kgkz) {
    if (bbk_socks_ms == "true") {
        socks5proxy = socks_mian("socks5-get", username)
        //   console.log(socks5proxy + "--IP请求--超时--" + username)

    }
    let bbk_cs = 0
    for (let i = 0; i < 3; i++) {
        if (bbk_socks_ms == "true") {
            var obj = { username, password, socks5proxy };
        } else {
            var obj = { username, password };
        }
        let qd = stxs.split(",");
        let body = request({
            method: "post",
            url: `${bbk_jk}/xcx/pwdLoginApi`,
            body: JSON.stringify(sign(obj)),
            headers: { "Content-Type": "application/json; charset=utf-8" },
            dataType: "json",
            timeOut: 80000
        });

        if (!body) {
            if (bbk_jksb) get_tx(bbk_jksb);
            sleep(3000);
            continue;
        }

        Debug("账密登录情况：" + JSON.stringify(body) + "-" + body.msg);
        let msg = body.msg || "";
        // 账号或密码不正确
        if (msg == "登录失败:账号或密码不正确" || msg == "账号或密码不正确") {

            get_tx(`账号->${decodeURIComponent(PIN)}\n-->${msg}`);
            if (mmcw == "true") {
                bucketSet("AutoJdck", PIN);
                bucketSet("AutoJdpin", PIN);
                bucketSet("who_pro_hmd", PIN);

            }
            mmtj = mmtj + 1
            
            return;
        }
        if (msg == "您的账号在当前应用已注销，无法继续使用，如需使用请重新注册新账号") {
            i = 5
            get_tx(`账号->${decodeURIComponent(PIN)}\n-->${msg}`)
            quchong(decodeURIComponent(PIN) + ":登录失败,原因:" + msg, decodeURIComponent(PIN))
            sb = sb + 1
            sleep(1000)
            return
        }
        if (msg == "强风控账号,登陆失败") {
            i = 5
            get_tx(`账号->${decodeURIComponent(PIN)}\n-->您的账号被强风控了,请您先使用短信验证码的方式登录一次,再发送:登录`)
            quchong(decodeURIComponent(PIN) + ":登录失败,原因:" + msg, decodeURIComponent(PIN))
            sb = sb + 1
            sleep(1000)
            breakIn(`账密添加+${PIN}`);
            let pin_del = bucketGet("AutoJdpin", PIN) || 0;
            if (bbk_aqzm == "true") {
                //var pin_del = bucketGet("AutoJdpin", PIN)
                if (pin_del == "") {
                    pin_del = 0
                    bucketSet("AutoJdpin", PIN, 1)
                } else {
                    if (parseInt(pin_del) >= bbk_zmdel) {
                        console.log("该账号已达到设定次数," + decodeURIComponent(PIN))
                        if (pro_hmd == "true") {
                            //开启过滤黑名单
                            bucketSet("who_pro_hmd", PIN, PIN)
                        } else {
                            notifyMasters(PIN + "该账密数据已达到设定次数未过验证,删除掉,并重置")
                            bucketDel("AutoJdck", PIN)
                            bucketDel("AutoJdpin", PIN)
                        }
                    } else {
                        bucketSet("AutoJdpin", PIN, parseInt(pin_del) + 1)
                    }
                }
            }
            return
        }

        // 登录成功
        if (body.code == 200) {
            login = true;
            cg = cg + 1
            let pin_del = bucketGet("AutoJdpin", PIN);
            if (pin_del) bucketSet("AutoJdpin", PIN);
            get_tx(`${bbk_tsy}->${msg}`);
            let str = msg;
            let start = str.indexOf('[') + 1;
            let end = str.indexOf(']');
            //ck_pin = encodeURIComponent(str.substring(start, end));
            ck_pin = str.substring(start, end)
            bucketSet("pin" + imType.toUpperCase(), ck_pin, GetUserID());
            bucketSet("who_pro_hmd", ck_pin);
            handleLoginSuccess(ck_pin);
            if (bbk_usertz != "true" && (GetContent == "账密刷新" || GetContent == "B账密刷新")) {
                for (let k = 0; k < qd.length; k++) {
                    let bind = bucketGet("pin" + qd[k].toUpperCase(), ck_pin);
                    if (bind || bind == 0) {
                        TXfs_tuisong(qd[k], bind, `===JD账号->更新成功===\n东东账号：${ck_pin}`);
                        sleep(1000);
                    }

                }
            }
            return;
        }

        // 其它错误处理
        var pin_del = bucketGet("AutoJdpin", PIN)
        if (msg.indexOf("非白名单") != -1) {
            Debug(msg + "出现非白名单");
            let bbk_token = bucketGet("who_tong", "bbk_token");
            if (!bbk_token) {
                notifyMasters(`账号->${decodeURIComponent(PIN)}\n-->${msg}\n请你到插件云配置中设置BBK的token,用于加白`);
                cuowu = true;
                return;
            } else {
                notifyMasters("尝试加白IP中...");
                add_ip(bbk_token);
                i = 1;
                //continue;
            }
        } else if (body.code == 128 || msg.indexOf("为了您的资产及隐私安全") != -1 || msg.indexOf("您的账号存在安全风险") != -1 || msg.indexOf("您的账号存在风险") != -1 || msg.indexOf("需要验证") != -1 || msg.indexOf("为了账号安全需要") != -1) {
            dx = dx + 1
            // get_tx(`账号->${decodeURIComponent(PIN)}\n失败原因-->${msg}`);您的账号存在风险，为了账号安全需要短信/语音验证，是否继续？
            breakIn(`账密添加+${PIN}`);
            if (bbk_aqzm == "true") {
                //var pin_del = bucketGet("AutoJdpin", PIN)
                if (pin_del == "") {
                    pin_del = 0
                    bucketSet("AutoJdpin", PIN, 1)
                } else {
                    if (parseInt(pin_del) >= bbk_zmdel) {
                        console.log("该账号已达到设定次数," + decodeURIComponent(PIN))
                        if (pro_hmd == "true") {
                            //开启过滤黑名单
                            bucketSet("who_pro_hmd", PIN, PIN)
                        } else {
                            notifyMasters(PIN + "该账密数据已达到设定次数未过验证,删除掉,并重置")
                            bucketDel("AutoJdck", PIN)
                            bucketDel("AutoJdpin", PIN)
                        }
                    } else {
                        bucketSet("AutoJdpin", PIN, parseInt(pin_del) + 1)
                    }
                }
            }
            quchong(`${decodeURIComponent(PIN)},原因:验证码`, decodeURIComponent(PIN));
            qrcode_api(body.jmp_url)
            if (kgkz == false) {

                var w = asse(`账号->${decodeURIComponent(PIN)}\n安全验证\n-->保存二维码,然后使用京东APP二维码识别，并完成验证，验证码/人脸识别验证\n-->验证后在回复：1`);
            } else {
                var w = asse(`账号->${decodeURIComponent(PIN)}\n安全验证\n-->保存二维码,然后使用京东APP二维码识别，并完成验证，验证码/人脸识别验证\n-->过完验证后，重新发送:账密登录`);
            }

            if (w == "" || w == false || w == "false") {
                bbk_add_yz = false
            } else {
                bbk_add_yz = true
            }

            return;
        } else if (msg.indexOf("操作过于频繁，请24小时后再试") != -1 || msg.indexOf("操作过于频繁证") != -1) {

            get_tx(`账号->${decodeURIComponent(PIN)}\n失败原因-->,先使用短信登录`);
            quchong(decodeURIComponent(PIN) + ":IP黑了", decodeURIComponent(PIN));
            pftj = pftj + 1
            sleep(1000);
            cuowu = true;
            return;
        } else if (msg.indexOf("验证码验证失败,请重新触发登录验证") != -1 || msg.indexOf("验证码服务器链接失败") != -1) {

            get_tx(`账号->${decodeURIComponent(PIN)}\n失败原因-->服务器失联,先使用短信登录`);
            quchong(decodeURIComponent(PIN) + ":服务器失联了", decodeURIComponent(PIN));
            pftj = pftj + 1
            sleep(1000);
            cuowu = true;
            return;
        } else if (msg.indexOf("check1请求失败,请重新触发登录验证") != -1 || msg.indexOf("页面已超时，请返回重试") != -1 || msg.indexOf("refresh验证失败,请重新触发登录验证") != -1 || msg.indexOf("访问服务器出错") != -1 || msg.indexOf("接收内容为空") != -1 || msg.indexOf("登录错误") != -1 || msg.indexOf("sid请求失败,请重新触发登录验证") != -1 || msg.indexOf("执行错误了哦") != -1 || msg.indexOf("请求没有返回数据") != -1 || msg.indexOf("服务器链接失败了哦") != -1) {
            if (bbk_socks_ms == "true") {
                socks5proxy = socks_mian("socks5-get", username)
            }
            bbk_cs++
            if (bbk_cs > 2) {
                get_tx(`账号->${decodeURIComponent(PIN)}\n--->登陆失败,重新发送：账密登录`);
                quchong(decodeURIComponent(PIN) + ",原因:" + msg, decodeURIComponent(PIN));
                i = 5
            } else {
                sleep(5000)
            }




        } else if (msg.indexOf("API请求Timeout失败，请检查网路重试") != -1) {

            if (bbk_socks_ms == "true") {
                socks5proxy = socks_mian("socks5-get", username)
                console.log(socks5proxy + "--IP请求---超时--" + username)
            }

        } else if (msg.indexOf("为了您的账号安全请到京东商城") != -1 || msg.indexOf("打开京东商城APP重新登录") != -1) {
            rltj++;
            let pin_del = bucketGet("AutoJdpin", PIN) || 0;
            if (bbk_aqzm == "true") {
                if (parseInt(pin_del) >= bbk_zmdel) {
                    console.log("该账号已达到设定次数," + decodeURIComponent(PIN));
                    if (pro_hmd == "true") {
                        bucketSet("who_pro_hmd", PIN, PIN);
                    } else {
                        notifyMasters(PIN + "该账密数据已达到设定次数未过验证,删除掉,并重置");
                        bucketDel("AutoJdck", PIN);
                        bucketDel("AutoJdpin", PIN);
                    }
                } else {
                    bucketSet("AutoJdpin", PIN, parseInt(pin_del) + 1);
                }
            }
            if (GetContent == "账密登录" || GetContent == "账密登陆" || GetContent == "帐密登陆" || GetContent == "帐密登录") {
                get_tx(`账号->${decodeURIComponent(PIN)}\n失败原因->请您先去京东APP上登录,如果登录还是出现这个，请您使用验证码登录,使用1或者3的方式登录\n再发送:登录`);
            }
            get_tx(``)
            quchong(`${decodeURIComponent(PIN)},原因:人脸`, decodeURIComponent(PIN));
            for (let k = 0; k < qd.length; k++) {
                let bind = bucketGet("pin" + qd[k].toUpperCase(), PIN);
                if (bind | bind == 0) {
                    TXfs_tuisong(qd[k], bind, `===JD账号->账密更新失败===\n东东账号->${decodeURIComponent(PIN)}\n失败原因->如果链接里面出现的是人脸识别认证,请您复制链接去京东上访问并过人脸验证\n再发送:登录`);
                }

            }
            if (bbk_yhm_ismin == "") {
            } else {
                let qd = bbk_yhm_ismin.split(",");
                for (let k = 0; k < qd.length; k++) {

                    // pushToGroups(`===JD账号->更新成功===\n东东账号：${ck_pin}`);
                    let txfs = qd[k].split(":")
                    let bind = bucketGet("pin" + txfs[0].toUpperCase(), PIN);
                    geroupts(txfs[0], txfs[1], bind, `===JD账号->账密更新失败===\n东东账号->${decodeURIComponent(PIN)}\n失败原因->如果链接里面出现的是人脸识别认证,请您复制链接去京东上访问并过人脸验证\n未及时更新并已通知次数:${pin_del}\n未及时更新并已通知次数:${pin_del}\n再发送:账密登录`);
                }
            }
            return;

        } else {
            breakIn(`账密添加+${PIN}`);
            sb++;
            get_tx(`账号->${decodeURIComponent(PIN)}\n登陆失败.原因-*->${msg}\n-->${jcsx}`);
            quchong(`${decodeURIComponent(PIN)}:登录失败,原因:${msg}`, decodeURIComponent(PIN));
            for (let k = 0; k < qd.length; k++) {
                let bind = bucketGet("pin" + qd[k].toUpperCase(), PIN);
                if (!bind) continue;
                let failMsg = (jcsx && jcsx != "null")
                    ? `===JD账号->账密更新失败===\n东东账号->${decodeURIComponent(PIN)}\n失败原因->${msg}-${body.code}\n${jcsx}`
                    : `===JD账号->账密更新失败===\n东东账号->${decodeURIComponent(PIN)}\n失败原因->${msg}-${body.code}\n请你使用短信登陆一次,指令发送:登陆`;
                if (!(GetContent == "账密登录" || GetContent == "账密登陆" || GetContent == "帐密登陆" || GetContent == "登录" || GetContent == "登陆")) {
                    TXfs_tuisong(qd[k], bind, failMsg);
                }
            }
            return;
        }
    }
}

//群组推送
function geroupts(tx, geroupid, qh, data) {
    push({
        imType: tx,
        userID: qh,
        title: "",
        groupCode: geroupid,
        content: data,
    })
}
//私聊推送
function TXfs_tuisong(tx, qh, data) {
    push({
        imType: tx,
        userID: qh,
        title: "",
        groupCode: "",
        content: data,
    })
}
function ql_cookie() {
    if (!config.qlName) {
        notifyMasters("未设置青龙名称,请你到插件云配置中设置");
        return;
    }
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
function qrcode_api(text) {
    //notifyMasters (`ks`)
    for (let j = 0; j < 3; j++) {
        let result = request({
            url: "http://106.52.219.147:8585/phpqrcode/qrcode_api.php?text=" + text,
            method: "get",
            /*form: {
                text: text,       // POST参数放这里
                size: 6,
                margin: 2
            },*/
            dataType: "json",
            timeout: 8000
        });
        if (result && result.code == 200) {
            try {
                j = 9
                let qr = result.data.base64.split(',')[1]
                // get_tx(qr)
                sendImage(`base64://` + qr)
                sendImage(`[CQ:image,file=${text}]`)
                //return result.data.base64;
            } catch (e) { }
        }

        // 失败延迟2秒再重试
        sleep(2000);
    }

    // 3次都失败
    return null;
}
function HQ_ip() {
    k = 0
    for (let j = 0; j < 3; j++) {
        request({
            url: "https://4.ipw.cn",
            method: "get",

            timeout: 8000
        }, function (error, response, header, body) {
            if (!error) {
                IP = body
                //msgs.push(`-->获取IP成功,${IP}`)
                k = 1
                j = 30
                return true
            } else {
                sleep(2000)
            }

        })
    }
    if (k = 0) {
        HQ_ip2()
    }
}
function HQ_ip2() {
    for (let j = 0; j < 5; j++) {
        request({
            url: "https://whois.pconline.com.cn/ipJson.jsp?json=true",
            method: "get",
            dataType: "json",
            timeout: 8000
        }, function (error, response, header, body) {
            if (!error) {
                if (body.regionCode == 0) {
                    IP = body.ip
                    // msgs.push(`-->获取IP成功,${IP}`)
                    j = 30
                }

                return true
            } else {
                sleep(2000)
            }

        })
    }
}
function add_ip(data) {
    var bbk_oldip = bucketGet("who_tong", "bbk_oldip")//旧白名单IP
    var bbk_gwip = bucketGet("who_tong", "bbk_gwip")//开启过滤黑名单
    if (bbk_gwip == "") {
        HQ_ip()
    } else {
        IP = bbk_gwip
    }
    if (bbk_oldip == "") {
        var obj = {
            ip: IP,
            token: data
        }
    } else {
        var obj = {
            ip: IP,
            oldip: bbk_oldip,
            token: data
        }
    }

    for (let i = 0; i < 3; i++) {
        try {
            request({
                method: "post",
                url: `http://bbk.tutututu.eu.org/xfFY4gMv`,
                body: JSON.stringify(obj),
                headers: {
                    "Content-Type": "application/json",
                },
                dataType: "json",
                timeOut: 10000
            }, function (error, response, header, body) {
                notifyMasters("BBK帐密通知：" + JSON.stringify(body))

                if (!error) {
                    if (body.code == 200) {
                        notifyMasters(`BBK帐密通知：IP更换成功成功\n${IP}\n旧IP:${bbk_oldip}`)
                        bucketSet("who_tong", "bbk_oldip", IP)//旧白名单IP
                        i = 10
                    } else {
                        Debug("IP上传失败")
                        sleep(2000)
                    }
                } else {
                    sleep(2000)
                }

            })

        } catch (err) { }
    }
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
            if (body.islogin == "0") {
                return false
            } else {
                return true
            }
        }
    } catch (e) { return true }
}
function jd_enen(cookie) {
    let pina = cookie.match(/(?<=pt_pin=)[^;]+/g)
    body = request({
        method: "post",
        url: `https://plogin.m.jd.com/cgi-bin/ml/mlogout?appid=300&returnurl=https%3A%2F%2Fm.jd.com%2F`,
        headers: {
            "Cookie": cookie,
            "User-Agent": UserAgents(),
            "authority": "plogin.m.jd.com",
        },
        // dataType: "json",
        timeOut: 8000
    })
    Debug("一键作废" + pina)
    get_tx("一键作废" + pina)
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
function hideMiddlePart(str, startLength = 3, endLength = 4) {
    if (str.length <= startLength + endLength) {
        return str;
    }
    const hiddenPart = `***`
    return str.substring(0, startLength) + hiddenPart + str.substring(str.length - endLength);
}
function getPin(cookie) {
    const match = cookie.match(/pt_pin=([^;]+)/);
    return match ? match[1] : "";
}
function getAllCookies(envs) {
    return envs.filter(function (_data) {
        return _data.name === "JD_COOKIE";
    });
}
function getUserBindPins() {
    return bucketKeys("pin" + imType.toUpperCase(), GetUserID()) || [];
}
function Dmian() {
    if (bbk_pay == "true") {//收费模式
        var qd = bucketGet("who_user_qd", userId)//获取用户积分
        if (qd == "") {
            get_tx("你还没有积分哦\n" + zd_jfts)
            bucketSet("who_user_qd", userId, JSON.stringify({ "day": 0, "creationTime": 0 }))
            return
        } else {
            if (isJsonString(qd)) {
                qd = JSON.parse(qd)
                if (parseInt(qd.day) >= parseInt(bbk_Charging)) {
                    //get_tx("积分充足,继续下一步任务\n当前积分" + qd.day)
                    if (qd.day == "0" || qd.day == 0) {
                        get_tx("积分不足,取消登录任务\n当前积分" + qd.day + "\n" + zd_jfts)
                        return
                    }
                } else {
                    get_tx("积分不足,取消登录任务\n当前积分" + qd.day + "\n" + zd_jfts)
                    return
                }
            } else {
                get_tx(`用户ID:${userId}\n数据出错,请联系管理员处理`)
            }
        }
        //绑定的
    }
    bind = bucketKeys("pin" + imType.toUpperCase(), userId)
    if (bind.length == 0) {
        //get_tx("没有与你绑定的账号，请你先登录")
        let p = asse("输入您绑定[JD]的手机号.")
        if (p == false) {

        } else {
            let w = asse("输入您[JD]的登录密码")
            if (w == false) {

            } else {
                spwdLoginApi(userId, p, w, false)
                if (bbk_add_yz == "true" || bbk_add_yz == true) {
                    get_tx("二次验证登录...")
                    sleep(7000)
                    spwdLoginApi(userId, p, w, true)
                }
                if (login) {
                    let data = JSON.stringify({ "account": p, "password": w, "cookie": "", "user": userId, "platform": imType })
                    bucketSet("AutoJdck", ck_pin, data)
                    if (bbk_pay == "true") {//收费模式
                        pay_jf()
                    }
                    if (bbk_glytz == "true") {
                        notifyMasters(`-->报告老板，[ ${decodeURIComponent(ck_pin)}]新增账号！
-->绑定客户：${userId}(${imType})`)
                    }
                    //调用青龙
                    if (zhongjianye == "true") {
                        Debug("使用中间页")
                        for (let j = 0; j < 3; j++) {

                            let qljs = bucketGet("A_zm_ck", ck_pin)
                            if (qljs == "") {

                            } else {
                                bucketSet("A_zm_ck", ck_pin)
                                breakIn(qljs)
                                j = 9
                            }
                            sleep(2000)
                        }
                    } else {
                        let qljs = bucketGet("who_tong", "bbk_qljson")
                        if (qljs == "") {
                            Debug("不调用青龙内CK")
                            //不获取CK
                        } else {
                            //获取CK
                            subCKToXZ(ck_pin)
                        }
                    }
                    login = false
                }
            }
        }

    } else {
        let containeta = qls(zmqly);
        let container, containerEnv;
        for (let qx = 0; qx < 5; qx++) {
            try {
                container = Qinglong(containeta.host, containeta.client_id, containeta.client_secret);
                containerEnv = container.ApiQL("envs", "", "get", "").data;
                break;
            } catch (e) {
                notifyMasters(`【BBK账密登录】链接容器【${zmqly}】失败，请检查配置是否正确或网络是否正常`);
                return;
            }
        }
        var ptpin = ""
        ptpin += "请选择你的操作，输入数字\n[0] 新增账号\n"
        let dat = 0
        for (let j = 0; j < bind.length; j++) {
            //get_tx(bind[j])
            var pin_ck = bucketGet("AutoJdck", bind[j])

            if (pin_ck == "") {
                //get_tx("没有存在")
            } else {
                let phon = JSON.parse(pin_ck)
                let jnStr = bucketGet("jdNotify", bind[j])
                if (jnStr == "") {
                    var CK_ZTID = "未登录\n"
                } else {
                    ql_cookie()
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
                if (bbk_pinck == "true") {
                    ptpin += `[${j + 1}] ${hideMiddlePart(decodeURIComponent(bind[j]))} [${phone(phon.account)}] ${CK_ZTID}\n`
                } else {
                    ptpin += `[${j + 1}] ${decodeURIComponent(bind[j])} [${phone(phon.account)}] ${CK_ZTID}\n`
                }

            }
        }
        if (dat == 0) {
            let p = asse("输入您绑定[JD]的手机号..")
            if (p == false) {

            } else {
                let w = asse("输入您[JD]的登录密码")
                if (w == false) {

                } else {
                    //get_tx(`${p}-${w}`)
                    get_tx("开始登录验证...")
                    spwdLoginApi(userId, p, w, false)
                    if (bbk_add_yz == "true" || bbk_add_yz == true) {
                        get_tx("二次验证登录...")
                        sleep(5000)
                        spwdLoginApi(userId, p, w, true)
                    } else {

                    }
                    if (login) {

                        let data = JSON.stringify({ "account": p, "password": w, "cookie": cookie, "user": userId, "platform": imType })
                        bucketSet("AutoJdck", ck_pin, data)
                        if (bbk_pay == "true") {//收费模式
                            pay_jf()
                        }
                        if (bbk_glytz == "true") {
                            notifyMasters(`-->报告老板，[ ${decodeURIComponent(ck_pin)} ]新增账号！
-->绑定客户：${userId}(${imType})`)

                        }
                        if (zhongjianye == "true") {
                            Debug("使用中间页")
                            for (let j = 0; j < 3; j++) {

                                let qljs = bucketGet("A_zm_ck", ck_pin)
                                if (qljs == "") {

                                } else {
                                    bucketSet("A_zm_ck", ck_pin)
                                    breakIn(qljs)
                                    j = 9
                                }
                                sleep(2000)
                            }
                        } else {
                            let qljs = bucketGet("who_tong", "bbk_qljson")
                            if (qljs == "") {
                                Debug("不调用青龙内CK")
                                //不获取CK
                            } else {
                                //获取CK
                                subCKToXZ(ck_pin)
                            }
                        }
                        login = false
                    }

                    return
                }
            }

        } else {
            get_tx(ptpin + "\n---------------\n如果账号有效则不需要再次登陆更新\n-->输入q退出")
        }

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
            let p = asse("输入您绑定[JD]的手机号")
            if (p == false) {

            } else {
                let w = asse("输入您[JD]的登录密码")
                if (w == false) {

                } else {
                    //get_tx(`${p}-${w}`)
                    get_tx("开始登录验证..")
                    spwdLoginApi(userId, p, w, false)
                    if (bbk_add_yz == "true" || bbk_add_yz == true) {
                        get_tx("二次验证登录..")
                        sleep(5000)
                        spwdLoginApi(userId, p, w, true)
                    }
                    if (login) {
                        let data = JSON.stringify({ "account": p, "password": w, "cookie": cookie, "user": userId, "platform": imType })
                        bucketSet("AutoJdck", ck_pin, data)
                        if (bbk_pay == "true") {//收费模式
                            pay_jf()
                        }
                        if (bbk_glytz == "true") {
                            notifyMasters(`-->报告老板，[ ${decodeURIComponent(ck_pin)} ]新增账号！
-->绑定客户：${userId}(${imType})`)
                        }
                        if (zhongjianye == "true") {
                            Debug("使用中间页")
                            for (let j = 0; j < 3; j++) {

                                let qljs = bucketGet("A_zm_ck", ck_pin)
                                if (qljs == "") {

                                } else {
                                    bucketSet("A_zm_ck", ck_pin)
                                    breakIn(qljs)
                                    j = 9
                                }
                                sleep(2000)
                            }

                        } else {
                            let qljs = bucketGet("who_tong", "bbk_qljson")
                            if (qljs == "") {
                                Debug("不调用青龙内CK")
                                //不获取CK
                            } else {
                                //获取CK
                                subCKToXZ(ck_pin)
                            }
                        }
                        login = false
                    }
                }
            }
        } else {
            get_tx("您选择的账号:" + decodeURIComponent(bind[choice - 1]) + "\n开始登录验证..")
            var pin_ck = bucketGet("AutoJdck", bind[choice - 1])
            var jnStr = bucketGet("jdNotify", bind[choice - 1])
            jn = JSON.parse(jnStr)
            cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
            let jc_ck = jdck(cookie)
            if (jc_ck) {
                get_tx(`当前账号[${decodeURIComponent(bind[choice - 1])}]有效,无需登录`)
                return
            } else {
                //get_tx("当前账号cookie失效,需要登录")
            }
            pin_ck = JSON.parse(pin_ck)
            spwdLoginApi(bind[choice - 1], pin_ck.account, pin_ck.password, false)
            if (bbk_add_yz == "true" || bbk_add_yz == true) {
                get_tx("二次验证登录..")
                sleep(5000)
                spwdLoginApi(bind[choice - 1], pin_ck.account, pin_ck.password, true)
            } else {

            }
            if (login) {
                if (bbk_glytz == "true") {
                    notifyMasters(`-->报告老板，[ ${decodeURIComponent(bind[choice - 1])} ]更新账号！
-->绑定客户：${userId}(${imType})`)
                }
                if (bbk_pay == "true") {//收费模式
                    pay_jf()
                }
                if (zhongjianye == "true") {
                    Debug("使用中间页")
                    for (let j = 0; j < 3; j++) {

                        let qljs = bucketGet("A_zm_ck", bind[choice - 1])
                        if (qljs == "") {

                        } else {
                            bucketSet("A_zm_ck", bind[choice - 1])
                            breakIn(qljs)
                            j = 9
                        }
                        sleep(2000)
                    }

                } else {
                    let qljs = bucketGet("who_tong", "bbk_qljson")
                    if (qljs == "") {
                        Debug("不调用青龙内CK")
                        //不获取CK
                    } else {
                        //获取CK
                        subCKToXZ(ck_pin)
                    }
                }
                login = false
            }

        }

    }

}//userId

function pay_jf() {
    var qd = bucketGet("who_user_qd", userId)//获取用户积分
    qd = JSON.parse(qd)
    bucketSet("who_user_qd", userId, JSON.stringify({ "day": parseInt(qd.day) - parseInt(bbk_Charging), "creationTime": qd.creationTime }))

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
function handleContent(value) {
    if (value === '' || value === false || value === "false") {
        return "不可用❌";
    }
    return "目前可用✔"; // 有效值直接返回
}
function bbk() {
    if (GetChatID() == "202793995" || GetChatID() == "858456556") {
        return
    }
    /*if (GetContent == "账密登录" || GetContent == "账密登陆" || GetContent == "帐密登陆" || GetContent == "帐密登陆") {
        if (bbk_qzkg == "true") {
            if (GetChatID() == 0 || GetChatID() == "0") {
                Dmian()
            } else {
                get_tx("管理员未开启群内使用\n请私聊发送")
                return
            }
        } else {
 
 
            Dmian()
        }
    }*/
    if (GetContent == "短信登录" || GetContent == "短信登陆") {
        if (vkey == "") {
            bbk_dx()
        } else {
            zack1_dx()
        }
    }
    if (GetContent == "登陆" || GetContent == "登录" || GetContent == "更新账号" || GetContent == "账密登录" || GetContent == "账密登陆" || GetContent == "帐密登陆" || GetContent == "帐密登陆") {
        //zack1_dx()
        if (vkey == "") {

            var p = asse(`请选择登录方式:
回复()内的数字编号即可
------------ 
(1)短信登录[${handleContent(bbk_dx_kga1)}] 
(2)账密登录[${handleContent(bbk_dx_kga2)}]
------------
[推荐使用账密登录可自动更新]`)
        } else {

            if (bbk_zdh == "true") {
                var p = asse(`请选择登录方式:
回复()内的数字编号即可
------------ 
(1)短信登录[${handleContent(bbk_dx_kga1)}] 
(2)账密登录[${handleContent(bbk_dx_kga2)}]

(3)账密登录[${handleContent(bbk_dx_kga3)}][推荐]
`)
//(4)手动登录[${handleContent(bbk_dx_kga4)}]【安卓手机推荐】
            } else {
                var p = asse(`请选择登录方式:
回复()内的数字编号即可
------------ 
(1)短信登录[${handleContent(bbk_dx_kga1)}] 
(2)账密登录[${handleContent(bbk_dx_kga2)}]
(3)语音短信登录[${handleContent(bbk_dx_kga3)}]
(4)手动登录[${handleContent(bbk_dx_kga4)}]
------------
当前登录可能无法使用，请留意群通知`)
            }

            //请使用状态可用的1和3有可能会有语音电话验证码,如果不来验证码时，请先关闭骚扰电话在尝试
        }
        if (p == false) {

        } else {
            if (p == "2" || p == 2) {
                if (bbk_dx_kga2 == "false" || bbk_dx_kga2 == "") {
                    get_tx("当前的方式无法使用,请您选择可用的,重新发送：登录")
                    return
                }
                if (bbk_qzkg == "true") {
                    if (GetChatID() == 0 || GetChatID() == "0") {
                        Dmian()
                    } else {
                        get_tx("管理员未开启群内使用\n请私聊发送")
                        return
                    }
                } else {


                    Dmian()
                }

            } else if (p == 3 || p == "3") {
                if (bbk_dx_kga3 == "false" || bbk_dx_kga3 == "") {
                    get_tx("当前的方式无法使用,请您选择可用的,重新发送：登录")
                    return
                }

                if (bbk_zdh == "true") {
                    breakIn("自动账密")
                } else {
                    zack_dx()
                }


            } else if (p == 4 || p == "4") {
                if (bbk_dx_kga4 == "false" || bbk_dx_kga4 == "") {
                    get_tx("当前的方式无法使用,请您选择可用的,重新发送：登录")
                    return
                }
                if (bbk_rlyz == "") { }
                else {
                    get_tx(bbk_rlyz)
                }

            } else {
                if (bbk_dx_kga1 == "false" || bbk_dx_kga1 == "") {
                    get_tx("当前的方式无法使用,请您选择可用的,重新发送：登录")
                    return
                }
                if (vkey == "") {
                    bbk_dx()
                } else {
                    zack1_dx()
                }

            }
        }

    }

    if (GetContent == "账密刷新" || GetContent == "B账密刷新") {

        /* if (dengdai() == false) {
             console.log("退出刷新")
             return
         }*/

        hmd_kg = false
        if (isAdmin() || imType == "croncmd") {
            mian()
        } else {
            return
        }
        bucketSet("who_tong", "bbk_tingzhi")
        bucketSet("who_tong", "bbk_jincheng")
    }
    if (GetContent == "enen刷新") {
        if (isAdmin() || imType == "croncmd") {
            enensx()
        } else {
            return
        }

    }
    if (GetContent == "黑名单刷新") {
        hmd_kg = true
        if (isAdmin() || imType == "croncmd") {
            mian()
        } else {
            return
        }
    }
    if (GetContent == "abc刷新") {
        hmd_kg = false
        if (isAdmin() || imType == "croncmd") {
            abcmian()
        } else {
            return
        }

    }

    if (GetContent == "全部黑名单刷新") {
        hmd_kg = true
        if (isAdmin() || imType == "croncmd") {
            qbmian()
        } else {
            return
        }

    }
    if (GetContent == "全部账密刷新") {
        if (isAdmin() || imType == "croncmd") {
            qbmian()
        } else {
            return
        }

    }
    if (GetContent == "账密停止" || GetContent == "帐密停止") {
        if (isAdmin() || imType == "croncmd") {
            //mian()
        } else {
            return
        }
        let text = bucketGet("who_tong", "bbk_tingzhi")
        if (text == "") {
            bucketSet("who_tong", "bbk_tingzhi", true)
        } else {
            bucketSet("who_tong", "bbk_tingzhi")
        }

        get_tx("提交停止任务")

        return

    }
    if (GetContent == "BBK版本") {
        get_tx(text_bbk)
        return
    }
    if (GetContent == "socks导入") {
        if (isAdmin() || imType == "croncmd") {
        } else {
            get_tx("叼毛!不要乱搞咯")
            return
        }
        get_tx("请回复socks5[一行一条]")
        let choice = input(30000, 1000)//表示等待用户输入，等待用户输入时间为30秒
        if (choice == 'q') {
            get_tx('退出成功')//给会话用户发送信息
            return
        }
        if (choice == '') {
            get_tx('输入超时，自动退出程序')
            return
        }
        const importResult = importSocks5(choice);
        if (importResult.success) {
            get_tx(importResult.message);
        } else {
            get_tx(importResult.message);
        }
    }
    if (GetContent == "账密重置" || GetContent == "帐密重置") {
        bucketSet("who_tong", "bbk_jincheng")
        get_tx("已重置刷新状态")
    }
    if (GetContent == "socksret" || GetContent == "socksout") {
        socks_mian(GetContent)
    }
}
bbk()
function bbk_dx() {

    var ptpin = "", data = "", pro_zm = "", dat = 0
    let bind = bucketKeys("pin" + imType.toUpperCase(), userId)
    if (bind.length == 0) {
        var p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
        if (p == false) {
            return
        }
        if (!checkModbile(p)) {
            get_tx('输入手机号错误，自动退出程序,请您重新发送：登录')
            return
        }


    } else {
        ptpin += "请选择你的操作，输入数字\n[0] 新增账号\n"
        for (let j = 0; j < bind.length; j++) {
            var pin_phone = bucketGet("Autophone", bind[j])
            let jnStr = bucketGet("jdNotify", bind[j])
            if (jnStr == "") {
                pro_zm = "未登录\n"
            } else {

                jn = JSON.parse(jnStr)
                cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                var jc_ck = jdck(cookie)
                if (jc_ck) {
                    pro_zm = `有效\n`
                } else {
                    pro_zm = `失效\n`
                }
            }


            if (pin_phone == "") {
                ptpin += `[${j + 1}] ${decodeURIComponent(bind[j])} [未记录手机号] ${pro_zm}\n`
            } else {
                ptpin += `[${j + 1}] ${decodeURIComponent(bind[j])} [${hideMiddlePart(pin_phone)}] ${pro_zm}\n`
                dat = 1
            }

        }
        if (dat == 0) {
            var p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
            if (p == false) {
                return
            }
            if (!checkModbile(p)) {
                get_tx('输入手机号错误，自动退出程序,请您重新发送：登录')
                return
            }

        } else {
            get_tx(ptpin)
            var choice = input(30000, 1000)//表示等待用户输入，等待用户输入时间为30秒
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
                p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
                if (p == false) {
                    return
                }
                if (!checkModbile(p)) {
                    get_tx('输入错误，自动退出程序')
                    return
                }
            } else {
                var pin_phone = bucketGet("Autophone", bind[choice - 1])
                if (pin_phone == "") {
                    p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
                    if (p == false) {
                        return
                    }
                    if (!checkModbile(p)) {
                        get_tx('输入手机号错误，自动退出程序,请您重新发送：登录')
                        return
                    }
                } else {
                    p = pin_phone
                }

            }
        }
    }

    var login_ds = bbk_sms(p)
    if (login_ds.code == 200) {
        // get_tx(login_ds.msg)
        let w = asse(`${hideMiddlePart(p)},${login_ds.msg}`)
        if (w == false) {

        } else {

            //get_tx(`${p}-${w}`)
            let sms_login = bbk_smsVerify(p, w)
            if (sms_login.code == 200) {
                get_tx(sms_login.msg)
                let str = sms_login.msg
                let start = str.indexOf('[') + 1;
                // 找到第一个右方括号的位置
                let end = str.indexOf(']');
                // 截取方括号之间的内容
                //ck_pin = encodeURIComponent(str.substring(start, end));
                ck_pin = str.substring(start, end)
                notifyMasters(`-->报告老板，[ ${decodeURIComponent(ck_pin)} ]短信1更新账号！\n-->绑定客户：${userId}(${imType})`)
                bucketGet("Autophone", ck_pin, p)
                handleLoginSuccess(ck_pin);
            } else {


                if (sms_login.msg == "验证码输入有误" || sms_login.msg == "登录失败:验证码输入错误") {
                    let w = asse(sms_login.msg + ",请您重新输入正确的验证码")
                    if (w !== false) {
                        if (!checkCode(w)) {
                            get_tx('输入验证码格式错误，自动退出程序,请您重新发送：登录')
                            return
                        }
                        let sms_login = bbk_smsVerify(p, w)
                        if (sms_login.code == 200) {
                            get_tx(sms_login.msg)
                            let str = sms_login.msg
                            let start = str.indexOf('[') + 1;
                            // 找到第一个右方括号的位置
                            let end = str.indexOf(']');
                            // 截取方括号之间的内容
                            //ck_pin = encodeURIComponent(str.substring(start, end));
                            ck_pin = str.substring(start, end)
                            notifyMasters(`-->报告老板，[ ${decodeURIComponent(ck_pin)} ]短信1更新账号！\n-->绑定客户：${userId}(${imType})`)
                            handleLoginSuccess(ck_pin);
                            return
                        }
                    }
                    get_tx(`${sms_login.msg},请您重新发送：登录`)


                } else if (sms_login.msg == "登录失败:您的账号存在风险，为了您的账号安全，打开京东商城APP重新登录，风险解除后即可正常使用") {
                    get_tx(`请您先去京东APP上登录,如果登录还是出现这个，请您使用验证码登录,使用1或者3的方式登录`)
                } else {
                    get_tx(sms_login.msg)
                    notifyMasters(JSON.stringify(sms_login))
                }
            }
            // get_tx("开始登录验证..")
        }
    } else {
        get_tx(login_ds.msg)

    }


}
function zack_dx() {

    var ptpin = "", data = "", pro_zm = "", dat = 0
    let bind = bucketKeys("pin" + imType.toUpperCase(), userId)
    if (bind.length == 0) {
        var p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）.....`)
        if (p == false) {
            return
        }
        if (!checkModbile(p)) {
            get_tx('输入手机号错误，自动退出程序,请您重新发送：登录')
            return
        }


    } else {
        ptpin += "请选择你的操作，输入数字\n[0] 新增账号\n"
        for (let j = 0; j < bind.length; j++) {
            var pin_phone = bucketGet("Autophone", bind[j])
            let jnStr = bucketGet("jdNotify", bind[j])
            if (jnStr == "") {
                pro_zm = "未登录\n"
            } else {

                jn = JSON.parse(jnStr)
                cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                var jc_ck = jdck(cookie)
                if (jc_ck) {
                    pro_zm = `有效\n`
                } else {
                    pro_zm = `失效\n`
                }
            }
            if (pin_phone == "") {
                ptpin += `[${j + 1}] ${decodeURIComponent(bind[j])} [未记录手机号] ${pro_zm}\n`
            } else {
                ptpin += `[${j + 1}] ${decodeURIComponent(bind[j])} [${hideMiddlePart(pin_phone)}] ${pro_zm}\n`
                dat = 1
            }

        }


        var p = null

        if (dat == 0) {
            p = promptMobile('输入手机号错误，自动退出程序,请您重新发送：登录')
            if (p === false || p === null) {
                return
            }
        } else {
            get_tx(ptpin)
            var choice = input(30000, 1000) // 等待用户输入30秒

            if (choice == 'q') {
                get_tx('退出成功')
                return
            }

            if (choice == '') {
                get_tx('输入超时，自动退出程序...')
                return
            }

            if (isNaN(choice) || choice > bind.length || choice < 0) {
                if (!checkModbile(choice)) {
                    get_tx('输入错误，自动退出程序..')
                    return
                }
            }

            // 允许输入 0 或直接输入手机号，走手动输入流程
            if (choice == 0) {
                p = promptMobile('输入错误，自动退出程序..')
                if (p === false || p === null) {
                    return
                }
            } else if (checkModbile(choice)) {
                p = choice
            } else {
                var pin_phone = bucketGet("Autophone", bind[choice - 1])
                if (pin_phone == "") {
                    p = promptMobile('输入手机号错误，自动退出程序,请您重新发送：登录')
                    if (p === false || p === null) {
                        return
                    }
                } else {
                    p = pin_phone
                }
            }
        }
    }

    var login_ds = zack_sms(p)
    if (login_ds.status == "fail") {
        get_tx("代理失效,请您重新发送：登录")
        return
    }
    if (login_ds.status == 200) {
        // get_tx(login_ds.msg)
        let w = asse(`${hideMiddlePart(p)},${login_ds.msg}`)
        if (w == false) {

        } else {

            //get_tx(`${p}-${w}`)
            let sms_login = zack_smsVerify(p, w, login_ds.data.guid, login_ds.data.lsid)
            if (sms_login.status == 200) {
                let str = sms_login.cookie
                ck_pin = str.match(/(?<=pt_pin=)[^;]+/g)
                let bbk_dxzdynr = bucketGet("who_tong", "bbk_dxzdynr") || "目前账密稳定，推送使用";
                get_tx(`报告老板，[ ${decodeURIComponent(ck_pin)} ],更新成功\n${bbk_dxzdynr}`)

                // 截取方括号之间的内容

                notifyMasters(`-->报告老板，[ ${decodeURIComponent(ck_pin)} ]短信2更新账号！\n-->绑定客户：${userId}(${imType})`)
                bucketSet("Autophone", ck_pin, p)
                breakIn(str)
                // handleLoginSuccess(ck_pin);
            } else if (login_ds.status == 118 || login_ds.status == 203) {
                if (bbk_rlyz == "") {
                    get_tx(`${sms_login.err_code}--${dd}..请您重新发送：登录`)
                } else {
                    get_tx(bbk_rlyz)
                }

                //get_tx(sms_login.msg)
            } else {
                if (sms_login.msg == "验证码输入错误" || sms_login.msg == "登录失败:验证码输入错误") {
                    let w = asse(sms_login.msg + ",请您重新输入正确的验证码")
                    if (w !== false) {
                        if (!checkCode(w)) {
                            get_tx('输入验证码格式错误，自动退出程序,请您重新发送：登录')
                            return
                        }
                        let sms_login = zack_smsVerify(p, w, login_ds.data.guid, login_ds.data.lsid)
                        if (login_ds.status == 443) {

                            get_tx("授权失效,请联系管理员处理")
                            return
                        }
                        if (sms_login.status == 200) {
                            get_tx(sms_login.msg)
                            let str = sms_login.cookie
                            ck_pin = str.match(/(?<=pt_pin=)[^;]+/g)
                            notifyMasters(`-->报告老板，[ ${decodeURIComponent(ck_pin)} ]短信2更新账号！\n-->绑定客户：${userId}(${imType})`)
                            breakIn(str)
                            // handleLoginSuccess(ck_pin);
                            return
                        }
                    }
                    get_tx(`${sms_login.msg},请您重新发送：登录`)


                } else if (sms_login.status == 118) {
                    //
                    if (bbk_rlyz == "") {
                        get_tx(`${sms_login.err_code}--${dd}..请您重新发送：登录`)
                    } else {
                        get_tx(bbk_rlyz)
                    }
                    /*if (bbk_wskey_dxjk == "") {
                        get_tx(`请您先去京东APP上登录,如果登录还是出现这个，请您使用验证码登录,使用1或者3的方式登录`)
                    } else {
                        let wskey_login = bucketGet("who_tong", "bbk_fkkg")
                        if (wskey_login == "true") {
                           // bbk_wskey_dy(p)
get_tx(`请您先去京东APP上登录,如果登录还是出现这个，请您使用验证码登录,使用1或者3的方式登录`)
                        } else {
                            get_tx(`请您先去京东APP上登录,如果登录还是出现这个，请您使用验证码登录,使用1或者3的方式登录`)
                        }
 
 
                    }*/

                } else if (sms_login.status == 203) {
                    get_tx(sms_login.msg + "," + 203)
                } else if (login_ds.status == 443) {
                    get_tx("授权失效,请联系管理员处理")
                    notifyMasters("授权失效,请联系管理员处理")
                } else {

                    get_tx(login_ds.msg)


                    notifyMasters(JSON.stringify(sms_login))
                }
            }
            // get_tx("开始登录验证..")
        }

    } else if (login_ds.status == 443) {
        get_tx("授权失效,请联系管理员处理")
        notifyMasters("授权失效,请联系管理员处理")
    } else {
        get_tx(login_ds.msg)
        notifyMasters(JSON.stringify(login_ds))
    }


}


// 获取并校验手机号
function promptMobile(errorMsg) {
    var tip = `短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）...`

    var mobile = asse(tip)
    if (mobile == false) {
        return false
    }

    if (!checkModbile(mobile)) {
        get_tx(errorMsg || '输入手机号错误，自动退出程序...')
        return null
    }

    return mobile
}
function zack1_dx() {

    var ptpin = "", data = "", pro_zm = "", dat = 0
    let bind = bucketKeys("pin" + imType.toUpperCase(), userId)
    if (bind.length == 0) {
        var p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
        if (p == false) {
            return
        }
        if (!checkModbile(p)) {
            get_tx('输入手机号错误，自动退出程序,请您重新发送：登录')
            return
        }


    } else {
        ptpin += "请选择你的操作，输入数字\n[0] 新增账号\n"
        for (let j = 0; j < bind.length; j++) {
            var pin_phone = bucketGet("Autophone", bind[j])
            let jnStr = bucketGet("jdNotify", bind[j])
            if (jnStr == "") {
                pro_zm = "未登录\n"
            } else {

                //get_tx(`${bind[j]}-空内容`)
                jn = JSON.parse(jnStr)
                cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                var jc_ck = jdck(cookie)
                if (jc_ck) {
                    pro_zm = `有效\n`
                } else {
                    pro_zm = `失效\n`
                }
            }
            if (pin_phone == "") {
                ptpin += `[${j + 1}] ${decodeURIComponent(bind[j])} [未记录手机号] ${pro_zm}\n`
            } else {
                ptpin += `[${j + 1}] ${decodeURIComponent(bind[j])} [${hideMiddlePart(pin_phone)}] ${pro_zm}\n`
                dat = 1
            }

        }
        if (dat == 0) {
            var p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
            if (p == false) {
                return
            }
            if (!checkModbile(p)) {
                get_tx('输入手机号错误，自动退出程序,请您重新发送：登录')
                return
            }

        } else {
            get_tx(ptpin)
            var choice = input(30000, 1000)//表示等待用户输入，等待用户输入时间为30秒
            if (choice == 'q') {
                get_tx('退出成功')//给会话用户发送信息
                return
            }
            if (choice == '') {
                get_tx('输入超时，自动退出程序2')
                return
            }
            if (isNaN(choice) || choice > bind.length || choice < 0) {


                if (!checkModbile(choice)) {
                    get_tx('输入错误，自动退出程序..')
                    return
                }
            }
            if (choice == 0) {
                p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
                if (p == false) {
                    return
                }
                if (!checkModbile(p)) {
                    get_tx('输入错误，自动退出程序')
                    return
                }
            } else if (checkModbile(choice)) {
                p = choice
            } else {
                var pin_phone = bucketGet("Autophone", bind[choice - 1])
                if (pin_phone == "") {
                    p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
                    if (p == false) {
                        return
                    }
                    if (!checkModbile(p)) {
                        get_tx('输入手机号错误，自动退出程序,请您重新发送：登录')
                        return
                    }
                } else {
                    p = pin_phone
                }

            }
        }
    }
    get_tx("稍等,正在开始登录...耐心等候")
    for (let k = 0; k < 3; k++) {
        try {
            proxyIp = xk()

            var login_ds = zack1_sms(p, proxyIp)
            if (login_ds.status == "fail") {
                get_tx("代理失效,请您重新发送：登录")
                proxyIp = xk()
            }
            if (login_ds.err_code == 200 || login_ds.err_code == 0) {
                k = 5
                // get_tx(login_ds.msg)
                let w = asse(`${hideMiddlePart(p)},${login_ds.msg}`)
                if (w == false || w == "q" || w == "Q") {

                } else {

                    //get_tx(`${p}-${w}`)
                    let sms_login = zack1_smsVerify(p, w, login_ds.guid, login_ds.token, login_ds.appid, proxyIp)
                    if (sms_login.err_code == 200 || sms_login.err_code == 0) {
                        let str = sms_login.cookie
                        ck_pin = str.match(/(?<=pt_pin=)[^;]+/g)
                        let bbk_dxzdynr = bucketGet("who_tong", "bbk_dxzdynr") || "目前账密稳定，推送使用：账密登录";
                        get_tx(`报告老板，[ ${decodeURIComponent(ck_pin)} ],更新成功\n${bbk_dxzdynr}`)

                        // 截取方括号之间的内容

                        notifyMasters(`-->报告老板，[ ${decodeURIComponent(ck_pin)} ]短信3更新账号！\n-->绑定客户：${userId}(${imType})`)
                        bucketSet("Autophone", ck_pin, p)
                        breakIn(str)
                        // handleLoginSuccess(ck_pin);
                    } else if (sms_login.err_code == 203) {
                        get_tx(sms_login.msg || sms_login.err_msg || "请求结果未知")
                        let dd = sms_login.msg || sms_login.err_msg || "请求结果未知"
                        get_tx(`${sms_login.err_code}--${dd}..请您重新发送：登录`)
                    } else if (sms_login.err_code == 8) {
                        if (bbk_wskey_dxjk == "") {
                            get_tx(`请您先去京东APP上登录,如果登录还是出现这个，请您使用验证码登录,使用1或者3的方式登录`)
                        } else {
                            let wskey_login = bucketGet("who_tong", "bbk_fkkg")
                            if (wskey_login == "true") {
                                // bbk_wskey_dy(p)
                                get_tx(`请您先去京东APP上登录,如果登录还是出现这个，请您使用验证码登录,使用1或者3的方式登录`)
                            } else {
                                get_tx(`请您先去京东APP上登录,如果登录还是出现这个，请您使用验证码登录,使用1或者3的方式登录`)
                            }
                        }
                    } else if (sms_login.err_code == 202) {
                        let dd = sms_login.msg || sms_login.err_msg || "请求结果未知"
                        get_tx(`${sms_login.err_code}--${dd}..请您重新发送：登录`)
                    } else if (sms_login.err_code == 118) {
                        let dd = sms_login.msg || sms_login.err_msg || "请求结果未知"
                        if (bbk_rlyz == "") {
                            get_tx(`${sms_login.err_code}--${dd}..请您重新发送：登录`)
                        } else {
                            get_tx(bbk_rlyz)
                        }
                        //get_tx(`${sms_login.err_code}--${dd}..请您重新发送：登录`)
                    } else if (sms_login.err_code == 443) {
                        get_tx("授权失效,请联系管理员处理")
                        notifyMasters("授权失效,请联系管理员处理")
                    } else {
                        if (sms_login.msg || sms_login.err_msg || "请求结果未知" == "验证码输入错误") {

                            let dd = sms_login.msg || sms_login.err_msg || "请求结果未知"
                            get_tx(`${dd}.....请您重新发送：登录`)
                        } else {

                            get_tx(sms_login.err_code)


                            notifyMasters(JSON.stringify(sms_login))
                        }
                    }
                    // get_tx("开始登录验证..")
                }
            } else if (login_ds.err_code == 179) {
                //k = 5
                get_tx(login_ds.err_msg)
                notifyMasters(login_ds.err_msg)
                proxyIp = xk()
            } else if (login_ds.err_code == 443) {
                k = 5
                get_tx("授权失效,请联系管理员处理")
                notifyMasters("授权失效,请联系管理员处理")
            } else if (login_ds.err_code == 100) {
                k = 5
                get_tx("登录失败,请您重新发送：登录")
            } else {
                k = 5
                get_tx(login_ds.msg || login_ds.err_msg || "请求结果未知")

                notifyMasters(JSON.stringify(login_ds))
            }
        } catch (e) { }
    }
}
function checkModbile(mobile) {
    var re = /^1[3,4,5,6,7,8,9][0-9]{9}$/;
    var result = re.test(mobile);
    if (!result) {
        return false;//若手机号码格式不正确则返回false
    }
    return true;
}
//验证码处理
function checkCode(code) {
    var re = /^[0-9]{6}$/;
    var result = re.test(code);
    if (!result) {
        return false;//若手机号码格式不正确则返回false
    }
    return true;
}
//-----BBK--------
function bbk_sms(mobile) {
    if (bbk_socks_ms == "true") {
        socks5proxy = socks_mian("socks5-get", mobile)
    }
    for (let i = 0; i < 3; i++) {
        if (bbk_socks_ms == "true") {
            var obj = { mobile, socks5proxy };
        } else {
            var obj = { mobile };
        }
        let qd = stxs.split(",");
        let qdsign = sign(obj)
        // get_tx(JSON.stringify(qdsign))
        //get_tx(qdsign.sign)
        let body = request({
            method: "get",
            url: `${bbk_jk}/xcx/sendSms?${objToStr(qdsign)}`,
            // body: JSON.stringify(sign(obj)),
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            dataType: "json",
            timeOut: 80000
        });

        if (!body) {
            if (bbk_jksb) get_tx(bbk_jksb);
            sleep(3000);
            continue;
        } else {
            i = 5
            // get_tx(JSON.stringify(body))
            return body
        }

    }
}
function bbk_smsVerify(mobile, authCode) {
    if (bbk_socks_ms == "true") {
        socks5proxy = socks_mian("socks5-get", mobile)
    }
    for (let i = 0; i < 3; i++) {
        if (bbk_socks_ms == "true") {
            var obj = { mobile, authCode, socks5proxy };
        } else {
            var obj = { mobile, authCode };
        }
        let qd = stxs.split(",");
        let qdsign = sign(obj)
        // get_tx(JSON.stringify(qdsign))
        //  get_tx(qdsign.sign)
        let body = request({
            method: "get",
            url: `${bbk_jk}/xcx/smsVerify?${objToStr(qdsign)}`,
            // body: JSON.stringify(sign(obj)),
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            dataType: "json",
            timeOut: 80000
        });

        if (!body) {
            if (bbk_jksb) get_tx(bbk_jksb);
            sleep(3000);
            continue;
        } else {
            i = 5
            // get_tx(JSON.stringify(body))
            return body
        }

    }
}
//-----其他接口--------
function zack_sms(mobile) {

    for (let i = 0; i < 3; i++) {
        var obj = { mobile, vkey };
        let qd = stxs.split(",");
        // let qdsign = sign(obj)
        // get_tx(JSON.stringify(qdsign))
        //get_tx(qdsign.sign)
        let body = request({
            method: "post",
            url: `https://jdsms.zack.xin/api/sms_vip.php?vkey=${vkey}`,
            body: JSON.stringify(obj),
            headers: { "Content-Type": "application/json; charset=utf-8" },
            dataType: "json",
            timeOut: 80000
        });
        console.log("发送验证码" + JSON.stringify(body))
        if (!body) {
            if (bbk_jksb) get_tx(bbk_jksb);
            sleep(3000);
            continue;
        } else {
            i = 5
            // get_tx(JSON.stringify(body))
            return body
        }

    }
}
function zack_smsVerify(mobile, smsCode, guid, lsid) {
    let isTask = "notask", ps = ""
    for (let i = 0; i < 3; i++) {

        var obj = { mobile, smsCode, vkey, isTask, ps, guid, lsid };
        console.log("登录" + JSON.stringify(obj))
        let qd = stxs.split(",");

        let body = request({
            method: "post",
            url: `https://jdsms.zack.xin/api/sms_vip.php?vkey=${vkey}`,
            body: JSON.stringify(obj),
            headers: { "Content-Type": "application/json; charset=utf-8" },
            dataType: "json",
            timeOut: 80000
        });
        console.log("登录" + JSON.stringify(body))
        if (!body) {
            if (bbk_jksb) get_tx(bbk_jksb);
            sleep(3000);
            continue;
        } else {
            i = 5
            // get_tx(JSON.stringify(body))
            return body
        }

    }
}

//-----BBK 短信wskey----
function bbk_wskey_dx() {

    var ptpin = "", data = "", pro_zm = "", dat = 0
    let bind = bucketKeys("pin" + imType.toUpperCase(), userId)
    if (bind.length == 0) {
        var p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
        if (p == false) {
            return
        }
        if (!checkModbile(p)) {
            get_tx('输入手机号错误，自动退出程序,请您重新发送：登录')
            return
        }


    } else {
        ptpin += "请选择你的操作，输入数字\n[0] 新增账号\n"
        for (let j = 0; j < bind.length; j++) {
            var pin_phone = bucketGet("Autophone", bind[j])
            let jnStr = bucketGet("jdNotify", bind[j])
            if (jnStr == "") {
                pro_zm = "未登录\n"
            } else {

                jn = JSON.parse(jnStr)
                cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
                var jc_ck = jdck(cookie)
                if (jc_ck) {
                    pro_zm = `有效\n`
                } else {
                    pro_zm = `失效\n`
                }
            }


            if (pin_phone == "") {
                ptpin += `[${j + 1}] ${decodeURIComponent(bind[j])} [未记录手机号] ${pro_zm}\n`
            } else {
                ptpin += `[${j + 1}] ${decodeURIComponent(bind[j])} [${hideMiddlePart(pin_phone)}] ${pro_zm}\n`
                dat = 1
            }

        }
        if (dat == 0) {
            var p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
            if (p == false) {
                return
            }
            if (!checkModbile(p)) {
                get_tx('输入手机号错误，自动退出程序,请您重新发送：登录')
                return
            }

        } else {
            get_tx(ptpin)
            var choice = input(30000, 1000)//表示等待用户输入，等待用户输入时间为30秒
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
                p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
                if (p == false) {
                    return
                }
                if (!checkModbile(p)) {
                    get_tx('输入错误，自动退出程序')
                    return
                }
            } else {
                var pin_phone = bucketGet("Autophone", bind[choice - 1])
                if (pin_phone == "") {
                    p = asse(`短信服务在线！请输入11位手机号：
（输入“q”即可退出会话）`)
                    if (p == false) {
                        return
                    }
                    if (!checkModbile(p)) {
                        get_tx('输入手机号错误，自动退出程序,请您重新发送：登录')
                        return
                    }
                } else {
                    p = pin_phone
                }

            }
        }
    }

    bbk_sms_wskey(p)
    //console.log("短信登录接口返回数据：" + "----" + login_ds.code + `${login_ds.uid}---${login_ds.cookie}`)
    console.log("短信登录接口返回数据：" + bbk_add_yz)
    if (bbk_add_yz) {
        get_tx("稍等,正在开始登录...耐心等候....")
        bbk_add_yz = false
        bbk_sms_uid()
        if (bbk_add_yz == false) {
            return
        }
        let w = asse(`${hideMiddlePart(p)},${bbk_add_yz}`)
        if (w == false) {

        } else {

            console.log("--***----" + bbk_add_yz)
            if (bbk_add_yz) {
                bbk_sms_verify(w)

            } else {
                get_tx("短信验证码发送失败,请您重新发送：登录")
            }

        }
        //get_tx(login_ds?.errorMsg + "---------")

    }


}
function bbk_wskey_dy(p) {

    var ptpin = "", data = "", pro_zm = "", dat = 0


    bbk_sms_wskey(p)
    //console.log("短信登录接口返回数据：" + "----" + login_ds.code + `${login_ds.uid}---${login_ds.cookie}`)
    console.log("短信登录接口返回数据：" + bbk_add_yz)
    if (bbk_add_yz) {
        //get_tx("稍等,正在开始登录...耐心等候....")
        bbk_add_yz = false
        bbk_sms_uid()
        if (bbk_add_yz == false) {
            return
        }
        let w = asse(`"稍等,正在开始登录...耐心等候...."`)
        if (w == false) {

        } else {

            console.log("--***----" + bbk_add_yz)
            if (bbk_add_yz) {
                bbk_sms_verify(w)

            } else {
                get_tx("短信验证码发送失败,请您重新发送：登录")
            }

        }
        //get_tx(login_ds?.errorMsg + "---------")

    }


}
//uid检测
function bbk_sms_uid() {
    // 先简单校验手机号格式（大陆11位数字）
    for (let i = 0; i < 6; i++) {
        let res = request({
            method: "get",
            url: `${bbk_wskey_dxjk}/sms/status?uid=${uid}`,
            headers: { "Cookie": cookie },
            dataType: "json",
            timeOut: 80000
        });


        if (res.code === 201 || res.code === 200) {
            get_tx(`短信验证码发送成功，`);
            bbk_add_yz = true
            return
        } else if (res.code === 199) {
            sleep(3000)
        } else if (res.code === 500) {
            get_tx(`${res.errorMsg}\n短信验证码发送失败,请您重新发送：登录`)
            bbk_add_yz = false
            return
        } else if (res.errorMsg.indexOf("验证码类型") > -1) {
            get_tx(`${res.errorMsg}\n短信验证码发送失败,请您重新发送：登录`)
            bbk_add_yz = false
            return
        }
    }
}

//获取验证码
function bbk_sms_wskey(phone) {
    // 先简单校验手机号格式（大陆11位数字）
    if (!phone || !/^1[3-9]\d{9}$/.test(phone)) {
        get_tx(`手机号格式错误: ${phone}，请检查后重试`);
        return;
    }

    for (let i = 0; i < 6; i++) {

        //let bodyData = { phone: phone };   // 根据实际接口调整字段名（可能是 "mobile" 或 "tel"）


        request({
            url: `${bbk_wskey_dxjk}/sms/sendSms?phone=${phone}`,
            method: "get",
            dataType: "json",
            timeOut: 80000
        }, function (error, response, header, res) {
            const simple = Object.fromEntries(
                Object.entries(header).map(([k, v]) => [k, v[0]])
            )
            cookie = simple["Set-Cookie"]
            uid = res.data?.uid
            if (res.code == 200) {
                i = 9
                get_tx(`短信验证码发送成功，uid: ${res.data?.uid || '无'}`);
                // return res.data?.uid || false // 返回uid供后续使用，如果接口没有返回uid则返回false
                bbk_add_yz = true
                return
            } else {
                get_tx(`发送..失败: ${res.errorMsg}`)
                sleep(2000)
            }
        })
    }
}
//获取COOKIE
function bbk_sms_verify(code) {
    // 先简单校验手机号格式（大陆11位数字）


    for (let i = 0; i < 5; i++) {
        console.log(`第 ${i + 1} 次尝试发送短信验证码，手机号: ${code}-${uid}`);

        //let bodyData = { phone: phone };   // 根据实际接口调整字段名（可能是 "mobile" 或 "tel"）

        let res = request({
            method: "get",
            url: `${bbk_wskey_dxjk}/sms/verify?code=${code}&uid=${uid}`,
            headers: { "Cookie": cookie },
            dataType: "json",
            timeOut: 80000
        });

        console.log(`第 ${i + 1} 次--bbk_sms_verify--响应: ${JSON.stringify(res)}`)

        if (res.code === 202) {
            let str = res.data?.cookie || ""
            let errorObj = {}
            try {
                errorObj = typeof res.errorMsg === 'string' ? JSON.parse(res.errorMsg) : res.errorMsg
            } catch (e) {
                console.log("errorMsg 解析失败：", e)
            }
            let start = errorObj?.validateUrl

            qrcode_api(start)
            get_tx(`保存二维码,然后使用京东APP二维码识别，并完成验证，验证码/人脸识别验证\n-->在发送：登录，在选择1或者3的方式登录`)
            return
        } else if (res.code === 500) {
            if (res.errorMsg.indexOf("请重新获取验证码") > -1) {
                get_tx(`${res.errorMsg}\n请您重新发送：登录`)
                return
            } else if (res.errorMsg.indexOf("验证码输入错误") > -1) {
                get_tx(`${res.errorMsg}\n请您重新发送：登录`)
                return
            } else {

            }

        }


    }

    //get_tx(`手机号 ${phone} 发送短信验证码失败，已重试3次`);
}

function normalizeHeaders(header) {
    const result = {};
    if (!header || typeof header !== "object") return result;

    for (const [k, v] of Object.entries(header)) {
        result[k] = Array.isArray(v) ? v[0] : v;
    }
    return result;
}






//-----其他接口1--------
function zack1_sms(mobile, proxyIp) {
    //  proxyIp=xk()
    for (let i = 0; i < 3; i++) {
        var obj = { mobile, proxyIp };
        // let qd = stxs.split(",");
        // let qdsign = sign(obj)
        console.log(JSON.stringify(obj) + "登录")
        //get_tx(qdsign.sign)
        let body = request({
            method: "post",
            url: `https://jdsms.zack.xin/jd/sms_wx/sms2/api/app.php?type=login&vkey=${vkey}`,
            body: JSON.stringify(obj),
            headers: { "Content-Type": "application/json;charset=UTF-8" },
            //dataType: "json",
            timeOut: 80000
        });
        console.log("发送验证码" + JSON.stringify(body))
        if (body) {
            i = 5
            // get_tx(JSON.stringify(body))
            console.log(`${typeof body}-body`);

            let data = strToJson(body)
            console.log(`${typeof data}-data--${data.err_code}`);


            return data

        } else {
            sleep(3000)
        }

    }
}
function zack1_smsVerify(mobile, smsCode, guid, token, appid, proxyIp) {
    let isTask = "notask", ps = ""
    for (let i = 0; i < 3; i++) {

        var obj = { mobile, smsCode, vkey, isTask, ps, guid, token, appid, proxyIp };
        console.log("登录.." + JSON.stringify(obj))
        let qd = stxs.split(",");

        let body = request({
            method: "post",
            url: `https://jdsms.zack.xin/jd/sms_wx/sms2/api/app.php?type=dophonelogin&vkey=${vkey}`,
            body: JSON.stringify(obj),
            headers: { "Content-Type": "application/json; charset=utf-8" },
            // dataType: "json",
            timeOut: 80000
        });
        console.log("zack1_smsVerify登录" + JSON.stringify(body))
        if (body) {
            i = 5
            // get_tx(JSON.stringify(body))
            return strToJson(body)
        } else {
            sleep(3000)
        }

    }
}
function strToJson(str) {
    if (typeof str !== 'string') return null;
    try {
        //  先清BOM头（关键解决ï报错）+ 首尾空白
        let jsonStr = str.trim().replace(/^\uFEFF/, '');
        //  原有修正逻辑不变
        jsonStr = jsonStr
            .replace(/(['"])?([a-zA-Z0-9_]+)(['"])?:/g, '"$2":')
            .replace(/'/g, '"')
            .replace(/,(\s*[}\]])/g, '$1');
        return JSON.parse(jsonStr);
    } catch (e) {
        console.log('解析失败', e);
        return null;
    }
}
function objToStr(form) {
    return Object.keys(form).map(function (k) {
        if (typeof form[k] === "object") {
            return encodeURIComponent(k) + '=' + encodeURIComponent(JSON.stringify(form[k]));
        } else {
            return encodeURIComponent(k) + '=' + encodeURIComponent(form[k])
        }
    }).join('&');
}





function sign(params) {
    let p1 = Object.assign({}, params);
    let ps = Object.keys(params).sort().map(key => {
        return {
            key: key,
            value: params[key]
        }
    });
    const n1 = ps.map(o => `${o.key}:${o.value}`).join('&');
    let ts = Date.now();
    let param = `${n1}${ts}`;
    let md5Str = CryptoJS.MD5(param).toString();
    let leftStr = md5Str.slice(0, 20).split("").reverse().join("");
    let resultArr = [];
    for (let i = 0; i < leftStr.length; i += 2) {
        resultArr.push(leftStr.substr(i, 2).split("").reverse().join(""));
    }
    let s = resultArr.join("") + md5Str.slice(20);
    p1.sign = s;
    p1.ts = ts;
    return p1;
}
function xk() {
    let body = request({
        url: bbk_xkip,
        method: "get",
        // body: water,
        headers: {
            //"Host": "h5.xss333.top:8001",
            "Content-Type": "application/json; charset=utf-8",
        },
        // dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    if (body) {
        console.log(body.trim() + "IP")
        return body.trim();
        /* if (body.status == 100) {
             //var IOP = `${body.data[0].ip}:${body.data[0].port}`
             return body
         }
    */
    }
}
function subCKToXZ(PIN) {
    // get_tx(PIN+"，PIN")        
    // try {
    //let name =xianbao
    //获取青龙容器名
    var containerData = JSON.parse(bucketGet("who_tong", "bbk_qljson"))
    // 获取容器对象
    let container

    try {
        container = Qinglong(containerData[0].host, containerData[0].client_id, containerData[0].client_secret)
        containerEnv = container.ApiQL("envs", "", "get", "").data
    } catch (e) {
        notifyMasters("【BBK账密登陆】链接同步容器失败，请检查配置是否正确或网络是否正常")
        return
    }
    // 在环境变量里面匹配USERID值 获取对应数据

    let msg
    try {
        let cookieObj = containerEnv.filter(function (_data) {
            return _data.name == "JD_COOKIE" && _data.value.indexOf(PIN) != -1
        });
        // 判断有没有找到相应ck对象
        if (cookieObj.length == 0) {
            get_tx("获取CK失败,重新登陆")
            return
        } else {
            let cookie = cookieObj[0].value
            var jd_pin = cookie.match(/(?<=pt_pin=)[^;]+/g)
            var jd_key = cookie.match(/(?<=pt_key=)[^;]+/g)
            var id_cookie = `pt_key=${jd_key};pt_pin=${jd_pin};`
            breakIn(id_cookie)
            if (bbk_delck == "true") {
                container.ApiQL("envs", "", "DELETE", `[${cookieObj[0].id}]`)
            }
            return
        }



    } catch (e) {

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

function dengdai() {
    let biaoji = false
    for (let i = 0; i < 10; i++) {
        let data = bucketGet("who_tong", "bbk_jincheng")
        if (data == "true" || data == true) {
            console.warn(`上一个进程还未完成,等待中...${i}...`)
            sleep(6000)
        } else {
            console.warn(`上一个进程完成开始执行.....`)
            bucketSet("who_tong", "bbk_jincheng", true)
            biaoji = true
            return true
        }

    }
    if (biaoji) {
        return true
    } else {
        return false
    }

}


/**
 * 统一初始化选择器（修复重复定义，兼容补全字段）
 * @param {string} jsonData - bucket存储的JSON字符串
 * @returns {Array} 选择器数据（含 value/maxCount/currentCount）
 * @throws {Error} 无配置或格式错误时抛出
 */
function initSelector(jsonData) {
    // 无配置直接抛出错误
    if (!jsonData || jsonData.trim() === "") {
        throw new Error("未检测到任何配置数据！\n\n💡 请先添加配置（JSON数组）：\n[{'value':'代理1|端口|账号|密码','maxCount':10},...]");
    }

    try {
        const items = JSON.parse(jsonData);
        // 验证数组格式
        if (!Array.isArray(items) || items.length === 0) {
            throw new Error('JSON必须是非空数组格式');
        }

        // 验证并补全字段
        return items.map(item => {
            if (!('value' in item)) throw new Error(`缺少"value"字段：${JSON.stringify(item)}`);
            if (!('maxCount' in item)) throw new Error(`缺少"maxCount"字段：${JSON.stringify(item)}`);
            if (typeof item.maxCount !== 'number' || item.maxCount <= 0 || !Number.isInteger(item.maxCount)) {
                throw new Error(`"maxCount"必须是正整数：${JSON.stringify(item)}`);
            }
            // 补全currentCount（兼容新增配置，默认0）
            const currentCount = ('currentCount' in item) ? item.currentCount : 0;
            if (currentCount < 0 || currentCount > item.maxCount) {
                throw new Error(`"currentCount"异常（需0-${item.maxCount}）：${JSON.stringify(item)}`);
            }
            return {
                value: item.value,
                maxCount: item.maxCount,
                currentCount: currentCount
            };
        });
    } catch (err) {
        throw new Error(`配置解析失败：${err.message}\n\n💡 正确示例：\n[
{"value":"474.ips5.vip|9125|2024765|ac630caa2","maxCount":10},
{"value":"14.22.114.104|2081|ozfm18q1|ozfm18q1","maxCount":8}
]`);
    }
}

/**
 * 平均概率获取一个值（获取后自动更新使用次数）
 * @param {Array} selector - 初始化后的选择器数据
 * @returns {any|null} 选中的值，无可用值返回null
 */
function getAverageValue(selector) {
    const availableItems = selector.filter(item => item.currentCount < item.maxCount);
    if (availableItems.length === 0) {
        get_tx("⚠️ 所有值都已达到最大使用次数，暂时无法获取！");
        return null;
    }

    // 按剩余次数加权计算
    const totalWeight = availableItems.reduce(
        (sum, item) => sum + (item.maxCount - item.currentCount),
        0
    );

    // 随机选中
    let randomNum = Math.random() * totalWeight;
    let selectedItem = null;
    for (const item of availableItems) {
        const remaining = item.maxCount - item.currentCount;
        randomNum -= remaining;
        if (randomNum <= 0) {
            selectedItem = item;
            break;
        }
    }

    selectedItem.currentCount++;
    return selectedItem.value;
}


/**
 * 顺序获取值（kfhq指令）- 平均顺序使用，循环选取剩余次数>0的项
 */
function socks_hq() {
    try {
        const storedJson = bucketGet("Auto_IP", "socks5");
        const selector = initSelector(storedJson);
        // 过滤出还有剩余次数的项（避免选到已用尽的）
        const availableItems = selector.filter(item => item.currentCount < item.maxCount);

        if (availableItems.length === 0) {
            const reply = "❌ 所有socks5节点已用尽次数！";
            notifyMasters(reply);
            console.log(`用户${userId}触发kfhq，无可用节点`);
            return;
        }

        // 关键：按数组顺序查找「上一次未选中/已选中但可继续使用」的项，实现顺序循环
        // 优先找 currentCount 最小的项；若有多个，按数组顺序取第一个（保证平均）
        let targetItem = availableItems.reduce((prev, curr) => {
            // 比较已用次数，取次数最少的；次数相同则保留先出现的
            return prev.currentCount < curr.currentCount ? prev : curr;
        }, availableItems[0]);

        // 递增当前选中项的使用次数
        targetItem.currentCount += 1;
        const result = targetItem.value;

        // 构建回复信息
        let reply = "🎯 顺序获取结果（平均分配）\n";
        reply += "----------------------------------------\n";
        reply += `选中值：${result}\n`;
        reply += `已用次数：第${targetItem.currentCount}次\n`;
        reply += `剩余次数：${targetItem.maxCount - targetItem.currentCount}次\n`;
        reply += "----------------------------------------\n";

        // notifyMasters(reply);
        const updatedJson = exportSelector(selector);
        bucketSet("Auto_IP", "socks5", updatedJson);
        console.log(`用户${userId}触发kfhq，顺序选中：${result}，已用次数：${targetItem.currentCount}`);
        return result;
    } catch (globalErr) {
        notifyMasters(`❌ 顺序获取socks5失败：\n${globalErr.message}`);
        console.error("异常详情：", globalErr);
    }
}
/**
 * 手动调整指定值的使用次数（支持增加/减少）
 * @param {Array} selector - 选择器数据
 * @param {any} targetValue - 目标值
 * @param {number} changeCount - 调整数量（正数=增加，负数=减少）
 * @returns {Object|null} 调整后的状态
 */
function adjustValueCount(selector, targetValue, changeCount) {
    // 参数验证
    if (!Array.isArray(selector) || selector.length === 0) {
        console.error("调整失败：选择器数据无效");
        return null;
    }
    if (typeof changeCount !== 'number' || !Number.isInteger(changeCount)) {
        console.error("调整失败：调整数量必须是整数");
        return null;
    }
    if (changeCount === 0) {
        console.warn("调整数量为0，无需操作");
        return selector.find(item => item.value === targetValue) || null;
    }

    // 查找目标值
    const targetItem = selector.find(item => item.value === targetValue);
    if (!targetItem) {
        console.error(`调整失败：未找到值 "${targetValue}"`);
        return null;
    }

    // 边界校验
    const newCurrentCount = targetItem.currentCount + changeCount;
    if (newCurrentCount < 0) {
        console.error(`调整失败：已用次数不能小于0（当前：${targetItem.currentCount}，调整：${changeCount}）`);
        return null;
    }
    if (newCurrentCount > targetItem.maxCount) {
        console.error(`调整失败：已用次数不能超过最大次数（最大：${targetItem.maxCount}，当前：${targetItem.currentCount}，调整：${changeCount}）`);
        return null;
    }

    // 执行调整
    targetItem.currentCount = newCurrentCount;
    const remaining = targetItem.maxCount - newCurrentCount;
    return {
        value: targetItem.value,
        maxCount: targetItem.maxCount,
        currentCount: targetItem.currentCount,
        remaining: remaining
    };
}

/**
 * 恢复指定值1次使用次数（currentCount-1，剩余+1）
 * @param {string} targetValue - 要恢复的目标值（默认提示用户输入）
 */
function huifucs(targetValue = null) {
    try {
        const storedJson = bucketGet("Auto_IP", "socks5");
        const selector = initSelector(storedJson);

        // 若未指定目标值，提示用户
        if (!targetValue || targetValue.trim() === "") {
            get_tx("📌 请回复要恢复的完整值（与配置一致）：\n示例：474.ips5.vip|9125|2024765|ac630caa2");
            // 监听用户后续回复（适配Aut插件的交互逻辑）
            return;
        }

        // 执行恢复（减少1次使用次数=恢复1次）
        const result = adjustValueCount(selector, targetValue.trim(), -1);
        if (result) {
            get_tx(`✅ 恢复成功！\n值：${result.value}\n已用次数：${result.currentCount}次\n剩余次数：${result.remaining}次`);
            // 保存修改
            const updatedJson = exportSelector(selector);
            bucketSet("Auto_IP", "socks5", updatedJson);
        } else {
            get_tx("❌ 恢复失败，请检查值是否正确或已用次数是否为0");
        }
    } catch (err) {
        get_tx(`❌ 恢复失败：\n${err.message}`);
        console.error("恢复异常：", err);
    }
}

function exportSelector(selector) {
    return JSON.stringify(selector);
}



/**
 * 工具函数：确保位置标记为有效整数（修复类型错误）
 * @returns {number} 有效位置索引
 */
function getValidCurrentPos(totalCount) {
    // 1. 从独立命名空间读取原始值（强制转为字符串处理）
    const storedPosStr = String(bucketGet(POS_NS, POS_KEY) || "0").trim();
    // 2. 严格转为整数（失败则返回0）
    let currentPos = parseInt(storedPosStr, 10);
    currentPos = isNaN(currentPos) ? 0 : currentPos;
    // 3. 边界校正（确保在0~totalCount-1之间）
    if (currentPos < 0 || currentPos >= totalCount) {
        currentPos = 0;
        // 同步校正存储的标记
        bucketSet(POS_NS, POS_KEY, "0");
    }
    return currentPos;
}

/**
 * 核心函数：顺序获取一个数据并更新位置标记（修复递增逻辑）
 * @returns {Object} 结果对象（含数据、位置标记、状态）
 */
function socks5Get() {
    try {
        // 1. 获取原始数据所有Key和总数量
        const allDataKeys = bucketKeys(DATA_NS);
        const totalCount = allDataKeys.length;

        // 2. 校验是否有数据
        if (totalCount === 0) {
            return {
                success: false,
                message: "❌ socks5命名空间下无任何数据！"
            };
        }

        // 3. 获取有效当前位置（修复类型错误和边界问题）
        const currentPos = getValidCurrentPos(totalCount);

        // 4. 强制验证当前位置对应的Key存在（双重保险）
        if (!allDataKeys[currentPos]) {
            throw new Error(`索引${currentPos}无对应数据，已自动重置`);
        }

        // 5. 获取原始数据（确保Key有效）
        const targetDataKey = allDataKeys[currentPos];
        const targetData = bucketGet(DATA_NS, targetDataKey);
        if (targetData === null || targetData === undefined) {
            return {
                success: false,
                message: `❌ 索引${currentPos}对应的数据为空！`
            };
        }

        // 6. 计算下一个位置（强制整数运算，避免NaN）
        const nextPos = (currentPos + 1) % totalCount; // 循环递增：0→1→2→...→totalCount-1→0

        // 7. 强制写入下一个位置标记（转为字符串存储，避免类型问题）
        bucketSet(POS_NS, POS_KEY, String(nextPos));

        // 8. 日志记录（便于排查位置变化）
        console.log(`用户${userId},当前位置${currentPos} → 下次位置${nextPos}，Key=${targetDataKey}`);

        // 9. 返回结果
        return {
            success: true,
            totalCount: totalCount,
            currentPos: currentPos,
            nextPos: nextPos,
            targetDataKey: targetDataKey,
            data: targetData,
            message: "✅ 数据获取成功！"
        };
    } catch (err) {
        console.error(`用户${userId}获取socks5数据失败：`, err);
        // 异常时重置位置标记
        bucketSet(POS_NS, POS_KEY, "0");
        return {
            success: false,
            message: `❌ 数据获取失败：${err.message}，已重置位置标记`
        };
    }
}

/**
 * 查询统计（实时获取最新位置，避免缓存）
 * @returns {Object} 统计结果
 */
function socks5Count() {
    try {
        const allDataKeys = bucketKeys(DATA_NS);
        const totalCount = allDataKeys.length;

        if (totalCount === 0) {
            return {
                success: false,
                message: "❌ socks5命名空间下无任何数据！"
            };
        }

        // 实时获取最新位置（不缓存）
        const currentPos = getValidCurrentPos(totalCount);
        const nextGetDataKey = allDataKeys[currentPos] || "无";

        return {
            success: true,
            message: `📊 socks5数据统计\n总数量：${totalCount}条\n当前位置标记：${currentPos}（索引）\n下次将获取：${nextGetDataKey}\n位置标记存储：${POS_NS}→${POS_KEY}`
        };
    } catch (err) {
        console.error(`用户${userId}查询socks5统计失败：`, err);
        return {
            success: false,
            message: `❌ 查询失败：${err.message}`
        };
    }
}

/**
 * 重置位置标记（强制写入0）
 * @returns {Object} 重置结果
 */
function socks5Reset() {
    try {
        bucketSet(POS_NS, POS_KEY, "0");
        console.log(`用户${userId}socks5-reset：位置标记已重置为0`);
        return {
            success: true,
            message: `✅ 位置标记已重置为0！\n下次将从第1条数据开始获取\n位置标记存储：${POS_NS}→${POS_KEY}`
        };
    } catch (err) {
        console.error(`用户${userId}重置socks5位置失败：`, err);
        return {
            success: false,
            message: `❌ 重置失败：${err.message}`
        };
    }
}

/**
 * 主逻辑：socks5 顺序调用
 */
function socks_mian(socks, phone) {
    const cmd = socks
    let result;

    switch (cmd) {
        case "socks5-get":
            result = socks5Get();
            if (result.success) {
                let reply = "🎯 socks5数据获取成功\n";
                reply += "----------------------------------------\n";
                reply += `总数据量：${result.totalCount}条,（第${result.currentPos + 1}条）\n`;
                reply += `获取数据：${result.data},使用号码:${phone}\n`;

                reply += "----------------------------------------\n";
                reply += `位置标记已更新为：${result.nextPos}（第${result.nextPos + 1}条）\n`;
                //notifyMasters(reply);
                return result.data
            } else {
                get_tx(result.message);
            }
            break;

        case "socksout":
            result = socks5Count();
            get_tx(result.message);
            break;

        case "socksret":
            result = socks5Reset();
            get_tx(result.message);
            break;

        default:
            get_tx("❌ 未知指令！\n支持指令：\n- socks5-get：顺序获取下一条数据\n- socks5-count：查询总数量+当前位置\n- socks5-reset：重置位置标记");
    }
}

/**
 * 导入 socks5 数据到 who_socks5 命名空间
 * @param {string} socks5Str - 多行 socks5 数据（每行格式：IP|端口|用户名|密码|[到期时间]）
 * @param {boolean} [overwrite=true] - 已存在相同用户名时是否覆盖（默认覆盖）
 * @returns {Object} 导入结果
 */
function importSocks5(socks5Str, overwrite = true) {
    try {
        // 1. 校验输入
        if (!socks5Str || socks5Str.trim() === "") {
            return {
                success: false,
                message: "❌ 导入失败：socks5 数据不能为空"
            };
        }

        // 2. 按行拆分数据（兼容 \n/\r\n 换行符）
        const lines = socks5Str.trim().split(/\r?\n/).filter(line => line.trim() !== "");
        if (lines.length === 0) {
            return {
                success: false,
                message: "❌ 导入失败：无有效行数据"
            };
        }

        // 3. 遍历处理每行数据
        let successCount = 0; // 成功导入数量
        let skipCount = 0;    // 跳过数量（重复且不覆盖/格式错误）
        let overwriteCount = 0; // 覆盖数量
        const importedUsers = []; // 成功导入的用户名列表

        for (const line of lines) {
            // 按 | 拆分每行（最多拆4段，剔除到期时间）
            const parts = line.split("|").map(item => item.trim()).filter(item => item !== "");

            // 校验格式：至少需要 IP、端口、用户名、密码（前4段）
            if (parts.length < 4) {
                console.warn(`跳过无效行：格式错误，行内容=${line}`);
                skipCount++;
                continue;
            }

            // 提取核心字段（剔除第5段及以后的到期时间）
            const [ip, port, username, password] = parts;
            // 校验核心字段有效性
            if (!ip || !port || !username || !password) {
                console.warn(`跳过无效行：核心字段为空，行内容=${line}`);
                skipCount++;
                continue;
            }

            // 检查用户名是否已存在
            const exists = bucketKeys(SOCKS5_NS).includes(username);
            if (exists && !overwrite) {
                console.warn(`跳过重复用户名：${username}（已存在且不覆盖）`);
                skipCount++;
                continue;
            }

            // 组装 socks5 连接串（格式：socks5://用户名:密码@IP:端口）
            const socks5Url = `${ip}|${port}|${username}|${password}`;

            // 写入到 who_socks5 命名空间（以用户名作为 Key）
            bucketSet(SOCKS5_NS, username, socks5Url);

            // 统计
            successCount++;
            importedUsers.push(username);
            if (exists && overwrite) {
                overwriteCount++;
            }
        }

        // 4. 结果汇总
        console.log(`socks5 导入完成：成功${successCount}条，跳过${skipCount}条，覆盖${overwriteCount}条`);
        return {
            success: true,
            message: `✅ socks5 数据导入成功！
总处理行数：${lines.length}条
成功导入：${successCount}条
跳过（格式错误/重复）：${skipCount}条
覆盖已有：${overwriteCount}条
成功导入的用户名：${importedUsers.slice(0, 10).join("、")}${importedUsers.length > 10 ? "..." : ""}`,
            successCount: successCount,
            skipCount: skipCount,
            overwriteCount: overwriteCount,
            importedUsers: importedUsers
        };
    } catch (err) {
        console.error("socks5 导入异常：", err);
        return {
            success: false,
            message: `❌ 导入异常：${err.message}`
        };
    }
}