//[disable:false]
//[pin:true]
//[tile: 订阅源集合]要与文件名相同，也可以不加，上传aut云时会自动将文件名设置为此头注
//[rule: 订阅列表] 匹配规则，多个规则时向下依次写多个
//[rule: 订阅拉黑] 匹配规则，多个规则时向下依次写多个
//[rule: 一键订阅] 匹配规则，多个规则时向下依次写多个
//[rule: 一键更新] 匹配规则，多个规则时向下依次写多个
//[rule: 插件搜索] 匹配规则，多个规则时向下依次写多个
//[rule: 插件下载] 匹配规则，多个规则时向下依次写多个
//[rule: 云动态] 匹配规则，多个规则时向下依次写多个
//[cron: */15 * * * *]
//[author: specter]作者,可以自定义，不定义的话，上传时会增加为aut云注册的用户名,收费插件一定要填写aut云账号
//[version: 1.3.6] 版本格式：1.0.0，不定义的话，上传时会自动增加此头注，默认为1.0.0 
//[class: 工具类]建议从工具类、查询类、娱乐类、餐饮类、影音类、生活类、图片类、游戏类等中选择，也可自定义
//[platform: qq,wx,tg]适用的平台 qq\wx\tg\wxmp之间选择，中间用英文逗号隔开
//[public: true] 是否公开发布？值为true 或 false，不定义的话，上传aut云时会自动设置为true
//[admin: true] 是否为管理员指令
//[price: 0.3] 上架价格
//[service: 2607401955]售后联系方式，service不完整，将不会审核上架
//[description: 指令：订阅列表，订阅拉黑，一键订阅，一键更新，插件搜索，插件下载，云动态。<br>云动态默认推送所有订阅源的更新和新增和下架，根据插件执行定时推送，也可以配参筛选。根据插件执行定时可以自动更新所有云市场插件，配参开启。插件权限需要cloud数据和autMan数据。更新日志（新增云动态仅推送已安装的插件动态，或者仅推送已订阅源动态，配参开启）] 
//[priority: 9999] 优先级，数字越大表示优先级越高
//[param: {"required":false,"key":"subscription.onlyInstall","bool":true,"placeholder":"云动态是否开启仅推送已安装的插件动态","name":"仅推送已安装","desc":"云动态是否开启仅推送已安装的插件动态"}]
//[param: {"required":false,"key":"subscription.onlySub","bool":true,"placeholder":"云动态是否开启仅推送已订阅源的动态","name":"仅推送已订阅","desc":"云动态是否开启仅推送已订阅源的动态"}]
//[param: {"required":false,"key":"subscription.offPush","bool":true,"placeholder":"云动态是否开启下架插件推送","name":"下架推送","desc":"云动态是否开启下架插件推送"}]
//[param: {"required":false,"key":"subscription.offCloud","bool":true,"placeholder":"关闭云动态自动推送","name":"关闭云动态自动推送","desc":"关闭云动态自动推送，默认云动态根据插件定时推送，勾选此项则不推送"}]
//[param: {"required":false,"key":"subscription.offPic","bool":true,"placeholder":"关闭云动态的图片显示","name":"关闭云动态的图片显示","desc":"关闭云动态的图片显示，默认云动态显示图片，勾选此项则只显示文字"}]
//[param: {"required":false,"key":"subscription.AutoUpdate","bool":true,"placeholder":"开启自动更新订阅市场的云插件","name":"自动更新","desc":"开启自动更新订阅市场的云插件"}]
//[param: {"required":false,"key":"subscription.PluginBlacklist","bool":false,"placeholder":"自动更新插件黑名单","name":"自动更新插件黑名单","desc":"自动更新插件黑名单，写在这里的插件将不会自动更新。填写订阅源:插件名，多个用英文逗号隔开。例如：specter:插件名,specter:插件名"}]

const tongzi = 'subscription'
const username = bucketGet("cloud", "username")
const password = bucketGet("cloud", "password")
const port = bucketGet("autMan", "port") || 8080
const PublicAddress = bucketGet(tongzi, 'PublicAddress')
const public = PublicAddress ? PublicAddress : bucketGet("autMan", "host_name")
const platform = GetImType()

