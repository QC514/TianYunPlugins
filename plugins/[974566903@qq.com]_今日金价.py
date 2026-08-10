//[pin:true]
//[title: 今日金价]
//[icon: https://pic2.ziyuan.wang/user/974566903/2025/08/jj_ab8218111b3f2.jpg]
//[price: 0]
//[class: 工具类]
//[author: 974566903@qq.com]
//[version: 1.7]
//[open_source: false]
//[platform: wx]
//[public:true]
//[service: 974566903]
//[imType:] 白名单,只在qq,wx生效
//[imType+:] 同上,不写+号默认为白名单模式
//[imType-:] 黑名单qq,除了qq生效
//[userId-:] 用户id同样支持黑白名单模式
//[groupId+:] 群id同样支持黑白名单模式
//[description: 关键词：今日金价，可查询基础金价、国内金店报价<br>新增关键词：金价监控通知|金价监控设置<br>温馨提示：金价监控通知需要设置计划任务,多群推送<br>2月21日更新接口]
//[rule: ^今日金价$]
//[rule: ^金价监控设置$]
//[rule: ^金价监控通知$]
//[imType: qx,qq]

// 参数配置
// [param: {"required":false,"key":"A_goldT.group_id","placeholder":"填写数字即可微信群ID，多个群号用#号分割（空留不推送）","name":"金价监控通知群ID","desc":"金价监控通知推送的微信群ID，支持多个群号，用#号分割"}]

async function main() {
    const command = GetContent();
    
    if (command === "今日金价") {
        await getCurrentGoldPrice();
    } else if (command === "金价监控设置") {
        await setupGoldPriceMonitor();
    } else if (command === "金价监控通知") {
        await checkGoldPriceAndNotify();
    }
}

async function getCurrentGoldPrice() {
    // 新的基础金价银价接口 - 已替换为你提供的GET接口
    let goldSilverMsg = await request({
        url: "https://i.jzj9999.com/res/quote/pq.json?m_t1774784547561=",
        headers: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254173b) XWEB/19201",
        },
        method: "get",
        dataType: "json",
        timeOut: 30000
    });

    // 保留原金店报价接口，不做任何修改
    let shopMsg = await request({
        url: "https://api.lolimi.cn/API/huangj/api.php",
        headers: {
            "Content-Type": "application/json"
        },
        method: "get",
        dataType: "json",
        timeOut: 30000
    });

    // 处理新接口基础金价银价数据 - 取Au99.99和JZJ_ag，保持原输出样式
    let baseGoldInfo = [];
    let silverTaxedInfo = null;
    let updateTime = "";

    // 校验新接口数据
    if (goldSilverMsg && goldSilverMsg.result === 0 && goldSilverMsg.items && goldSilverMsg.items.length > 0) {
        // 取 Au99.99 黄金
        const goldItem = goldSilverMsg.items.find(item => item.code === "Au99.99");
        // 取 JZJ_ag 白银
        const silverItem = goldSilverMsg.items.find(item => item.code === "JZJ_ag");

        // 黄金数据（保持原有字段名：回购价BP=bidprice，销售价SP=askprice）
        if (goldItem) {
            baseGoldInfo.push(`
商品：黄金
回购价：${goldItem.bidprice}
销售价：${goldItem.askprice}
最高价：${goldItem.high}
最低价：${goldItem.low}`);
            updateTime = formatTimestamp(goldItem.stime);
        }

        // 白银数据
        if (silverItem) {
            silverTaxedInfo = `
商品：白银（含税）
回购价：${silverItem.bidprice}
销售价：${silverItem.askprice}
最高价：${silverItem.high}
最低价：${silverItem.low}`;
        }
    }

    // 处理金店数据 - 完全保留原代码
    let targetShops = ["内地周大福", "内地六福珠宝", "周六福"];
    let shopInfo = [];
    let shopUpdateTime = "";

    if (shopMsg && shopMsg["国内十大金店"] && shopMsg["国内十大金店"].length > 0) {
        for (let shop of shopMsg["国内十大金店"]) {
            if (targetShops.includes(shop.品牌)) {
                shopInfo.push(`
{${shop.品牌}}
黄金价格: ${shop.黄金价格} ${shop.单位}`);
                
                if (shop.报价时间 && shop.报价时间 > shopUpdateTime) {
                    shopUpdateTime = shop.报价时间;
                }
            }
        }
        
        if (shopInfo.length > 0 && shopUpdateTime) {
            shopInfo.push(`
报价时间: ${shopUpdateTime}`);
        }
    }

    // 合并输出（完全原样）
    let finalOutput = "今日金价信息汇总";

    if (baseGoldInfo.length > 0 || silverTaxedInfo) {
        finalOutput += "\n\n=== 基础金价数据 ===";
        if (baseGoldInfo.length > 0) {
            finalOutput += baseGoldInfo.join("");
        }
        if (silverTaxedInfo) {
            finalOutput += `\n${silverTaxedInfo}`;
        }
        if (updateTime) {
             finalOutput += `\n实时时间：${updateTime}`;
        }
    }

    if (shopInfo.length > 0) {
        finalOutput += "\n\n=== 国内金店报价 ===" + shopInfo.join("");
    }

    if (finalOutput === "今日金价信息汇总") {
        finalOutput += "\n\n暂无最新金价、银价及金店报价数据，接口请求失败或数据格式异常";
    }

    sendText(finalOutput);
}

