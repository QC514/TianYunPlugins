//[create_at: 2026-03-02 17:05:07]
//[title: 随机视频图集]
//[class: 影音类]
//[author: 297129582]作者,收费插件一定要填写aut云账号
//[disable:false] 禁用开关，true 表示禁用，false 表示可用
//[admin: false] 是否为管理员指令
//[open_source: false]是否开源
//[icon: https://bbs.autman.cn/assets/files/2023-12-12/1702408610-992864-favicon.ico]图标链接地址，支持http和https
//[rule: dy?] 匹配规则，多个规则时向下依次写多个
//[rule: 视频菜单] 匹配规则，多个规则时向下依次写多个
//[rule: 图集菜单] 匹配规则，多个规则时向下依次写多个
//[rule: 数据统计] 匹配规则，多个规则时向下依次写多个
//[rule: 随机短视频] 匹配规则，多个规则时向下依次写多个
//[priority: 99999999999999999999999999999999999999999] 优先级，数字越大表示优先级越高
//[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
//[version: 1.0.5]版本号
//[price: 0.5] 上架价格
//[cron: */30 * * * *] 每天小时推送
//[description: 随机指令：dy视频/dy图集。也可以指定发送某人的视频或图集。菜单指令为：dy视频菜单（视频指令缺省用法：dy菜单）/dy图集菜单 。根据菜单可以发送指定名字的视频，指令为：dy视频芊芊（缺省用法：dy芊芊）/dy图集倩倩。设置推送群指令：set otto suiji_push_groups qqgroup:123,wxgroup:456,tggroup:-100123] 使用方法尽量写具体
//[service: <img src="https://pic.fglt.net/common/a8/common_4_verify_icon.gif" border="0"><b>官方权威认证</b>QQ：297129582 群：<a target="_blank" href="http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=iFQxHXG9uoPF_Mg--CEqAaAwuiOHUxxB&authKey=UBgOgDGMPyqtUzreMqcIsRczdy7KUQas4WiKuHfY%2FE%2B%2BtWophV0XimqByZKJdSiy&noverify=0&group_code=933677015"><font color=blue>933677015</font></a>]售后联系方式
Debug("随机视频图集");
"use strict";
var short_url = get("dsptj_dwz");
var apiUrl1 = "http://dy.jx.cangg.cn/api/random_link?";
var apiUrl2 = "http://dy1.jx.cangg.cn/api/random_link?";
var caidan = "http://dy.jx.cangg.cn/api/statistics?list_type=";
var imType = ImType();


function parseCommand(cmd) {
    console.log("[指令解析] 原始指令内容: " + cmd);
    //cmd = cmd.replace(/dy/, 'dy').trim();
    console.log("[指令解析] 预处理后指令: " + cmd);
    
    // 统一处理菜单指令
    if (cmd === "视频菜单" || cmd === "dy视频菜单") {
        console.log("[指令解析] 识别为视频菜单指令");
        return { type: "menu", mediaType: "video" };
    }
    if (cmd === "图集菜单" || cmd === "dy图集菜单") {
        console.log("[指令解析] 识别为图集菜单指令");
        return { type: "menu", mediaType: "album" };
    }
    
    // 处理统计指令
    if (cmd === "数据统计") {
        console.log("[指令解析] 识别为统计指令");
        return { type: "statistics" };
    }
    
    // 处理帮助指令
    if (cmd === "随机短视频" || cmd === "dy帮助") {
        console.log("[指令解析] 识别为帮助指令");
        return { type: "help" };
    }
    
    // 处理dy指令（视频/图集）
    const pattern = /^dy(?:\s+)?(视频|图集)?(?:\s+)?([\u4e00-\u9fa5a-zA-Z0-9]+)?$/;
    const match = cmd.match(pattern);
    
    if (match) {
        return {
            type: "media",
            media: match[1] || "视频", // 默认视频类型
            name: match[2] || null
        };
        console.log(`[指令解析] 识别为媒体指令: 类型=${result.media}, 名称=${result.name || "空"}`);
        return result;
    }
    
    // 未知指令
    console.log("[指令解析] 无法识别的指令类型");
    return { type: "unknown" };
}



// 全局变量，用于存储分页状态
var paginationState = {
    isActive: false,
    data: null
};

// 辅助函数：发送当前页内容
function sendPage(lines, currentPage, totalPages, mediaType) {
    var start = (currentPage - 1) * 10;
    var end = start + 10;
    var pageContent = lines.slice(start, Math.min(end, lines.length)).join('\n');
    var menuType = mediaType === 'album' ? '图集' : '视频';
    var message = '-----' + menuType + '菜单-----\n' + pageContent;
    
    if (currentPage === 1) {
        // 第一页显示总页数和操作提示
        if (totalPages === 1){
            if (menuType === "视频") {
                message += '\n\n(例：dy暖央)';
            } else {
                message += '\n\n(例：dy图集香香)';
            }
            message += '\n共' + totalPages + '页';
        } else {
            if (menuType === "视频") {
                message += '\n\n(例：dy暖央)';
            } else {
                message += '\n\n(例：dy图集香香)';
            }
            message += '\n共' + totalPages + '页      「下一页」';
        }
    } else if (currentPage < totalPages) {
        // 中间页
        if (menuType === "视频") {
            message += '\n\n(例：dy暖央)';
        } else {
            message += '\n\n(例：dy图集香香)';
        }
        message += '\n第' + currentPage + '/' + totalPages + '页      「下一页」';
    } else {
        // 最后一页
        if (menuType === "视频") {
            message += '\n\n(例：dy暖央)';
        } else {
            message += '\n\n(例：dy图集香香)';
        }
        message += '\n第' + currentPage + '/' + totalPages + '页   已到最后一页';
    }
    
    sendText(message);
}