var GetContent = GetContent()
let myUrl = public ? public : `http://127.0.0.1:${port}`
let Cookie = ''
var subList = []
var contactObj = {}

function main() {
    if (GetContent == '插件搜索') {
        search()
    } else if (GetContent == '插件下载') {
        PluginDownload()
    } else if (GetContent == '一键订阅') {
        Onekey()
    } else if (GetContent == '一键更新') {
        updatePlugins()
    } else if (GetContent == '订阅列表') {
        showList()
    } else if (GetContent == '订阅拉黑') {
        block()
    } else {
        if (!GetContent) {
            sleep(getRandomNumber())
        }
        if (bucketGet(tongzi, "offCloud") != 'true' || GetContent === '云动态') {
            getColud()
        }
        if (GetContent == '云动态') {
            return
        }
        if (bucketGet(tongzi, "AutoUpdate") == 'true') {
            updatePlugins()
        }
    }
}

function PluginDownload() {
    if (!checkUrl()) {
        sendText('请输入你的autman公网地址和端口，例:http://31.29.116.33:8200')
        var msg = ShuRu()
        if (msg) {
            bucketSet(tongzi, "PublicAddress", msg);
            if (msg[msg.length - 1] == '/') {
                msg = msg.substring(0, msg.length - 1);
            }
            myUrl = msg
        }
    }
    if (!getCookie()) {
        return
    }

    sendText('请输入订阅源名称')
    var msg = ShuRu()
    if (msg) {
        if (msg === '官方') {
            msg = ''
        }
        let plugins = getPlugins(msg)
        if (plugins.length > 0) {
            let str = plugins.map((item, index) => `${index + 1}：${item.title}\n${item.price ? '💰价格：' + item.price + '元' : '🎁免费'}`).join('\n')
            let Aut = getAut(msg)
            sendText(`获取到${plugins.length}个插件\n${str}`)
            sendText(`当前订阅源的aut余额：${Aut}元\n请输入要下载的插件名称`)
            var pluginName = ShuRu()
            if (pluginName) {
                let plugin = plugins.find(item => item.title === pluginName)
                if (plugin) {
                    plugin.VersionChange = `0=>${plugin.version}`
                    updateLocalPlugin(plugin)
                    sendText(`插件描述：${plugin.description}`)
                } else {
                    sendText('没有找到该插件')
                }
            }
        } else {
            sendText('该订阅源异常')
        }
    }
}

function getAut(params) {
    let body = request({
        "url": `${myUrl}/js/aut?tab=${params}`,
        "method": "post",
        "headers": {
            Cookie
        },
        "timeOut": 30000,
    })
    // Debug(body)
    if (body.includes('200')) {
        let res = JSON.parse(body)
        if (res.code === 200) {
            return res.data.aut / 100
        } else {
            return '获取失败'
        }
    } else {
        return '获取失败'
    }
}

function getPlugins(params, page = 1, accumulatedPlugins = []) {
    let body = request({
        "url": `${myUrl}/js/cloud?tab=${params}&keyword=&class=&page=${page}&pageSize=100&orderby=`,
        "method": "get",
        "timeOut": 30000,
    });

    if (body.includes('200')) {
        let res = JSON.parse(body);
        if (res.code === 200) {
            let plugins = res.data.data;
            let total = res.data.total;
            let pageSize = 100;

            if (plugins) {
                let mappedPlugins = plugins.map(item => {
                    return {
                        "title": item.title,
                        'language': item.language,
                        "author": item.author,
                        "version": item.version,
                        "price": item.price,
                        "description": item.description
                    }
                });
                accumulatedPlugins = accumulatedPlugins.concat(mappedPlugins);

                // If there are more pages, recursively fetch the next page
                if (page * pageSize < total) {
                    return getPlugins(params, page + 1, accumulatedPlugins);
                } else {
                    return accumulatedPlugins;
                }
            } else {
                return accumulatedPlugins;
            }
        }
    } else {
        return accumulatedPlugins;
    }
}

