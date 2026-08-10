//[pin:true]
//[disable:false]
//[create_at: 2024-07-17 10:19:39]
//[author: zq8884]
//[public: true]
//[price: 14.9]
//[open_source: false]
//[title: JD未来活动定时pro]
//[router: /send_private_msg]
//[method: post]
//[method: get]
//[version: 1.7.5]
//[service: qq421148494]
//[priority: 999]
//[icon: http://166.108.197.159:3000/configData/icon/0_容器/Sunpanel_A.png]
//[description: 接管青龙/内置容器通知，并推送到autMan，脚本容器配置文件里加入以下参数（直接复制到青龙/内置容器）：<br/>export GOBOT_URL="http://autMan地址:端口/send_private_msg"<br/>export GOBOT_TOKEN=""<br/>注：此插件生效需重启autMan。<br/>教程：<a href="https://docs.qq.com/doc/DY3N5c1FOSUtkYnFl">点击这里访问</a> <br/>【V1.5.9：新增M定时签到随机定时设置】<br/>【V1.6.0：新增M试用通知开关】<br/>【V1.6.1：修复空白的实物推送信息。】<br/>【V1.6.4：增加M签到ID转9R开关、实物中奖自定义标题。】<br/>【V1.6.7：适配环境直播中奖京豆通知】<br/>【V1.6.9：添加【JD未来活动定时pro】通知开关。<br/>【V1.7.3：增加通知白名单、黑名单功能配参、新增京豆、实物推送个人。】]

//[param: {"required":true,"key":"zq8884.toOthers","bool":false,"placeholder":"如：qqgroup:123,qqindiv:456","name":"定时任务发送目标","desc":"不知道怎么用的话，空着即可"}]
//[param: {"required":true,"key":"zq8884.jingyun_cron_time","bool":false,"placeholder":"cron表达式","name":"jingyun签到定时","desc":"例如：57 59 23,9 1-31 * *"}]
//[param: {"required":true,"key":"zq8884.9R_cron_time","bool":false,"placeholder":"59 23","name":"9R签到同步时间","desc":"例如：59 23代表会在23点59分发送定时推送任务"}]
//[param: {"spliter":true}]
//[param: {"required":true,"key":"zq8884.sign_cron_time","bool":false,"placeholder":"英文逗号间隔","name":"签到、大牌浏览定时时间","desc":"例如：0,12"}]
//[param: {"required":true,"key":"zq8884.minuteRange","bool":false,"placeholder":"0-10","name":"M签到有礼定时分钟随机数","desc":"例如：0-5  定时时间将在0到5分钟内随机定时，如果设置整数则固定该时间，避免同一时间任务过多，造成拥堵。"}]
//[param: {"required":true,"bool":true,"key":"zq8884.pointswitch","placeholder":"false","name":"只有积分的签到是否定时","desc":"M签到活动只有积分的签到是否增加定时"}]
//[param: {"required":true,"bool":true,"key":"zq8884.ifCronNotFirstday","placeholder":"false","name":"非首日是否定时","desc":"M签到活动非首日是否定时"}]
//[param: {"required":true,"bool":true,"key":"zq8884.MsignCollect","placeholder":"false","name":"M签到有礼ID收集开关","desc":"M签到有礼收集成9R签到开关，核心功能，打√为开启。"}]
//[param: {"required":true,"bool":true,"key":"zq8884.toSelfswitch","placeholder":"false","name":"M签到有礼关闭自处理","desc":"M签到ID收集后，关闭对应活动ID的自处理，打√为开启"}]
//[param: {"required":true,"key":"zq8884.meiriqiang_early_time","bool":false,"placeholder":"5000","name":"每日抢提前时间","desc":"例如：5000=5秒"}]
//[param: {"required":true,"key":"zq8884.jinli_early_time","bool":false,"placeholder":"3000","name":"购物车锦鲤提前开奖时间","desc":"例如：3000=3秒"}]
//[param: {"spliter":true}]
//[param: {"required":true,"bool":true,"key":"zq8884.jingyunswitch","placeholder":"false","name":"jingyun签到收集开关","desc":"jingyun签到收集开关"}]
//[param: {"spliter":true}]
//[param: {"required":true,"bool":true,"key":"zq8884.notify_repeat","placeholder":"false","name":"重复活动id签到通知","desc":"重复活动id签到通知开关"}]
//[param: {"required":true,"bool":true,"key":"zq8884.notify_SignhasStarted","placeholder":"false","name":"非首日签到通知","desc":"非首日签到通知开关"}]
//[param: {"required":true,"bool":true,"key":"zq8884.notify_addcron","placeholder":"false","name":"添加定时任务通知","desc":"【JD未来活动定时pro】"}]
//[param: {"required":true,"bool":true,"key":"zq8884.notify_delete","placeholder":"false","name":"删除定时任务通知","desc":"【删除自动定时】"}]
//[param: {"required":true,"bool":true,"key":"zq8884.notify_repeat_cron","placeholder":"false","name":"重复的定时任务通知","desc":"定时指令已存在，忽略"}]
//[param: {"spliter":true}]
//[param: {"required":true,"bool":true,"key":"zq8884.logswitch","placeholder":"false","name":"调试日志开关","desc":"autMan实时日志显示"}]
//[param: {"spliter":true}]
//[param: {"spliter":true}]
//[param: {"required":true,"bool":true,"key":"zq8884.awardnotify","placeholder":"false","name":"京豆/实物中奖通知管理员开关","desc":"中奖是否通知管理员"}]
//[param: {"spliter":true}]
//[param: {"required":true,"bool":true,"key":"zq8884.lognotify","placeholder":"false","name":"通知运行开关","desc":"通知运行开关（不打√即静默脚本监控日志）"}]
//[param: {"required":false,"key":"zq8884.notifyWhitelist","bool":false,"placeholder":"京东,红包","name":"通知白名单关键词","desc":"多个关键词用英文逗号分隔，留空则全部通知"}]
//[param: {"required":false,"key":"zq8884.notifyBlacklist","bool":false,"placeholder":"活动已结束","name":"通知黑名单关键词","desc":"多个关键词用英文逗号分隔，存在任一关键词则不通知"}]
//[param: {"spliter":true}]
//[param: {"required":true,"key":"zq8884.awardtext","bool":false,"placeholder":"恭喜大兄弟薅到限时抽奖京豆","name":"京豆中奖通知自定义前缀","desc":"例如：恭喜大兄弟薅到限时抽奖京豆"}]
//[param: {"required":true,"key":"zq8884.awardtitle","bool":false,"placeholder":"中奖通知标题","name":"京豆中奖通知标题","desc":"例如：京东抽奖中奖通知："}]
//[param: {"spliter":true}]
//[param: {"required":true,"key":"zq8884.beanspushConfigs","bool":false,"placeholder":"平台:群号,平台:群号","name":"京豆中奖通知(群组)","desc":"如：wx:123456,qq:123456  支持多群组通知"}]
//[param: {"required":true,"key":"zq8884.beanspushConfigsgeren","bool":false,"placeholder":"平台:ID,平台:ID","name":"京豆中奖通知(个人)","desc":"如：wx:123456,qq:123456  支持多用户通知"}]
//[param: {"required":true,"key":"zq8884.awardbeans","bool":false,"placeholder":"0","name":"中奖京豆通知限值","desc":"京豆大于等于?才进行通知，默认0"}]
//[param: {"required":true,"key":"zq8884.blockKeywords","bool":false,"placeholder":"已填地址","name":"京豆中奖屏蔽关键词","desc":"默认：“已填地址”，多个用英文逗号分割 防止被韭菜看到实物信息"}]
//[param: {"required":true,"key":"zq8884.awardshiwutitle","bool":false,"placeholder":"实物中奖通知标题","name":"实物中奖通知标题","desc":"例如：京东实物中奖通知："}]
//[param: {"required":true,"key":"zq8884.shiwupushConfigs","bool":false,"placeholder":"平台:群号,平台:群号","name":"实物中奖通知（群组）","desc":"如：wx:123456,qq:123456  支持多群组通知"}]
//[param: {"required":true,"key":"zq8884.shiwupushConfigsgeren","bool":false,"placeholder":"平台:ID,平台:ID","name":"实物中奖通知（个人）","desc":"如：wx:123456,qq:123456  支持多用户通知"}]
//[param: {"spliter":true}]
//[param: {"required":true,"bool":true,"key":"zq8884.MTryuse","placeholder":"false","name":"M试用有礼通知","desc":"M试用有礼通知开关"}]
//[param: {"spliter":true}]


/*bucketGet("zq8884","9R_cron_time");
bucketGet("zq8884","jingyun_cron_time");
bucketGet("zq8884","sign_cron_time");
bucketGet("zq8884","minuteRange");
bucketGet("zq8884","meiriqiang_early_time");
bucketGet("zq8884","jinli_early_time");
bucketGet("zq8884","notify_repeat");
bucketGet("zq8884","notify_SignhasStarted");
bucketGet("zq8884","notify_delete");
bucketGet("zq8884","notify_repeat_cron");
bucketGet("zq8884","logswitch");
bucketGet("zq8884","pointswitch");
bucketGet("zq8884","toSelfswitch");
bucketGet("zq8884","awardtext");
bucketGet("zq8884","awardtitle");
bucketGet("zq8884","beanspushConfigs");
bucketGet("zq8884","shiwupushConfigs");
bucketGet("zq8884","blockKeywords");*/

/*var jingyunswitch = bucketGet("zq8884", "jingyunswitch");
jingyunswitch = jingyunswitch === 'true'; // 将字符串转换为布尔值

var logswitch = bucketGet("zq8884", "logswitch");
logswitch = logswitch === 'true'; // 将字符串转换为布尔值

var pointswitch = bucketGet("zq8884", "pointswitch");
pointswitch = pointswitch === 'true'; // 将字符串转换为布尔值

var MsignCollect = bucketGet("zq8884", "MsignCollect");
MsignCollect = MsignCollect === 'true'; // 将字符串转换为布尔值

var toSelfswitch = bucketGet("zq8884", "toSelfswitch");
toSelfswitch = toSelfswitch === 'true'; // 将字符串转换为布尔值

var awardnotify = bucketGet("zq8884", "awardnotify");
awardnotify = awardnotify === 'true'; // 将字符串转换为布尔值

var lognotify = bucketGet("zq8884", "lognotify");
lognotify = lognotify === 'true'; // 将字符串转换为布尔值

var notify_repeat_cron = bucketGet("zq8884", "notify_repeat_cron");
notify_repeat_cron = notify_repeat_cron === 'true'; // 将字符串转换为布尔值

var notify_repeat = bucketGet("zq8884", "notify_repeat");
notify_repeat = notify_repeat === 'true'; // 将字符串转换为布尔值

var notify_SignhasStarted = bucketGet("zq8884", "notify_SignhasStarted");
notify_SignhasStarted = notify_SignhasStarted === 'true'; // 将字符串转换为布尔值

var ifCronNotFirstday = bucketGet("zq8884", "ifCronNotFirstday");
ifCronNotFirstday = ifCronNotFirstday === 'true'; // 将字符串转换为布尔值

var MTryuse = bucketGet("zq8884", "MTryuse");
MTryuse = MTryuse === 'true'; // 将字符串转换为布尔值
*/
var jingyunswitch = bucketGet("zq8884", "jingyunswitch") === 'true';
var logswitch = bucketGet("zq8884", "logswitch") === 'true';
var pointswitch = bucketGet("zq8884", "pointswitch") === 'true';
var MsignCollect = bucketGet("zq8884", "MsignCollect") === 'true';
var toSelfswitch = bucketGet("zq8884", "toSelfswitch") === 'true';
var awardnotify = bucketGet("zq8884", "awardnotify") === 'true';
var lognotify = bucketGet("zq8884", "lognotify") === 'true';
var notify_addcron = bucketGet("zq8884", "notify_addcron") === 'true';
var notify_repeat_cron = bucketGet("zq8884", "notify_repeat_cron") === 'true';
var notify_repeat = bucketGet("zq8884", "notify_repeat") === 'true';
var notify_SignhasStarted = bucketGet("zq8884", "notify_SignhasStarted") === 'true';
var ifCronNotFirstday = bucketGet("zq8884", "ifCronNotFirstday") === 'true';
var MTryuse = bucketGet("zq8884", "MTryuse") === 'true';
var toOthers = bucketGet("zq8884", "toOthers") || "";

