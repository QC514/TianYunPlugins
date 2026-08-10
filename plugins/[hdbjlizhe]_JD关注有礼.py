// [author: hdbjlizhe]
// [version: v1.0.6]
// [title: JD关注有礼]
// [description: 将关注有礼短链线报（线报中包含关键字“关注有礼”）转发机器人，自动解析成M变量和船长变量，拉起脚本运行。]
// [platform: qq,wx,tg]
// [public:true]
// [price: 0.00]
// [service: qq282617666]
//=======================================================
// [rule: raw 关注有礼]
// [admin: false ]
// [disable:false]
// [priority: 7777777777777]

Debug("JD关注有礼")
Continue()
var ctn = GetContent()
var reg = /u\.jd\.com\/[0-9a-zA-Z]{7}/g
var reg2 = /hrl=\'(.+?)\';/
var shorts=[]
var shopids = []

while ((result = reg.exec(ctn)) != null) {
    shorts.push(result[0])
}
for(i=0;i<shorts.length;i++){
    //获取访问内容
    var body = request({
        url: "https://" +shorts[i],
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
            let m="export M_FOLLOW_SHOP_ARGV=\""+shopurl+"\""
            breakIn(m)
            if(shopurl){
                shopid = getShopid(shopurl)
                if (shopid) {
                    shopids.push(shopid)
                }
            }
        }
    }
}

if (shopids.length > 0) {
    var v1 = "export jd_shopFollowGiftId=\"" + shopids.join("&") + "\""
    breakIn(v1)
    sendText(v1)
}

function getShopid(url) {
    Debug(url)
    reg = /shopId=(\d{5,})&/
    shopid = reg.exec(url)
    if (shopid && shopid.length >= 2) {
        return shopid[1]
    }else{
        return ""
    }
}