function updatePlugins() {
    if (!checkUrl()) {
        sendText('请输入你的autman公网地址和端口，例:http://31.29.116.33:8200')
        var msg = ShuRu()
        if (msg) {
            bucketSet(tongzi, "PublicAddress", msg);
            if (msg[msg.length - 1] == '/') {
                msg = msg.substring(0, msg.length - 1);
            }
            myUrl = msg
        }
    }
    if (!getCookie()) {
        return
    }

    let LocalPlugin = getLocalPlugin()
    if (LocalPlugin.length > 0) {
        Debug(JSON.stringify(LocalPlugin))
        let data = getCloudVersion(LocalPlugin)
        if (data.length > 0 && GetContent == '一键更新') {
            let choose = []

            let str = data.map((item, index) => `${index + 1}：订阅名称：${item.author}\n     插件名称：${item.title}\n     版本变化：${item.VersionChange}`)
            str.unshift(`请选择要更新的插件：\n0：全部`)
            str.push(`\n选择其中几个请用英文逗号,隔开，如：1,3,5`)
            sendChunks(str)
            var msg = ShuRu()

            if (msg === "0") {
                choose = data;
            } else if (msg) {
                msg = msg.split(',');
                choose = msg.map(item => data[parseInt(item) - 1])
            } else {
                return
            }

            if (choose.length > 0) {
                let updateArr = ArraySorting(choose)
                updateArr.forEach(item => {
                    updateLocalPlugin(item)
                })
            }
        } else if (data.length > 0) {
            let updateArr = ArraySorting(data)
            updateArr.forEach(item => {
                updateLocalPlugin(item)
            })
        } else {
            sendText('🌻全部插件均为最新版本')
        }
    } else {
        sendText('没有找到本地插件')
    }
}

//获取500-6500之间的随机数
function getRandomNumber() {
    return Math.floor(Math.random() * (6500 - 500 + 1)) + 500;
}

function ArraySorting(arr) {
    // 找到符合条件的项
    let targetIndex = arr.findIndex(item => item.author === 'specter' && item.title === '订阅源集合');

    // 如果找到符合条件的项
    if (targetIndex !== -1) {
        // 移除该项并将其添加到数组末尾
        arr.push(arr.splice(targetIndex, 1)[0]);
    }
    return arr;
}

function updateLocalPlugin(item) {
    if (!GetContent) {
        sleep(getRandomNumber())
    }
    item.tab = item.author === 'hdbjlizhe' ? '' : item.author

    let body = request({
        "url": `${myUrl}/js/install?language=${item.language}&title=${encodeURIComponent(item.title)}&author=${item.author}&tab=${item.tab}`,
        headers: {
            Cookie
        },
        "method": "post",
        "timeOut": 60000,
    })
    // Debug(body)
    if (!body) {
        notifyMasters(body)
        notifyMasters(`订阅名称：${item.author}\n插件名称：【${item.title}】\n更新结果：失败❌\n失败原因：检查autMan后台-插件市场-订阅市场源，是否订阅了${item.author}`)
        return
    }
    let res = JSON.parse(body)
    item.author = item.author === 'hdbjlizhe' ? '官方' : item.author

    if (res.code === 200) {
        if (GetContent == '一键更新') {
            sendText(`订阅名称：${item.author}\n插件名称：【${item.title}】\n版号变化：${item.VersionChange}\n更新结果：成功✅`)
        } else {
            notifyMasters(`订阅名称：${item.author}\n插件名称：【${item.title}】\n版号变化：${item.VersionChange}\n更新结果：成功✅`)
        }
    } else {
        Debug(body)
        notifyMasters(`订阅名称：${item.author}\n插件名称：【${item.title}】\n更新结果：失败❌：${body}`)
    }
}

function getCloudVersion(LocalPlugin) {
    let body = request({
        "url": `http://47.99.156.63:55555/versions`,
        "method": "post",
        body: LocalPlugin,
        "timeOut": 30000,
    })
    // Debug(body)
    let res = JSON.parse(body)
    if (res.code === 200) {
        return res.data
    } else {
        return []
    }
}