// 监听用户输入的函数
function waitForNextPageCommand(mediaType, paginationData) {
    if (!paginationData || paginationData.currentPage >= paginationData.totalPages) {
        paginationState.isActive = false;
        paginationState.data = null;
        return;
    }
    
    console.log('[分页监听] 等待用户输入，超时时间：10000ms');
    
    // 使用input()监听用户输入，超时时间10秒
    var T = input(10000);
    
    console.log('[分页监听] 用户输入：', T);
    
    if (T === "下一页") {
        // 用户输入了"下一页"，发送下一页内容
        paginationData.currentPage++;
        sendPage(paginationData.lines, paginationData.currentPage, paginationData.totalPages, paginationData.mediaType);
        
        // 如果不是最后一页，继续监听下一页指令
        if (paginationData.currentPage < paginationData.totalPages) {
            waitForNextPageCommand(mediaType, paginationData);
        } else {
            // 最后一页，结束分页
            console.log('[分页监听] 已到最后一页，结束分页');
            paginationState.isActive = false;
            paginationState.data = null;
        }
    }
}

// 主函数：显示分页菜单
function showMenu(mediaType) {
    console.log('[菜单处理] 开始处理' + (mediaType === 'album' ? '图集' : '视频') + '菜单请求');
    
    try {
        var type = mediaType === "album" ? "album" : "video";
        var statUrl = caidan + type;
        
        console.log('[菜单处理] 调用菜单API: ' + statUrl);
        var statRes = request({
            url: statUrl,
            dataType: "json",
            method: "get",
            timeout: 5000
        });
        
        console.log('[菜单处理] API响应状态: ' + (statRes ? "成功" : "失败"));
        
        if (statRes && statRes.user_types) {
            var lines = statRes.user_types.split('\n');
            var totalPages = Math.ceil(lines.length / 10);
            var currentPage = 1;
            
            // 存储分页数据
            var paginationData = {
                lines: lines,
                currentPage: currentPage,
                totalPages: totalPages,
                mediaType: mediaType
            };
            
            // 发送第一页
            sendPage(lines, currentPage, totalPages, mediaType);
            
            // 设置分页状态
            paginationState.isActive = true;
            paginationState.data = paginationData;
            
            // 如果不是最后一页，启动input监听
            if (currentPage < totalPages) {
                console.log('[菜单处理] 启动input监听下一页指令');
                waitForNextPageCommand(mediaType, paginationData);
            } else {
                // 只有一页，直接结束
                paginationState.isActive = false;
                paginationState.data = null;
            }
            
            console.log('[菜单处理] 已发送第1页，共' + totalPages + '页，等待用户输入...');
        } else {
            console.error('[菜单处理] API返回数据格式异常:', statRes);
            sendText("获取菜单失败，数据格式异常");
        }
    } catch (error) {
        console.error("[菜单处理] 异常错误信息:", error.message, "堆栈:", error.stack);
        sendText("获取菜单时发生异常：" + error.message);
    }
    
    console.log('[菜单处理] ' + (mediaType === 'album' ? '图集' : '视频') + '菜单处理完成');
}




function showStatistics() {
    // 这里可以添加实际的统计功能
    const tongji = request({
            url: caidan,
            dataType: "json",
            method: "get",
            timeout: 5000
        });
    sendText(`----数据统计----\n视频：${tongji.视频.statistics.videos}\n图集：${tongji.图集.statistics.images}\n历史调用：${tongji.random_api_usage.total_calls}\n今日调用：${tongji.random_api_usage.daily_calls}`);
    //sendText("统计功能开发中，敬请期待！\n当前版本：1.0.3");
}

function showHelp() {
    const helpText = [
        "📺 随机视频图集使用说明 📸",
        "----------------------",
        "1. 随机视频：dy视频",
        "2. 随机图集：dy图集",
        "3. 指定视频：dy视频+作者名",
        "   (简写：dy作者名)",
        "4. 指定图集：dy图集作者名",
        "5. 视频名单：视频菜单",
        "6. 图集名单：图集菜单",
        "7. 统计信息：数据统计",
        "----------------------",
        "示例：",
        "dy暖央 → 发送暖央的视频",
        "dy图集荼荼 → 发送荼荼的图集"
    ].join("\n");
    
    sendText(helpText);
}

