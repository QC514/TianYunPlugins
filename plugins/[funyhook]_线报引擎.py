//[author: funyhook]
//[create_at: 2023-09-02 11:33:43]
//[version: 6]
//[title: 线报引擎]
//[service: funyhook]
//[description: 爬虫羊毛线报(红包，零钱，满减...)引擎，自动采集/分发薅羊毛线报，默认15秒采集一次\n【使用方法】1、设置发送群组命令，set otto wool_push_groups qqgroup:123,wxgroup:456,tbgroup:-100123,tggroup:123 <br/>关键词黑名单功能发送：线报黑名单]
//[public: true]
//[class: 工具类]
//[price: 5]
//[rule: 羊毛线报测试]
//[rule: 线报黑名单]
//[rule: 线报授权查询]
//[rule: 开启线报]
//[rule: 关闭线报]
//[cron: 0/15 * * * * * ]
//[icon: https://gitee.com/aa2128/static/raw/master/icon/%E5%8D%A1%E9%80%9A%E7%BB%B5%E7%BE%8A.png]
//[priority: 999999999]优先级
//[disable: false]
//[admin:true]
//==========================参数配置数据（最下面）===============================
// [param: {"required":true,"bool":true,"key":"otto.wool_status","placeholder":"","name":"线报开关","desc":"是否开启线报"}]
// [param: {"required":true,"bool":false,"key":"otto.wool_push_groups","placeholder":"qq:123,wx:456,wb:456,tb:123","name":"推送群组","desc":"qq:123,wx:456,wb:456,tb:123"}]


const msg = GetContent()

const aut_ver = call("version")()["sn"]//获取当前系统版本

let api_url = {}