function getLocalPlugin() {
    let body = request({
        "url": `${myUrl}/js/details`,
        headers: {
            Cookie
        },
        "method": "get",
        "timeOut": 30000,
    })
    // Debug(body)
    let res = JSON.parse(body)

    let blacklist = bucketGet(tongzi, "PluginBlacklist") || ''
    blacklist = blacklist.split(',').map(item => item.trim())
    Debug(blacklist)

    if (res.code === 200) {
        return res.data
            .filter(item => {
                const pluginPathWithoutExtension = item.plugin_path.replace(/\.[^/.]+$/, "");
                return pluginPathWithoutExtension.includes(':') &&
                    !blacklist.includes(pluginPathWithoutExtension) &&
                    !blacklist.includes(item.plugin_path);
            })
            .map(({ author, language, title, version }) => ({
                author,
                language,
                title,
                version
            }));
    }

    return [];
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

function search() {
    sendText('请输入搜索的插件名称')
    var msg = ShuRu()
    let str = []
    if (msg) {
        let data = searchPlugins(msg)
        if (data) {
            let sortData = sortPrice(data)
            getContactObj()
            sortData.forEach(([key, value]) => {
                const element = value;
                str.push(`订阅源：${key || '官方'}`)

                let contactInfo = '';
                if (contactObj[key]) {
                    const contact = contactObj[key] || {}
                    const contactParts = [
                        contact.ads ? `📢公告：${contact.ads}` : '',
                        contact.contact_admin ? `\n📱管理员联系方式：${contact.contact_admin}` : '',
                        contact.contact_bot ? `\n📱机器人联系方式：${contact.contact_bot}` : ''
                    ];
                    contactInfo = contactParts.filter(Boolean).join('');
                    str.push(contactInfo)
                }

                element.forEach((item, index) => {
                    str.push(`【${index + 1}】名称：${item.title}`)
                    str.push(`    版本：${item.version || '暂无'}`)
                    str.push(`    价格：${item.price || '🎁免费'}`)
                    str.push(`    描述：${optimizeText(item.description) || '暂无'}`)
                    str.push(``)
                })
                str.push(`--------------------------`)
            });
            sendChunks(str)
        } else {
            sendText('没有搜索结果')
        }
    }
}

function sortPrice(data) {
    // 1. 对每个键对应的数组内部按价格排序
    Object.keys(data).forEach(key => {
        data[key].sort((a, b) => a.price - b.price);
    });

    // 2. 对整个对象按照每个数组中最小价格排序
    const sortedEntries = Object.entries(data).sort((a, b) => {
        const minPriceA = Math.min(...a[1].map(item => item.price));
        const minPriceB = Math.min(...b[1].map(item => item.price));
        return minPriceA - minPriceB;
    });

    // 3. 返回排序后的键值对数组，而非普通对象
    return sortedEntries;
}

function optimizeText(text) {
    const offPic = bucketGet(tongzi, 'offPic')
    if (offPic == 'true' || offPic == true) {
        return text
    }

    let result = '';
    let lastIndex = 0;

    if (!text) {
        return result;
    }

    // 替换换行标签
    text = text.replace(/<\/?br\s*\/?>/gi, '\n');

    // 处理 img 标签
    const imgRegex = /<img\s+(?:[^>]*?\s+)?src="([^"]*)"(?:\s+alt="[^"]*")?[^>]*>/gi;
    let match;

    while ((match = imgRegex.exec(text)) !== null) {
        // 添加 img 标签之前的文本
        result += text.slice(lastIndex, match.index);

        // 执行 image 函数并添加结果
        const src = match[1];
        result += image(src);

        lastIndex = imgRegex.lastIndex;
    }

    // 添加剩余的文本
    result += text.slice(lastIndex);

    return result;
}