function main() {
    var data = request({ url: apiUrl1, dataType: "json" }).link;
    var content = `[CQ:video,file=${data}]`;
    if (imType == "fake") {
        var pushGroups = get("suiji_push_groups")
        Debug(pushGroups)
        var pgs = pushGroups.split(",")
        var groups = []
        for (i = 0; i < pgs.length; i++) {
            groups[i] = {
                imType: pgs[i].slice(0, 2),
                groupCode: pgs[i].slice(8),
            }
        }
        Debug(JSON.stringify(groups))
        for (var i = 0; i < groups.length; i++) {
            groups[i]["content"] = content
            push(groups[i])
        }
    } else {
        
        try {
            console.log("[主流程] === 开始处理指令 ===");
            const cmd = GetContent().trim();
            console.log("[主流程] 接收到原始指令: " + cmd);
            
            const command = parseCommand(cmd);
            console.log(`[主流程] 解析结果: 类型=${command.type}, 参数=${JSON.stringify(command)}`);
            
            switch (command.type) {
                case "media":
                    console.log("[主流程] 执行媒体处理流程");
                    handleMediaCommand(command);
                    break;
                    
                case "menu":
                    console.log("[主流程] 执行菜单显示流程");
                    showMenu(command.mediaType);
                    break;
                    
                case "statistics":
                    console.log("[主流程] 执行统计显示流程");
                    showStatistics();
                    break;
                    
                case "help":
                    console.log("[主流程] 执行帮助显示流程");
                    showHelp();
                    break;
                    
                case "unknown":
                default:
                    console.log("[主流程] 未知指令处理");
                    sendText("未知指令，发送「帮助」查看使用说明");
                    break;
            }
            console.log("[主流程] === 指令处理完成 ===");
        } catch (error) {
            console.error("[主流程] 全局异常捕获:", error.message, "堆栈:", error.stack);
            sendText("处理名单出错：" + error.message);
        }
    }
}

function handleMediaCommand(command) {
    // 构建API请求参数
    const query = [];
    query.push("media=" + encodeURIComponent(command.media));
    if (command.name) {
        query.push("name=" + encodeURIComponent(command.name));
    }
    
    const queryString = query.join("&");
    const res = body(queryString);
    
    if (!res || !res.link) {
        throw new Error("未找到指定作者内容\n发送「" + command.media + "菜单」获取名单");
    }
    
    // 类型判断
    const isAlbum = command.media === "图集";
    
    if (isAlbum) {
        send_photo(res.link);
    } else {
        let videoUrl = res.link;
        
        // 抖音重定向处理
        console.debug && console.debug("[2] 开始抖音重定向处理...");
        const finalUrl = request({
            url: videoUrl,
            dataType: "location",
            timeout: 8000,
            headers: {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        });
        
        if (typeof finalUrl === "string" && finalUrl.indexOf("http") === 0) {
            videoUrl = finalUrl;
            console.debug && console.debug("[3] 最终地址:", videoUrl);
        } else {
            throw new Error("视频可能被删除");
        }
        
        console.log(`↓↓↓发送视频↓↓↓`);
        console.log(videoUrl);
        sendVideo(videoUrl);
        console.log(`↑↑↑视频发送完成↑↑↑`);
    }
}


function short_links(url) {
    //console.log(JSON.stringify(url));
    body = request({
        url: `${short_url}${url}`,
        method: "get",
    });
    //console.log(JSON.stringify(body));
    if (body) {
        return body;
    } else {
        return;
    }
}

function body(url) {
    const paramValue = url.replace(/\\/g, '');
    // 定义两个API地址
    const apiUrls = [apiUrl1, apiUrl2];
    // 遍历API地址，尝试请求
    for (const apiUrl of apiUrls) {
        const body = request({
            url: `${apiUrl}${paramValue}`,
            dataType: "json",
            method: "get",
            headers: { "User-Agent": "Mozilla/5.0 (Linux; Android 12; SM-G9880) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36 EdgA/106.0.1370.47" },
            timeout: 5000
        });
        if (body) {
            //console.log(JSON.stringify(body));
            return body;// 如果请求成功，直接返回结果
        }
    }
    console.log("草泥马，2个地址都请求失败");
    return;
}

function send_photo(videoLink) {
    console.log(`↓↓↓发送图集↓↓↓`);
    let imgs = videoLink;
    let limit = get("sendCosImgTotleLimit");
    if (!limit) {
        limit = videoLink.length;
    }
    imgs.length = limit;
    let onceLimit = get("sendCosImgOnceLimit");
    if (!onceLimit) {
        onceLimit = 9;
    }
    let onceSleep = get("sendCosImgOnceSleep");
    if (!onceSleep) {
        onceSleep = 1000;
    }
    msg = "";
    for (var i = 1, len = imgs.length; i <= len; i++) {
        if(GetImType()=="wx"){
            msg += image(short_links(encodeURIComponent(imgs[i - 1])));
        } else {
            msg += image(imgs[i - 1]);
        }
        if (i % onceLimit == 0) {
            sendText(msg);
            msg = "";
            sleep(onceSleep);
        }
    }
    if (msg.length > 0) {
        sendText(msg);
    }
    console.log(imgs);
    console.log(`↑↑↑图集发送完成↑↑↑`);
}

main();