//[rule:^([\s\S]+)u.jd.com+([\s\S]+)$]
//[rule:^https://u.jd.com+([\s\S]+)$]

//[priority: 9999999999999]
//[title: 链接还原]
//[disable:false]
//[author: qingge] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]从工具类、查询类、娱乐类、餐饮类、影音类、生活类、图片类、游戏类等中选择
//[platform: qq,wx,tg,qb]适用的平台 qq/wx/tg/wxmp之间选择，中间用英文逗号隔开
//[public: true] 是否公开发布？值为true或false，不设置则上传aut云时会自动设置为true
//[price: 1] 上架价格
//[admin: false] 
//[version: 0.1.5] 
//[description: u.jd.com短链接还原并内部处理] 
//[service:97393412]
var GetContent = GetContent()
function mian(){
    let password = getCaption(GetContent, '+');
    var reg = /u\.jd\.com\/[0-9a-zA-Z]{7}/g
    var reg2 = /hrl=\'(.+?)\';/
    var shorts = []

    while ((result = reg.exec(password)) != null) {
        shorts.push(result[0])
    }
    for (i = 0; i < shorts.length; i++) {
        //获取访问内容
        var body = request({
            url: "https://" + shorts[i],
            "method": "get",
        })
        //Debug(body)
        if (body) {
            //提取访问内容中链接
            hrl = reg2.exec(body)
            if (hrl.length >= 2) {
                //获取目标链接
                var shopurl = request({
                    url: hrl[1],
                    "method": "get",
                    "dataType": "location"
                })
                Debug(shopurl)
                breakIn(shopurl)
            }
        }
    }
}
function getCaption(obj, text) {
    let index = obj.lastIndexOf(text) + text.length - 1;

    obj = obj.substring(index + 1, obj.length);
    return obj;
}

mian() 