const reg = /#小程序:\/\/[^/]+\/[\w-]{15}/;
const a_reg = /<a[^>]*href=['"]([^"]*)['"][^>]*>(.*?)<\/a>/g;

const plugin_key_pre = `vhook_wool_`
const plugin_name = getTitle()

let blackWords = ["互助", "垃圾袋", "炸年兽", "30-29", "农保底10新", "开钱包", "速度随时黄", "快快快", "10-88", "38", "://美团外卖超市鲜花买菜水果极速达", "外卖美食买菜酒店电影购物", "刚中快"]
let blackUids = [91819, 105359,106295,99459]
const headers = {
    'Connection': `keep-alive`,
    'Content-Type': `application/json; charset=UTF-8`,
    'X-Canary': `client=iOS,app=adrive,version=v4.1.3`,
    'User-Agent': `AliApp(AYSD/4.1.3) com.alicloud.smartdrive/4.1.3 Version/16.3 Channel/201200 Language/zh-Hans-CN /iOS Mobile/iPhone15,2`,
    'Accept-Language': `zh-CN,zh-Hans;q=0.9`,
    'Accept': `*/*`
};

function clearUrl(str) {
    let arr = ["…", "item.jd.com", " ... "];
    if (containsParam(str, arr)) {
        return str.replace(/(https?|http|ftp|file):\/\/[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]/g, "");
    }
    return str
}

//判断是否包含数组中的某个元素
function containsParam(str, arr) {
    return arr.filter(n => str.indexOf(n) > -1).length > 0
}


/**
 * 删除过期缓存
 * */
function delExpireCache() {
    let cacheIds = bucketKeys("wool");
    for (const cacheId of cacheIds) {
        let date = bucketGet("wool", cacheId)
        date = new Date(date)
        let now = getToday()
        let day = getDaysBetween(date, now);
        if (!isNaN(day) && day >= 2) {
            bucketDel('wool', cacheId)
        }
    }
}

//发送消息
function push_msg(content) {
    let groups = get("wool_push_groups");

    let grpu_arr = groups.split(",");
    for (let i = 0; i < grpu_arr.length; i++) {
        const imType = grpu_arr[i].split(":")[0].substr(0, 2);
        const chatID = grpu_arr[i].split(":")[1];
        console.log(`推送平台：${imType}，群号：${chatID}`)
        push({
            imType: imType, //发送到指定渠道,如qq,wx,必须
            groupCode: chatID, //可选
            content: content, //发送消息
        }) //给指定im发送消息
    }
}

function check_denpcy(plugin){
    try {
        if(aut_ver>"2.6.5" && get("env") !== "dev"){
            plugin = `funyhook:${plugin}`
        }
        importJs(plugin)
    } catch (e) {
        let content = `${getTitle()}请检查是否安装以下依赖插件：`
        content += `\n【${plugin}】`
        content += `\n请前往autman面板-市场管理-应用市场-【funyhook】-安装缺失插件`
        console.log(content)
        throw new Error(content)
    }
}

function main() {
    check_denpcy("hook.js")

    if (msg==="开启线报" && isAdmin()){
        set("otto","wool_status","true");
        return sendText(`【${getTitle()}】提示：已开启线报引擎`)
    }
    if (msg==="关闭线报" && isAdmin()){
        set("otto","wool_status","false");
        return sendText(`【${getTitle()}】提示：已关闭线报引擎`)
    }
    //校验处理
    if (get("wool_status") === "false") {
        return
    }
    // if (!check_aut_ver(getTitle())) return
    // if (!check_plugin_ver(plugin_key_pre, getVersion(), getTitle(), "")) return
    //
    // let nowHour = timeFmt("yyyy-MM-dd-HH")
    // let cache = get("wool_check")
    // if (!cache) {
    //     cache = nowHour
    //     set("wool_check", "0")
    // }
    //sleep(Math.round(Math.random() * 5000))
    // let check = checkCode(plugin_key_pre)
    // if (check.success !== true) {
    //     if (ImType() === "fake" && cache !== nowHour) {
    //         set("wool_check", nowHour)
    //         return notifyMasters(`autman插件【${getTitle()}】提示：${check.msg}`)
    //     } else {
    //         return sendText(`autman插件【${getTitle()}】提示：${check.msg}`)
    //     }
    // }
    api_url = {
        woorUrl:'https://app.xiaodigu.cn/mag/info/v2/channel/infoListByCatId?step=10&channel_id=52&uniqid=61c5dcf4edb4c&is_app_first=-1&cat_id=112&p=1'
    }
    //指令处理
    {
        // if (msg === "线报授权查询" && isAdmin()) {
        //     return sendText(`autman插件【${getTitle()}】授权到期时间：${check.data.exipire}`)
        // }
        if (msg === "羊毛线报测试" && isAdmin()) {
            push_msg("羊毛线报测试")
            return
        }
        if (msg === "线报黑名单" && isAdmin()) {
            let content = `=====${plugin_name}黑名单=====`
            content += `\n请选择序号编辑(-删除，0添加，q退出)：`
            let blackWordStr = bucketGet('wool', "blackWords");
            let black_wrod_arr
            if (blackWordStr) {
                black_wrod_arr = JSON.parse(blackWordStr);
            } else {
                black_wrod_arr = blackWords
            }
            for (let i = 0; i < black_wrod_arr.length; i++) {
                content += `\n${i + 1}. ${black_wrod_arr[i]}`
            }
            sendText(content)
            const p = input(120000)
            if (!p || p === "q") {
                return sendText(`${plugin_name}：已退出`)
            }
            if (p[0] === "-") {
                let del = black_wrod_arr[p["1"] - 1]
                black_wrod_arr = black_wrod_arr.filter(item => item !== del);
                bucketSet('wool', "blackWords", JSON.stringify(black_wrod_arr))
                return sendText(`已删除黑名单关键词：${del}`)
            }
            if (p[0] === "0") {
                sendText(`${plugin_name}：请在【2分钟】内输入 黑名单关键词:`);
                const b = input(30000);
                if (b) {
                    if (black_wrod_arr.some(item => item === b)) return sendText(`${plugin_name}：已包含黑名单关键词${b},无需重复添加！`)
                    black_wrod_arr.push(b);
                    bucketSet('wool', "blackWords", JSON.stringify(black_wrod_arr))
                    return sendText(`已添加黑名单关键词：${b}，请发送："线报黑名单" 查看`)
                }
            }
            return false;
        }
    }
    //自动抓取
    {
        delExpireCache()
        let groups = get("wool_push_groups");
        if (!groups) {
            return sendText(`【线报引擎】：请先设置分发群组 set otto wool_push_groups qqgroup:123,wxgroup:456,tbgroup:-100123,tggroup:123 `)
        }
        let has_wool=false
        let response = request({
            url: 'https://app.xiaodigu.cn/mag/info/v2/channel/infoListByCatId?step=10&channel_id=52&uniqid=61c5dcf4edb4c&is_app_first=-1&cat_id=112&p=1',
            headers: headers,
            method: "get",
            dataType: "json",
        })
        if (response.success && response.code === 100) {
            let dataList = response.list;
            for (let i = 0; i < dataList.length; i++) {
                let content;
                sleep(2000)
                let data = dataList[i]
                const dataId = data.id;
                let userInfo = data.user

                const chacheData = bucketGet('wool', dataId);
                if (chacheData) {
                    //console.log("【线报引擎】 ：线报重复，不再发送")
                    continue;
                }
                bucketSet('wool', dataId, timeFmt("yyyy-MM-dd"))
                if (blackUids.includes(userInfo.id)) {
                    console.log(`命中blackUids黑名单 ，跳过：${userInfo.id}`)
                    continue;
                }
                has_wool=true
                let detail = request({
                    url: `https://app.xiaodigu.cn/mag/circle/v3/show/showView?content_id=${dataId}`,
                    headers: headers,
                    method: "get",
                    dataType: "json",
                })
                if (detail.code !== 100) {
                    continue
                }
                if (detail.success !== true) {
                    continue
                }
                let title = ``
                // if (detail.show.title!==null) {
                //     title += detail.show.title + "\n"
                // }else{
                //     title+= detail.show.sharedata.title+"\n"
                // }
                let detail_imgs = []
                if (data.type === 1) {
                    let reg_res = a_reg.exec(detail.show.content)
                    if (reg_res) {
                        title += "\n" + detail.show.content.replace(reg_res[0], reg_res[1])
                    } else {
                        title += `\n${detail.show.content}`
                    }
                    if (detail.show.rel_article_info){
                        let real_title= detail.show.rel_article_info.title
                        reg_res = a_reg.exec(real_title)
                        if (reg_res) {
                            title += "\n" + real_title.replace(reg_res[0], reg_res[1])
                        } else {
                            title += `\n${real_title}`
                        }
                    }
                } else {
                    for (const detail_content of detail.show.content) {
                        if (detail_content.type === "text") {
                            let reg_res = a_reg.exec(detail_content.content)
                            if (reg_res) {
                                title += "\n" + detail_content.content.replace(reg_res[0], reg_res[1])
                            } else {
                                title += `\n${detail_content.content}`
                            }

                        }
                        if (detail_content.type === "img") {
                            for (const img of detail_content.list) {
                                detail_imgs.push(img.pic_url)
                            }

                        }

                    }
                }
                if (containsParam(title, blackWords)) {
                    continue;
                }
                title = title.replace(title.match(reg), title.match(reg) + " \n")
                title = `${timeFmt("yy-MM-dd HH:mm:ss")} ${data.user.id}-${dataId}\n \n ${title}`
                //图片
                if (detail.show.pics_arr.length > 0) {
                    detail.show.pics_arr.forEach(pic => {
                        title = title + "\n" + image(pic.url)
                    })
                }
                //图片
                if (detail_imgs.length > 0) {
                    detail_imgs.forEach(pic => {
                        title = title + "\n" + image(pic)
                    })
                }
                content = clearUrl(title);
                push_msg(content)
            }
        } else {
            console.log(JSON.stringify(response))
        }
        if(has_wool){
            console.log(`${getTitle()}，线报自动抓取中.....本次有✅线报`)
        }
        

    
    }
}

main()
