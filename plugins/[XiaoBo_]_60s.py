//[create_at: 2025-10-24 09:14:18]
// [title: 60s]
// [author: XiaoBo_]
// [language: es5]
// [icon: https://img.icons8.com/fluency/96/news.png]
// [version: 1.1.2]
// [class: 新闻类]
// [platform: qq,qb,wx,tb,tg,web]
// [public: true]
// [price: 0.3]
// [service: 使用问题请联系邮箱：aboutnanbo@163.com  QQ群：753669173]
// [description: 📰 60秒早报插件<br><br>📋 每日60秒早报插件，获取当日最新资讯。支持图文和纯文字两种展示方式，每天早上7:30自动推送。<br><br>📝 使用命令：<br>• 早报 / 新闻 / 60秒 / 60s - 获取早报（根据配置显示图文或文字）<br>• 文字早报 / 文本早报 - 强制获取纯文字格式<br>• 图文早报 / 图片早报 - 强制获取图文格式<br><br>📊 数据来源：微信公众号：《每天100秒读懂世界》，官方权威数据，稳定实时。]

// [rule: ^(早报|新闻|60秒|60s)$]
// [rule: ^(文字早报|文本早报)$]
// [rule: ^(图文早报|图片早报)$]
// [rule: ^早报数据$]
// [cron: 30 7 * * *]
// [admin: false]
// [disable: false]
// [priority: 10]

// [param: {"required":true,"key":"60s.outputType","bool":true,"placeholder":"true","name":"图文模式","desc":"开启后默认以图片形式发送早报，关闭则发送纯文字"}]
// [param: {"required":false,"key":"60s.apiUrl","bool":false,"placeholder":"http://192.168.5.11:4399/v2/60s","name":"API地址","desc":"60秒早报API接口地址，默认使用官方接口"}]
// [param: {"required":false,"key":"60s.timeout","bool":false,"placeholder":"10000","name":"请求超时(毫秒)","desc":"API请求超时时间，单位毫秒，默认10000"}]
// [param:{"required":false,"key":"60s.push_groups","bool":false,"placeholder":"qqgroup:123,wxgroup:123,tggroup:-100123","name":"推送群","desc":"设置定时推送，格式：qqgroup:123,wxgroup:123,tggroup:-100123"}]



var API_URL = bucketGet("60s", "apiUrl") || "https://60s.aboutnb.com/v2/60s";
var OUTPUT_TYPE = bucketGet("60s", "outputType") !== "false";

function fetch60sNews() {
    var response = request({
        url: API_URL,
        dataType: "json"
    });
    return response.data;
}

function formatNewsText(newsData) {
    var text = "📰 每日60秒早报\n━━━━━━━━━━━━━━━\n";
    text += "📅 " + newsData.date + " " + newsData.day_of_week + "\n";
    text += "🌙 农历：" + newsData.lunar_date + "\n━━━━━━━━━━━━━━━\n\n";

    for (var i = 0; i < newsData.news.length; i++) {
        text += (i + 1) + ". " + newsData.news[i] + "\n\n";
    }

    text += "━━━━━━━━━━━━━━━\n☀️ " + newsData.tip + "\n";
    text += "━━━━━━━━━━━━━━━\n🔗 详情：" + newsData.link;
    return text;
}

function send60sNewsText() {
    sendText(formatNewsText(fetch60sNews()));
}

function send60sNewsImage() {
    sendImage(fetch60sNews().image);
}

var imType = ImType();
var content = GetContent().trim();

// 定时推送
if (imType == "fake") {
        // 处理推送群
        var pushGroups = bucketGet("60s", "push_groups")
        Debug(pushGroups)
        var pgs = pushGroups.split(",")
        var groups = []
        for (i = 0; i < pgs.length; i++) {
            groups[i] = {
                imType: pgs[i].slice(0, 2),
                groupCode: pgs[i].slice(8),
            }
        }
        for (var i = 0; i < groups.length; i++) {
            groups[i]["content"] = OUTPUT_TYPE ? image(fetch60sNews().image) : formatNewsText(fetch60sNews());
            push(groups[i])
        }

}else if (content == "早报" || content == "新闻" || content == "60秒" || content == "60s") {
    OUTPUT_TYPE ? send60sNewsImage() : send60sNewsText();
} else if (content == "文字早报" || content == "文本早报") {
    send60sNewsText();
} else if (content == "图文早报" || content == "图片早报") {
    send60sNewsImage();
} else if (content == "早报数据" && isAdmin()) {
    sendText(JSON.stringify(fetch60sNews(), null, 2));
}