function splitArrayIntoChunks(array) {
    const option = { "qq": 8000, "wb": 6000, "wx": 4000 };
    const maxLength = option[platform] || 4000;

    let results = [];
    let currentChunk = [];
    let currentLength = 0;

    for (let item of array) {
        const itemLength = item.length;

        if (currentLength + itemLength <= maxLength) {
            currentChunk.push(item);
            currentLength += itemLength;
        } else {
            if (currentChunk.length > 0) {
                results.push(currentChunk);
            }
            currentChunk = [item];
            currentLength = itemLength;
        }
    }

    if (currentChunk.length > 0) {
        results.push(currentChunk);
    }

    return results;
}

function sendChunks(array) {
    let chunks = splitArrayIntoChunks(array)
    chunks.forEach(item => {
        let sendStatus = sendText(item.join('\n'))
        Debug(sendStatus + '发送状态')
        if (sendStatus == "<nil>" || sendStatus == "") {
            Debug('发送失败')
            const replacedArray = item.map(text => text.replace(/\[CQ:image,file=([^\]]+)\]/g, '$1'));
            sendText(replacedArray.join('\n'))
        }
        sleep(1000)
    })
}

function sendChunksAdmin(array) {
    let chunks = splitArrayIntoChunks(array)
    chunks.forEach(item => {
        let sendStatus = notifyMasters(item.join('\n'))
        Debug(sendStatus + '发送状态')
        if (sendStatus == "<nil>") {
            const replacedArray = item.map(text => text.replace(/\[CQ:image,file=([^\]]+)\]/g, '$1'));
            notifyMasters(replacedArray.join('\n'))
        }
        sleep(1000)
    })
}

function block() {
    getSubList()
    let black = bucketGet(tongzi, "Blacklist") || [];
    let sub = subList.map(item => item.source)
    let str = sub.map((item, index) => {
        let str = `${index + 1}：${item}`
        if (black.includes(item)) {
            str += '(已拉黑)'
        }
        return str
    })
    str.unshift(`请选择要拉黑的订阅源：\n0：全部`)
    str.push(`选择其中几个请用英文逗号,隔开，如：1,3,5`)
    sendText(str.join('\n'))
    var msg = ShuRu()
    let choose = []
    if (msg === "0") {
        choose = sub;
    } else if (msg) {
        msg = msg.split(',');
        choose = msg.map(item => sub[parseInt(item) - 1])
        black = Array.isArray(black) ? black : black.split(',');
        black = [...new Set(black.concat(choose))];
        bucketSet(tongzi, "Blacklist", black);
        sendText('已拉黑' + choose.join('，'))
    } else {
        return
    }
}

function Onekey() {
    if (!checkUrl()) {
        sendText('请输入你的autman公网地址和端口，例:http://31.29.116.33:8200')
        var msg = ShuRu()
        if (msg) {
            bucketSet(tongzi, "PublicAddress", msg);
            if (msg[msg.length - 1] == '/') {
                msg = msg.substring(0, msg.length - 1);
            }
            myUrl = msg
        }
    }
    if (!getCookie()) {
        return
    }
    getSubList()
    let sub = subList.filter(item => item.online).map(item => item.source)
    let alreadySub = getSubscription()
    let notSub = sub.filter(item => alreadySub.indexOf(item) === -1)

    let black = ObtainBlacklist()
    notSub = notSub.filter(item => black.indexOf(item) === -1)

    if (notSub.length === 0) {
        sendText('所有订阅源都已订阅')
        return
    } else {
        let str = notSub.map((item, index) => `${index + 1}：${item}`)
        str.unshift(`请选择要订阅的未订阅源：\n0：全部`)
        str.push(`选择其中几个请用英文逗号,隔开，如：1,3,5`)
        sendText(str.join('\n'))
        var msg = ShuRu()
        let choose = []
        if (msg === "0") {
            choose = notSub;
        } else if (msg) {
            msg = msg.split(',');
            choose = msg.map(item => notSub[parseInt(item) - 1])
        } else {
            return
        }
        if (choose.length !== 0) {
            Debug(choose)
            goToSub(choose)
        }
    }
}