var notifyWhitelist = bucketGet("zq8884","notifyWhitelist") || "";
var notifyBlacklist = bucketGet("zq8884","notifyBlacklist") || "";







//检查版本
version = call("version")()["sn"]
Debug("系统版本：" + version)
if (version >= "1.1.5") {
    Debug("路由流程")
    var router = getRouter()
    Debug("路由：" + router)
    var method = getMethod()
    Debug("方法：" + method)
    var params = getRouterParams()
    Debug("参数：" + JSON.stringify(params))
    var data = getRouterData()
    Debug("内容：" + data)
    data=data?data:JSON.stringify(params)
    var obj = JSON.parse(data)
	
	

	
	
	
if (lognotify) {
    var message = obj.message
        .replace(/本通知 By：https:\/\/github\.com\/whyour\/qinglong/g, "")
        .replace(/好物推荐：https:\/\/u\.jd\.com\/[0-9A-Za-z]{7}/g, "");
    
    var shouldNotify = true; // 新增状态标记变量[7](@ref)

    // 白名单过滤逻辑改造
    if(notifyWhitelist){
        var whiteKeywords = notifyWhitelist.split(',').filter(function(k){ 
            return k.trim(); 
        });
        if(whiteKeywords.length > 0) {
            var whiteRegex = new RegExp(whiteKeywords.join('|'), 'i');
            shouldNotify = whiteRegex.test(message); // 用布尔值代替return[3,5](@ref)
        }
    }

    // 黑名单过滤逻辑改造
    if(notifyBlacklist && shouldNotify){ 
        var blackKeywords = notifyBlacklist.split(',').filter(function(k){
            return k.trim();
        });
        if(blackKeywords.length > 0) {
            var blackRegex = new RegExp(blackKeywords.join('|'), 'i');
            shouldNotify = !blackRegex.test(message); // 反转匹配结果[5](@ref)
        }
    }

    // 最终发送判断
    if(shouldNotify){
        notifyMasters(message + "\n-------------\nautMan运行结果通知");
    }
}


	
	
//京豆中奖推送
    if (/🐶|(?<=】\s*\d+)\s*京豆|(?<=】\s*\d+)\s*豆|(?:】.*?：\d+个京豆)|(?:.*?)(\d+)京豆/.test(obj.message)) {
    //if (/🐶|(?<=】\s*\d+)\s*京豆|(?<=】\s*\d+)\s*豆|(?:】.*?：\d+个京豆)/.test(obj.message)) {
    // 从存储桶中获取屏蔽关键词，并转换为数组
    var blockKeywordsStr = bucketGet("zq8884", "blockKeywords");
    var blockKeywords = blockKeywordsStr ? blockKeywordsStr.split(',') : ["已填地址"];
    var regex1 = /【京东账号\d+】([^：]+)：([\s\S]*?)(?=(【京东账号|\s*$))/g;  // 适配9R豆子
    //var regex2 = /【([a-zA-Z0-9_-]+)】(?:.*?)(\d+)京豆/g;  // 适配M豆子
    var regex2 = /【([a-zA-Z0-9_-]+(?:\([^\)]+\))?)】\D*(\d+)京豆/g;  // 适配M豆子
    //var regex3 = /【([a-zA-Z0-9_-]+(?:\([^\)]+\))?)】\D*(\d+)豆/g;  // 适配M豆子
    var regex4 = /【([a-zA-Z0-9_-]+)】([^：]+)：(\d+)个京豆/g;  // 适配M豆子
	var regex5 = /【京东账号(\d+)】([^：]+) 获得: 恭喜您中奖咯 (\d+)京豆/g; //环境直播豆子
	// 新增 regex6：适配 【账号】豆数量豆 格式（如：29【jd_**qQc】20豆）
    var regex6 = /【(.*?)】(\d+)豆/g; 


    var results = [];
    var match;

    var awardtext = bucketGet("zq8884", "awardtext");
    var awardtitle = bucketGet("zq8884", "awardtitle");

    // 设置京豆数量的阈值
    var awardbeans = bucketGet("zq8884", "awardbeans");
    var threshold = parseInt(awardbeans);

    // 将消息内容按行分割为数组
    var lines = obj.message.split('\n');

    // 逐行处理日志内容
    lines.forEach(function(line) {
        // 解析每一行的内容（针对 regex1）
        while ((match = regex1.exec(line)) !== null) {
            var account = match[1].trim();
            var allAwards = match[2]; // 获取该账号的所有奖励内容

            // 提取所有京豆奖励，使用正则匹配每一个京豆奖励
            var beansMatches = allAwards.match(/\d+京豆/g) || [];

            // 过滤掉包含屏蔽关键词的项和京豆数量小于阈值的项
            var filteredAwards = beansMatches.filter(function(award) {
                var beans = parseInt(award);
                return !blockKeywords.some(function(keyword) {
                    return allAwards.includes(keyword);
                }) && beans >= threshold;
            });

            // 如果有符合条件的奖项，则加入结果列表
            if (filteredAwards.length > 0) {
                var awards = filteredAwards.map(function(award) {
                    return award + '🐶';
                }).join('，');
                results.push("【" + account + "】 " + awardtext + " " + awards);
            }
        }

        // 处理新的日志格式（针对 regex2）
        while ((match = regex2.exec(line)) !== null) {
            var account = match[1].trim();
            var beans = parseInt(match[2].trim());
            var awards = beans + '京豆🐶';

            // 检查是否包含屏蔽关键词以及京豆数量是否大于等于阈值
            var shouldBlock = blockKeywords.some(function(keyword) {
                return awards.includes(keyword);
            });

            // 仅当京豆数量大于等于阈值且不包含屏蔽关键词时，才加入结果列表
            if (!shouldBlock && beans >= threshold) {
                results.push("【" + account + "】 " + awardtext + " " + awards);
            }
        }

        // 处理【账号】豆的格式（针对 regex3）
        /*while ((match = regex3.exec(line)) !== null) {
            var account = match[1].trim();  // 提取账号部分
            var beans = parseInt(match[2].trim());  // 提取豆的数量
			var awards = beans + '京豆🐶';

            // 检查是否包含屏蔽关键词以及豆数量是否大于等于阈值
            var shouldBlock = blockKeywords.some(function(keyword) {
                return account.includes(keyword);
            });

            // 仅当豆数量大于等于阈值且不包含屏蔽关键词时，才加入结果列表
            if (!shouldBlock && beans >= threshold) {
                results.push("【" + account + "】 " + awardtext + " " + awards);
            }
        }*/

        // 处理新的日志格式【账号】奖项描述：京豆数量（针对 regex4）
        while ((match = regex4.exec(line)) !== null) {
            var account = match[1].trim();  // 提取账号
            var awardDescription = match[2].trim();  // 提取奖项描述
            var beans = parseInt(match[3].trim());  // 提取京豆数量
			var awards = beans + '京豆🐶';

            // 检查是否包含屏蔽关键词以及京豆数量是否大于等于阈值
            var shouldBlock = blockKeywords.some(function(keyword) {
                return awardDescription.includes(keyword);
            });

            // 仅当京豆数量大于等于阈值且不包含屏蔽关键词时，才加入结果列表
            if (!shouldBlock && prizeBeans >= threshold) {
                results.push("【" + account + "】 " + awardDescription + " " + awards);
            }
        }
		
		// 处理直播抽奖日志（针对 regex5）
        while ((match = regex5.exec(line)) !== null) {
            var account = match[1].trim();  // 提取账号部分
            var username = match[2].trim();  // 提取用户名
            var prizeBeans = parseInt(match[3].trim());  // 提取京豆数量
            var awards = prizeBeans + '京豆🐶';  // 生成奖励信息

            // 检查是否包含屏蔽关键词以及京豆数量是否大于等于阈值
            var shouldBlock = blockKeywords.some(function(keyword) {
                return line.includes(keyword);
            });

            // 仅当京豆数量大于等于阈值且不包含屏蔽关键词时，才加入结果列表
            if (!shouldBlock && prizeBeans >= threshold) {
               results.push("【" + username + "】 " + awardtext + " " + awards);  // 不再输出账号编号，仅输出用户名 
            }
        }
    
	
        // 新增：处理 【账号】豆数量豆 格式（针对 regex6）	
	    while ((match = regex6.exec(line)) !== null) {
        var account = match[1].trim();  // 提取账号（如 jd_**qQc）
        var beans = parseInt(match[2].trim());  // 提取豆数量（如 20）
        var awards = beans + '京豆🐶';  // 格式化奖励文本

        // 检查屏蔽关键词及阈值
        var shouldBlock = blockKeywords.some(function(keyword) {
            return line.includes(keyword); // 检查整行是否含屏蔽词
        });

        // 符合条件则加入结果
        if (!shouldBlock && beans >= threshold) {
            results.push("【" + account + "】 " + awardtext + " " + awards);
        }
    }
	
	
	
	
	
	
	
	});

    // 如果 results 数组有内容，则进行推送
    if (results.length > 0) {
        // 增加标题
        var title = awardtitle + "\n---------------\n";
        var finalMessage = title + results.join('\n');

        // 推送合并后的消息（第一个推送） 
        var beanspushConfigs = bucketGet("zq8884", "beanspushConfigs"); 
        var pushConfigArray = beanspushConfigs.split(',');

        // 群组推送
        pushConfigArray.forEach(function(config) {
            var [imType, groupCode] = config.split(':').map(item => item.trim());
            push({
                imType: imType,
                groupCode: groupCode,
                content: finalMessage
            });
        });

        // 个人推送
        var beanspushConfigsgeren = bucketGet("zq8884", "beanspushConfigsgeren");
        if (beanspushConfigsgeren) {
            var gerenConfigArray = beanspushConfigsgeren.split(',').filter(Boolean);
            gerenConfigArray.forEach(function(config) {
                var [imType, userID] = config.split(':').map(item => item.trim());
                if (imType && userID) {
                    push({
                        imType: imType,
                        userID: userID,
                        title: "",
                        groupCode: "",  // 清空群组参数
                        content: finalMessage
                    });
                }
            });
        }

        // 通知管理员
        if (awardnotify) {
            notifyMasters(finalMessage);
        }
    }
}



        
        //实物中奖推送
