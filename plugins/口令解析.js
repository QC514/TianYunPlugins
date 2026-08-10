
//[rule:^.*?起丨住丨力.*?$]
//[rule:^.*?(连续签到|快来签到|签到还有|每天来|每日来|新增签|口令解析成功|快来一起冲榜).*?]
//[rule:^.*?口令解析成功([\s\S]+)$]
//[rule:^([\s\S]+|.*?)(:/！|:/￥|￥|！)([\s\S]+)(￥)([\s\S]+|.*?)$]
//[rule:^.*?(寳|Dσδδng|Dσδ|椋|棟|ōσng|gong|猄|菄|椋|Jiιng|hong|融App|马上就能拿到大奖|快来一起冲榜).*?]
//[title: 口令解析]
//[author: qingge] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]从工具类、查询类、娱乐类、餐饮类、影音类、生活类、图片类、游戏类等中选择
//[platform: qq,wx,tg,qb]适用的平台 qq/wx/tg/wxmp之间选择，中间用英文逗号隔开
//[public: true] 是否公开发布？值为true或false，不设置则上传aut云时会自动设置为true
//[price: 0.5] 上架价格
//[version: 1.2.4] 
//[admin: false] 
//[description: 直接发口令,关键字拦截口令,可能不完善<br/>更多自定义:是否开启返回完整链接,助力码<br/>如果插件不能啥用，需要关闭奥特曼自带JD口令解析<br/>适配更多口令类型<br/>3-31自定义口令解析sign接口<br/>5.16 增加适配更多口令<br/>11.3 修复非邀请助力类活动时,自动拉起洞察<br/> 11.13 剔除滥截取指令问题<br/> 12.23 回退版本,使用自定义接口] 
//[service:97393412]
//[disable:false]
//[priority: 99999999998]
// [param: {"required":false,"key":"who.kl_sign","placeholder":"false","name":"sign接口","desc":"例如:http://sign.lolkda.top/api"}]
// [param: {"required":false,"key":"who.kl_url","bool":true,"placeholder":"false","name":"回复链接","desc":"默认不开启,需要开启则打勾"}]
// [param: {"required":false,"key":"who.kl_zlm","bool":true,"placeholder":"false","name":"返回助力码","desc":"默认不开启,需要开启则打勾"}]
// [param: {"required":false,"key":"who.kl_hjjzl","bool":true,"placeholder":"false","name":"黄金饺调用","desc":"默认不开启,需要开启则打勾"}]
// [param: {"required":false,"key":"who.kl_3czl","bool":true,"placeholder":"false","name":"3C数码调用","desc":"默认不开启,需要开启则打勾"}]

let sign = bucketGet("who", "kl_sign")
var GetContent = GetContent()
let kl_url = bucketGet("who", "kl_url")
let kl_zlm = bucketGet("who", "kl_zlm")
let kl_hjjzl = bucketGet("who", "kl_hjjzl")
let kl_xzzzl = bucketGet("who", "kl_xzzzl")
let kl_3czl = bucketGet("who", "kl_3czl")
//sendText("收到"+GetContent)
Debug("收到..口令"+GetContent)
if (GetContent.indexOf("融App") != -1||GetContent.indexOf("马上就能拿到大奖") != -1||GetContent.indexOf("快来一起冲榜") != -1) {
breakIn("捕鱼口令+"+GetContent)

}else{
kouling2(GetContent)
}