function ObtainBlacklist() {
    let black = bucketGet(tongzi, "Blacklist");
    if (typeof black !== 'string' || black.trim() === '') {
        black = [];
    } else {
        black = black.split(',').map(item => item.trim()).filter(item => item !== ''); // 过滤掉空字符串
    }
    return black;
}

function showList() {
    getSubList();
    const str = subList.map((item, index) => {
        const { source, online, contact, title } = item;
        const statusIndicator = online ? '' : '（❌离线）';

        let contactInfo = '';
        if (contact) {
            const contactParts = [
                contact.ads ? `\n📢公告：${contact.ads}` : '',
                contact.contact_admin ? `\n📱管理员联系方式：${contact.contact_admin}` : '',
                contact.contact_bot ? `\n📱机器人联系方式：${contact.contact_bot}` : ''
            ];
            contactInfo = contactParts.filter(Boolean).join('');
        }
        // Debug(contactInfo)
        return `📰${index + 1}：${source}${statusIndicator}${contactInfo}\n📜插件：【${title.join('，')}】\n`;
    });

    sendChunks(str);
}

function checkUrl() {
    const urls = [`http://127.0.0.1:${port}`, public, `http://192.168.0.1:${port}`,];
    for (let url of urls) {
        Debug(url)
        let body = request({
            "url": `${url}/login`,
            "method": "post",
        });
        // Debug(body);
        if (body) {
            myUrl = url
            return true;
        }
    }
}

function getCookie() {
    Debug(`${myUrl}/login`)
    let res = false
    request({
        "url": `${myUrl}/login`, //请求链接
        "method": "post", //请求方法
        formData: {
            username,
            password
        },
        "timeOut": 30000,
    }, function (error, response, header, body) {
        Debug(body)
        if (header['Set-Cookie']) {
            Cookie = header['Set-Cookie'][0]
            res = true
        } else {
            Debug(username)
            Debug(password)
            sendText('1.检查奥特曼后台-系统管理-插件权限-订阅源集合-开启autMan数据和cloud数据。\n2.检查面板登陆的账号密码与云账户密码是否一致，不一致则改为一致。\n3.检查奥特曼后台-本地开发-数据管理-cloud桶子中云账户名或密码是否正确。')
            res = false
        }
    })
    return res
}

function getSubList() {
    let body = request({
        "url": "http://47.99.156.63:55555/data2",
        "method": "get",
        "timeOut": 30000,
    })
    // Debug(body)
    let res = JSON.parse(body)
    if (res.code === 200) {
        subList = res.data
        let onlineSub = subList.filter(item => item.online)
        sendText(`总数：${res.ALL}\n非空白源：${res.data.length}\n当前在线：${onlineSub.length}`)
    }
}

function getContactObj() {
    let body = request({
        "url": "http://47.99.156.63:55555/contact",
        "method": "get",
        "timeOut": 30000,
    })
    // Debug(body)
    let res = JSON.parse(body)
    if (res.code === 200) {
        contactObj = res.data
    }
}

function getSubscription() {
    let body = request({
        "url": `${myUrl}/market/subs?searchValue=`,
        "method": "get",
        headers: {
            Cookie
        },
        "timeOut": 30000,
    })
    let res = JSON.parse(body)
    if (res.code === 200) {
        return res.data.map(item => item.author)
    }
}

function goToSub(choose) {
    choose.forEach(item => {
        let body = request({
            "url": `${myUrl}/market/subs`,
            "method": "post",
            headers: {
                Cookie
            },
            body: [
                {
                    "name": item,
                    "author": item
                }
            ],
            "timeOut": 30000,
        })
        Debug(body)
        let res = JSON.parse(body)
        if (res.code === 200) {
            sendText(`订阅成功：${item}`)
        } else {
            sendText(`订阅失败：${item}\n原因：${res.message}`)
        }
    })
}

function searchPlugins(title) {
    Debug(title)
    let body = request({
        "url": `http://47.99.156.63:55555/search?search=` + encodeURIComponent(title), //请求链接
        "method": "get", //请求方法
        "timeOut": 30000,
    })
    // Debug(body)
    if (body === '{}') {
        return false
    } else {
        return JSON.parse(body)
    }
}