if (MTryuse || !/M试用有礼/.test(obj.message)) {
    if (/已填地址/.test(obj.message) && !/已经兑完|明日再来/.test(obj.message)) {
        var results = [];
        var processedAccounts = new Set();
        var awardshiwutitle = bucketGet("zq8884", "awardshiwutitle");
        var awardshiwupt = bucketGet("zq8884", "awardshiwupt");
        var awardshiwugroupcode = bucketGet("zq8884", "awardshiwugroupcode");

        // 处理包含“(已填地址)🎁”和“已填地址”的情况
        var regex = /【京东账号\d+】(.*?)：(.*?$已填地址$🎁|.*?已填地址)|addressId=.*?,prizeName=(.*?),ptpin=(.*?),.*?已填地址/g;
        var match;
        while ((match = regex.exec(obj.message)) !== null) {
            var account = match[1] ? match[1].trim() : match[4].trim();
            var prizeInfo = match[2] ? match[2].trim() : match[3].trim();

            if (!/京豆|豆/.test(prizeInfo) && !processedAccounts.has(account)) {
                results.push(account + "：" + prizeInfo);
                processedAccounts.add(account);
            }
        }

        var linkMatch = obj.message.match(/https?:\/\/[^\s]+/);
        if (linkMatch) {
            results.push("活动链接：" + linkMatch[0]);
        }

        var hasPrizeInfo = results.some(item => !item.startsWith("活动链接："));

        if (hasPrizeInfo) {
            var title = awardshiwutitle + "\n---------------\n";
            var finalMessage = title + results.join('\n');

            // 群组推送
            var shiwupushConfigs = bucketGet("zq8884", "shiwupushConfigs");
            var pushConfigArray = shiwupushConfigs.split(',');
            pushConfigArray.forEach(function(config) {
                var [imType, groupCode] = config.split(':').map(item => item.trim());
                push({
                    imType: imType,
                    groupCode: groupCode,
                    content: finalMessage
                });
            });

            // 新增个人推送
            var shiwupushConfigsgeren = bucketGet("zq8884", "shiwupushConfigsgeren");
            if (shiwupushConfigsgeren) {
                var gerenConfigArray = shiwupushConfigsgeren.split(',').filter(Boolean);
                gerenConfigArray.forEach(function(config) {
                    var [imType, userID] = config.split(':').map(item => item.trim());
                    if (imType && userID) {
                        push({
                            imType: imType,
                            userID: userID,
                            title: "",
                            groupCode: "", // 清空群组参数
                            content: finalMessage
                        });
                    }
                });
            }

            if (awardnotify) {
                notifyMasters(finalMessage);
            }
        }
    }
}





        if (jingyunswitch) {         //jingyun签到id开关
        if (/jingyun 签到/.test(obj.message)) {    
		
		//var now = new Date();
        //var currentMonth = now.getMonth() + 1; // getMonth() 返回的是从0开始的月份索引
		//var monthPrefix = currentMonth.toString();  // 当前月份转为字符串作为前缀使用

            var urlPattern = /(https:\/\/jingyun[\S]+)/;
            var urlMatch = obj.message.match(urlPattern);
    
            if (urlMatch) {
                var activityUrl = urlMatch[1];
                var cronTime = bucketGet("zq8884", "jingyun_cron_time");		
                var actType = "\n活动类型：jingyun签到"
                var envVarName = 'jd_jingyun_sign_urls';
				var memo = 'jingyun签到活动URL收集';
				//var memo = '【' + monthPrefix + '月】jingyun签到活动URL'; // 添加月份前缀和月份单位，以及中括号
        
                var cronTaskExists = false;
                var cs = cron.get(); 
                for (var i = 0; i < cs.length; i++) {
                    if (cs[i].memo === memo) {
                        cronTaskExists = true;
                        var cmdMatch = cs[i].cmd.match(/="(.*)"/);
                        var cmdActivityUrls = cmdMatch ? cmdMatch[1].split('@') : [];

                        if (!cmdActivityUrls.includes(activityUrl)) {
                            cmdActivityUrls.push(activityUrl);
                            var newCmd = 'export ' + envVarName + '="' + cmdActivityUrls.join('@') + '"';
                            cron.update({
                                id: cs[i].id,
                                cron: cronTime,
                                cmd: newCmd,
                                toSelf: true,
								toOthers: cs[i].toOthers,
								memo: memo,
                            });
                            if (notify_addcron) {							
                            notifyMasters("【JD未来活动定时pro】\n" + actType + "\n当前活动URL数量：" + cmdActivityUrls.length + "\n添加活动URL：" + activityUrl + "\n自动定时：" + cronTime + "\n备注：" + memo);
   						    }                     
						}
                        break;
                    }
                }

                if (!cronTaskExists) {
                    var newCmd = 'export ' + envVarName + '="' + activityUrl + '"';
                    cron.add({
                        cron: cronTime,
                        cmd: newCmd,
                        toSelf: true,
                        memo: memo,
						toOthers: toOthers,
                    });
                    if (notify_addcron) {						
                    notifyMasters("【JD未来活动定时pro】\n" + actType + "\n定时内容：" + newCmd + "\n自动定时：" + cronTime + "\n备注：" + memo);
    				}                 
				}
            } 
        }
		
		}

		
        if (/M每日领奖/.test(obj.message) && /还没到开抢时间/.test(obj.message)) {
    
        function getTodayDateString() {
        // 在这里实现获取当前日期的逻辑，例如：
        // 注意，这里假设你使用的是ISO 8601日期格式，如果是其他格式，请相应调整
        var today = new Date();
        return today.toISOString().split('T')[0];}

        if (logswitch) {
        console.log("条件满足");
        Debug("条件满足");
				}
		
		//检查日志内容是否有未开始
        var pattern = /还没到开抢时间/;
        var pattern2 = /M签到有礼/;
        var patternM = /活动已结束/;
        var pattern3 = /M每日领奖/;
        
        var bl = pattern.test(obj.message);
        var bl2 = pattern2.test(obj.message) && !patternM.test(obj.message);
        var bl3 = pattern3.test(obj.message) && pattern.test(obj.message);

        if (logswitch) {
        Debug("是否为M每日领奖：" + bl3);
				}
        
        //匹配2023-09-28 00:00:00至2023-10-30 18:00:00字样
        var datePattern = /\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?[ ]?[至|-][ ]?\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配结果，数组
        var rlt = datePattern.exec(obj.message)
        //匹配开奖时间2023-09-28 00:00:00字样
        var datePattern2 = /每日开抢:\d{2}:\d{2}/
        //匹配开奖时间结果，数组
        var rlt2 = datePattern2.exec(obj.message)
        //去除“开奖时间:”字样
              	 
		if (rlt2) {
        // 获取今天的日期
        var todayDate = getTodayDateString();
        // 格式化开始时间
        rlt2[0] = todayDate + ' ' + rlt2[0].replace(/每日开抢:/g, "") + ':00';
		var timeString = rlt2[0]	
		var parts = timeString.split(' ')
        var year = parseInt(parts[0].slice(0, 4))
        var month = parseInt(parts[0].slice(5, 7)) - 1 // 月份从1开始计数
        var day = parseInt(parts[0].slice(8, 10))
        var hours = parseInt(parts[1].slice(0, 2))
        var minutes = parseInt(parts[1].slice(3, 5))
        var seconds = parseInt(parts[1].slice(6))
       // 创建一个新的Date对象，然后减去3秒
        var originalDate = new Date(year, month, day, hours, minutes, seconds)
		var meiriqiang_early_time = bucketGet("zq8884","meiriqiang_early_time")
        var newDate = new Date(originalDate.getTime() - meiriqiang_early_time) 
        var dateString = newDate.getFullYear() + '-' + (newDate.getMonth() + 1).toString().padStart(2, '0') + '-' + newDate.getDate().toString().padStart(2, '0') + ' ' + newDate.getHours().toString().padStart(2, '0') + ':' + newDate.getMinutes().toString().padStart(2, '0') + ':' + newDate.getSeconds().toString().padStart(2, '0')
        // 将新的时间添加回rlt2[0]
        rlt2[0] = dateString;
          // 然后你可以像之前那样使用rlt2[0]

        if (logswitch) {
        Debug(rlt2[0]);
				}
				
        }

        //备注
        var memo
        if (bl3 && rlt2) {//M每日领奖
            memo = rlt2[0]//备注
        } else if (rlt) {//未来活动或签到有礼
            memo = rlt[0]//备注
        }
		

        if (logswitch) {
        Debug("备注时间：" + memo)
				}

        //匹配变量
        var exptPattern = /export \S+=\"\S+\"/
        //匹配结果，字符串
        var expt = exptPattern.exec(obj.message).toString()
		
 
        if (logswitch) {
        Debug("变量：" + expt)
				}


        var hasThisCron = false
        var cs = cron.get()
        for (i = 0; i < cs.length; i++) {
            if (cs[i].cmd == expt) {
                if (bl3 && rlt2) {//M每日领奖
                    cron.delete(cs[i].id)
					hasThisCron = true   //3/15 新加
                    break
                } else {
                    hasThisCron = true
                    break
                }
            }
        }

        //autMan里没有此变量的定时指令时
        if (!hasThisCron) {
            if (bl3 && rlt2) {//M每日领奖
                dateStr = rlt2[0].toString()
				
        if (logswitch) {
        Debug("每日抢好礼（超级无线）定时：" + dateStr)
				}
				
				seconds = dateStr.split(":")
				secondStart = seconds[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "") // 提取秒并处理空格
                // 如果秒为空，设置为0
                if (secondStart == "") {
                    secondStart = "0"
			    }
				
			
                mins = dateStr.split(":")
                minuteStart = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (minuteStart == "") {
                    minuteStart = "0"
                }
                hours = mins[0].split(" ")
                hourStart = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (hourStart == "") {
                    hourStart = "0"
                }
                ymd = hours[0].split("-")
                yearStart = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                monthStart = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                dayStart = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
//
				cn = secondStart + " " + minuteStart + " " + hourStart + " " + dayStart + " " + monthStart + " *"
                //添加定时指令
               
        if (logswitch) {
        Debug("M每日领奖：" + cn)
				}
				if (notify_addcron) {
                notifyMasters("【JD未来活动定时pro】\n" + "活动时间：" + rlt2[0] + "\n活动类型：M每日领奖" + "\n自动定时：" + cn + "\n定时内容：" + expt)
  				}                 
				id = cron.add({
                    cron: cn,
                    cmd: expt,
                    toSelf: true,
                    toOthers: toOthers,
                    memo: memo,
                })
               
        if (logswitch) {
        Debug("定时指令ID：" + id)
				}
				
            } 
        } else {
        if (notify_repeat_cron) {
        notifyMasters(expt + "\n--------------\n定时指令已存在，忽略")

        if (logswitch) {
        Debug("已存在此定时指令")
				}             
				}
				
        }
    }


         //if (/export/.test(obj.message) && /京豆|E卡|e卡|红包|积分|活动未开始/.test(obj.message)) {//有export字样，M类脚本日志
		if (/export/.test(obj.message) && (/京豆|E卡|e卡|红包|活动未开始/.test(obj.message) || (pointswitch && /积分/.test(obj.message)))) {
        // 执行的逻辑
	
		//检查日志内容是否有未开始
        var pattern = /未开始/;
        var pattern2 = /M签到有礼/;
        var patternM = /活动已结束|垃圾活动/;
        var pattern3 = /M购物车锦鲤/;
        
        var bl = pattern.test(obj.message);
        var bl2 = pattern2.test(obj.message) && !patternM.test(obj.message);
        var bl3 = pattern3.test(obj.message);
		
		



        if (logswitch) {
        Debug("是否为M购物车锦鲤：" + bl3);      
				}
				
        //匹配2023-09-28 00:00:00至2023-10-30 18:00:00字样
        var datePattern = /\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?[ ]?[至|-][ ]?\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配结果，数组
        var rlt = datePattern.exec(obj.message)
		

        if (logswitch) {
			Debug("是否为XXX至XXX字样格式：" + rlt);
			}
	
		
		
		
        //匹配开奖时间2023-09-28 00:00:00字样
        var datePattern2 = /开奖时间:\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配开奖时间结果，数组
        var rlt2 = datePattern2.exec(obj.message)
		

        if (logswitch) {
        Debug("是否为2023-09-28 00:00:00字样格式：" + rlt2);
				}
		
		if (rlt2) {
        var timeString = rlt2[0].replace(/开奖时间:/, "") // 去除“开奖时间:”
        //去除“开奖时间:”字样
		// 解析时间字符串（这里假设是YYYY-MM-DD HH:MM:SS格式）
		
        var parts = timeString.split(' ')
        var year = parseInt(parts[0].slice(0, 4))
        var month = parseInt(parts[0].slice(5, 7)) - 1 // 月份从1开始计数
        var day = parseInt(parts[0].slice(8, 10))
        var hours = parseInt(parts[1].slice(0, 2))
        var minutes = parseInt(parts[1].slice(3, 5))
        var seconds = parseInt(parts[1].slice(6))
       // 创建一个新的Date对象，然后减去3秒
        var originalDate = new Date(year, month, day, hours, minutes, seconds)
		var jinli_early_time = bucketGet("zq8884","jinli_early_time")
        var newDate = new Date(originalDate.getTime() - jinli_early_time) // 3000毫秒等于3秒
        var dateString = newDate.getFullYear() + '-' + (newDate.getMonth() + 1).toString().padStart(2, '0') + '-' + newDate.getDate().toString().padStart(2, '0') + ' ' + newDate.getHours().toString().padStart(2, '0') + ':' + newDate.getMinutes().toString().padStart(2, '0') + ':' + newDate.getSeconds().toString().padStart(2, '0')
        // 将新的时间添加回rlt2[0]
        rlt2[0] = dateString;
          // 然后你可以像之前那样使用rlt2[0]
		  

        if (logswitch) {
        Debug(rlt2[0])
				}
		}
		
        //var datePattern3 = /已经开奖/
		//var rlt3 = datePattern3.exec(obj.message)
		//Debug("是否已开奖" + rlt3);




        //备注
        var memo
        if (bl3 && rlt2) {//购物车锦鲤
            memo = rlt2[0]//备注
        } else if (rlt) {//未来活动或签到有礼
            memo = rlt[0]//备注
        }
		


        if (logswitch) {
        Debug("备注时间：" + memo)
				}

        //匹配变量
        var exptPattern = /export \S+=\"\S+\"/
        //匹配结果，字符串
        var expt = exptPattern.exec(obj.message).toString()
		


        if (logswitch) {
        Debug("变量：" + expt)
				}
				
				
				
	    //判定是否未开始	
        var hasStarted = false;
        if (bl || bl2 || bl3) {
        if (logswitch) {			
            Debug("活动未开始，继续执行");
				}			
        } else {
            hasStarted = true;
            // 活动已经开始
        }



        //检查变量是否重复
        var hasThisCron = false
        var cs = cron.get()
        for (i = 0; i < cs.length; i++) {
            if (cs[i].cmd == expt) {				
                if (bl3 && rlt2) {   //购物车锦鲤且存在开奖时间，所以开奖了，删除定时指令
				//if (bl3 && rlt3) {
                    cron.delete(cs[i].id) //
					hasThisCron = true   //删除并设置为true，并打印最后的结果：已存在此定时指令
                    break
                } 					
				else {
                    hasThisCron = true  //设置为true，并打印最后的结果：已存在此定时指令
                    break
                }
            }
        }
		
		
		


		
		
		
		

        //autMan里没有此变量的定时指令时
        //if (!hasThisCron) {
		if (!hasThisCron && !hasStarted) {
            if (bl3 && rlt2) {//购物车锦鲤开奖活动
                dateStr = rlt2[0].toString()

        if (logswitch) {
        Debug("购物车锦鲤开奖时间：" + dateStr)
				}
				
				seconds = dateStr.split(":")
				secondStart = seconds[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "") // 提取秒并处理空格
        // 如果秒为空，设置为0
                if (secondStart == "") {
                    secondStart = "0"
			    }
					
                mins = dateStr.split(":")
                minuteStart = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (minuteStart == "") {
                    minuteStart = "0"
                }
                hours = mins[0].split(" ")
                hourStart = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (hourStart == "") {
                    hourStart = "0"
                }
                ymd = hours[0].split("-")
                yearStart = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                monthStart = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                dayStart = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                cn = secondStart + " " + minuteStart + " " + hourStart + " " + dayStart + " " + monthStart + " *"

                //添加定时指令


                if (logswitch) {
                Debug("购物车锦鲤开奖定时：" + cn)
				}
				
	            if (notify_addcron) {				
                notifyMasters("【JD未来活动定时pro】\n" + "活动时间：" + rlt2[0] + "\n活动类型：购物车锦鲤开奖" + "\n自动定时：" + cn + "\n定时内容：" + expt)
                }                
				id = cron.add({
                    cron: cn,
                    cmd: expt,
                    toSelf: true,
                    toOthers: toOthers,
                    memo: memo,
                })
				

               if (logswitch) {
                Debug("定时指令ID：" + id)
				}
				
            } else if (rlt) {//未来活动或签到有礼
                dateStr = rlt[0].toString().split("至")[0]
				
				
				seconds = dateStr.split(":")
				secondStart = seconds[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "") // 提取秒并处理空格
        // 如果秒为空，设置为0
                if (secondStart == "") {
                    secondStart = "0"
			    }
				
				
				
				
                mins = dateStr.split(":")
                minuteStart = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (minuteStart == "") {
                    minuteStart = "0"
                }
                hours = mins[0].split(" ")
                hourStart = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (hourStart == "") {
                    hourStart = "0"
                }
                ymd = hours[0].split("-")
                yearStart = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                monthStart = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                dayStart = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
//
				cn = secondStart + " " + minuteStart + " " + hourStart + " " + dayStart + " " + monthStart + " *"

                //获取结束时间
                dateStr = rlt.toString().split("至")[1]
                mins = dateStr.split(":")
                minuteEnd = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (minuteEnd == "") {
                    minuteEnd = "0"
                }
                hours = mins[0].split(" ")
                hourEnd = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (hourEnd == "") {
                    hourEnd = "0"
                }
                ymd = hours[0].split("-")
                yearEnd = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                monthEnd = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                dayEnd = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")

                var actType = "\n活动类型：未来活动"
				
				

				
				
	


 if (bl2) { // 签到有礼
    var minuteRange = bucketGet("zq8884", "minuteRange") || "0-10"; // 获取自定义的分钟范围，默认为 "0-10"
    if (logswitch) {
    Debug("获取到的 minuteRange 值: " + minuteRange); // 打印获取到的 minuteRange 值
    }
    var randomMinute;

    // 解析 minuteRange，生成对应的随机分钟数
    if (minuteRange.indexOf("-") > -1) {
        var rangeParts = minuteRange.split("-");
        var min = parseInt(rangeParts[0], 10);
        var max = parseInt(rangeParts[1], 10);

        // 检查解析的 min 和 max 是否正确
       if (logswitch) {
        Debug("解析的范围: min = " + min + ", max = " + max);
        }
        // 生成 min 到 max 范围内的随机整数
        randomMinute = Math.floor(Math.random() * (max - min + 1)) + min;

        // 检查生成的 randomMinute 值
      if (logswitch) {
        Debug("生成的随机分钟数: randomMinute = " + randomMinute);
        }        
    } else {
        randomMinute = parseInt(minuteRange, 10) || 0; // 如果不是范围，则直接使用指定的数值，默认为 0

        // 检查直接解析的 randomMinute 值
        if (logswitch) {
        Debug("直接使用的分钟数: randomMinute = " + randomMinute);
        }  
    }

    var SignhasStarted = false;
    var sign_cron_time = bucketGet("zq8884", "sign_cron_time");
    var currentDate = new Date(); // 获取当前日期
    var activityStartTime = new Date(yearStart, monthStart - 1, dayStart, hourStart, minuteStart, secondStart);

    if (monthStart == monthEnd && yearStart == yearEnd) {
        if (activityStartTime.toDateString() === currentDate.toDateString() || ifCronNotFirstday) {
            cn = randomMinute + " " + sign_cron_time + " " + dayStart + "-" + dayEnd + " " + monthStart + " *";
        } else {
            SignhasStarted = true;
            if (notify_SignhasStarted) {
                notifyMasters("非首日签到，跳过添加新的cron任务");
            }
            if (logswitch) {
                Debug("活动开始时间不是今天，且 ifCronNotFirstday 为 false，跳过定时");
            }
        }
    } else {
        if (parseInt(monthStart) > parseInt(monthEnd)) { // 跨年
            if (activityStartTime.toDateString() === currentDate.toDateString() || ifCronNotFirstday) {
                cn = randomMinute + " " + sign_cron_time + " 1-31 " + monthStart + "," + monthEnd + " *";
            } else {
                SignhasStarted = true;
                if (notify_SignhasStarted) {
                    notifyMasters("非首日签到，跳过添加新的cron任务");
                }
                if (logswitch) {
                    Debug("活动开始时间不是今天，且 ifCronNotFirstday 为 false，跳过定时");
                }
            }
        } else {
            if (activityStartTime.toDateString() === currentDate.toDateString() || ifCronNotFirstday) {
                cn = randomMinute + " " + sign_cron_time + " 1-31 " + monthStart + "-" + monthEnd + " *";
            } else {
                SignhasStarted = true;
                if (notify_SignhasStarted) {
                    notifyMasters("非首日签到，跳过添加新的cron任务");
                }
                if (logswitch) {
                    Debug("活动开始时间不是今天，且 ifCronNotFirstday 为 false，跳过定时");
                }
            }
        }
    }
    actType = "\n活动类型：签到有礼";
}






				
			

			
				// 定义正则表达式以匹配 activityId
				//var activityIdPattern = /activityId=([a-fA-F0-9]+)|id=([a-fA-F0-9]+)/;
				// 提取 activityId
				//var activityIdMatch = activityIdPattern.exec(expt);
				//Debug("提取的activityIdMatch：" + activityIdMatch);
				//var activityid = activityIdMatch ? activityIdMatch[1] : null;
				
                //判定ID是否重复部分
				var activityIdPattern = /activityId=([a-fA-F0-9]+)|id=([a-fA-F0-9]+)|giftId=([a-fA-F0-9]+)|#([a-fA-F0-9]+)/;
				// 执行匹配
				var activityIdMatch = expt.match(activityIdPattern);
				// 调试输出
				Debug("提取的id：" + JSON.stringify(activityIdMatch));
				// 处理匹配结果
				if (activityIdMatch) {
    				// 获取第一个非空匹配的捕获组
    				var activityid = activityIdMatch[1] || activityIdMatch[2] || activityIdMatch[3];
   				 if (logswitch) {
       				 Debug("提取到的Id: " + (activityid || "未找到Id"));
   				 }
				} else {
  				  if (logswitch) {
        				Debug("未找到任何匹配项");
    				}
				}
						
				 if (logswitch) {
                 Debug("提取的Id：" + activityid);
				}			
				
				var cs = cron.get();
				var hasThisCron = false; // 用于跟踪是否已有相应的cron任务

				if (activityid) {
   				 // 遍历现有的cron任务列表，检查是否有相应的activityid
   				 for (var i = 0; i < cs.length; i++) {
     				   if (cs[i].cmd.includes(activityid)) {
      				      hasThisCron = true; // 如果找到了，设置hasThisCron为true
      				      break; // 如果找到相应的activityid，就不需要再继续遍历
      				  }
   				 }

   				 // 如果不存在相应的cron任务,且SignhasStarted为false（签到为首日），可以添加新任务
   				 if (!hasThisCron &&!SignhasStarted) {
       				 // 添加新的cron任务


                if (logswitch) {
                 Debug("定时：" + cn)
				}
				
                id = cron.add({
                    cron: cn,
                    cmd: expt,
                    toSelf: true,
                    toOthers: toOthers,
                    memo: memo,
                })
				
				if (notify_addcron) {
                notifyMasters("【JD未来活动定时pro】\n" + "活动时间：" + rlt[0] + actType + "\n自动定时：" + cn + "\n定时内容：" + expt)
                }

                if (logswitch) {
                Debug("定时指令ID：" + id)
				}
				
   				 } else {


                 if (logswitch) {
                 Debug("activityid已存在，跳过添加新的cron任务");
				}
				


                if (notify_repeat) {
                    notifyMasters("已存在的活动ID\n" + activityid + "\n跳过添加新的cron任务");
                
				}
   				 }
				} else {


                if (logswitch) {
                Debug("未能提取有效的activityId");
				}
				}
				
				
		
            } else {//没有给出明确时间的未来活动
                let month, day;
                date = new Date();
                date.setTime(date.getTime() + 24 * 60 * 60 * 1000);
                month = date.getMonth() + 1;
                day = date.getDate();

                id = cron.add({
                    cron: "0 0 " + day + " " + month + " *",
                    cmd: expt,
                    toSelf: true,
                    toOthers: toOthers,
                    memo: memo,
                })
				if (notify_addcron) {
                notifyMasters("【JD未来活动定时pro】\n" + "活动时间：未知" + "\n自动定时：" + cn + "\n定时内容：" + expt)
                }
			}
        } else {
            


        if (notify_repeat_cron) {
        notifyMasters(expt + "\n--------------\n定时指令已存在或活动已开始，忽略")

        if (logswitch) {
        Debug("已存在此定时指令或活动已开始")
				}             
				}

        }
    }