function kouling2(kou) {
    Debug("收到口令"+kou)
    let kouling = {
        code: kou
    }
    for (let i = 0; i < 9; i++) {
        let body = request({
            url: sign + "/jComExchange",
            method: "post",
            body: JSON.stringify(kouling),
            headers: {
                "Content-Type": "application/json",
            },
            dataType: "json",//数据类型json(json数据类型)、location(跳转页)
            timeOut: 8000
        })
        Debug(JSON.stringify(body) + kou)
        if (body) {

            if (body.code == 0 ||body.Code == 200 ||body.status == 200 || body.msg == "获取成功") {


                let data = body.data.jumpUrl
                Debug(data)
                if (data.indexOf("口令转换失败") != -1) {
                    sleep(1000)
                } else {
                    i = 10
                    if (kl_url == "true") {
                        if (data.indexOf("Bc9WX7MpCW7nW9QjZ5N3fFeJXMH") > -1) {
                        } else {
                            sendText(data)
                        }

                    }
                    if (data.indexOf("jd.com") > -1) {
                        var parts = data.split('?');

                        if (parts.length > 1) {
                            if (parts[0] !== "") {
                                var params = parts[1].split('&');
                                //sendText(data)
                                for (var J = 0; J < params.length; J++) {
                                    var param = params[J].split('=');
                                    //

                                    if (param[0] === "wegameInviterId" || param[0] === "inviterId" || param[0] === "inviteCode" || param[0] === "wegameInviterId") {
                                        // 对获取到的值进行解码（如果需要的话）
                                        //sendText(`param[0]=${param[1]}`)
                                        if (kl_zlm == "true") {
                                            sendText(`获取到助力码\n${decodeURIComponent(param[1])}`)
                                        }
                                        // return decodeURIComponent(param[1]);

                                        if (data.indexOf("38fBeMPN3sLNzhvpxCZBbsteaLsv") > -1) {//黄金饺
                                            if (kl_hjjzl == "true") {
                                                breakIn(`黄金+${decodeURIComponent(param[1])}`)
                                                // breakIn(data)
                                            }

                                        } else if (data.indexOf("B2Y13x641hwWfpsoRenCzfbz4jR") > -1) {//赚赚

                                            if (kl_xzzzl == "true") {
                                                breakIn(`赚赚助力+` + decodeURIComponent(param[1]))
                                            }
                                        } else if (data.indexOf("3ABYwYuC87Dcx4gZYGKw6fqtE8WN") > -1) {//3c数码
                                            // sendText("判断到--3c数码")
                                            if (kl_3czl == "true") {
                                                breakIn(`数码+${decodeURIComponent(param[1])}`)
                                            }
                                        } else if (data.indexOf("3n8vJTvbf18Ey2dMDiSCQCpeaooW") > -1) {//3c数码
                                            if (kl_3czl == "true") {
                                                breakIn(`文具+${decodeURIComponent(param[1])}`)
                                            }
                                        } else if (data.indexOf("2bMhVoqyXAxUsjkBkTurGZUHAAji") > -1) {//3c数码
                                            breakIn(`推红包+${decodeURIComponent(param[1])}`)
                                        } else if (data.indexOf("2vvWrigCKrEDr1QUSmorqk8rbteV") > -1) {//3c数码
                                            breakIn(`推金+${decodeURIComponent(param[1])}`)

                                        } else if (data.indexOf("4N8Es4Ws9agaWFHMbtWpEjMtzCXU") > -1) {//3c数码
                                            breakIn(`开学礼+${decodeURIComponent(param[1])}`)

                                        } else if (data.indexOf("T3kLpNbq8AJQZtTwfRF9o1HBhKP") > -1) {//3c数码
                                            breakIn(`潮电+${decodeURIComponent(param[1])}`)
                                        } else if (data.indexOf("Bc9WX7MpCW7nW9QjZ5N3fFeJXMH") > -1 || data.indexOf("42HV4J3Q87B2xFQMJk81PCc1mEs3") > -1) {
                                            //sendText("判断到--新农场")
                                            sendText(`新农场助力码\n${decodeURIComponent(param[1])}`)
                                            breakIn(`新助力码助力+${decodeURIComponent(param[1])}`)
                                        } else if (data.indexOf("Bkfj1KTXRrTkmpwkQsmRf33WZbC") > -1) {
                                            //sendText("判断到--欢乐挖宝")
                                            breakIn(data)

                                        } else {
                                            sendText(`找不到对应活动,获取到助力码\n${decodeURIComponent(param[1])}`)
                                        }

                                    } else {
                                        // sendText(`找不到对应活动\n活动地址:\n${data}`)
                                    }
                                }

                            } else {
                                sendText("收到数据为空")
                            }

                        }
                    } else {
                        breakIn(data)
                    }
                }


            } else {
                //sendText(JSON.stringify(body))
            }
        }
    }
}