async function setupGoldPriceMonitor() {
    // 新接口
    let goldSilverMsg = await request({
        url: "https://i.jzj9999.com/res/quote/pq.json?m_t1774784547561=",
        headers: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254173b) XWEB/19201",
        },
        method: "get",
        dataType: "json",
        timeOut: 30000
    });

    if (!goldSilverMsg || goldSilverMsg.result !== 0 || !goldSilverMsg.items || goldSilverMsg.items.length === 0) {
        sendText("获取金价数据失败，请稍后重试");
        return;
    }

    const goldItem = goldSilverMsg.items.find(item => item.code === "Au99.99");
    if (!goldItem) {
        sendText("未找到黄金数据");
        return;
    }

    const currentHighPrice = parseFloat(goldItem.high);
    const currentAskPrice = parseFloat(goldItem.askprice);

    sendText(`当前金价信息：
商品：黄金(Au99.99)
销售价：${goldItem.askprice}
最高价：${goldItem.high}
最低价：${goldItem.low}

请输入您要监控的目标价格\n当金价最高价超过此价格时会发送群通知📢\n\n输入Q/q退出设置`);

    const targetPriceInput = input(60000);
    
    if (!targetPriceInput || targetPriceInput === "") {
        sendText("操作已取消或超时");
        return;
    }

    if (targetPriceInput.toLowerCase() === 'q') {
        sendText("已取消金价监控设置");
        return;
    }

    const targetPrice = parseFloat(targetPriceInput);
    if (isNaN(targetPrice)) {
        sendText("输入的价格无效，请输入一个有效的数字");
        return;
    }

    bucketSet("gold_price_monitor", "target_price", targetPrice.toString());
    bucketSet("gold_price_monitor", "current_high_price", currentHighPrice.toString());
    bucketSet("gold_price_monitor", "current_ask_price", currentAskPrice.toString());
    bucketSet("gold_price_monitor", "last_notification_time", Date.now().toString());
    
    sendText(`✅ 金价监控设置成功！
当前金价最高价：${currentHighPrice}
您设置的监控价格：${targetPrice}
当金价最高价超过 ${targetPrice} 时|将会发送群通知`);
}

async function checkGoldPriceAndNotify() {
    // 新接口
    let goldSilverMsg = await request({
        url: "https://i.jzj9999.com/res/quote/pq.json?m_t1774784547561=",
        headers: {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254173b) XWEB/19201",
        },
        method: "get",
        dataType: "json",
        timeOut: 30000
    });

    if (!goldSilverMsg || goldSilverMsg.result !== 0 || !goldSilverMsg.items || goldSilverMsg.items.length === 0) {
        sendText("获取金价数据失败，请稍后重试");
        return;
    }

    const goldItem = goldSilverMsg.items.find(item => item.code === "Au99.99");
    if (!goldItem) {
        sendText("未找到黄金数据");
        return;
    }

    const currentHighPrice = parseFloat(goldItem.high);
    const targetPriceStr = bucketGet("gold_price_monitor", "target_price");
    
    if (!targetPriceStr) {
        sendText(`当前金价信息：
商品：黄金(Au99.99)
销售价：${goldItem.askprice}
最高价：${goldItem.high}
最低价：${goldItem.low}

您尚未设置金价监控价格，请先使用"金价监控设置"命令设置监控价格。`);
        return;
    }
    
    const targetPrice = parseFloat(targetPriceStr);
    if (isNaN(targetPrice)) {
        sendText(`当前金价信息：
商品：黄金(Au99.99)
销售价：${goldItem.askprice}
最高价：${goldItem.high}
最低价：${goldItem.low}

您设置的监控价格无效，请重新使用"金价监控设置"命令设置监控价格。`);
        return;
    }

    if (currentHighPrice > targetPrice) {
        let response = `🚨 金价提醒 🚨
金价已超过您的监控价格！

📈 当前金价(Au99.99):
销售价：${goldItem.askprice}
最高价：${goldItem.high}
最低价：${goldItem.low}

🎯 您设置的监控价格：${targetPrice}
⏰ 更新时间：${formatTimestamp(goldItem.stime)}

请及时关注金价变化！`;

        const lastNotificationTimeStr = bucketGet("gold_price_monitor", "last_notification_time") || "0";
        const lastNotificationTime = parseInt(lastNotificationTimeStr);
        const currentTime = Date.now();
        
        if (currentTime - lastNotificationTime > 600000) {
            bucketSet("gold_price_monitor", "last_notification_time", currentTime.toString());
            
            const groupId = bucketGet("A_goldT", "group_id");
            if (!groupId || groupId === "") {
                response += `\n⚠️ 未配置群ID，无法发送群通知`;
                sendText(response);
            } else {
                const groupIds = groupId.split('#').filter(id => id.trim() !== '');
                
                if (groupIds.length === 0) {
                    response += `\n⚠️ 未配置有效的群ID，无法发送群通知`;
                    sendText(response);
                } else {
                    let successCount = 0;
                    
                    for (const singleGroupId of groupIds) {
                        const trimmedGroupId = singleGroupId.trim();
                        if (trimmedGroupId) {
                            try {
                                push({
                                    imType: "wx",
                                    groupCode: trimmedGroupId,
                                    content: response
                                });
                                successCount++;
                            } catch (error) {
                                console.error(`发送群通知到群 ${trimmedGroupId} 失败:`, error);
                            }
                        }
                    }
                    
                    response += `\n✅ 已发送金价提醒通知到 ${successCount} 个群组`;
                    sendText(response);
                }
            }
        } else {
            response += `\nℹ️ 距离上次通知不足10分钟，本次不重复发送群通知`;
            sendText(response);
        }
    } else {
        sendText(`当前金价信息：
商品：黄金(Au99.99)
销售价：${goldItem.askprice}
最高价：${goldItem.high}
最低价：${goldItem.low}

您设置的监控价格：${targetPrice}

✅ 当前金价未超过监控价格，无需发送通知`);
    }
}