if (MsignCollect) {    //M签到转9R开关
    if (/M签到有礼/.test(obj.message) && /signActivity/.test(obj.message) && /活动时间/.test(obj.message) && !/该活动已经结束|活动已结束|垃圾活动|活动不存在/.test(obj.message)) {
        var now = new Date();
        var currentMonth = now.getMonth() + 1;
        //var monthPrefix = currentMonth.toString();
		var monthPrefix = currentMonth.toString().padStart(2, '0'); // 03月格式
        var ToselfTime = bucketGet("zq8884", "9R_cron_time");
        var cronTime = ToselfTime + " 1-31 " + currentMonth + " *";
        
        var actType = "\n活动类型：M签到有礼转9R签到";
        var exptPattern = /export \S+=\"\S+\"/;
        var exptMatch = exptPattern.exec(obj.message);
        var expt = exptMatch ? exptMatch[0] : null;

        if (logswitch) {
            Debug("变量：" + expt);
        }

        var activityIdMatch = expt.match(/activityId=([a-fA-F0-9]+)/);
        var venderIdMatch = expt.match(/venderId=([a-fA-F0-9]+)/);
        var activityId;
        var venderId;
        var envVarName;
        var exptUpdated;
        var cronTaskExists = false;

        if (activityIdMatch) {
            activityId = activityIdMatch[1];
            venderId = venderIdMatch ? venderIdMatch[1] : null;

            if (expt.indexOf('lzkj-isv.isvjcloud.com/sign/signActivity') !== -1) {
                envVarName = 'jd_wxSign_sign_lzkj_Ids';
                memo = '【' + monthPrefix + '月】内联LZKJ_SIGN';
                var combinedId = activityId;
            } else if (expt.indexOf('lzkj-isv.isvjcloud.com/sign/sevenDay/signActivity') !== -1) {
                envVarName = 'jd_wxSign_sevenDay_lzkj_Ids';
                memo = '【' + monthPrefix + '月】内联LZKJ_SEVENDAY';
                var combinedId = activityId;
            } else if (expt.indexOf('cjhy-isv.isvjcloud.com/sign/signActivity') !== -1) {
                envVarName = 'jd_wxSign_sign_cjhy_Ids';
                memo = '【' + monthPrefix + '月】内联CJHY_SIGN';
                var combinedId = venderId ? activityId + ':' + venderId : activityId;
            } else if (expt.indexOf('cjhy-isv.isvjcloud.com/sign/sevenDay/signActivity') !== -1) {
                envVarName = 'jd_wxSign_sevenDay_cjhy_Ids';
                memo = '【' + monthPrefix + '月】内联CJHY_SEVENDAY';
                var combinedId = venderId ? activityId + ':' + venderId : activityId;
            } else if (expt.indexOf('cjhy-isv.isvjcloud.com/signNew/signActivity') !== -1) {
                envVarName = 'jd_wxSign_signNew_cjhy_Ids';
                memo = '【' + monthPrefix + '月】内联CJHY_SIGNNEW';
                var combinedId = venderId ? activityId + ':' + venderId : activityId;
            }

            var cs = cron.get();
            for (var i = 0; i < cs.length; i++) {
                if (cs[i].memo === memo) {
                    cronTaskExists = true;
                    var cmdMatch = cs[i].cmd.match(/="(.*)"/);
                    var cmdActivityIds = cmdMatch ? cmdMatch[1].split(',') : [];
                    if (cmdActivityIds.indexOf(combinedId) === -1) {
                        cmdActivityIds.push(combinedId);
                        var newCmd = 'export ' + envVarName + '="' + cmdActivityIds.join(',') + '"';
                        cron.update({
                            id: cs[i].id,
                            cron: cronTime,
                            cmd: newCmd,
                            toSelf: true,
                            toOthers: toOthers,
                            memo: memo,
                        });
                        var notifyMessage = "【JD未来活动定时pro】\n" + actType + 
                            "\n当前签到id数量：" + cmdActivityIds.length + 
                            "\n添加活动id：" + combinedId + 
                            "\n自动定时：" + cronTime + 
                            "\n备注：" + memo;
                        if (notify_addcron) {
                            notifyMasters(notifyMessage);
                        }
                        if (toSelfswitch) {
                            ClosetoSelfTask(expt);
                        }
                    }
                    break;
                }
            }

            // ============= 修改点：同步重试逻辑 =============
            if (!cronTaskExists) {
                var maxRetries = 3; // 最大重试次数
                var retryCount = 0;
                var existsInRetry = false;

                // 同步循环检查
                while (retryCount < maxRetries && !existsInRetry) {
                    var csRetry = cron.get();
                    for (var j = 0; j < csRetry.length; j++) {
                        if (csRetry[j].memo === memo) {
                            existsInRetry = true;
                            break;
                        }
                    }
                    retryCount++;
                }

                if (!existsInRetry) {
                    var newCmd = 'export ' + envVarName + '="' + combinedId + '"';
                    cron.add({
                        cron: cronTime,
                        cmd: newCmd,
                        toSelf: true,
                        toOthers: toOthers,
                        memo: memo,
                    });
                    if (logswitch) {
                        Debug("创建新任务: " + memo);
                    }
                    var notifyMessage = "【JD未来活动定时pro】\n" + actType + 
                        "\n定时内容：" + newCmd + 
                        "\n自动定时：" + cronTime + 
                        "\n备注：" + memo;
                    if (notify_addcron) {
                        notifyMasters(notifyMessage);
                    }
                    if (toSelfswitch) {
                        ClosetoSelfTask(expt);
                    }
                } else {
                    if (logswitch) {
                        Debug("任务已存在: " + memo);
                    }
                }
            }
            // ============= 修改结束 =============
        }

        function ClosetoSelfTask(expt) {
            var MDPQDexpt = expt;
            if (logswitch) {
                Debug("整理后的环境变量：" + MDPQDexpt);
            }
            var cs = cron.get();
            var currentMonth = new Date().getMonth() + 1;
            for (var i = 0; i < cs.length; i++) {
                if (cs[i].cmd == MDPQDexpt) {
                    var cronParts = cs[i].cron.split(' ');
                    var monthExpression = cronParts[3];
                    var isRange = monthExpression.indexOf('-') !== -1;
                    var rangeParts = monthExpression.split('-');
                    var shouldUpdateCron = false;
                    if (isRange) {
                        var endMonth = parseInt(rangeParts[1], 10);
                        if (currentMonth === endMonth) {
                            shouldUpdateCron = true;
                        }
                    } else {
                        if (parseInt(monthExpression, 10) === currentMonth) {
                            shouldUpdateCron = true;
                        }
                    }
                    if (shouldUpdateCron) {
                        var id = cs[i].id;
                        var newmemo = "已内联9R签到 关闭自处理\n【备注】" + cs[i].memo;
                        if (logswitch) {
                            Debug("待关闭自处理的ID为:" + id);
                        }
                        cron.update({
                            id: id,
                            cron: cs[i].cron,
                            cmd: cs[i].cmd,
                            toSelf: false,
                            toOthers: cs[i].toOthers,
                            memo: newmemo,
                        });
                        if (notify_addcron) {
                            notifyMasters("【JD未来活动定时pro】\n【M签到变量】\n" + expt + "\n【注意】" + newmemo);
                        }
                        break;
                    }
                }
            }
        }
    }
}

		
	    if (/大牌联合/.test(obj.message)) {   
			


        if (logswitch) {
        console.log("条件满足");
		Debug("条件满足")
		}

		
		//检查日志内容是否有未开始
        var pattern = /未开始/;
        var pattern2 = /大牌联合/;
        var patternM = /活动已结束/;
        var pattern3 = /XXX/;
        
        var bl = pattern.test(obj.message);
        var bl2 = pattern2.test(obj.message) && !patternM.test(obj.message);
        var bl3 = pattern3.test(obj.message);


		
        // 正则表达式，匹配开始时间和结束时间
        var startTimePattern = /开始时间：(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})?)/;
        var endTimePattern = /结束时间：(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})?)/;

        // 使用match方法提取开始时间和结束时间
        var startTimeMatch = startTimePattern.exec(obj.message);
        var endTimeMatch = endTimePattern.exec(obj.message);

        // 确保至少有一个匹配
        if (startTimeMatch && endTimeMatch) {
        // 提取开始时间和结束时间，并添加秒
        var startTime = startTimeMatch[1] + ":00";
        var endTime = endTimeMatch[1] + ":59";

        // 去除“开始时间”和“结束时间”
        startTime = startTime.replace("开始时间：", "");
        endTime = endTime.replace("开始时间：", "");

        // 连接开始时间和结束时间
        var combotime = startTime + "～" + endTime;
		var rlt = [combotime]        //数组重新格式化，将整体零散数组整合成一个元素，否则memo读取的是第一个数字“2”

        // 输出结果，保留完整的时间格式

                if (logswitch) {
        console.log(rlt); // 输出：2024-04-01 00:00:00～2024-04-30 23:59:00
        }
        } else {


        if (logswitch) {
        console.log("未找到开始时间和结束时间");
        }
        }
		

        //匹配开奖时间2023-09-28 00:00:00字样
        var datePattern2 = /开始时间：\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配开奖时间结果，数组
        var rlt2 = datePattern2.exec(obj.message)
        //去除“开奖时间:”字样
        if (rlt2) {
            rlt2[0] = rlt2[0].replace(/开始时间：/g, "")
        if (logswitch) {
                 Debug(rlt2[0])
        }
        }

        //备注
        var memo
        if (bl3 && rlt2) {//幸运抽奖（超级无线）
            memo = rlt2[0]//备注
        } else if (rlt) {//未来活动或签到有礼

            memo = rlt[0]//备注
        }
               
        if (logswitch) {
        Debug("备注时间：" + memo)
        }

        //匹配变量
		var exptPattern = /【活动ID】(\w+)/
        var envVarName = 'jd_dplh_viewShop_ids';
        if (logswitch) {		
        Debug("变量：" + exptPattern)
        }
		// 匹配结果，返回的是匹配到的数组或者null
		var exptMatch = exptPattern.exec(obj.message);
		// 如果有匹配结果，将其转换为字符串
		if (exptMatch) {
        var activityId = exptMatch[0].replace(/【活动ID】/, "")

        if (logswitch) {
        Debug("变量：" + activityId)
        }
		               }
		
		var expt = 'export ' + envVarName + '="' + activityId + '"';
		
      
        if (logswitch) {
        Debug("变量：" + expt)
        }


        //签到有礼
        // if (bl2) {
        //     //从变量expt中获取变量值
        //     newMsg = expt.split("=\"")[1].replace(/\"/g, "")
        //     if (/^http/.test(newMsg)) {
        //         Debug("签到有礼变量：" + newMsg)
        //         autMan.Session(newMsg)
        //     }
        // }


        //检查变量是否重复
        var hasThisCron = false
        var cs = cron.get()
        for (i = 0; i < cs.length; i++) {
            if (cs[i].cmd == expt) {
                if (bl3 && rlt2) {//幸运抽奖（超级无线）定时
                    cron.delete(cs[i].id)
					hasThisCron = true   //3/15 新加
                    break
                } else {
                    hasThisCron = true
                    break
                }
            }
        }

        //autMan里没有此变量的定时指令时
        if (!hasThisCron) {
           if (rlt) {//大牌联合
                dateStr = rlt[0].toString().split("～")[0]
                mins = dateStr.split(":")
                minuteStart = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (minuteStart == "") {
                    minuteStart = "0"
                }
                hours = mins[0].split(" ")
                hourStart = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (hourStart == "") {
                    hourStart = "0"
                }
                ymd = hours[0].split("-")
                yearStart = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                monthStart = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                dayStart = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                cn = minuteStart + " " + hourStart + " " + dayStart + " " + monthStart + " *"

                //获取结束时间
                dateStr = rlt.toString().split("～")[1]
                mins = dateStr.split(":")
                minuteEnd = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (minuteEnd == "") {
                    minuteEnd = "0"
                }
                hours = mins[0].split(" ")
                hourEnd = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (hourEnd == "") {
                    hourEnd = "0"
                }
                ymd = hours[0].split("-")
                yearEnd = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                monthEnd = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                dayEnd = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")

                var actType = "\n活动类型：大牌联合"
                if (bl2) {//大牌联合
				
				var sign_cron_time = bucketGet("zq8884","sign_cron_time");
                    //签到有礼定时
                    if (monthStart == monthEnd) {
                        //cn = "0 0,10 " + dayStart + "-" + dayEnd + " " + monthStart + " *"
			          cn = "0 " + sign_cron_time +  " " + dayStart + "-" + dayEnd + " " + monthStart + " *"		
                    } else {
                        if (parseInt(monthStart) > parseInt(monthEnd)) {//跨年
                            //cn = "0 0,10 1-31 " + monthStart + "," + monthEnd + " *"
							cn = "0 " + sign_cron_time + " 1-31 " + monthStart + "," + monthEnd + " *"
                        } else {
                            //cn = "0 0,10 1-31 " + monthStart + "-" + monthEnd + " *"        //10点补签
							cn = "0 " + sign_cron_time + " 1-31 " + monthStart + "-" + monthEnd + " *"
                        }
                    }
                    actType = "\n活动类型：大牌联合"
                }

                //添加定时指令

                 Debug("定时：" + cn)

				
                id = cron.add({
                    cron: cn,
                    cmd: expt,
                    toSelf: true,
                    toOthers: toOthers,
                    memo: memo,
                })
				if (notify_addcron) {
                notifyMasters("【JD未来活动定时pro】\n" + "活动时间：" + rlt[0] + actType + "\n自动定时：" + cn + "\n定时内容：" + expt)
                }      
        if (logswitch) {
        Debug("定时指令ID：" + id)
            }
				
            } else {//没有给出明确时间的未来活动
                let month, day;
                date = new Date();
                date.setTime(date.getTime() + 24 * 60 * 60 * 1000);
                month = date.getMonth() + 1;
                day = date.getDate();

                id = cron.add({
                    cron: "0 0 " + day + " " + month + " *",
                    cmd: expt,
                    toSelf: true,
                    toOthers: toOthers,
                    memo: memo,
                })
				if (notify_addcron) {
                notifyMasters("【JD未来活动定时pro】\n" + "活动时间：未知" + "\n自动定时：" + cn + "\n定时内容：" + expt)
				}
            }
        } else {
        if (notify_repeat_cron) {
        notifyMasters(expt + "\n--------------\n定时指令已存在，忽略")

        if (logswitch) {
        Debug("已存在此定时指令")
        }		
				           
				}
        }
    }

	
         //9R幸运抽奖
		if (/幸运抽奖（超级无线）/.test(obj.message) && /未开始/.test(obj.message) && /京豆|E卡|e卡|红包|积分/.test(obj.message)) {//9R幸运抽奖
		

    	

		
		//检查日志内容是否有未开始
        var pattern = /未开始/;
        var pattern2 = /M签到有礼/;
        var patternM = /活动已结束/;
        var pattern3 = /幸运抽奖（超级无线）/;
        
        var bl = pattern.test(obj.message);
        var bl2 = pattern2.test(obj.message) && !patternM.test(obj.message);
        var bl3 = pattern3.test(obj.message) && pattern.test(obj.message);
        if (logswitch) {
        Debug("是否为幸运抽奖（超级无线）：" + bl3);
				}
        
        //匹配2023-09-28 00:00:00至2023-10-30 18:00:00字样
        var datePattern = /\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?[ ]?[至|-][ ]?\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配结果，数组
        var rlt = datePattern.exec(obj.message)
        //匹配开奖时间2023-09-28 00:00:00字样
        var datePattern2 = /开始时间：\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配开奖时间结果，数组
        var rlt2 = datePattern2.exec(obj.message)
        //去除“开奖时间:”字样
		
		
		if (rlt2) {
        // 格式化开始时间
		var timeString = rlt2[0].replace(/开始时间：/g, "") + ':00';
		var parts = timeString.split(' ')
        var year = parseInt(parts[0].slice(0, 4))
        var month = parseInt(parts[0].slice(5, 7)) - 1 // 月份从1开始计数
        var day = parseInt(parts[0].slice(8, 10))
        var hours = parseInt(parts[1].slice(0, 2))
        var minutes = parseInt(parts[1].slice(3, 5))
        var seconds = parseInt(parts[1].slice(6))
       // 创建一个新的Date对象，然后减去3秒
        var originalDate = new Date(year, month, day, hours, minutes, seconds)
        var newDate = new Date(originalDate.getTime() - 3000) // 3000毫秒等于3秒
        var dateString = newDate.getFullYear() + '-' + (newDate.getMonth() + 1).toString().padStart(2, '0') + '-' + newDate.getDate().toString().padStart(2, '0') + ' ' + newDate.getHours().toString().padStart(2, '0') + ':' + newDate.getMinutes().toString().padStart(2, '0') + ':' + newDate.getSeconds().toString().padStart(2, '0')
        // 将新的时间添加回rlt2[0]
        rlt2[0] = dateString;
          // 然后你可以像之前那样使用rlt2[0]


        if (logswitch) {
        Debug(rlt2[0]);
				}
        }

        //备注
        var memo
        if (bl3 && rlt2) {//幸运抽奖（超级无线）
            memo = rlt2[0]//备注
        } else if (rlt) {//未来活动或签到有礼
            memo = rlt[0]//备注
        }


        if (logswitch) {
        Debug("备注时间：" + memo)
				}

        //匹配变量
        var exptPattern = /[a-zA-Z]+:\/\/[^\s]*activityType=(10001|10004|10020|10021|10026|10031|10041|10042|10046|10054|10062|10063|10073|10080)[^\s]*/
        //匹配结果，字符串
        var expt = exptPattern.exec(obj.message).toString()

        if (logswitch) {
        Debug("变量：" + expt)
				}

        //签到有礼
        // if (bl2) {
        //     //从变量expt中获取变量值
        //     newMsg = expt.split("=\"")[1].replace(/\"/g, "")
        //     if (/^http/.test(newMsg)) {
        //         Debug("签到有礼变量：" + newMsg)
        //         autMan.Session(newMsg)
        //     }
        // }

        //检查变量是否重复
        var hasThisCron = false
        var cs = cron.get()
        for (i = 0; i < cs.length; i++) {
            if (cs[i].cmd == expt) {
                if (bl3 && rlt2) {//幸运抽奖（超级无线）定时到了，删除定时
                    cron.delete(cs[i].id)
					hasThisCron = true   //3/15 新加
                    break
                } else {
                    hasThisCron = true
                    break
                }
            }
        }

        //autMan里没有此变量的定时指令时
        if (!hasThisCron) {
            if (bl3 && rlt2) {//幸运抽奖（超级无线）定时
                dateStr = rlt2[0].toString()


        if (logswitch) {
        Debug("幸运抽奖（超级无线）定时：" + dateStr)
				}
				
				seconds = dateStr.split(":")
				secondStart = seconds[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "") // 提取秒并处理空格
        // 如果秒为空，设置为0
                if (secondStart == "") {
                    secondStart = "0"
			    }
				
				
				
				
                mins = dateStr.split(":")
                minuteStart = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (minuteStart == "") {
                    minuteStart = "0"
                }
                hours = mins[0].split(" ")
                hourStart = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (hourStart == "") {
                    hourStart = "0"
                }
                ymd = hours[0].split("-")
                yearStart = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                monthStart = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                dayStart = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                cn = secondStart + " " + minuteStart + " " + hourStart + " " + dayStart + " " + monthStart + " *"
                //添加定时指令


        if (logswitch) {
        Debug("幸运抽奖（超级无线）定时：" + cn)
				}
				if (notify_addcron) {
                notifyMasters("【JD未来活动定时pro】\n" + "活动时间：" + rlt2[0] + "\n活动类型：幸运抽奖（超级无线）定时" + "\n自动定时：" + cn + "\n定时内容：" + expt)
                }
				id = cron.add({
                    cron: cn,
                    cmd: expt,
                    toSelf: true,
                    toOthers: toOthers,
                    memo: memo,
                })

        if (logswitch) {
        Debug("定时指令ID：" + id)
				}
            } 
        } else {
			
        if (notify_repeat_cron) {
        notifyMasters(expt + "\n--------------\n定时指令已存在，忽略")

        if (logswitch) {
        Debug("已存在此定时指令")
				}             
				}
        }
    }


         //9R幸运抽奖
		if (/店铺抽奖（超级无线/.test(obj.message) && /未开始/.test(obj.message) && /京豆|E卡|e卡|红包|积分/.test(obj.message)) {//9R幸运抽奖
    	

		
		//检查日志内容是否有未开始
        var pattern = /未开始/;
        var pattern2 = /M签到有礼/;
        var patternM = /活动已结束/;
        var pattern3 = /店铺抽奖（超级无线/;
        
        var bl = pattern.test(obj.message);
        var bl2 = pattern2.test(obj.message) && !patternM.test(obj.message);
        var bl3 = pattern3.test(obj.message) && pattern.test(obj.message);
        if (logswitch) {
        Debug("是否为幸运抽奖（超级无线）：" + bl3);
				}
        
        //匹配2023-09-28 00:00:00至2023-10-30 18:00:00字样
        var datePattern = /\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?[ ]?[至|-][ ]?\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配结果，数组
        var rlt = datePattern.exec(obj.message)
        //匹配开奖时间2023-09-28 00:00:00字样
        var datePattern2 = /开始时间：\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配开奖时间结果，数组
        var rlt2 = datePattern2.exec(obj.message)
        //去除“开奖时间:”字样
		
		
		if (rlt2) {
        // 格式化开始时间
		var timeString = rlt2[0].replace(/开始时间：/g, "") + ':00';
		var parts = timeString.split(' ')
        var year = parseInt(parts[0].slice(0, 4))
        var month = parseInt(parts[0].slice(5, 7)) - 1 // 月份从1开始计数
        var day = parseInt(parts[0].slice(8, 10))
        var hours = parseInt(parts[1].slice(0, 2))
        var minutes = parseInt(parts[1].slice(3, 5))
        var seconds = parseInt(parts[1].slice(6))
       // 创建一个新的Date对象，然后减去3秒
        var originalDate = new Date(year, month, day, hours, minutes, seconds)
        var newDate = new Date(originalDate.getTime() - 3000) // 3000毫秒等于3秒
        var dateString = newDate.getFullYear() + '-' + (newDate.getMonth() + 1).toString().padStart(2, '0') + '-' + newDate.getDate().toString().padStart(2, '0') + ' ' + newDate.getHours().toString().padStart(2, '0') + ':' + newDate.getMinutes().toString().padStart(2, '0') + ':' + newDate.getSeconds().toString().padStart(2, '0')
        // 将新的时间添加回rlt2[0]
        rlt2[0] = dateString;
          // 然后你可以像之前那样使用rlt2[0]


        if (logswitch) {
        Debug(rlt2[0]);
				}
        }

        //备注
        var memo
        if (bl3 && rlt2) {//幸运抽奖（超级无线）
            memo = rlt2[0]//备注
        } else if (rlt) {//未来活动或签到有礼
            memo = rlt[0]//备注
        }

        if (logswitch) {
        Debug("备注时间：" + memo)
				}

        //匹配变量
        var exptPattern = /[a-zA-Z]+:\/\/[^\s]*wxDrawActivity[^\s]*/
        //匹配结果，字符串
        var expt = exptPattern.exec(obj.message).toString()
        if (logswitch) {
        Debug("变量：" + expt)
				}



        //检查变量是否重复
        var hasThisCron = false
        var cs = cron.get()
        for (i = 0; i < cs.length; i++) {
            if (cs[i].cmd == expt) {
                if (bl3 && rlt2) {//店铺抽奖（超级无线）定时到了，删除定时
                    cron.delete(cs[i].id)
					hasThisCron = true   //3/15 新加
                    break
                } else {
                    hasThisCron = true
                    break
                }
            }
        }

        //autMan里没有此变量的定时指令时
        if (!hasThisCron) {
            if (bl3 && rlt2) {//幸运抽奖（超级无线）定时
                dateStr = rlt2[0].toString()          
        if (logswitch) {
        Debug("店铺抽奖（超级无线）定时：" + dateStr)
				}
				
				seconds = dateStr.split(":")
				secondStart = seconds[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "") // 提取秒并处理空格
        // 如果秒为空，设置为0
                if (secondStart == "") {
                    secondStart = "0"
			    }
				
				
				
				
                mins = dateStr.split(":")
                minuteStart = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (minuteStart == "") {
                    minuteStart = "0"
                }
                hours = mins[0].split(" ")
                hourStart = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (hourStart == "") {
                    hourStart = "0"
                }
                ymd = hours[0].split("-")
                yearStart = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                monthStart = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                dayStart = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                cn = secondStart + " " + minuteStart + " " + hourStart + " " + dayStart + " " + monthStart + " *"
                //添加定时指令

        if (logswitch) {
        Debug("店铺抽奖（超级无线）定时：" + cn)
				}
				if (notify_addcron) {
                notifyMasters("【JD未来活动定时pro】\n" + "活动时间：" + rlt2[0] + "\n活动类型：店铺抽奖（超级无线）定时" + "\n自动定时：" + cn + "\n定时内容：" + expt)
                }
				id = cron.add({
                    cron: cn,
                    cmd: expt,
                    toSelf: true,
                    toOthers: toOthers,
                    memo: memo,
                })

        if (logswitch) {
        Debug("定时指令ID：" + id)
				}
				
            } 
        } else {
        if (notify_repeat_cron) {
        notifyMasters(expt + "\n--------------\n定时指令已存在，忽略")

        if (logswitch) {
        Debug("已存在此定时指令")
				}
				}
        }
    }


         //9R每日抢
		if (/每日抢好礼（超级无线）/.test(obj.message) && /未到开抢时间/.test(obj.message)) {//9R每日抢
    
        function getTodayDateString() {
        // 在这里实现获取当前日期的逻辑，例如：
        // 注意，这里假设你使用的是ISO 8601日期格式，如果是其他格式，请相应调整
        var today = new Date();
        return today.toISOString().split('T')[0];}

        if (logswitch) {
        console.log("条件满足");
        Debug("条件满足");
				}
		
		//检查日志内容是否有未开始
        var pattern = /未到开抢时间/;
        var pattern2 = /M签到有礼/;
        var patternM = /活动已结束/;
        var pattern3 = /每日抢好礼（超级无线）/;
        
        var bl = pattern.test(obj.message);
        var bl2 = pattern2.test(obj.message) && !patternM.test(obj.message);
        var bl3 = pattern3.test(obj.message) && pattern.test(obj.message);

        if (logswitch) {
        Debug("是否为每日抢好礼（超级无线）：" + bl3);
				}
        
        //匹配2023-09-28 00:00:00至2023-10-30 18:00:00字样
        var datePattern = /\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?[ ]?[至|-][ ]?\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配结果，数组
        var rlt = datePattern.exec(obj.message)
        //匹配开奖时间2023-09-28 00:00:00字样
        var datePattern2 = /开始时间：\d{2}:\d{2}/
        //匹配开奖时间结果，数组
        var rlt2 = datePattern2.exec(obj.message)
        //去除“开奖时间:”字样
              	 
		if (rlt2) {
        // 获取今天的日期
        var todayDate = getTodayDateString();
        // 格式化开始时间
        rlt2[0] = todayDate + ' ' + rlt2[0].replace(/开始时间：/g, "") + ':00';
		var timeString = rlt2[0]	
		var parts = timeString.split(' ')
        var year = parseInt(parts[0].slice(0, 4))
        var month = parseInt(parts[0].slice(5, 7)) - 1 // 月份从1开始计数
        var day = parseInt(parts[0].slice(8, 10))
        var hours = parseInt(parts[1].slice(0, 2))
        var minutes = parseInt(parts[1].slice(3, 5))
        var seconds = parseInt(parts[1].slice(6))
       // 创建一个新的Date对象，然后减去3秒
        var originalDate = new Date(year, month, day, hours, minutes, seconds)
		var meiriqiang_early_time = bucketGet("zq8884","meiriqiang_early_time")
        var newDate = new Date(originalDate.getTime() - meiriqiang_early_time) 
        var dateString = newDate.getFullYear() + '-' + (newDate.getMonth() + 1).toString().padStart(2, '0') + '-' + newDate.getDate().toString().padStart(2, '0') + ' ' + newDate.getHours().toString().padStart(2, '0') + ':' + newDate.getMinutes().toString().padStart(2, '0') + ':' + newDate.getSeconds().toString().padStart(2, '0')
        // 将新的时间添加回rlt2[0]
        rlt2[0] = dateString;
          // 然后你可以像之前那样使用rlt2[0]

        if (logswitch) {
        Debug(rlt2[0]);
				}
				
        }

        //备注
        var memo
        if (bl3 && rlt2) {//每日抢好礼（超级无线）
            memo = rlt2[0]//备注
        } else if (rlt) {//未来活动或签到有礼
            memo = rlt[0]//备注
        }
		

        if (logswitch) {
        Debug("备注时间：" + memo)
				}

        //匹配变量
        var exptPattern = /[a-zA-Z]+:\/\/[^\s]*activityType=(10022)[^\s]*/
        //匹配结果，字符串
        var expt = exptPattern.exec(obj.message).toString()
		
 
        if (logswitch) {
        Debug("变量：" + expt)
				}

        //签到有礼
        // if (bl2) {
        //     //从变量expt中获取变量值
        //     newMsg = expt.split("=\"")[1].replace(/\"/g, "")
        //     if (/^http/.test(newMsg)) {
        //         Debug("签到有礼变量：" + newMsg)
        //         autMan.Session(newMsg)
        //     }
        // }

        //检查变量是否重复
        var hasThisCron = false
        var cs = cron.get()
        for (i = 0; i < cs.length; i++) {
            if (cs[i].cmd == expt) {
                if (bl3 && rlt2) {//每日抢好礼（超级无线）
                    cron.delete(cs[i].id)
					hasThisCron = true   //3/15 新加
                    break
                } else {
                    hasThisCron = true
                    break
                }
            }
        }

        //autMan里没有此变量的定时指令时
        if (!hasThisCron) {
            if (bl3 && rlt2) {//每日抢好礼（超级无线）
                dateStr = rlt2[0].toString()
				
        if (logswitch) {
        Debug("每日抢好礼（超级无线）定时：" + dateStr)
				}
				
				seconds = dateStr.split(":")
				secondStart = seconds[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "") // 提取秒并处理空格
                // 如果秒为空，设置为0
                if (secondStart == "") {
                    secondStart = "0"
			    }
				
			
                mins = dateStr.split(":")
                minuteStart = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (minuteStart == "") {
                    minuteStart = "0"
                }
                hours = mins[0].split(" ")
                hourStart = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (hourStart == "") {
                    hourStart = "0"
                }
                ymd = hours[0].split("-")
                yearStart = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                monthStart = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                dayStart = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
//
				cn = secondStart + " " + minuteStart + " " + hourStart + " " + dayStart + " " + monthStart + " *"
                //添加定时指令
               
        if (logswitch) {
        Debug("每日抢好礼（超级无线）：" + cn)
				}
				if (notify_addcron) {
                notifyMasters("【JD未来活动定时pro】\n" + "活动时间：" + rlt2[0] + "\n活动类型：每日抢好礼（超级无线）定时" + "\n自动定时：" + cn + "\n定时内容：" + expt)
                }
				id = cron.add({
                    cron: cn,
                    cmd: expt,
                    toSelf: true,
                    toOthers: toOthers,
                    memo: memo,
                })
               
        if (logswitch) {
        Debug("定时指令ID：" + id)
				}
				
            } 
        } else {
        if (notify_repeat_cron) {
        notifyMasters(expt + "\n--------------\n定时指令已存在，忽略")

        if (logswitch) {
        Debug("已存在此定时指令")
				}             
				}
				
        }
    }


		

        if (/签到（超级无线V2）/.test(obj.message)) {//签到（超级无线V2）
        //if (/签到（超级无线V2）/.test(obj.message) && /京豆|E卡|e卡|红包/.test(obj.message)) {//签到（超级无线V2）
  
			
      
        if (logswitch) {
        console.log("条件满足");
		Debug("条件满足")
				}
		
		//检查日志内容是否有未开始
        var pattern = /未开始/;
        var pattern2 = /签到（超级无线V2）/;
        var patternM = /活动已结束/;
        var pattern3 = /幸运抽奖（超级无线）/;
        
        var bl = pattern.test(obj.message);
        var bl2 = pattern2.test(obj.message) && !patternM.test(obj.message);
        var bl3 = pattern3.test(obj.message);
        
		
        if (logswitch) {
        Debug("是否为幸运抽奖（超级无线）：" + bl3);
				}
		
        // 正则表达式，匹配开始时间和结束时间
        var startTimePattern = /【开始时间】(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})?)/;
        var endTimePattern = /【结束时间】(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})?)/;

        // 使用match方法提取开始时间和结束时间
        var startTimeMatch = startTimePattern.exec(obj.message);
        var endTimeMatch = endTimePattern.exec(obj.message);

        // 确保至少有一个匹配
        if (startTimeMatch && endTimeMatch) {
        // 提取开始时间和结束时间，并添加秒
        var startTime = startTimeMatch[1] + ":00";
        var endTime = endTimeMatch[1] + ":59";

        // 去除“开始时间”和“结束时间”
        startTime = startTime.replace("【开始时间】", "");
        endTime = endTime.replace("【结束时间】", "");

        // 连接开始时间和结束时间
        var combotime = startTime + "～" + endTime;
		var rlt = [combotime]        //数组重新格式化，将整体零散数组整合成一个元素，否则memo读取的是第一个数字“2”

        // 输出结果，保留完整的时间格式


        if (logswitch) {
        console.log(rlt); // 输出：2024-04-01 00:00:00～2024-04-30 23:59:00
				}
        } else {


        if (logswitch) {
        console.log("未找到开始时间和结束时间");
				}
        }
		

        //匹配开奖时间2023-09-28 00:00:00字样
        var datePattern2 = /开始时间：\d{4}\-\d{2}\-\d{2}[ ]?\d{2}:\d{2}(:\d{2})?/
        //匹配开奖时间结果，数组
        var rlt2 = datePattern2.exec(obj.message)
        //去除“开奖时间:”字样
        if (rlt2) {
            rlt2[0] = rlt2[0].replace(/开始时间：/g, "")
               
        if (logswitch) {
        Debug(rlt2[0])
				}
        }

        //备注
        var memo
        if (bl3 && rlt2) {//幸运抽奖（超级无线）
            memo = rlt2[0]//备注
        } else if (rlt) {//未来活动或签到有礼

            memo = rlt[0]//备注
        }
        

        if (logswitch) {
        Debug("备注时间：" + memo)
				}

        //匹配变量
        var exptPattern = /https:\/\/[A-Za-z0-9\-\._~:\/\?#\[\]@!$&'\*\+,%;\=]*interaction[A-Za-z0-9\-\._~:\/\?#\[\]@!$&'\*\+,%;\=]*/
        //匹配结果，字符串
        var expt = exptPattern.exec(obj.message).toString()

        if (logswitch) {
        Debug("变量：" + expt)
				}


        //签到有礼
        // if (bl2) {
        //     //从变量expt中获取变量值
        //     newMsg = expt.split("=\"")[1].replace(/\"/g, "")
        //     if (/^http/.test(newMsg)) {
        //         Debug("签到有礼变量：" + newMsg)
        //         autMan.Session(newMsg)
        //     }
        // }


        //检查变量是否重复
        var hasThisCron = false
        var cs = cron.get()
        for (i = 0; i < cs.length; i++) {
            if (cs[i].cmd == expt) {
                if (bl3 && rlt2) {//幸运抽奖（超级无线）定时
                    cron.delete(cs[i].id)
					hasThisCron = true   //3/15 新加
                    break
                } else {
                    hasThisCron = true
                    break
                }
            }
        }

        //autMan里没有此变量的定时指令时
        if (!hasThisCron) {
              if (rlt) {//未来活动或签到有礼
                dateStr = rlt[0].toString().split("～")[0]
                mins = dateStr.split(":")
                minuteStart = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (minuteStart == "") {
                    minuteStart = "0"
                }
                hours = mins[0].split(" ")
                hourStart = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (hourStart == "") {
                    hourStart = "0"
                }
                ymd = hours[0].split("-")
                yearStart = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                monthStart = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                dayStart = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                cn = minuteStart + " " + hourStart + " " + dayStart + " " + monthStart + " *"

                //获取结束时间
                dateStr = rlt.toString().split("～")[1]
                mins = dateStr.split(":")
                minuteEnd = mins[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (minuteEnd == "") {
                    minuteEnd = "0"
                }
                hours = mins[0].split(" ")
                hourEnd = hours[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                if (hourEnd == "") {
                    hourEnd = "0"
                }
                ymd = hours[0].split("-")
                yearEnd = ymd[0].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                monthEnd = ymd[1].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")
                dayEnd = ymd[2].replace(/(^\s*)|(\s*)/g, "").replace(/(^0*)/g, "")

                var actType = "\n活动类型：未来活动"
                if (bl2) {//签到有礼
				
				var sign_cron_time = bucketGet("zq8884","sign_cron_time");
                    //签到有礼定时
                    if (monthStart == monthEnd) {
                        //cn = "0 0,10 " + dayStart + "-" + dayEnd + " " + monthStart + " *"
			          cn = "0 " + sign_cron_time +  " " + dayStart + "-" + dayEnd + " " + monthStart + " *"		
                    } else {
                        if (parseInt(monthStart) > parseInt(monthEnd)) {//跨年
                            //cn = "0 0,10 1-31 " + monthStart + "," + monthEnd + " *"
							cn = "0 " + sign_cron_time + " 1-31 " + monthStart + "," + monthEnd + " *"
                        } else {
                            //cn = "0 0,10 1-31 " + monthStart + "-" + monthEnd + " *"        //10点补签
							cn = "0 " + sign_cron_time + " 1-31 " + monthStart + "-" + monthEnd + " *"
                        }
                    }
                    actType = "\n活动类型：签到（超级无线V2）"
                }

                //添加定时指令
                
				if (logswitch) {
                 Debug("定时：" + cn)
				}
				
                id = cron.add({
                    cron: cn,
                    cmd: expt,
                    toSelf: true,
                    toOthers: toOthers,
                    memo: memo,
                })
				if (notify_addcron) {
                notifyMasters("【JD未来活动定时pro】\n" + "活动时间：" + rlt[0] + actType + "\n自动定时：" + cn + "\n定时内容：" + expt)
                }     
        if (logswitch) {
        Debug("定时指令ID：" + id)
				}
				
            } else {//没有给出明确时间的未来活动
                let month, day;
                date = new Date();
                date.setTime(date.getTime() + 24 * 60 * 60 * 1000);
                month = date.getMonth() + 1;
                day = date.getDate();

                id = cron.add({
                    cron: "0 0 " + day + " " + month + " *",
                    cmd: expt,
                    toSelf: true,
                    toOthers: toOthers,
                    memo: memo,
                })
				if (notify_addcron) {
                notifyMasters("【JD未来活动定时pro】\n" + "活动时间：未知" + "\n自动定时：" + cn + "\n定时内容：" + expt)
                }
            }
        } 
		else {
        if (notify_repeat_cron) {
        notifyMasters(expt + "\n--------------\n定时指令已存在，忽略")

        if (logswitch) {
        Debug("已存在此定时指令")
				}             
				}
				
        }
    }
	

	
    // 定义匹配活动结束和奖励发完的正则表达式
       var activityEndPattern = /活动已结束|奖品已领光|垃圾或领完|垃圾活动|才能参与抽奖|已达到活动期间最大抽奖次数|没有豆子|奖品已(经)?发完|礼包已经不存在|签满([1-9]|[12][0-9]|3[01])天后不能再参加了/;
       var rewardsPattern = /\s*\d+天\s+.*(?:\d+份|已发完|\b0份\b)\s*|\s*\d+(?:积分|京豆)\s+\(总剩\s+\d+\s+日剩\s+\d+\)/gm;
       var endWithRewardsPattern = /\s*\d+天.*?\s*(\b0份|已发完).*$|\(总剩\s+0\s+日剩\s+0\)/;
       var exptPattern = /(export \S+="https?:\/\/[^\s"]+")|https?:\/\/(?!shop\.m\.jd\.com)[^\s"]+/;

       // 检查活动是否结束，若结束则删除定时任务
       if (activityEndPattern.test(obj.message)) {
           deleteSchedule();
       } else {
           // 匹配奖励信息并处理
           var matches = obj.message.match(rewardsPattern);
           if (matches) {
               var allMatchesAsString = matches.join('\n');
               if (logswitch) {
                   console.log("All Matches: \n" + allMatchesAsString);
               }

        // 判断最后两行是否满足条件
        var lines = allMatchesAsString.trim().split('\n').filter(line => line.trim() !== '');
        if (lines.length >= 2) {
            var [secondLastLine, lastLine] = [lines[lines.length - 2], lines[lines.length - 1]];
            if (logswitch) {
                console.log("Debug secondLastLine: " + secondLastLine);
                console.log("Debug lastLine: " + lastLine);
            }

            // 若满足条件则删除定时任务
            if (endWithRewardsPattern.test(secondLastLine) && endWithRewardsPattern.test(lastLine)) {
                if (logswitch) {
                    console.log("Both lines meet the conditions. Deleting schedule...");
                       }
                       deleteSchedule();
                   }
               }
           }
       }
	
	
	  	
	   

			
	  // 删除定时任务函数
function deleteSchedule() {
    var exptMatch = exptPattern.exec(obj.message);
    if (exptMatch) {
        var expt = exptMatch[0];
        if (logswitch) {
            console.log("待删除的变量为: " + expt);
        }

        var cs = cron.get();
        for (var i = 0; i < cs.length; i++) {
            if (cs[i].cmd === expt) {
                var id = cs[i].id;
                if (logswitch) {
                    console.log("查询到任务ID: " + id);
                    console.log("待删除的ID为: " + id);
                }

                cron.delete(id);
                if (bucketGet("zq8884", "notify_delete") === 'true') {
                    notifyMasters("【删除自动定时】\n" + expt);
                }
                break;
            }
        }
    }
}
	
	
	
	
	/*
	  	// 定义匹配特定结束短语的正则表达式
        var activityEndPattern = /活动已结束|奖品已领光|垃圾或领完|垃圾活动|才能参与抽奖|已达到活动期间最大抽奖次数|没有豆子|奖品已(经)?发完|礼包已经不存在|签满([1-9]|[12][0-9]|3[01])天后不能再参加了/;

	   if (activityEndPattern.test(obj.message)) {
		  
       deleteSchedule();
        }
				
		
		
      //最后一行奖励为已发完，删除定时
       var rewardsPattern = /\s*\d+天\s+.*(?:\d+份|已发完|\b0份\b)\s*|\s*\d+(?:积分|京豆)\s+\(总剩\s+\d+\s+日剩\s+\d+\)/gm;   //6/3改


       var matches = obj.message.match(rewardsPattern);
       var allMatchesAsString; // 我们将在这里存储所有匹配的结果作为一个字符串

       if (matches) {
           allMatchesAsString = matches.join('\n'); // 使用换行符连接所有匹配的结果，形成整体字符串


        if (logswitch) {
        console.log("All Matches: \n" + allMatchesAsString);
				}
       }

       // 新增逻辑：判断最后两行是否都满足条件
       if (allMatchesAsString) {
           var lines = allMatchesAsString.trim().split('\n').filter(line => line.trim() !== '');
           if (lines.length >= 2) {
               var secondLastLine = lines[lines.length - 2];
               var lastLine = lines[lines.length - 1];

               // 正则表达式匹配结束条件
               var endWithRewardsPattern = /\s*\d+天.*?\s*(\b0份|已发完).*$|\(总剩\s+0\s+日剩\s+0\)/;    

               // 输出调试信息


        if (logswitch) {
               console.log("Debug secondLastLine: " + secondLastLine);
               console.log("Debug lastLine: " + lastLine);
				}

               // 如果最后两行都满足结束条件的模式，则执行删除定时任务
               if (endWithRewardsPattern.test(secondLastLine) && endWithRewardsPattern.test(lastLine)) {


              if (logswitch) {
              console.log("Both the second last line and the last line meet the conditions. Deleting schedule...");
				}
                   deleteSchedule(); // 调用下面定义的删除定时任务函数
               }
           }
       }
	   

			
	  //删除定时任务函数
       function deleteSchedule() {
	   var exptPattern = /(export \S+="https?:\/\/[^\s"]+")|https?:\/\/(?!shop\.m\.jd\.com)[^\s"]+/        //6/6更新
	   var exptMatch = exptPattern.exec(obj.message);
       if (exptMatch) {
       var expt = exptMatch[0];


        if (logswitch) {
        Debug("待删除的变量为:"+expt)
				}
	   var hasThisCron = false
       var cs = cron.get();
        // 查找并删除匹配的定时任务
        for (i = 0; i < cs.length; i++) {
           if (cs[i].cmd == expt) {
			   

        if (logswitch) {
        Debug("查询到任务ID:" + cs[i].id)
				}
				
				var id = cs[i].id
				
        if (logswitch) {
        Debug("待删除的ID为:"+id)
				}
				
                cron.delete(cs[i].id)			
				var notify_delete = bucketGet("zq8884", "notify_delete");
                notify_delete = notify_delete === 'true'; // 将字符串转换为布尔值

                if (notify_delete) {
                    notifyMasters("【删除自动定时】\n" + expt)
                
				}
				
				
                break
                    }
                }   
            }
        }	
	
	
	
	*/
	
	
	
	
	
	
	
        //响应
    var j = {
        "status": "OK",
        "retcode": 0,
    }
    response(j)
	


}