function getColud() {
    try {
        let body = request({
            "url": `http://47.99.156.63:55555/cloud?username=` + encodeURIComponent(username), //请求链接
            "method": "get", //请求方法
            "timeOut": 30000,
        })
        // Debug(body)
        let result = JSON.parse(body)
        if (result.data == 'init') {
            sendText('☁️【云动态】\n暂无新增和更新')
        } else {
            let res = result.data
            let str = ['☁️【云动态】'];
            let locaSub = {};
            let locaSubName = [];
            const array = bucketKeys('autMarketSubs');
            if (array && array.length > 0) {
                for (const item of array) {
                    let data = bucketGet('autMarketSubs', item)
                    data = JSON.parse(data)
                    locaSub[data.author] = data.name
                }
                locaSubName = Object.keys(locaSub)
            }

            let offPush = bucketGet(tongzi, "offPush");
            let onlyInstall = bucketGet(tongzi, "onlyInstall");
            let onlySub = bucketGet(tongzi, "onlySub");
            let black = ObtainBlacklist()
            let LocalPluginName = []
            if (onlyInstall == 'true') {
                if (!getCookie()) {
                    return
                }
                let LocalPlugin = getLocalPlugin()
                LocalPluginName = LocalPlugin.map(item => `${item.author}:${item.title}`)
            }

            for (const key in res) {
                if (Object.hasOwnProperty.call(res, key)) {
                    if (black.includes(key)) continue
                    if (onlySub == 'true' && !locaSubName.includes(key)) continue

                    const ele = res[key];
                    const subName = locaSub[key];
                    const subscriptionInfo = `🗣️订阅源：${key}${key !== subName && subName ? `(${subName})` : ''}`;
                    str.push(subscriptionInfo);

                    const newScript = [];
                    const updateScript = [];
                    const removeScript = []

                    // 使用 forEach 遍历并分类插件
                    ele.forEach(item => {
                        if (LocalPluginName.length > 0) {
                            const name = `${key}:${item.title}`
                            if (!LocalPluginName.includes(name)) {
                                return
                            }
                        }

                        if (!item.newVersion) {
                            removeScript.push(item);
                        } else if (item.oldVersion) {
                            updateScript.push(item);
                        } else {
                            newScript.push(item);
                        }
                    });

                    // 拼接新增插件信息
                    if (newScript.length > 0) {
                        str.push(`-------➕新增插件-------`);
                        newScript.forEach((item, index) => {
                            str.push(`【${index + 1}】${item.title}(${item.newVersion})`);
                            str.push(`【价格】${item.price || '🎁免费'}`);
                            if (item.description) {
                                str.push(`【描述】${optimizeText(item.description)}\n`);
                            }
                        });
                    }

                    // 拼接更新插件信息
                    if (updateScript.length > 0) {
                        str.push(`-------🔄更新插件-------`);
                        updateScript.forEach((item, index) => {
                            str.push(`【${index + 1}】${item.title}(${item.oldVersion}=>${item.newVersion})`);
                            str.push(`【价格】${item.price || '🎁免费'}`);
                            if (item.description) {
                                str.push(`【描述】${optimizeText(item.description)}\n`);
                            }
                        });
                    }

                    if (removeScript.length > 0 && offPush == 'true') {
                        str.push(`-------❌下架插件-------`);
                        removeScript.forEach((item, index) => {
                            str.push(`【${index + 1}】${item.title}(${item.oldVersion})`);
                        });
                    }

                    if (newScript.length > 0 || updateScript.length > 0 || removeScript.length > 0) {
                        str.push('');
                    } else {
                        str.pop()
                    }
                }
            }
            if (str.length !== 1) {
                str.pop();
            } else {
                str.push('暂无新增和更新');
            }

            if (GetContent == '云动态') {
                sendChunks(str)
            } else {
                if (str.length !== 2) {
                    Debug('云动态定时推送管理员')
                    sendChunksAdmin(str)
                }
            }
        }
    } catch (error) {
        Debug(error)
        // notifyMasters(error)
    }
}

main()
