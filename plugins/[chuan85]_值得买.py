//[create_at: 2025-04-18 16:55:52]
//[author: chuan85]
//[title: 值得买]
//[language: es5]
//[class: 工具类]
//[service: 63579686]
//[disable: false]
//[admin: false]
//[rule: ^zdm$]
//[priority: 0]
//[open_source: false]
//[icon: https://www.smzdm.com/favicon.ico]
//[version: 1.0.0]
//[public: true]
//[price: 0.1]
//[description: 什么值得买3小时好价（TOP20），指令“zdm”] 
function main() {
    request({
        url: "https://suzhi.fun/api/post/list",
        headers: {
            "Content-Type": "application/json"
        },
        method: "POST",
        body: JSON.stringify({"s": "0002001"}),
        dataType: "json",
        timeOut: 10000 // 10秒超时
    }, function (error, response, header, body) {
        if (error || response.statusCode !== 200) {
            sendText("请求失败，请稍后再试。");
            return;
        }

        if (!body.data || !body.data.l) {
            sendText("没有找到价格信息。");
            return;
        }

        const items = Object.keys(body.data.l).slice(0, 20);
        let content = "";

        items.forEach((key, index) => {
            const t = body.data.l[key].t;
            const u = body.data.l[key].u;
            const ls = body.data.l[key].ls;
            content += `${index + 1}.${t}【${ls}】\n${u}\n\n`;
        });

        sendText(content);
    });
}

main();