//[title: 疯狂星期四KFC]
//[language: es5]
//[class: 娱乐类]
//[service: 0] 售后联系方式
//[author:qw21560]
//[disable: false] 禁用开关，true表示禁用，false表示可用
//[admin: false] 是否为管理员指令
//[rule: 疯狂星期四]
//[rule: 周四]
//[rule: kfc]
//[rule: KFC]
//[rule: 肯德基]匹配规则，多个规则时向下依次写多个
//[priority: 100] 优先级，数字越大表示优先级越高
//[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
//[open_source: false]是否开源
//[icon: ]图标链接地址，请使用48像素的正方形图标，支持http和https
//[version: 1.0.0]版本号
//[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
//[price: 0] 上架价格
//[description: 今天是肯德基疯狂星期四，谁请我吃？V我50] 使用方法尽量写具体
function main() {
    var data = request({
        url: "https://oiapi.net/API/KFC/",
        "method": "get"
    })
    sendText(JSON. parse (data).message)
}
main()