async function checkGoldPrice() {
    try {
        const targetPriceStr = bucketGet("gold_price_monitor", "target_price");
        if (!targetPriceStr) return;
        
        const targetPrice = parseFloat(targetPriceStr);
        if (isNaN(targetPrice)) return;

        // 新接口
        let goldSilverMsg = await request({
            url: "https://i.jzj9999.com/res/quote/pq.json?m_t1774784547561=",
            headers: {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254173b) XWEB/19201",
            },
            method: "get",
            dataType: "json",
            timeOut: 30000
        });

        if (!goldSilverMsg || goldSilverMsg.result !== 0 || !goldSilverMsg.items || goldSilverMsg.items.length === 0) {
            console.log("获取金价数据失败");
            return;
        }

        const goldItem = goldSilverMsg.items.find(item => item.code === "Au99.99");
        if (!goldItem) {
            console.log("未找到黄金数据");
            return;
        }

        const currentHighPrice = parseFloat(goldItem.high);
        
        if (currentHighPrice > targetPrice) {
            const lastNotificationTimeStr = bucketGet("gold_price_monitor", "last_notification_time") || "0";
            const lastNotificationTime = parseInt(lastNotificationTimeStr);
            const currentTime = Date.now();
            
            if (currentTime - lastNotificationTime > 600000) {
                bucketSet("gold_price_monitor", "last_notification_time", currentTime.toString());
                
                const groupId = bucketGet("A_goldT", "group_id");
                if (!groupId || groupId === "") {
                    console.log("未配置群ID，无法发送群通知");
                    return;
                }
                
                const groupIds = groupId.split('#').filter(id => id.trim() !== '');
                
                if (groupIds.length === 0) {
                    console.log("未配置有效的群ID，无法发送群通知");
                    return;
                }
                
                for (const singleGroupId of groupIds) {
                    const trimmedGroupId = singleGroupId.trim();
                    if (trimmedGroupId) {
                        const notificationMessage = `🚨 金价提醒 🚨
金价已超过您的监控价格！

📈 当前金价(Au99.99):
销售价：${goldItem.askprice}
最高价：${goldItem.high}
最低价：${goldItem.low}

🎯 您设置的监控价格：${targetPrice}
⏰ 更新时间：${formatTimestamp(goldItem.stime)}

请及时关注金价变化！`;
                        
                        try {
                            push({
                                imType: "wx",
                                groupCode: trimmedGroupId,
                                content: notificationMessage
                            });
                            console.log("金价监控通知已发送到群：" + trimmedGroupId);
                        } catch (error) {
                            console.error(`发送群通知到群 ${trimmedGroupId} 失败:`, error);
                        }
                    }
                }
            }
        }
    } catch (error) {
        console.error("检查金价时发生错误:", error);
    }
}

// 时间戳格式化函数
function formatTimestamp(timestamp) {
    if (!timestamp) return "";
    const date = new Date(parseInt(timestamp) * 1000);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

main();