//[title: 天气]
//[language: es5]
//[class: 查询类]
//[service: 0] 售后联系方式
//[author: qw21560]
//[disable: false] 禁用开关，true表示禁用，false表示可用
//[admin: false] 是否为管理员指令
//[rule: ?天气] 匹配规则，多个规则时向下依次写多个
//[priority: 100] 优先级，数字越大表示优先级越高
//[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
//[open_source: false]是否开源
//[icon: 图标url]图标链接地址，请使用48像素的正方形图标，支持http和https
//[version: 1.0.1]版本号
//[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
//[price: 0] 上架价格
//[description: 天气。北京天气  更新稳定接口] 使用方法尽量写具体
function main() {
    var address = param(1) //匹配规则第一个问号的值
    var isCron = false //标记是否定时任务
    if (address == "") { //定时任务时为空，给address赋予默认值宁波
        address = ""
        isCron = true
    }
    var content = request({ // 内置http请求函数
        "url": "http://api.yujn.cn/api/qqtq.php?msg="+address , //请求链接
        "method": "get", //请求方法
        //"dataType": "json", //这里接口直接返回文本，所以不需要指定json类型数据
    })
    if (!content) {
        data = "哎呀数据没找到。。。" //请求失败时，返回的文字
    }
    if (!isCron) {
        sendText(content) //主动询问时进行回复
    } else {
        push({ imType: "", groupCode: "", content: content }) //定时任务发起群组推送
    }
}

main()