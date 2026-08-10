//[title: 懒羊羊翻唱歌曲]
//[language: es5]
//[class: 娱乐类]
//[author:qw21560]
//[service: 0] 售后联系方式
//[disable: false] 禁用开关，true表示禁用，false表示可用
//[admin: false] 是否为管理员指令
//[rule: 懒羊羊] 匹配规则，多个规则时向下依次写多个
//[priority: 0] 优先级，数字越大表示优先级越高
//[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
//[open_source: false]是否开源
//[icon: 图标url]图标链接地址，请使用48像素的正方形图标，支持http和https
//[version: 1.0.0]版本号
//[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
//[price: 0] 上架价格
//[description: 懒羊羊翻唱歌曲视频，指令：懒羊羊] 使用方法尽量写具体
var url = "http://api.yujn.cn/api/lyy.php?type=video"
var red = request({
        url: url,
        dataType: "location",
    })
Debug(red)
sendVideo(red)