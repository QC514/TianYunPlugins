// [author: hdbjlizhe]
// [version: 1.0.1]
// [title: 短链解析]
// [icon:https://bbs.autman.cn/assets/files/2024-04-10/1712739078-943779-dbc9b85ea63f7038bef14985868b4c18.jpg]
// [description: 短链解析,指令：dljx 短链，主要是将那个跳转链接解析原始链接来]
// [price: 0.00]
// [service: 282617666]
// [rule: raw dljx (.+)]
// [admin: false]
url=param(1)
Debug("链接："+url)
var shopurl = request({
    url: url,
    "method": "get",
    "dataType": "location"
})
//Debug(shopurl)
if (shopurl) {
    sendText(shopurl)
    breakIn(shopurl)
}