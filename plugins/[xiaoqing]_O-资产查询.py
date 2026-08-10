//[disable:false]
//[title: O-资产查询]
//[author: xiaoqing] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 查询类]从工具类、查询类、娱乐类、餐饮类、影音类、生活类、图片类、游戏类等中选择
//[public: true] 是否公开发布？值为true或false，不设置则上传aut云时会自动设置为true
//[price: 3] 上架价格
//[version: 1.9.3] 
//[admin: false] 
//[platform: qq,wx,tg,wb,qb]
//[priority: 9999999999]
//[service: Q:97393412]
//[description: 指令：【资产查询】或【京豆】    需要给qinglong权限,获取名方法:奥特曼后台-容器管理--对接容器--名称<br/>快捷设置:云应用市场-我的-插件配置<br/>快捷设置:云应用市场-我的-插件配置<br/>插件交流群：858456556<br/>--------<br/>设置图片模式：set jd_cookie enable_bill true<br/>文字模式set jd_cookie enable_bill false] 
// [param: {"required":true,"key":"otto.who_ck","placeholder":"容器名称","name":"青龙名称","desc":"获取名方法:奥特曼后台-容器管理--对接容器--名称"}]
// [param: {"required":false,"key":"otto.dh_kg","bool":true,"placeholder":"false","name":"单号查询","desc":"单个账号查询开关"}]
// [param: {"required":false,"key":"otto.who_sq","bool":true,"placeholder":"false","name":"授权控制","desc":"暂时没有作用"}]
// [param: {"required":true,"key":"otto.ql_hyy","placeholder":"请你先发送：登录","name":"没账号时提示","desc":"没有与你绑定的账号，请对我说：“登陆”"}]
// [param: {"required":true,"key":"otto.ql_sx","placeholder":"请你先发送：登录","name":"失效回复语","desc":"你的账号已失效，请对我说：“登陆”"}]
// [param: {"required":true,"key":"otto.who_zdy","placeholder":"你需要自定义的内容","name":"尾部自定义语","desc":"尾部自定义提示内容"}]
// [param: {"required":false,"key":"otto.tupin","bool":true,"placeholder":"false","name":"图床","desc":"打开则用本地图床，默认关闭即可"}]
// [param: {"required":false,"key":"otto.h5st","bool":true,"placeholder":"false","name":"备用端口","desc":"H5st端口"}]
// [param: {"required":false,"key":"otto.dh_DL","bool":true,"placeholder":"false","name":"代理池开关","desc":"是否开启调用使用代理池"}]
// [param: {"required":true,"key":"otto.ql_APIDL","placeholder":"例如:http://192.168.3.121:8080","name":"API代理地址","desc":"仅支持代理池，不支持API代理,"}]
// [param: {"required":false,"key":"otto.plantBean","bool":true,"placeholder":"false","name":"种豆得豆","desc":"关闭则不查"}]
// [param: {"required":false,"key":"otto.farm_home","bool":true,"placeholder":"false","name":"新版农场","desc":"关闭则不查"}]
// [param: {"required":false,"key":"otto.dh_code","bool":true,"placeholder":"false","name":"助力码","desc":"打开则收集助力码"}]
// [param: {"required":false,"key":"otto.Fruit","bool":true,"placeholder":"false","name":"旧版农场","desc":"关闭则不查"}]
// [param: {"required":false,"key":"otto.jksq","bool":true,"placeholder":"false","name":"健康社区","desc":"关闭则不查"}]
// [param: {"required":false,"key":"otto.getPlusScore","bool":true,"placeholder":"false","name":"plus分数","desc":"5个分数值，建议关闭，关闭则不查"}]
// [param: {"required":false,"key":"otto.getjingBeanDetail","bool":true,"placeholder":"false","name":"到期京豆","desc":"关闭则不查"}]
// [param: {"required":false,"key":"otto.Coupon","bool":true,"placeholder":"false","name":"优惠卷","desc":"关闭则不查"}]
// [param: {"required":false,"key":"otto.cardInfo","bool":true,"placeholder":"false","name":"京东超市","desc":"关闭则不查"}]
// [param: {"required":false,"key":"otto.UserCard","bool":true,"placeholder":"false","name":"京东E卡","desc":"关闭则不查"}]
//=========================================
//[rule:^京豆$]
//[rule:^资产查询$]



var h5_ver = ""
var msgs = []
var icons = []
var nc_h5 = ""
var nc_ua = ""
//日期转字符串格式
function DateToStr(date) {
    var year = date.getFullYear();//年
    var month = date.getMonth();//月
    var day = date.getDate();//日
    return year + "-" +
        ((month + 1) > 9 ? (month + 1) : "0" + (month + 1)) + "-" +
        (day > 9 ? day : ("0" + day));
}
//即将到期的京豆
function getjingBeanDetail(cookie) {
    let douadou = ""
    let xdouadou = ""
    try {
        data = request({
            "url": "https://api.m.jd.com/client.action?functionId=jingBeanDetail&lmt=0&clientVersion=11.4.4&build=98651&client=android&partner=vivo&eid=eidA0e4b8122bcsbmU8cxX6JSnmFF7Cl6g5doplPHkfs3QZUs0dlNmQtEHko4TLPY2XSploxRKqK/yB2Qua2TymGyKXI2yYXc9VXWPrC9hJ5ALtEHnlT&sdkVersion=29&lang=zh_CN&harmonyOs=0&networkType=wifi&uts=0f31TVRjBSsqndu4%2FjgUPz6uymy50MQJXQvVqUBgQhGnerd2wImVdyFkNKQomq7BgrTQfs76xQdZ223tbYtRLlq4KctudrEdbOY24QB8XMv4HNbaM7x9wkM%2BmQjfk5%2FAJ1QoLbkQync6BUgJi0Uu1xsZUIzaMpDVlPaobeyFcpJgDrt8TQc2gCLProedSbKLTB8TqeEbJKH7pLgSX50zfQ%3D%3D&uemps=0-0-0&ext=%7B%22prstate%22%3A%220%22%2C%22pvcStu%22%3A%221%22%7D&avifSupport=1&ef=1&ep=%7B%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%22%2C%22ts%22%3A1675559773634%2C%22ridx%22%3A-1%2C%22cipher%22%3A%7B%22area%22%3A%22CJvpCJY3D18nDtc5XzY0CNG%3D%22%2C%22d_model%22%3A%22VtO4CtHMGG%3D%3D%22%2C%22wifiBssid%22%3A%22ZNCnDzY5DtO4ENLvCtCnCtY0EJSmDNLwDQGyZJq1CWY%3D%22%2C%22osVersion%22%3A%22CJK%3D%22%2C%22d_brand%22%3A%22dwv2bm%3D%3D%22%2C%22screen%22%3A%22CtO0CIenCNqm%22%2C%22uuid%22%3A%22CwG4Y2VvCNG1ZJq5ZNZwYG%3D%3D%22%2C%22aid%22%3A%22CwG4Y2VvCNG1ZJq5ZNZwYG%3D%3D%22%2C%22openudid%22%3A%22CwG4Y2VvCNG1ZJq5ZNZwYG%3D%3D%22%7D%2C%22ciphertype%22%3A5%2C%22version%22%3A%221.2.0%22%2C%22appname%22%3A%22com.jingdong.app.mall%22%7D&st=1675559805181&sign=fdd25a51d7bcb5fe708212df5cd7297a&sv=110",
            "body": `body={"pageNo":1,"pageSize":20}`,
            method: "post",
            "headers": {
                'Host': 'api.m.jd.com',
                'User-Agent': "Mozilla/5.0 (Linux; Android 12; SM-G9880) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36 EdgA/106.0.1370.47",
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Cookie': cookie,
                'content-length': 56,
            },
            dataType: "json",
            "timeout": 30000,
        })
        if (data.code == 0) {
            icons.push("jdicons/toin.jpg")
            // sendText(JSON.stringify(data))

            msgs.push("💸💸💸临期京豆明细💸💸💸")
            let doudou = JSON.stringify(data.others.jingBeanExpiringInfo.detailList)
            let doushao = JSON.parse(doudou)
            //  msgs.push(doushao.length)
            douadou = ""
            for (var key in doushao) {
                let doux = doushao[key].eventMassage
                let dousa = doushao[key].amount
                let fg = doux.split("即");
                // xdouadou +=fg[0]
                // douadou += dousa+"豆\n"
                douadou = `【${fg[0]}】过期${dousa}豆`

                msgs.push(douadou)
            }
            //  msgs.push(xdouadou)
            // msgs.push(douadou)

        }

    } catch (err) {
    }
}
//健康社区
function jksq(cookie) {
    try {
        body = request({
            method: "post",
            url: "https://api.m.jd.com/",
            body: "functionId=jdhealth_getHomeData&body=%7B%7D&client=wh5&clientVersion=1.0.0&uuid=",
            headers: {
                "Host": " api.m.jd.com",
                "accept": " application/json, text/plain, */*",
                "user-agent": UserAgents(),
                "origin": " https://h5.m.jd.com",
                "x-requested-with": " com.jingdong.app.mall",
                "sec-fetch-site": " same-site",
                "sec-fetch-mode": " cors",
                "sec-fetch-dest": " empty",
                "referer": " https://h5.m.jd.com/",
                "accept-language": " zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": cookie,
                "content-type": " application/x-www-form-urlencoded",
                "Connection": "keep-alive"
            },
            //  dataType: "json",
            timeOut: 30000
        })
        data = JSON.parse(body)
        if (data.code == 0) {
            msgs.push("【健康社区】" + data.data.result.userScore + "能量")
        }
    } catch (err) {
        Debug(err)
    }
}
//plus分数
function getPlusScore(cookie, kg) {
    h42_nc(`{"functionId":"windControl_queryScore_v1","config":{"appId":"b63ff","appid":"plus_business","version":"4.1","ua":"jdapp;iPhone;10.1.4;13.5;XM6DWDL787K7EJCAP8Z73OY3FBTK26JKY4PK1M7E;network/wifi;model/iPhone12,1;addressid/0;appBuild/167814;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1"},"body":{}}`)
    var DL_api = bucketGet("otto", "ql_APIDL")//代理开关功能
    for (let k = 0; k < 2; k++) {
        try {
            body = request({
                useproxy: kg,
                proxyAddr: DL_api,
                method: "post",
                url: `https://api.m.jd.com/api?functionId=windControl_queryScore_v1`,
                body: nc_h5,
                headers: {
                    "Host": "api.m.jd.com",
                    "accept": "application/json, text/plain, */*",
                    "user-agent": nc_ua,
                    "origin": "https://plus.m.jd.com",
                    "x-rp-client": "h5_1.0.0",
                    "referer": "https://plus.m.jd.com/rights/windControl",
                    "Cookie": cookie,
                    "x-referer-page": "https://plus.m.jd.com/rights/windControl",
                    "content-type": "application/x-www-form-urlencoded;charset=UTF-8"
                },
                // dataType: "json",
                timeOut: 90000
            })
            data = JSON.parse(body)
            if (data.code == "1000") {
                var cx_PlusScore = get("getPlusScore")//代理开关功能
                if (cx_PlusScore == "true" || cx_PlusScore == true) {
                    icons.push("jdicons/zhxy.jpg")
                    msgs.push("【账户信息】" + data.rs.userDimensionScore.accountInfo + "/5")
                    icons.push("jdicons/zhxy.jpg")
                    msgs.push("【购物合规】" + data.rs.userDimensionScore.shop + "/5")
                    icons.push("jdicons/zhxy.jpg")
                    msgs.push("【购物历史】" + data.rs.userDimensionScore.shopAfter + "/5")
                    icons.push("jdicons/zhxy.jpg")
                    msgs.push("【信用价值】" + data.rs.userDimensionScore.baiScore + "/5")
                    icons.push("jdicons/zhxy.jpg")
                    msgs.push("【售后行为】" + data.rs.userDimensionScore.active + "/5")
                }
                icons.push("jdicons/zhxy.jpg")
                msgs.push("【会员分值】" + data.rs.userSynthesizeScore.totalScore)
                icons.push("jdicons/zhxy.jpg")
                msgs.push("【评估周期】" + data.rs.scoreUserInfo.calEndDate)
                k = 5
            } else {
                sleep(1000)
            }
        } catch (err) {
            Debug(err)
        }
    }
}
function ql_cs(name) {//设置容器
    var qls = bucketGet("qinglong", "QLS")
    if (qls) {
        let QLS = JSON.parse(qls)
        for (i = 0; i < QLS.length; i++) {
            if (QLS[i].name === name) {
                let data = {
                    host: QLS[i].host,
                    client_id: QLS[i].client_id,
                    client_secret: QLS[i].client_secret
                }
                Debug("指定获取【" + name + "】的数据")
                return JSON.stringify(data)
            }
        }
    }
}
function h42_nc(h5_body) {
    var DL_kg = get("h5st")//代理开关功能
    if (DL_kg == "true") {
        h5st_url = `http://110.40.165.213:3004/universal`
    } else {
        h5st_url = `http://110.40.165.213:3000/universal`
    }
    let body = request({
        url: h5st_url,
        method: "post",
        body: h5_body,
        headers: {
            "Content-Type": "application/json",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    if (body) {
        if (body.code = 200) {
            nc_h5 = body.data
            nc_ua = body.ua
        }
        return true
    } else {
        return false
    }
}
//获取豆豆明细
function getJingBeanBalanceDetail(cookie, page) {
    Debug("总豆查询")
    let body = escape(JSON.stringify({
        "pageSize": "20",
        "page": page.toString()
    }
    ))
    let options = {
        url: "https://api.m.jd.com/client.action?functionId=getJingBeanBalanceDetail",
        method: "post",
        dataType: "json",
        body: "body=" + body + "&appid=ld",
        headers: {
            "User-Agent": UserAgents(),
            "Host": "api.m.jd.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": cookie
        }
    }
    let beaninfo = request(options)
    return beaninfo
}
function getJingBeanBalanceDetail2(cookie, page) {
    let todayIn = 0//今日收入
    let yesterIn = 0//昨日收入
    //Debug("总豆查询")
    body = encodeURIComponent(JSON.stringify({ "pageSize": "20", "page": page.toString() }))
    data = request({
        "url": "https://bean.m.jd.com/beanDetail/detail.json?page=" + page,
        "body": "body=" + body + "&appid=ld",
        "headers": {
            'User-Agent': UserAgents(),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie,
        },
        "timeout": 10000,
        "json": true
    })
    return data
}
//汇总豆豆
function sumBean(cookie) {
    Debug("统计收入")
    //统计收入
    var todayIn = 0
    var todayOut = 0
    var yesterIn = 0
    var yesterOut = 0
    //获取当前日期
    var curDate = new Date();
    var yesDate = new Date();
    yesDate.setDate(curDate.getDate() - 1)
    //日期字符串
    strToday = DateToStr(curDate)
    strYester = DateToStr(yesDate)
    page = 1
    while (true) {
        data = getJingBeanBalanceDetail2(cookie, page)
        Debug(JSON.stringify(data))
        exitWhile = false
        if (data) {
            obj = data
            try {
                if (!data.jingDetailList) {
                    data = { jingDetailList: getJingBeanBalanceDetail(cookie, page).detailList }
                }
            }
            catch (e) {
                return
            }
            for (i = 0; i < data.jingDetailList.length; i++) {
                dateStr = data.jingDetailList[i].date
                if (dateStr.slice(0, 10) == strToday) {
                    amount = parseInt(data.jingDetailList[i].amount)
                    if (amount > 0) {
                        todayIn += amount
                    } else {
                        todayOut += amount
                    }
                } else if (dateStr.slice(0, 10) == strYester) {
                    amount = parseInt(data.jingDetailList[i].amount)
                    if (amount > 0) {
                        yesterIn += amount
                    } else {
                        yesterOut += amount
                    }

                } else {
                    exitWhile = true
                    break
                }
            }
        } else {
            break
        }
        if (exitWhile) {
            break
        }
        page++
    }
    icons.push("jdicons/toin.jpg")
    msgs.push("【今日收入】" + todayIn + "(支出" + todayOut + ")")
    icons.push("jdicons/yein.jpg")
    msgs.push("【昨日收入】" + yesterIn + "(支出" + yesterOut + ")")
}
//京东超市
function cardInfo(cookie) {
    h42_nc(`{"functionId":"atop_channel_marketCard_cardInfo","config":{"appId":"35fa0","appid":"jd-super-market","version":"4.3","ua":"jdapp;iPhone;10.1.4;13.5;XM6DWDL787K7EJCAP8Z73OY3FBTK26JKY4PK1M7E;network/wifi;model/iPhone12,1;addressid/0;appBuild/167814;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1"},"body":{"babelChannel":"ttt41","isJdApp":"1","isWx":"0"}}`)
    try {
        body = request({
            method: "post",
            url: `https://api.m.jd.com/atop_channel_marketCard_cardInfo`,
            body: nc_h5,
            headers: {
                "Host": "api.m.jd.com",
                "accept": "*/*",
                "x-rp-client": "h5_1.0.0",
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": nc_ua,
                "x-referer-page": "https://pro.m.jd.com/mall/active/3KehY4eAj3D1iLzFB7p5pb68qXkT/index.html",
                "origin": "https://pro.m.jd.com",
                "x-requested-with": "com.jingdong.app.mall",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://pro.m.jd.com/mall/active/3KehY4eAj3D1iLzFB7p5pb68qXkT/index.html?babelChannel=ttt41&navh=49&stath=31&tttparams=Puv4564rgeyJhZGRyZXNzSWQiOjgwMjQzODQ3NzAsImRMYXQiOjAsImRMbmciOjAsImdMYXQiOiIyMC44OTQwNDkiLCJnTG5nIjoiMTA5Ljk2MjQ1IiwiZ3BzX2FyZWEiOiIxOV8xNjc3XzE2NzlfNjQwNCIsImxhdCI6MjAuODkzNjczLCJsbmciOjEwOS45NjI3NjYsIm1vZGVsIjoiUmVkbWkgSzQwIEdhbWluZyIsInBvc0xhdCI6IjIwLjg5NDA0OSIsInBvc0xuZyI6IjEwOS45NjI0NSIsInByc3RhdGUiOiIwIiwidWVtcHMiOiIwLTAtMiIsInVuX2FyZWEiOiIxOV8xNjc3XzE2NzlfNjQwNC9J9",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": cookie,
            },
            dataType: "json",
            timeOut: 90000
        })
        if (body.code == 0) {
            let balance = body.data.floorData.items[0].marketCardVO.balance;
            icons.push("jdicons/jscoin.jpg")
            if (balance == "0.00") {
                Debug("京东超市内没有余额？")
            } else {
                msgs.push("【京东超市】" + balance + "R")
            }
        }
    } catch (err) {
    }
}
//获取红包数据
function getRedPacket(cookie) {
    request({
        url: `https://api.m.jd.com/client.action?functionId=myhongbao_getUsableHongBaoList&body=%7B%22appId%22%3A%22appHongBao%22%2C%22appToken%22%3A%22apphongbao_token%22%2C%22platformId%22%3A%22appHongBao%22%2C%22platformToken%22%3A%22apphongbao_token%22%2C%22platform%22%3A%221%22%2C%22orgType%22%3A%222%22%2C%22country%22%3A%22cn%22%2C%22childActivityId%22%3A%22-1%22%2C%22childActiveName%22%3A%22-1%22%2C%22childActivityTime%22%3A%22-1%22%2C%22childActivityUrl%22%3A%22-1%22%2C%22openId%22%3A%22-1%22%2C%22activityArea%22%3A%22-1%22%2C%22applicantErp%22%3A%22-1%22%2C%22eid%22%3A%22-1%22%2C%22fp%22%3A%22-1%22%2C%22shshshfp%22%3A%22-1%22%2C%22shshshfpa%22%3A%22-1%22%2C%22shshshfpb%22%3A%22-1%22%2C%22jda%22%3A%22-1%22%2C%22activityType%22%3A%221%22%2C%22isRvc%22%3A%22-1%22%2C%22pageClickKey%22%3A%22-1%22%2C%22extend%22%3A%22-1%22%2C%22organization%22%3A%22JD%22%7D&appid=JDReactMyRedEnvelope&client=apple&clientVersion=7.0.0`,
        headers: {
            "Cookie": cookie,
            "Host": "api.m.jd.com",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://h5.m.jd.com",
            "User-Agent": "JD4iPhone/167774 (iPhone; iOS 14.7.1; Scale/3.00)",
            "Accept-Language": "zh-Hans-CN;q=1",
            //"Accept-Encoding": "gzip, deflate, br",
        },
        method: "post",
        json: true
    }, function (error, response, header, body) {
        Debug("检查红包数据是否有错误：" + error)
        //Debug(JSON.stringify(obj))
        if (!error) {
            data = body;
            jxRed = 0,
                jsRed = 0,
                jdRed = 0,
                jdhRed = 0,
                jdwxRed = 0,
                jdGeneralRed = 0,
                jxRedExpire = 0,
                jsRedExpire = 0,
                jdRedExpire = 0,
                jdhRedExpire = 0;
            jdwxRedExpire = 0,
                jdGeneralRedExpire = 0

            let t = new Date();
            t.setDate(t.getDate() + 1);
            t.setHours(0, 0, 0, 0);
            t = parseInt((t - 1000));

            for (let vo of data.hongBaoList || []) {
                if (vo.orgLimitStr) {
                    if (vo.orgLimitStr.includes("京喜") && !vo.orgLimitStr.includes("特价")) {
                        jxRed += parseFloat(vo.balance)
                        if (vo['endTime'] === t) {
                            jxRedExpire += parseFloat(vo.balance)
                        }
                        continue;
                    } else if (vo.orgLimitStr.includes("购物小程序")) {
                        jdwxRed += parseFloat(vo.balance)
                        if (vo['endTime'] === t) {
                            jdwxRedExpire += parseFloat(vo.balance)
                        }
                        continue;
                    } else if (vo.orgLimitStr.includes("京东商城")) {
                        jdRed += parseFloat(vo.balance)
                        if (vo['endTime'] === t) {
                            jdRedExpire += parseFloat(vo.balance)
                        }
                        continue;
                    } else if (vo.orgLimitStr.includes("极速") || vo.orgLimitStr.includes("京东特价") || vo.orgLimitStr.includes("京喜特价")) {
                        jsRed += parseFloat(vo.balance)
                        if (vo['endTime'] === t) {
                            jsRedExpire += parseFloat(vo.balance)
                        }
                        continue;
                    } else if (vo.orgLimitStr && vo.orgLimitStr.includes("京东健康")) {
                        jdhRed += parseFloat(vo.balance)
                        if (vo['endTime'] === t) {
                            jdhRedExpire += parseFloat(vo.balance)
                        }
                        continue;
                    }
                }
                jdGeneralRed += parseFloat(vo.balance)
                if (vo['endTime'] === t) {
                    jdGeneralRedExpire += parseFloat(vo.balance)
                }

            }
            balance = (jxRed + jsRed + jdRed + jdhRed + jdwxRed + jdGeneralRed).toFixed(2);
            jxRed = jxRed.toFixed(2);
            jsRed = jsRed.toFixed(2);
            jdRed = jdRed.toFixed(2);
            jdhRed = jdhRed.toFixed(2);
            jdwxRed = jdwxRed.toFixed(2);
            jdGeneralRed = jdGeneralRed.toFixed(2);
            expiredBalance = (jxRedExpire + jsRedExpire + jdRedExpire + jdhRedExpire + jdwxRedExpire + jdGeneralRedExpire).toFixed(2);
            if (bucketGet("jd_cookie", "enable_bill") == "true") {
                msgs.push("----->红包明细<-----");
                icons.push("jdicons/jchb.jpg")
                msgs.push("【红包总额】" + balance + "(总过期" + expiredBalance + ")");
                if (jxRed > 0) {
                    icons.push("jdicons/jshb.jpg")
                    msgs.push("【京喜红包】" + jxRed + "(将过期" + jxRedExpire.toFixed(2) + ")");
                }
                if (jsRed > 0) {
                    icons.push("jdicons/jshb.jpg")
                    msgs.push("【惊喜红包】" + jsRed + "(将过期" + jsRedExpire.toFixed(2) + ")");
                }

                if (jdRed > 0) {
                    icons.push("jdicons/jdhb.jpg")
                    msgs.push("【京东红包】" + jdRed + "(将过期" + jdRedExpire.toFixed(2) + ")");
                }

                if (jdhRed > 0) {
                    icons.push("jdicons/jkhb.jpg")
                    msgs.push("【健康红包】" + jdhRed + "(将过期" + jdhRedExpire.toFixed(2) + ")");
                }

                if (jdwxRed > 0) {
                    icons.push("jdicons/jdhb.jpg")
                    msgs.push("【微小程序】" + jdwxRed + "(将过期" + jdwxRedExpire.toFixed(2) + ")");
                }

                if (jdGeneralRed > 0) {
                    icons.push("jdicons/syhb.jpg")
                    msgs.push("【平台通用】" + jdGeneralRed + "(将过期" + jdGeneralRedExpire.toFixed(2) + ")");
                }
            } else {
                msgs.push("🧧🧧🧧红包明细🧧🧧🧧");
                icons.push("jdicons/jdhb.jpg")
                msgs.push("【红包总额】" + balance + "(总过期" + expiredBalance + ")");
                if (jxRed > 0) {
                    icons.push("jdicons/jdhb.jpg")
                    msgs.push("【京喜红包】" + jxRed + "(将过期" + jxRedExpire.toFixed(2) + ")");
                }
                if (jsRed > 0) {
                    icons.push("jdicons/jdhb.jpg")
                    msgs.push("【惊喜红包】" + jsRed + "(将过期" + jsRedExpire.toFixed(2) + ")");
                }
                if (jdRed > 0) {
                    icons.push("jdicons/jdhb.jpg")
                    msgs.push("【京东红包】" + jdRed + "(将过期" + jdRedExpire.toFixed(2) + ")");
                }
                if (jdhRed > 0) {
                    icons.push("jdicons/jdhb.jpg")
                    msgs.push("【健康红包】" + jdhRed + "(将过期" + jdhRedExpire.toFixed(2) + ")");
                }
                if (jdwxRed > 0) {
                    icons.push("jdicons/jdhb.jpg")
                    msgs.push("【微小程序】" + jdwxRed + "(将过期" + jdwxRedExpire.toFixed(2) + ")");
                }
                if (jdGeneralRed > 0) {
                    icons.push("jdicons/jdhb.jpg")
                    msgs.push("【平台通用】" + jdGeneralRed + "(将过期" + jdGeneralRedExpire.toFixed(2) + ")");
                }
            }
        } else {
            icons.push("jdicons/jdhb.jpg")
            msgs.push("【红包数据】返回空数据")
        }
    })
}
//领取现金
function lxj(cookie) {
    try {
        body = request({
            method: "post",
            url: `https://api.m.jd.com/api?functionId=user_getUserInfo_v2`,
            body: `functionId=cash_mob_home&body={\"version\":\"1\",\"channel\":\"app\"}&appid=signed_wh5&client=android&clientVersion=12.1.0&screen=344*0&wqDefault=false&build=98891&osVersion=10&networkType=wifi&d_brand=vivo&d_model=V1824BA&partner=vivo&uuid=2346833656560343-5356839346636616`,
            headers: {
                "Host": " api.m.jd.com",
                "accept": " application/json, text/plain, */*",
                "x-rp-client": " h5_1.0.0",
                "user-agent": UserAgents(),
                "origin": " https://h5.m.jd.com",
                "x-requested-with": " com.jingdong.app.mall",
                "sec-fetch-site": " same-site",
                "sec-fetch-mode": " cors",
                "sec-fetch-dest": " empty",
                "referer": " https://h5.m.jd.com/",
                "accept-language": " zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": cookie,
                "content-type": " application/x-www-form-urlencoded",
                "Connection": "keep-alive"
            },
            // dataType: "json",
            timeOut: 30000
        })
        data = JSON.parse(body)
        if (data.code == 0) {
            icons.push("jdicons/jdhb.jpg")
            msgs.push("【领现金】" + data.data.result.signMoney)
        }
    } catch (err) {
        Debug(err)
    }
}
//特价金币
function tjjb(cookie) {
    // var DL_api = bucketGet("who-tong", "ql_APIDL")//代理开关功能
    h42_nc(`{"functionId":"MyAssetsService.execute","config":{"appId":"be221","appid":"jx_h5","version":"4.1","ua":"jdapp;iPhone;10.1.4;13.5;XM6DWDL787K7EJCAP8Z73OY3FBTK26JKY4PK1M7E;network/wifi;model/iPhone12,1;addressid/0;appBuild/167814;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1"},"body":{"method":"goldShopPage","data":{"channel":1},"sceneval":2,"buid":325,"appCode":"","time":1702819711663,"signStr":"e060832c71c3f6021dc0337211f7081e"}}`)

    try {
        let t = new Date().getTime()
        body = request({
            //  useproxy: true,
            //proxyAddr: "http://" + pro,
            //  proxyAddr: DL_api,
            method: "post",
            url: `https://api.m.jd.com/api?functionId=MyAssetsService.execute`,
            body: nc_h5,
            headers: {
                "Cookie": cookie,
                "Host": "https://gold.jd.com",
                "Origin": "https://gold.jd.com",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive",
                "User-Agent": nc_ua,
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://gold.jd.com/",
            },
            dataType: "json",
            timeOut: 30000
        })
        icons.push("jdicons/jdms.jpg")
        if (body.data.isLogin) {
            ltjb = body.data.balanceVO.goldBalance
            tjbi = ltjb / 10000
            msgs.push("【特价金币】" + ltjb + "金币≈" + tjbi.toFixed(2) + "元")
        } else if (body.data.isLogin == "true") {
            ltjb = body.data.balanceVO.goldBalance
            tjbi = ltjb / 10000
            msgs.push("【特价金币】" + ltjb + "金币≈" + tjbi.toFixed(2) + "元")
        }
    } catch (err) {
    }
}
//京东积分话费兑换
function hfjf(cookie) {
    try {
        let t = new Date().getTime()
        let encstr = call('md5')(t + "e9c398ffcb2d4824b4d0a703e38yffdd")
        body = request({
            method: "post",
            url: `https://dwapp.jd.com/user/dwSignInfo`,
            body: JSON.stringify({ "t": t, "encStr": encstr }),
            headers: {
                "Cookie": cookie,
                "Host": "dwapp.jd.com",
                "content-length": 63,
                "accept": "*/*",
                "origin": "https://mypoint.jd.com",
                "User-Agent": UserAgents(),
                "Content-Type": "application/json",
                "browser-type": 3,
                "referer": "https://mypoint.jd.com/",
                "referer": "https://prodev.m.jd.com/mall/active/eEcYM32eezJB7YX4SBihziJCiGV/index.html"
            },
            //dataType: "json",
            timeOut: 30000
        })
        data = JSON.parse(body)
        if (data.code == 200) {
            //sendText("【积分话费】"+data.data.totalNum+"分(兑换)")
            msgs.push("【积分话费】" + data.data.totalNum + "分")
        }
    } catch (err) {
        Debug(err)
    }
}
function totalBean(cookie) {
    try {
        request({
            url: "https://wq.jd.com/user/info/QueryJDUserInfo?sceneval=2",
            method: "post",
            headers: {
                "Accept": "application/json,text/plain, */*",
                "Content-Type": "application/x-www-form-urlencoded",
                //"Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-cn",
                "Connection": "keep-alive",
                "Cookie": cookie,
                "Referer": "https://wqs.jd.com/my/jingdou/my.shtml?sceneval=2",
                "User-Agent": UserAgents()
            }
        }, function (error, response, header, body) {
            Debug("检查账户总览数量是否有错误：" + error)
            if (!error) {
                obj = JSON.parse(body)
                Debug(JSON.stringify(obj))
                if (obj.retcode == 0) {
                    msgs.push("【东东账号】" + obj.base.curPin)
                    icons.push("jdicons/jdzh.jpg")
                    msgs.push("【账户昵称】" + obj.base.nickname)
                    // msgs.push("【绑定号码】" + obj.base.mobile)
                    //icons.push("jdicons/zhxy.jpg")

                    //msgs.push("【会员分值】" + obj.base.userLevel)
                    icons.push("jdicons/zhxx.jpg")
                    msgs.push("【京享分值】" + obj.base.jvalue)
                    icons.push("jdicons/bean.jpg")
                    msgs.push("【豆豆总量】" + obj.base.jdNum)
                    // msgs.push("【实名情况】" + obj.isRealNameAuth)
                }
            }
        })
    } catch (err) {
    }
}
//优惠券信息
function getCoupon(cookie) {
    try {
        request({
            url: "https://wq.jd.com/activeapi/queryjdcouponlistwithfinance?state=1&wxadd=1&filterswitch=1&_=" + Date.now() + "&sceneval=2&g_login_type=1&callback=jsonpCBKB&g_ty=ls",
            headers: {
                'authority': 'wq.jd.com',
                'User-Agent': UserAgents(),
                'accept': '*/*',
                'referer': 'https://wqs.jd.com/',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'cookie': cookie
            },
            timeout: 10000
        }, function (error, response, header, body) {
            Debug("优惠券信息：" + error)
            if (!error) {
                YunFeiTitle = "";
                YunFeiQuan = 0;
                YunFeiQuanEndTime = "";
                YunFeiTitle2 = "";
                YunFeiQuan2 = 0;
                YunFeiQuanEndTime2 = "";

                data = JSON.parse(body.match(new RegExp(/jsonpCBK.?\((.*);*/))[1]);

                let useable = data.coupon.useable;

                todayEndTime = new Date(new Date(new Date().getTime()).setHours(23, 59, 59, 999)).getTime();

                tomorrowEndTime = new Date(new Date(new Date().getTime() + 24 * 60 * 60 * 1000).setHours(23, 59, 59, 999)).getTime();
                platFormInfo = "";

                Debug("优惠券数量：" + useable.length);

                cpKind = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                cpStyle = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                cpType = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                for (let i = 0; i < useable.length; i++) {
                    cpKind[useable[i].couponKind]++
                    cpStyle[useable[i].couponStyle]++
                    cpType[useable[i].coupontype]++
                }
                let message = ""
                message = "【券券明细】"
                if (cpStyle[3] > 0) {
                    message += cpStyle[3] + "京券 "
                }
                if (cpStyle[0] > 0) {
                    message += cpStyle[0] + "东券 "
                }
                if (cpStyle[2] > 0) {
                    message += cpStyle[2] + "运费券 "
                }
                if (cpStyle[8] > 0) {
                    message += cpStyle[8] + "支付券 "
                }

                icons.push("jdicons/jscoin.jpg")
                msgs.push(message)

                for (let i = 0; i < useable.length; i++) {
                    if (useable[i].limitStr.indexOf('全品类') > -1) {
                        beginTime = useable[i].beginTime;
                        if (beginTime < new Date().getTime() && useable[i].quota <= 100 && useable[i].coupontype == 1) {
                            couponName = useable[i].limitStr;
                            if (useable[i].platFormInfo) {
                                platFormInfo = useable[i].platFormInfo;
                            }
                            var decquota = parseFloat(useable[i].quota).toFixed(2);
                            var decdisc = parseFloat(useable[i].discount).toFixed(2);
                            let mssage = "【全品类券】满" + decquota + "减" + decdisc + "元";
                            if (useable[i].endTime < todayEndTime) {
                                mssage += "(今日过期," + platFormInfo + ")";
                            } else if (useable[i].endTime < tomorrowEndTime) {
                                mssage += "(明日过期," + platFormInfo + ")";
                            } else {
                                mssage += "(" + platFormInfo + ")";
                            }
                            icons.push("jdicons/jscoin.jpg")
                            msgs.push(mssage)
                        }
                    }

                    if (useable[i].couponTitle.indexOf('运费券') > -1 && useable[i].limitStr.indexOf('自营商品运费') > -1) {
                        if (!YunFeiTitle) {
                            YunFeiTitle = useable[i].couponTitle;
                            YunFeiQuanEndTime = unixTimeFmt(parseInt(useable[i].endTime) / 1000, 0, 'yyyy-MM-dd');
                            //Debug(YunFeiQuanEndTime)
                            YunFeiQuan += 1;
                        } else {
                            if (YunFeiTitle == useable[i].couponTitle) {
                                YunFeiQuanEndTime = unixTimeFmt(parseInt(useable[i].endTime) / 1000, 0, 'yyyy-MM-dd');
                                //Debug(YunFeiQuanEndTime)
                                YunFeiQuan += 1;
                            } else {
                                if (!YunFeiTitle2)
                                    YunFeiTitle2 = useable[i].couponTitle;
                                if (YunFeiTitle2 == useable[i].couponTitle) {
                                    YunFeiQuanEndTime2 = unixTimeFmt(parseInt(useable[i].endTime) / 1000, 0, 'yyyy-MM-dd');
                                    YunFeiQuan2 += 1;
                                }
                            }
                        }
                    }

                    if (useable[i].couponTitle.indexOf('特价版APP活动') > -1 && useable[i].limitStr == '仅可购买活动商品') {
                        beginTime = useable[i].beginTime;
                        if (beginTime < new Date().getTime() && useable[i].coupontype == 1) {
                            if (useable[i].platFormInfo) {
                                platFormInfo = useable[i].platFormInfo;
                            }
                            var decquota = parseFloat(useable[i].quota).toFixed(2);
                            var decdisc = parseFloat(useable[i].discount).toFixed(2);
                            let mssage = "【特价版券】满" + decquota + "减" + decdisc + "元";
                            if (useable[i].endTime < todayEndTime) {
                                mssage += "(今日过期," + platFormInfo + ")\n";
                            } else if (useable[i].endTime < tomorrowEndTime) {
                                mssage += "(明日过期," + platFormInfo + ")\n";
                            } else {
                                mssage += "(" + platFormInfo + ")\n";
                            }
                            icons.push("jdicons/jscoin.jpg")
                            msgs.push(mssage)
                        }
                    }


                    if (useable[i].couponStyle == 7 || useable[i].couponStyle == 8) {
                        let mssage = ""
                        beginTime = useable[i].beginTime;
                        if (beginTime > new Date().getTime() || useable[i].quota > 50 || useable[i].coupontype != 1) {
                            continue;
                        }
                        if (useable[i].couponStyle == 8) {
                            couponType = "【支付立减】";
                        } else {
                            couponType = "【白条优惠】";
                        }
                        if (useable[i].discount < useable[i].quota)
                            mssage += couponType + ":满" + useable[i].quota + "减" + useable[i].discount + "元";
                        else
                            mssage += couponType + ":立减" + useable[i].discount + "元";
                        if (useable[i].platFormInfo)
                            platFormInfo = useable[i].platFormInfo;

                        if (useable[i].endTime < todayEndTime) {
                            mssage += "(今日过期," + platFormInfo + ")";
                        } else if (useable[i].endTime < tomorrowEndTime) {
                            mssage += "(明日将过期," + platFormInfo + ")";
                        } else {
                            mssage += "(" + platFormInfo + ")";
                        }
                        icons.push("jdicons/jscoin.jpg")
                        msgs.push(mssage)
                    }
                }
                if (YunFeiQuan > 0) {
                    icons.push("jdicons/jscoin.jpg")
                    msgs.push("【免运费券】" + YunFeiQuan + "(有效期至：" + YunFeiQuanEndTime + ")")
                }
                if (YunFeiQuan2 > 0) {
                    icons.push("jdicons/jscoin.jpg")
                    msgs.push("【免运费券】" + YunFeiQuan2 + "(有效期至：" + YunFeiQuanEndTime2 + ")")
                }
            }

        })
    } catch (err) {
    }
}
//检查账号
function jd_ck(cookie) {
    try {
        let t = new Date().getTime()
        body = request({
            method: "post",
            url: `https://api.m.jd.com/?functionId=MyAssetsService.execute&appid=market-task-h5`,
            body: `functionId=MyAssetsService.execute&body={"method":"goldShopPage","data":{"channel":1}}&_t=` + t + `&appid=market-task-h5`,
            headers: {
                "Cookie": cookie,
                "Host": "https://gold.jd.com",
                "Origin": "https://gold.jd.com",
                "Accept": "application/json, text/plain, */*",
                "Connection": "keep-alive",
                "User-Agent": UserAgents(),
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://gold.jd.com/",
            },
            dataType: "json",
            timeOut: 30000
        })
        if (body.data.isLogin) {
            return true
        } else if (body.data.isLogin == "true") {
            return true
        } else {
            return false
        }
    } catch (err) {
    }
}
//种豆得豆
function plantBean(cookie, kg) {
    try {
        var DL_api = bucketGet("who-tong", "ql_APIDL")//代理开关功能
        h42_nc(`{"functionId":"plantBeanIndex","config":{"appId":"d246a","appid":"signed_wh5","version":"3.1","ua":"jdapp;iPhone;10.1.4;13.5;XM6DWDL787K7EJCAP8Z73OY3FBTK26JKY4PK1M7E;network/wifi;model/iPhone12,1;addressid/0;appBuild/167814;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1"},"body":{"monitor_source":"plant_m_plant_index","monitor_refer":"","version":"9.2.4.3"}}`)
        body = request({
            useproxy: kg,
            proxyAddr: DL_api,
            method: "get",
            url: `https://api.m.jd.com/client.action?` + nc_h5 + `ext={"prstate":"0"}&aid=64effbeff0217b1f&uemps=0-2-999`,
            headers: {
                "Cookie": cookie,
                "Host": "api.m.jd.com",
                "Accept": "*/*",
                "User-Agent": nc_ua,
                "Content-Type": "application/json",
                "Referer": "https://plantearth.jd.com/",
            },
            dataType: "json",
            timeOut: 30000
        })
        if (body.code == 0) {
            if (typeof body.data.roundList !== "undefined") {
                let roundList = JSON.stringify(body.data.roundList)
                roundList = JSON.parse(roundList)
                icons.push("jdicons/ddnc.jpg")
                msgs.push("【种豆得豆】" + roundList[0].dateDesc + ",成长值:" + roundList[0].growth + ",获得京豆:" + roundList[0].awardBeans + "\n" + roundList[1].dateDesc + ",成长值:" + roundList[1].growth)
            }
        }
    } catch (err) {
    }
}

//新版农村
function farm_home(cookie, kg) {
    var DL_api = bucketGet("otto", "ql_APIDL")//代理开关功能
    var pina = cookie.match(/(?<=pt_pin=)[^;]+/g)
    for (let k = 0; k < 2; k++) {
        //try {
        let config = {
            "appId": "c57f6",
            "appid": "signed_wh5",
            "version": "4.2",
            "ua": "jdapp;iPhone;10.1.4;13.5;XM6DWDL787K7EJCAP8Z73OY3FBTK26JKY4PK1M7E;network/wifi;model/iPhone12,1;addressid/0;appBuild/167814;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1"
        }
        let bodya = {
            "version": 1
        }
        let home = { "config": config, "body": bodya, "functionId": "farm_home" }
        h5st_nc(home)
        let body = request({
            useproxy: kg,
            proxyAddr: DL_api,
            url: `https://api.m.jd.com/client.action`,
            method: "post",
            body: nc_h5,
            headers: {
                "Host": "api.m.jd.com",
                // "content-length": "1348",
                "accept": "application/json, text/plain, */*",
                "x-rp-client": "h5_1.0.0",
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": nc_ua,
                "x-referer-page": "https://h5.m.jd.com/pb/015686010/Bc9WX7MpCW7nW9QjZ5N3fFeJXMH/index.html",
                "origin": "https://h5.m.jd.com",
                "x-requested-with": "com.jingdong.app.mall",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://h5.m.jd.com/",
                //"accept-encoding": "gzip, deflate, br",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": cookie,
            },
            dataType: "json",
            timeOut: 80000
        })
        Debug("检查新版农场的数据：" + JSON.stringify(body))
        if (body.code == 0) {
            if (body.data.bizCode == 0) {
                k=3
                if (typeof body.data.result.skuName !== "undefined") {
                    icons.push("jdicons/ddnc.jpg")
                    msgs.push("【新农场种植】" + body.data.result.skuName)
                    icons.push("jdicons/ddnc.jpg")
                    msgs.push("【新农场进度】" + body.data.result.treeFullStage + "/5，" + body.data.result.waterTips)
                    if (bucketGet("jd_cookie", "enable_bill") == "true") {
                        icons.push("jdicons/ddnc.jpg")
                        msgs.push("【新农场水滴】" + body.data.result.bottleWater)
                    } else {
                        msgs.push("【新农场水滴】" + body.data.result.bottleWater + "💧")
                    }
                    var dh_code = get("dh_code")//代理开关功能
                    if (dh_code == "true" || dh_code == true) {
                        var txfs = bucketGet("Fruit_new", pina)
                        if (txfs == "" || txfs == null) {
                            sendText("未收集过新版农场助力码-助力码是：" + body.data.result.farmHomeShare.inviteCode)
                            bucketSet("Fruit_new", pina, body.data.result.farmHomeShare.inviteCode)
                        }
                    }
                } else {
                    msgs.push("【新农场种植】未种植")
                    
                }

            }
        }
        //  } catch (err) {
        // }
    }
}
function h5st_nc(home) {
    var DL_kg = get("h5st")//代理开关功能
    if (DL_kg == "true") {
        h5st_url = `http://110.40.165.213:3004/home`
    } else {
        h5st_url = `http://110.40.165.213:3000/home`
    }
    let body = request({
        url: h5st_url,
        method: "post",
        body: home,
        headers: {
            "Content-Type": "application/json",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    if (body) {
        if (body.code = 200) {
            nc_h5 = body.data
            nc_ua = body.ua
        }
        return true
    } else {
        return false
    }
}

//京东E卡
function UserCard(cookie) {
    h42_nc(`{"functionId":"queryChannelUserCard","config":{"appId":"aea58","appid":"mygiftcard","version":"4.1","ua":"jdapp;iPhone;10.1.4;13.5;XM6DWDL787K7EJCAP8Z73OY3FBTK26JKY4PK1M7E;network/wifi;model/iPhone12,1;addressid/0;appBuild/167814;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1"},"body":{}}`)
    try {
        body = request({
            method: "post",
            url: `https://api.m.jd.com/api?functionId=queryChannelUserCard`,
            body: nc_h5,
            headers: {
                "Host": "api.m.jd.com",
                "content-length": "1012",
                "accept": "application/json, text/plain, */*",
                "x-rp-client": "h5_1.0.0",
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": nc_ua,
                "x-referer-page": "https://o.jd.com/",
                "origin": "https://o.jd.com",
                "x-requested-with": "com.jingdong.app.mall",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://o.jd.com/",
                //"accept-encoding": "gzip, deflate, br",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": cookie,
            },
            dataType: "json",
            timeOut: 90000
        })
        if (body.code == "000000") {
            if (body.data.totalAmount == "0.00") {
                Debug("礼卡内没有余额？")
            } else {
                icons.push("jdicons/jscoin.jpg")
                msgs.push("【礼卡余额】" + body.data.totalAmount + "R")
            }

        }
    } catch (err) {
    }
}
//东东农场
function xin_h5(h5_body) {
    var DL_kg = get("h5st")//代理开关功能
    if (DL_kg == "true") {
        h5st_url = `http://110.40.165.213:3004/getForFarm`
    } else {
        h5st_url = `http://110.40.165.213:3000/getForFarm`
    }
    let body = request({
        url: h5st_url,
        method: "post",
        body: h5_body,
        headers: {
            "Content-Type": "application/json",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    if (body) {
        if (body.code = 200) {
            nc_h5 = body.data
        }
        return true
    } else {
        return false
    }
}
function xin_ua() {
    nc_h5 = ""
    nc_ua = ""
    var DL_kg = get("h5st")//代理开关功能
    if (DL_kg == "true") {
        h5st_url = `http://110.40.165.213:3004/UA`
    } else {
        h5st_url = `http://110.40.165.213:3000/UA`
    }
    let body = request({
        url: h5st_url,
        method: "post",
        body: {},
        headers: {
            "Content-Type": "application/json",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    if (body) {
        if (body.code = 200) {
            nc_ua = body.data
            var ucxa = nc_ua.split(";")
            //sendText(ucxa[2])
            h5_ver = ucxa[2]
        }
        return true
    } else {
        return false
    }
}
function getJdFruit(cookie,kg) {
    var DL_api = bucketGet("who-tong", "ql_APIDL")//代理开关功能
    var pina = cookie.match(/(?<=pt_pin=)[^;]+/g)

    for (let k = 0; k < 2; k++) {
        xin_ua()
        try {
            let bodya = {
                version: 24,
                channel: 1,
                babelChannel: "121",
                lat: "0",
                lng: "0"
            }
            let home = { appId: "8a2af", "fn": "initForFarm", "body": bodya, apid: "signed_wh5", ver: String(h5_ver), "cl": "ios", "user": String(pina), "code": 1, ua: nc_ua }
            xin_h5(home)
            request({
                useproxy: kg,
                proxyAddr: DL_api,
                url: "https://api.m.jd.com/client.action",
                method: "post",
                body: nc_h5,
                headers: {
                    "accept": "*/*",
                    "Host": "api.m.jd.com",
                    "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "x-requested-with": "com.jingdong.app.mall",
                    "cookie": cookie,
                    "origin": "https://carry.m.jd.com",
                    "referer": "https://carry.m.jd.com/",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                    'User-Agent': nc_ua,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                timeout: 80000
            }, function (error, response, header, body) {
                let obj = JSON.parse(body)
                Debug("检查东东农场的数据：" + JSON.stringify(obj.farmUserPro))
                if (!error) {
                    if (obj.code == "0" || obj.code == "0") {
                        if (typeof obj.farmUserPro !== "undefined") {
                            var zlms = obj.farmUserPro.shareCode
                            ojbk = 100 * obj.farmUserPro.treeEnergy / obj.farmUserPro.treeTotalEnergy
                            objk = Math.round(ojbk)
                            icons.push("jdicons/ddnc.jpg")
                            if (objk.toFixed(2) == "100.00" || objk.toFixed(2) == 100.00) {
                                msgs.push("【东东农场】" + obj.farmUserPro.name + ",水果成熟了")
                            } else if (obj.farmUserPro.treeEnergy == "6000" || obj.farmUserPro.treeEnergy == 6000) {
                                msgs.push("【东东农场】" + obj.farmUserPro.name + ",水果成熟了")
                            } else {
                                msgs.push("【东东农场】" + obj.farmUserPro.name + "(" + objk.toFixed(2) + "%)")
                            }
                            icons.push("jdicons/ddnc.jpg")
                            msgs.push("【剩余水滴】" + obj.farmUserPro.totalEnergy + "💧")
                            var dh_code = get("dh_code")//代理开关功能
                            if (dh_code == "true" || dh_code == true) {
                                //收集助力码部分
                                var txfs = bucketGet("Fruit", pina)
                                if (txfs == "" || txfs == null) {
                                    sendText("未收集过旧版农场助力码-助力码是：" + zlms)
                                    bucketSet("Fruit", pina, zlms)
                                }
                            }
                            //结束收集助力码代码
                            k = 5
                        }
                    }
                } else {
                    Debug("农场查询失败")
                }
            })
            sleep(500)
        } catch (err) {
        }
    }
}
//天天领红包小程序版
function MiniTask(cookie, kg) {
    var DL_api = bucketGet("who-tong", "ql_APIDL")//代理开关功能
    var pina = cookie.match(/(?<=pt_pin=)[^;]+/g)

    xin_ua()
    try {

        let home = { "appId": "60d61", "fn": "MiniTask_ChannelPage", "body": {}, "apid": "hot_channel", "ver": String(h5_ver), "cl": "android", "user": String(pina), "code": 1, "ua": nc_ua }
        xin_h5(home)
        request({
            useproxy: kg,
            proxyAddr: DL_api,
            url: "https://api.m.jd.com/MiniTask_ChannelPage?" + nc_h5,
            method: "post",
            //body: nc_h5,
            headers: {
                "Host": "api.m.jd.com",
                "Referer": "https://servicewechat.com/wx91d27dbf599dff74/745/page-frame.html",
                "User-Agent": nc_ua,
                "cookie": cookie + "wxapp_type=1;wxapp_version=9.15.10;wxapp_scene=1089;cid=5;gender=0;province=;city=;country=;nickName=" + pina + ";"
            },
            timeout: 80000
        }, function (error, response, header, body) {
            let obj = JSON.parse(body)
            Debug("天天领红包小程序版：" + JSON.stringify(obj))
            if (!error) {
                if (obj.code == "0" || obj.code == "0") {
                    var pont = obj.data.point / 1000
                    msgs.push("【省钱金币】" + obj.data.point + "金币≈" + pont.toFixed(2) + "元")
                } else {
                    sleep(1000)
                }
            } else {
                Debug("农场查询失败")
            }
        })
        sleep(1000)
    } catch (err) {
    }
}
function proxy() {
    var DL_api = get("ql_APIDL")//代理开关功能
    let body = request({
        url: DL_api,
        method: "get",
        // body: water,
        headers: {
            //"Host": "h5.xss333.top:8001",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        dataType: "text",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })
    //  sendText(body)
    return body
}

var USER_AGENTS = [
    "jdltapp;iPad;3.7.0;14.4;network/wifi;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;2346663656561603-4353564623932316;network/wifi;model/ONEPLUS A5010;addressid/0;aid/2dfceea045ed292a;oaid/;osVer/29;appBuild/1436;psn/BS6Y9SAiw0IpJ4ro7rjSOkCRZTgR3z2K|10;psq/5;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/10.5;jdv/;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/oppo;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ONEPLUS A5010 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.1;59d6ae6e8387bd09fe046d5b8918ead51614e80a;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone12,1;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/;pv/1.26;apprpd/;ref/JDLTSubMainPageViewController;psq/0;ads/;psn/59d6ae6e8387bd09fe046d5b8918ead51614e80a|3;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.1;Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;13.5;22d679c006bf9c087abf362cf1d2e0020ebb8798;network/wifi;ADID/10857A57-DDF8-4A0D-A548-7B8F43AC77EE;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone12,1;addressid/2378947694;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/15.7;apprpd/Allowance_Registered;ref/JDLTTaskCenterViewController;psq/6;ads/;psn/22d679c006bf9c087abf362cf1d2e0020ebb8798|22;jdv/0|kong|t_1000170135|tuiguang|notset|1614153044558|1614153044;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;2616935633265383-5333463636261326;network/UNKNOWN;model/M2007J3SC;addressid/1840745247;aid/ba9e3b5853dccb1b;oaid/371d8af7dd71e8d5;osVer/29;appBuild/1436;psn/t7JmxZUXGkimd4f9Jdul2jEeuYLwxPrm|8;psq/6;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/5.6;jdv/;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/xiaomi;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 10; M2007J3SC Build/QKQ1.200419.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045135 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.3;d7beab54ae7758fa896c193b49470204fbb8fce9;network/4g;ADID/97AD46C9-6D49-4642-BF6F-689256673906;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;9;D246836333735-3264353430393;network/4g;model/MIX 2;addressid/138678023;aid/bf8bcf1214b3832a;oaid/308540d1f1feb2f5;osVer/28;appBuild/1436;psn/Z/rGqfWBY/h5gcGFnVIsRw==|16;psq/3;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 9;osv/9;pv/13.7;jdv/;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/xiaomi;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 9; MIX 2 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045135 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.4;eb5a9e7e596e262b4ffb3b6b5c830984c8a5c0d5;network/wifi;ADID/5603541B-30C1-4B5C-A782-20D0B569D810;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,2;addressid/1041002757;hasOCPay/0;appBuild/101;supportBestPay/0;pv/34.6;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/5;ads/;psn/eb5a9e7e596e262b4ffb3b6b5c830984c8a5c0d5|44;jdv/0|androidapp|t_335139774|appshare|CopyURL|1612612940307|1612612944;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;21631ed983b3e854a3154b0336413825ad0d6783;network/3g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,4;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.47;apprpd/;ref/JDLTSubMainPageViewController;psq/8;ads/;psn/21631ed983b3e854a3154b0336413825ad0d6783|9;jdv/0|direct|-|none|-|1614150725100|1614225882;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;13.5;500a795cb2abae60b877ee4a1930557a800bef1c;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone8,1;addressid/669949466;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/9.11;apprpd/;ref/JDLTSubMainPageViewController;psq/10;ads/;psn/500a795cb2abae60b877ee4a1930557a800bef1c|11;jdv/;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPad;3.7.0;14.4;f5e7b7980fb50efc9c294ac38653c1584846c3db;network/wifi;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPad6,3;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/231.11;pap/JA2020_3112531|3.7.0|IOS 14.4;apprpd/;psn/f5e7b7980fb50efc9c294ac38653c1584846c3db|305;usc/kong;jdv/0|kong|t_1000170135|tuiguang|notset|1613606450668|1613606450;umd/tuiguang;psq/2;ucp/t_1000170135;app_device/IOS;utr/notset;ref/JDLTRedPacketViewController;adk/;ads/;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;19fef5419f88076c43f5317eabe20121d52c6a61;network/wifi;ADID/00000000-0000-0000-0000-000000000000;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,8;addressid/3430850943;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/10.4;apprpd/;ref/JDLTSubMainPageViewController;psq/3;ads/;psn/19fef5419f88076c43f5317eabe20121d52c6a61|16;jdv/0|kong|t_1001327829_|jingfen|f51febe09dd64b20b06bc6ef4c1ad790#/|1614096460311|1614096511;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "jdltapp;iPhone;3.7.0;12.2;f995bc883282f7c7ea9d7f32da3f658127aa36c7;network/4g;ADID/9F40F4CA-EA7C-4F2E-8E09-97A66901D83E;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,4;addressid/525064695;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/11.11;apprpd/;ref/JDLTSubMainPageViewController;psq/2;ads/;psn/f995bc883282f7c7ea9d7f32da3f658127aa36c7|22;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 12.2;Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;5366566313931326-6633931643233693;network/wifi;model/Mi9 Pro 5G;addressid/0;aid/5fe6191bf39a42c9;oaid/e3a9473ef6699f75;osVer/29;appBuild/1436;psn/b3rJlGi AwLqa9AqX7Vp0jv4T7XPMa0o|5;psq/4;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/5.4;jdv/;ref/HomeFragment;partner/xiaomi;apprpd/Home_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; Mi9 Pro 5G Build/QKQ1.190825.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045135 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.4;4e6b46913a2e18dd06d6d69843ee4cdd8e033bc1;network/3g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,2;addressid/666624049;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/54.11;apprpd/MessageCenter_MessageMerge;ref/MessageCenterController;psq/10;ads/;psn/4e6b46913a2e18dd06d6d69843ee4cdd8e033bc1|101;jdv/0|kong|t_2010804675_|jingfen|810dab1ba2c04b8588c5aa5a0d44c4bd|1614183499;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.2;c71b599e9a0bcbd8d1ad924d85b5715530efad06;network/wifi;ADID/751C6E92-FD10-4323-B37C-187FD0CF0551;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,8;addressid/4053561885;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/263.8;apprpd/;ref/JDLTSubMainPageViewController;psq/2;ads/;psn/c71b599e9a0bcbd8d1ad924d85b5715530efad06|481;jdv/0|kong|t_1001610202_|jingfen|3911bea7ee2f4fcf8d11fdf663192bbe|1614157052210|1614157056;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.2;Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;2d306ee3cacd2c02560627a5113817ebea20a2c9;network/4g;ADID/A346F099-3182-4889-9A62-2B3C28AB861E;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,3;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/;pv/1.35;apprpd/Allowance_Registered;ref/JDLTTaskCenterViewController;psq/0;ads/;psn/2d306ee3cacd2c02560627a5113817ebea20a2c9|2;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;28355aff16cec8bcf3e5728dbbc9725656d8c2c2;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,2;addressid/833058617;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.10;apprpd/;ref/JDLTWebViewController;psq/9;ads/;psn/28355aff16cec8bcf3e5728dbbc9725656d8c2c2|5;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;13.5;24ddac73a3de1b91816b7aedef53e97c4c313733;network/4g;ADID/598C6841-76AC-4512-AA97-CBA940548D70;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone11,6;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/12.6;apprpd/;ref/JDLTSubMainPageViewController;psq/5;ads/;psn/24ddac73a3de1b91816b7aedef53e97c4c313733|23;jdv/0|kong|t_1000170135|tuiguang|notset|1614126110904|1614126110;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;d7732ba60c8ff73cc3f5ba7290a3aa9551f73a1b;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone12,1;addressid/25239372;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/8.6;apprpd/;ref/JDLTSubMainPageViewController;psq/5;ads/;psn/d7732ba60c8ff73cc3f5ba7290a3aa9551f73a1b|14;jdv/0|kong|t_1001226363_|jingfen|5713234d1e1e4893b92b2de2cb32484d|1614182989528|1614182992;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;ca1a32afca36bc9fb37fd03f18e653bce53eaca5;network/wifi;ADID/3AF380AB-CB74-4FE6-9E7C-967693863CA3;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone8,1;addressid/138323416;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/72.12;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/ca1a32afca36bc9fb37fd03f18e653bce53eaca5|109;jdv/0|kong|t_1000536212_|jingfen|c82bfa19e33a4269a5884ffc614790f4|1614141246;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;7346933333666353-8333366646039373;network/wifi;model/ONEPLUS A5010;addressid/138117973;aid/7d933f6583cfd097;oaid/;osVer/29;appBuild/1436;psn/T/eqfRSwp8VKEvvXyEunq09Cg2MUkiQ5|17;psq/4;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/11.4;jdv/0|kong|t_1001849073_|jingfen|495a47f6c0b8431c9d460f61ad2304dc|1614084403978|1614084407;ref/HomeFragment;partner/oppo;apprpd/Home_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ONEPLUS A5010 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
    "jdltapp;android;3.7.0;11;4626269356736353-5353236346334673;network/wifi;model/M2006J10C;addressid/0;aid/dbb9e7655526d3d7;oaid/66a7af49362987b0;osVer/30;appBuild/1436;psn/rQRQgJ 4 S3qkq8YDl28y6jkUHmI/rlX|3;psq/4;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 11;osv/11;pv/3.4;jdv/;ref/HomeFragment;partner/xiaomi;apprpd/Home_Main;eufv/1;Mozilla/5.0 (Linux; Android 11; M2006J10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045513 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.4;78fc1d919de0c8c2de15725eff508d8ab14f9c82;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,1;addressid/137829713;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/23.11;apprpd/;ref/JDLTSubMainPageViewController;psq/10;ads/;psn/78fc1d919de0c8c2de15725eff508d8ab14f9c82|34;jdv/0|iosapp|t_335139774|appshare|Wxfriends|1612508702380|1612534293;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;0373263343266633-5663030363465326;network/wifi;model/Redmi Note 7;addressid/590846082;aid/07b34bf3e6006d5b;oaid/17975a142e67ec92;osVer/29;appBuild/1436;psn/OHNqtdhQKv1okyh7rB3HxjwI00ixJMNG|4;psq/3;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/2.3;jdv/;ref/activityId=8a8fabf3cccb417f8e691b6774938bc2;partner/xiaomi;apprpd/jsbqd_home;eufv/1;Mozilla/5.0 (Linux; Android 10; Redmi Note 7 Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Mobile Safari/537.36",
    "jdltapp;android;3.7.0;10;3636566623663623-1693635613166646;network/wifi;model/ASUS_I001DA;addressid/1397761133;aid/ccef2fc2a96e1afd;oaid/;osVer/29;appBuild/1436;psn/T8087T0D82PHzJ4VUMGFrfB9dw4gUnKG|76;psq/5;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/73.5;jdv/0|kong|t_1002354188_|jingfen|2335e043b3344107a2750a781fde9a2e#/|1614097081426|1614097087;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/yingyongbao;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ASUS_I001DA Build/QKQ1.190825.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,2;addressid/138419019;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/5.7;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/6;ads/;psn/4ee6af0db48fd605adb69b63f00fcbb51c2fc3f0|9;jdv/0|direct|-|none|-|1613705981655|1613823229;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;network/wifi;ADID/F9FD7728-2956-4DD1-8EDD-58B07950864C;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,1;addressid/1346909722;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/30.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/40d4d4323eb3987226cae367d6b0d8be50f2c7b3|39;jdv/0|kong|t_1000252057_0|tuiguang|eba7648a0f4445aa9cfa6f35c6f36e15|1613995717959|1613995723;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;ADID/5D306F0D-A131-4B26-947E-166CCB9BFFFF;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,6;addressid/138164461;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/7.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/d40e5d4a33c100e8527f779557c347569b49c304|7;jdv/0|kong|t_1001226363_|jingfen|3bf5372cb9cd445bbb270b8bc9a34f00|1608439066693|1608439068;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPad;3.7.0;14.5;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPad8,9;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/;pv/1.20;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/5;ads/;psn/d9f5ddaa0160a20f32fb2c8bfd174fae7993c1b4|3;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.5;Mozilla/5.0 (iPad; CPU OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;network/wifi;ADID/31548A9C-8A01-469A-B148-E7D841C91FD0;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/10.5;apprpd/;ref/JDLTSubMainPageViewController;psq/4;ads/;psn/a858fb4b40e432ea32f80729916e6c3e910bb922|12;jdv/0|direct|-|none|-|1613898710373|1613898712;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;13.5;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,2;addressid/2237496805;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/13.6;apprpd/;ref/JDLTSubMainPageViewController;psq/5;ads/;psn/48e495dcf5dc398b4d46b27e9f15a2b427a154aa|15;jdv/0|direct|-|none|-|1613354874698|1613952828;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;3346332626262353-1666434336539336;network/wifi;model/ONEPLUS A6000;addressid/0;aid/3d3bbb25af44c59c;oaid/;osVer/29;appBuild/1436;psn/ECbc2EqmdSa7mDF1PS1GSrV/Tn7R1LS1|6;psq/8;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/2.67;jdv/0|direct|-|none|-|1613822479379|1613991194;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/oppo;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ONEPLUS A6000 Build/QKQ1.190716.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
    "jdltapp;android;3.7.0;8.1.0;8363834353530333132333132373-43D2930366035323639333662383;network/wifi;model/16th Plus;addressid/0;aid/f909e5f2c464c7c6;oaid/;osVer/27;appBuild/1436;psn/c21YWvVr77Hn6 pOZfxXGY4TZrre1 UOL5hcPbCEDMo=|3;psq/10;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 8.1.0;osv/8.1.0;pv/2.15;jdv/;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/jsxdlyqj09;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 8.1.0; 16th Plus Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045514 Mobile Safari/537.36",
    "jdltapp;android;3.7.0;11;1343467336264693-3343562673463613;network/wifi;model/Mi 10 Pro;addressid/0;aid/14d7cbd934eb7dc1;oaid/335f198546eb3141;osVer/30;appBuild/1436;psn/ZcQh/Wov sNYfZ6JUjTIUBu28 KT0T3u|1;psq/24;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 11;osv/11;pv/1.24;jdv/;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/xiaomi;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 11; Mi 10 Pro Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 Mobile Safari/537.36",
    "jdltapp;android;3.7.0;10;8353636393732346-6646931673935346;network/wifi;model/MI 8;addressid/1969998059;aid/8566972dfd9a795d;oaid/4a8b773c3e307386;osVer/29;appBuild/1436;psn/PhYbUtCsCJo r 1b8hwxjnY8rEv5S8XC|383;psq/14;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/374.14;jdv/0|iosapp|t_335139774|liteshare|CopyURL|1609306590175|1609306596;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/jsxdlyqj09;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.4;6d343c58764a908d4fa56609da4cb3a5cc1396d3;network/wifi;ADID/4965D884-3E61-4C4E-AEA7-9A8CE3742DA7;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,1;addressid/70390480;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.24;apprpd/MyJD_Main;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fafter%2Findex.action%3FcategoryId%3D600%26v%3D6%26entry%3Dm_self_jd;psq/4;ads/;psn/6d343c58764a908d4fa56609da4cb3a5cc1396d3|17;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;13.6.1;4606ddccdfe8f343f8137de7fea7f91fc4aef3a3;network/4g;ADID/C6FB6E20-D334-45FA-818A-7A4C58305202;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone10,1;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/5.9;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/8;ads/;psn/4606ddccdfe8f343f8137de7fea7f91fc4aef3a3|5;jdv/0|iosapp|t_335139774|liteshare|Qqfriends|1614206359106|1614206366;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.6.1;Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;3b6e79334551fc6f31952d338b996789d157c4e8;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,1;addressid/138051400;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/14.34;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/12;ads/;psn/3b6e79334551fc6f31952d338b996789d157c4e8|46;jdv/0|kong|t_1001707023_|jingfen|e80d7173a4264f4c9a3addcac7da8b5d|1613837384708|1613858760;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;1346235693831363-2373837393932673;network/wifi;model/LYA-AL00;addressid/3321567203;aid/1d2e9816278799b7;oaid/00000000-0000-0000-0000-000000000000;osVer/29;appBuild/1436;psn/45VUZFTZJkhP5fAXbeBoQ0   O2GCB I|7;psq/5;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/5.8;jdv/0|iosapp|t_335139774|liteshare|CopyURL|1614066210320|1614066219;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/huawei;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; LYA-AL00 Build/HUAWEILYA-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.3;c2a8854e622a1b17a6c56c789f832f9d78ef1ba7;network/wifi;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPhone12,5;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/3.9;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/8;ads/;psn/c2a8854e622a1b17a6c56c789f832f9d78ef1ba7|6;jdv/0|direct|-|none|-|1613541016735|1613823566;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;9;;network/wifi;model/MIX 2S;addressid/;aid/f87efed6d9ed3c65;oaid/94739128ef9dd245;osVer/28;appBuild/1436;psn/R7wD/OWkQjYWxax1pDV6kTIDFPJCUid7C/nl2hHnUuI=|3;psq/13;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 9;osv/9;pv/1.42;jdv/;ref/activityId=8a8fabf3cccb417f8e691b6774938bc2;partner/xiaomi;apprpd/jsbqd_home;eufv/1;Mozilla/5.0 (Linux; Android 9; MIX 2S Build/PKQ1.180729.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;network/wifi;Mozilla/5.0 (Linux; Android 10; Redmi Note 7 Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.4;network/3g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "jdltapp;iPad;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/1;lang/zh_CN;model/iPad6,3;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/231.11;pap/JA2020_3112531|3.7.0|IOS 14.4;apprpd/;psn/f5e7b7980fb50efc9c294ac38653c1584846c3db|305;usc/kong;jdv/0|kong|t_1000170135|tuiguang|notset|1613606450668|1613606450;umd/tuiguang;psq/2;ucp/t_1000170135;app_device/IOS;utr/notset;ref/JDLTRedPacketViewController;adk/;ads/;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;13.5;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone8,1;addressid/669949466;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/9.11;apprpd/;ref/JDLTSubMainPageViewController;psq/10;ads/;psn/500a795cb2abae60b877ee4a1930557a800bef1c|11;jdv/;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;network/3g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,4;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.47;apprpd/;ref/JDLTSubMainPageViewController;psq/8;ads/;psn/21631ed983b3e854a3154b0336413825ad0d6783|9;jdv/0|direct|-|none|-|1614150725100|1614225882;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;network/3g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,4;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.47;apprpd/;ref/JDLTSubMainPageViewController;psq/8;ads/;psn/21631ed983b3e854a3154b0336413825ad0d6783|9;jdv/0|direct|-|none|-|1614150725100|1614225882;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/3.15;apprpd/;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fchat%2Findex.action%3Fentry%3Djd_m_JiSuCommodity%26pid%3D7763388%26lng%3D118.159665%26lat%3D24.504633%26sid%3D31cddc2d58f6e36bf2c31c4e8a79767w%26un_area%3D16_1315_3486_0;psq/12;ads/;psn/c10e0db6f15dec57a94637365f4c3d43e05bbd48|4;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/3.15;apprpd/;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fchat%2Findex.action%3Fentry%3Djd_m_JiSuCommodity%26pid%3D7763388%26lng%3D118.159665%26lat%3D24.504633%26sid%3D31cddc2d58f6e36bf2c31c4e8a79767w%26un_area%3D16_1315_3486_0;psq/12;ads/;psn/c10e0db6f15dec57a94637365f4c3d43e05bbd48|4;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone13,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/3.15;apprpd/;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fchat%2Findex.action%3Fentry%3Djd_m_JiSuCommodity%26pid%3D7763388%26lng%3D118.159665%26lat%3D24.504633%26sid%3D31cddc2d58f6e36bf2c31c4e8a79767w%26un_area%3D16_1315_3486_0;psq/12;ads/;psn/c10e0db6f15dec57a94637365f4c3d43e05bbd48|4;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,6;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/2813715704;pv/67.38;apprpd/MyJD_Main;ref/https%3A%2F%2Fh5.m.jd.com%2FbabelDiy%2FZeus%2F2ynE8QDtc2svd36VowmYWBzzDdK6%2Findex.html%3Flng%3D103.957532%26lat%3D30.626962%26sid%3D4fe8ef4283b24723a7bb30ee87c18b2w%26un_area%3D22_1930_49324_52512;psq/4;ads/;psn/5aef178f95931bdbbde849ea9e2fc62b18bc5829|127;jdv/0|direct|-|none|-|1612588090667|1613822580;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,2;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/6.28;apprpd/;ref/JDLTRedPacketViewController;psq/3;ads/;psn/d7beab54ae7758fa896c193b49470204fbb8fce9|8;jdv/0|kong|t_1001707023_|jingfen|79ad0319fa4d47e38521a616d80bc4bd|1613800945610|1613824900;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone12,1;addressid/3104834020;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.6;apprpd/;ref/JDLTSubMainPageViewController;psq/5;ads/;psn/c633e62b5a4ad0fdd93d9862bdcacfa8f3ecef63|6;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,1;addressid/1346909722;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/30.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/40d4d4323eb3987226cae367d6b0d8be50f2c7b3|39;jdv/0|kong|t_1000252057_0|tuiguang|eba7648a0f4445aa9cfa6f35c6f36e15|1613995717959|1613995723;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.3;network/wifi;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone10,1;addressid/1346909722;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/30.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/40d4d4323eb3987226cae367d6b0d8be50f2c7b3|39;jdv/0|kong|t_1000252057_0|tuiguang|eba7648a0f4445aa9cfa6f35c6f36e15|1613995717959|1613995723;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.3;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,6;addressid/138164461;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/7.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/d40e5d4a33c100e8527f779557c347569b49c304|7;jdv/0|kong|t_1001226363_|jingfen|3bf5372cb9cd445bbb270b8bc9a34f00|1608439066693|1608439068;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,6;addressid/138164461;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/7.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/d40e5d4a33c100e8527f779557c347569b49c304|7;jdv/0|kong|t_1001226363_|jingfen|3bf5372cb9cd445bbb270b8bc9a34f00|1608439066693|1608439068;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,6;addressid/138164461;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/7.8;apprpd/;ref/JDLTSubMainPageViewController;psq/7;ads/;psn/d40e5d4a33c100e8527f779557c347569b49c304|7;jdv/0|kong|t_1001226363_|jingfen|3bf5372cb9cd445bbb270b8bc9a34f00|1608439066693|1608439068;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;13.5;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,2;addressid/2237496805;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/13.6;apprpd/;ref/JDLTSubMainPageViewController;psq/5;ads/;psn/48e495dcf5dc398b4d46b27e9f15a2b427a154aa|15;jdv/0|direct|-|none|-|1613354874698|1613952828;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 13.5;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;android;3.7.0;10;network/wifi;model/ONEPLUS A6000;addressid/0;aid/3d3bbb25af44c59c;oaid/;osVer/29;appBuild/1436;psn/ECbc2EqmdSa7mDF1PS1GSrV/Tn7R1LS1|6;psq/8;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/2.67;jdv/0|direct|-|none|-|1613822479379|1613991194;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/oppo;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 10; ONEPLUS A6000 Build/QKQ1.190716.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
    "jdltapp;android;3.7.0;8.1.0;network/wifi;model/16th Plus;addressid/0;aid/f909e5f2c464c7c6;oaid/;osVer/27;appBuild/1436;psn/c21YWvVr77Hn6 pOZfxXGY4TZrre1 UOL5hcPbCEDMo=|3;psq/10;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 8.1.0;osv/8.1.0;pv/2.15;jdv/;ref/com.jd.jdlite.lib.personal.view.fragment.JDPersonalFragment;partner/jsxdlyqj09;apprpd/MyJD_Main;eufv/1;Mozilla/5.0 (Linux; Android 8.1.0; 16th Plus Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045514 Mobile Safari/537.36",
    "jdltapp;android;3.7.0;11;network/wifi;model/Mi 10 Pro;addressid/0;aid/14d7cbd934eb7dc1;oaid/335f198546eb3141;osVer/30;appBuild/1436;psn/ZcQh/Wov sNYfZ6JUjTIUBu28 KT0T3u|1;psq/24;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 11;osv/11;pv/1.24;jdv/;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/xiaomi;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 11; Mi 10 Pro Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 Mobile Safari/537.36",
    "jdltapp;android;3.7.0;10;network/wifi;model/MI 8;addressid/1969998059;aid/8566972dfd9a795d;oaid/4a8b773c3e307386;osVer/29;appBuild/1436;psn/PhYbUtCsCJo r 1b8hwxjnY8rEv5S8XC|383;psq/14;adk/;ads/;pap/JA2020_3112531|3.7.0|ANDROID 10;osv/10;pv/374.14;jdv/0|iosapp|t_335139774|liteshare|CopyURL|1609306590175|1609306596;ref/com.jd.jdlite.lib.jdlitemessage.view.activity.MessageCenterMainActivity;partner/jsxdlyqj09;apprpd/MessageCenter_MessageMerge;eufv/1;Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045140 Mobile Safari/537.36",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone8,4;addressid/1477231693;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/21.15;apprpd/MyJD_Main;ref/https%3A%2F%2Fgold.jd.com%2F%3Flng%3D0.000000%26lat%3D0.000000%26sid%3D4584eb84dc00141b0d58e000583a338w%26un_area%3D19_1607_3155_62114;psq/0;ads/;psn/2c822e59db319590266cc83b78c4a943783d0077|46;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,1;addressid/70390480;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.24;apprpd/MyJD_Main;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fafter%2Findex.action%3FcategoryId%3D600%26v%3D6%26entry%3Dm_self_jd;psq/4;ads/;psn/6d343c58764a908d4fa56609da4cb3a5cc1396d3|17;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,1;addressid/70390480;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.24;apprpd/MyJD_Main;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fafter%2Findex.action%3FcategoryId%3D600%26v%3D6%26entry%3Dm_self_jd;psq/4;ads/;psn/6d343c58764a908d4fa56609da4cb3a5cc1396d3|17;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,1;addressid/70390480;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.24;apprpd/MyJD_Main;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fafter%2Findex.action%3FcategoryId%3D600%26v%3D6%26entry%3Dm_self_jd;psq/4;ads/;psn/6d343c58764a908d4fa56609da4cb3a5cc1396d3|17;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone9,1;addressid/70390480;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.24;apprpd/MyJD_Main;ref/https%3A%2F%2Fjdcs.m.jd.com%2Fafter%2Findex.action%3FcategoryId%3D600%26v%3D6%26entry%3Dm_self_jd;psq/4;ads/;psn/6d343c58764a908d4fa56609da4cb3a5cc1396d3|17;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPhone;3.7.0;14.4;network/4g;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone12,3;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/;pv/3.49;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/7;ads/;psn/9e0e0ea9c6801dfd53f2e50ffaa7f84c7b40cd15|6;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdltapp;iPad;3.7.0;14.4;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPad7,5;addressid/;hasOCPay/0;appBuild/1017;supportBestPay/0;pv/4.14;apprpd/MyJD_Main;ref/MyJdMTAManager;psq/3;ads/;psn/956c074c769cd2eeab2e36fca24ad4c9e469751a|8;jdv/0|;adk/;app_device/IOS;pap/JA2020_3112531|3.7.0|IOS 14.4;Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
]
function UserAgents() {
    return USER_AGENTS[parseInt(Math.random() * USER_AGENTS.length)]
}

function jdd_ck(cookie) {
    try {
        body = request({
            method: "post",
            url: `https://plogin.m.jd.com/cgi-bin/ml/islogin`,
            headers: {
                "Cookie": cookie,
                "User-Agent": UserAgents(),
                "referer": "https://gold.jd.com/",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            //dataType: "json",
            timeOut: 30000
        })
        //  sendText(JSON.stringify(body))
        body = JSON.parse(body)
        if (body.islogin == "1") {
            return true
        } else {
            return false
        }
    } catch (err) {
    }
}
//
function vip_h5(cookie) {
    try {

        let body = request({
            url: `https://api.m.jd.com/api?functionId=pg_channel_page_data&appid=vip_h5&body={"paramData":{"token":"60143dce-1cde-44de-8130-a6e5579e1567"}}&h5st=20240425194639037;mnit5i5tyg6z9ni2;5ddd4;tk03web301d2741lMysyKzF2amJK4xyMWzsVrRhu1zgGaBKUbgfJgdmAKnXqUQUui2qDwPQ24yDU4NojEyeCSi6IvA8R;b5a2e115177ca007c1217d12f1f86a6c88812c2bac0f7d36ed67ea8ff9685ff3;4.7;1714045599037;TKmWS38lKRMNqeQubDgtXpVdlfsMwOLGTw4pfJMO9lU1QL9aWgA1nRmPIYtdsZ8mv8sNsTalBJF9SO1K3zkXma1xVnvbx4wG0U1cgmsIqFvRlnHH5GKetligoEU5aeSKd0ZO4V8ujreSupG8TL9Rv6Ut_KZ77ROv-4RoG0pOedqiTEL_Pk2HUyhvjPECCNRxpvpI6ah8ivStjs4v6BRM4VuXmGXLQxnzWC2brFz6gPwfO-FsAg2jX-m1ShHGeUHCJR03Rci5ZZU03jhnTBmRllde8u0P8OtFHdVypr5iSRkKhkoH5waYQV5RpWp0dM4afQ8cDEzgEBg7Oathc99BHSpAzojzkqzlcZRI3JpEQ3Yyej2hynIKyluP91cXqevcdG0PXV_NPzHZtCWNNjRXlUxNjWl7AxYmz8Xxn07tGnSl4MW_dJW-9RdU3-ny7LZTynUfmSFfZHG8tj-BuNUaoldL9PrXEmLFIRmC-D44vhRM48n77H_6xfkTg6aj3bvrfo-3LTO_wiZDcKM1SkWuRZQn0_MGf3sXGE7LWKFYYJaqox3eItEywRwF0cVU49L_k_gY_iiD-MR3isJKYe4XvRHECOXnQ5WrYhfzsbNpAQhlH5HwIq9i6SdMtJRHmUmaTZr8&eid=&x-api-eid-token=`,
            method: "post",
            headers: {
                "Host": "api.m.jd.com",
                "content-length": "1039",
                "accept": "application/json",
                "user-agent": 'jdapp;android;12.6.0;;;M/5.0;appBuild/99141;ef/1;ep/{"hdid":"JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw = ","ts":1714045594586,"ridx":-1,"cipher":{"sv":"CJO = ","ad":"DtHvZwZsZWZwCNSnD2SnZq == ","od":"CwG1DtUnZtDwYJK2CzvwEK == ","ov":"CzK = ","ud":"DtHvZwZsZWZwCNSnD2SnZq == "},"ciphertype":5,"version":"1.2.0","appname":"com.jingdong.app.mall"};jdSupportDarkMode/0;Mozilla/5.0 (Linux; Android 11; M2012K10C Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046283 Mobile Safari/537.36',
                "content-type": "application/javascript",
                "origin": "https://vipgrowth.m.jd.com",
                "x-requested-with": "com.jingdong.app.mall",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://vipgrowth.m.jd.com/",
                //"accept-encoding": "gzip, deflate, br",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cookie": cookie,
            },
            dataType: "json",
            timeOut: 80000
        })
        if (body.success == "true" || body.success == true) {
            //  sendText(`${body.data.floorInfoList[0].floorData.jxScoreInfo.jxScore}`)
            msgs.push("【京享分值】" + body.data.floorInfoList[0].floorData.jxScoreInfo.jxScore)
        }
    } catch (err) {
    }
}
function zlm(ck) {
    let pina = ck.match(/(?<=pt_pin=)[^;]+/g)
    let tiquzlm = bucketGet("Fruit", pina)
    if (tiquzlm) {
        km_wza = bucketKeys("zlm")//网络验证网站
        if (km_wza.indexOf(tiquzlm) > -1) {
            let zltz = bucketGet("zlm", tiquzlm)
            let date = new Date(zltz * 1000);
            Y = date.getFullYear();
            M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1);
            D = date.getDate();
            s = date.getSeconds();
            //sendText("账号：" + decodeURIComponent(pina) + "\n助力到期时间：" + zltz)
            msgs.push("【旧版助力到期】" + Y + "-" + M + "-" + D)
        } else {
            //msgs.push("【未开农场助力，需开通\n联系管理员】")
        }
    } else {
        //sendText("获取不到【" + decodeURIComponent(pina) + "】的助力码")
    }
}
function xbzlm(ck) {
    let pina = ck.match(/(?<=pt_pin=)[^;]+/g)
    let tiquzlm = bucketGet("Fruit_new", pina)
    if (tiquzlm) {
        km_wza = bucketKeys("xbzlm")//网络验证网站
        if (km_wza.indexOf(tiquzlm) > -1) {
            let zltz = bucketGet("xbzlm", tiquzlm)
            let date = new Date(zltz * 1000);
            Y = date.getFullYear();
            M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1);
            D = date.getDate();
            s = date.getSeconds();
            //sendText("账号：" + decodeURIComponent(pina) + "\n助力到期时间：" + zltz)
            msgs.push("【新版助力到期】" + Y + "-" + M + "-" + D)
        } else {
            //msgs.push("【未开农场助力，需开通\n联系管理员】")
        }
    } else {
        //sendText("获取不到【" + decodeURIComponent(pina) + "】的助力码")
    }
}
function asset(cookie) {
    var remar = cookie.match(/(?<=pt_pin=)[^;]+/g)
    //msgs.push("【东东账号】"+decodeURIComponent(remar))
    var DL_kg = get("dh_DL")//代理开关功能
    //账户情况
    //totalBean(cookie)
    newUserInfo(cookie)
    vip_h5(cookie)
    if (DL_kg == "true") {
        getPlusScore(cookie, true)

    } else {
        getPlusScore(cookie, false)
    }
    //统计豆收入
    try {
        sumBean(cookie)
    } catch (error) {
        console.log(error)
    }
    //领现金
    //lxj(cookie)
    var cx_UserC = get("UserCard")//代理开关功能
    if (cx_UserC == "true" || cx_UserC == true) {
        UserCard(cookie)
    }
    //话费积分 
    hfjf(cookie)
    //京东超市 
    var cx_Info = get("cardInfo")//代理开关功能
    if (cx_Info == "true" || cx_Info == true) {
        cardInfo(cookie)
    }
    //特价金币 
    tjjb(cookie)
    if (DL_kg == "true") {
        MiniTask(cookie, true)

    } else {
        MiniTask(cookie, false)
    }
    var cx_Fruit = get("Fruit")//代理开关功能
    if (cx_Fruit == "true" || cx_Fruit == true) {
        if (DL_kg == "true") {
            getJdFruit(cookie, true)
        } else {
            getJdFruit(cookie, false)
        }
    }
    //新农场数据
    var cx_home = get("farm_home")//代理开关功能
    if (cx_home == "true" || cx_home == true) {
        if (DL_kg == "true") {
            farm_home(cookie, true)
        } else {
            farm_home(cookie, false)
        }
    }
    //种豆得豆
    var cx_Bean = get("plantBean")//代理开关功能
    if (cx_Bean == "true" || cx_Bean == true) {
        if (DL_kg == "true") {
            plantBean(cookie, true)
        } else {
            plantBean(cookie, false)
        }
    }
    //健康社区
    var cx_jksq = get("jksq")//代理开关功能
    if (cx_jksq == "true" || cx_jksq == true) {
        jksq(cookie)
    }


    //红包情况
    getRedPacket(cookie)
    //优惠券情况
    var cx_jksq = get("Coupon")//代理开关功能
    if (cx_jksq == "true" || cx_jksq == true) {
        getCoupon(cookie)
    }
    //到期京豆
    var cx_jksq = get("getjingBeanDetail")//代理开关功能
    if (cx_jksq == "true" || cx_jksq == true) {
        getjingBeanDetail(cookie)
    }
    var shouquan = get("who_sq")//代理开关功能
    if (shouquan == "true" || shouquan == true) {
        zlm(cookie)
        xbzlm(cookie)
        Debug(remar + "---------")
        let who_time = user_vip_time(remar)
        if (who_time == false) {
            sendText(decodeURIComponent(remar) + ",已经到期,请及时充值")
        } else {
            Debug(decodeURIComponent(remar) + ",还没到期")
            msgs.push(who_time)
        }
    }

    var who_zdy = get("who_zdy")//代理开关功能
    if (who_zdy == null || who_zdy == "") {

    } else {
        msgs.push(who_zdy)
    }
    if (bucketGet("jd_cookie", "enable_bill") == "true") {
        img = drawList({
            //图标
            "background": {
                "color": { r: 255, g: 255, b: 255, a: 255 },
                //"image": "jdicons/foot.jpg"
            },
            "icon": {
                "images": icons,//图标数组,图标类型支持path本地相对路径，url网络图版，base64编码图片
            },
            "text": {
                "color": { r: 0, g: 0, b: 20, a: 255 },//文字颜色
                "size": 48,//文字大小
                "texts": msgs,//文字内容
            },
            "head": {
                "image": "jdicons/head.jpg"//图片
            },
            "foot": {
                "image": "jdicons/foot.jpg"//图片
            }
        })
        var Tc_tupin = get("tupin")//代理开关功能
        if (Tc_tupin == "true") {
            sendImage(img["url"])
        } else {
            username = bucketGet("cloud", "username")
            password = bucketGet("cloud", "password")
            let dd = img["base64"]
            ib = encodeURIComponent(dd)
            body = request({
                url: "http://aut.zhelee.cn/imgUpload",
                method: "post",
                dataType: "json",
                formData: {
                    username: username,
                    password: password,
                    imgBase64: ib
                },
            })
            sendImage(body.result.path)
        }
        msgs = ""
    } else {


        sendText(msgs.join("\n") + "\n")
        msgs = ""
    }
}
//账号信息
function newUserInfo(cook) {
    str = cook.match(/pin=(\S*);/)[1];
    let pin = decodeURIComponent(str)
    msgs.push("【东东账号】" + pin)
    var plus = ""
    let data = request({
        url: 'https://me-api.jd.com/user_new/info/GetJDUserInfoUnion',
        method: "get",
        headers: {
            cookie: cook,
            Accept: 'application/json, text/plain',
            'Content-Type': 'application/json;charset=UTF-8',
            'User-Agent': UserAgents()
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 30000
    })

    if (data.msg == "success") {
        Debug(JSON.stringify(data.data))
        let obj = data.data.userInfo
        //msgs.push("【东东账号】" + obj.baseInfo.curPin)
        msgs.push("【账户昵称】" + obj.baseInfo.nickname)
        if (obj.isPlusVip == 1 || obj.plusStatus == "1") {
            plus = "PLUS会员"

        } else {
            plus = "非PLUS会员"
        }
        msgs.push("【" + obj.baseInfo.levelName + "】" + plus)
        msgs.push("【豆豆总额】" + data.data.assetInfo.beanNum)
    }
}
//到期时间
function user_vip_time(ID) {
    let user = bucketGet("who_user_vip", ID)
    Debug(user + "------用户名")
    if (user == "") {
        let time_who = Date.parse(new Date()).toString();//获取到毫秒的时间戳，精确到毫秒
        time_who = parseInt(time_who / 1000);
        bucketSet("who_user_vip", ID, time_who)
        user = bucketGet("who_user_vip", ID)

    } else {
        var time = Date.parse(new Date()).toString();//获取到毫秒的时间戳，精确到毫秒
        time = parseInt(time / 1000);
        if (user <= time) {
            Debug("已经到期")
            return false
        } else {
            Debug("还未到期")
            var date = new Date(user * 1000);
            var time = Date.parse(new Date()).toString();//获取到毫秒的时间戳，精确到毫秒
            var mss = date - time
            var days = parseInt(mss / (1000 * 60 * 60 * 24));
            var hours = parseInt((mss % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            Y = date.getFullYear();
            M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1);
            D = date.getDate() + ' ';
            s = date.getSeconds();
            let days_time_a = `【到期时间】${Y}-${M}-${D}`
            return days_time_a

        }

    }
}
//检测到期时间
function user_vip_jc(ID) {
    let user = bucketGet("who_user_vip", ID)
    if (user == "") {
        let time_who = Date.parse(new Date()).toString();//获取到毫秒的时间戳，精确到毫秒
        time_who = parseInt(time_who / 1000);
        bucketSet("who_user_vip", ID, time_who)
        user = bucketGet("who_user_vip", ID)
        return true
    } else {
        var time = Date.parse(new Date()).toString();//获取到毫秒的时间戳，精确到毫秒
        time = parseInt(time / 1000);
        if (user <= time) {
            //sendText("已经到期")
            return false
        } else {
            //sendText("还未到期")
            return true
        }

    }
}
function main() {

    var name_ck = get("who_ck")//青龙信息
    var dh_kg = get("dh_kg")//单号查询
    var ql_hyy = get("ql_hyy")//单号查询
    var ql_sx = get("ql_sx")//单号查询
    let yessage = ""//有效
    let nessage = ""
    var ql_a = ""
    let ql_toke = ""
    let ckxa = ""
    var ckx = ""
    //媒介
    imType = ImType()
    //用户id
    userId = GetUserID()
    //绑定的京东账号
    jds = bucketKeys("pin" + imType.toUpperCase(), userId)
    let cookies = []
    var cookie = ""
    try {
        if (jds.length == 0) {
            sendText(ql_hyy)
        } else {
            //sendText("你一共有" + jds.length + "个号..\n")
            if (name_ck) {
                ql_a = JSON.parse(ql_cs(name_ck))
            } else {
                sendText("未指定使用【容器】调用CK查询")
            }
            ql_toke = ql_dl(ql_a.host, ql_a.client_id, ql_a.client_secret)
            ckxa = ql_tokex(ql_a.host, ql_toke.token_type, ql_toke.token)
            ckx = ql_token(ql_a.host, ql_toke.token_type, ql_toke.token)
            if (dh_kg == "true") {
                //使用单号查询方式
                if (jds.length == 1) {
                    nessage = jds[0]
                } else {
                    jdsIndex = []
                    for (i = 0; i < jds.length; i++) {
                        jdsIndex[i] = (i + 1) + ". " + decodeURIComponent(jds[i])
                    }
                    sendText("请选择要查询的账号：(q：取消查询)\n0.查询全部\n" + jdsIndex.join("\\n"))
                    let index = input(30000)
                    Debug(index)
                    i = parseInt(index)
                    if (index == "q" || index == "" || index == "Q") {
                        sendText("取消查询任务")
                        return
                    }
                    //查询全部
                    if (i == 0 || i == "0") {
                        JDS_PIN = bucketKeys("pin" + imType.toUpperCase(), userId)
                        // jds = bucketKeys("pin" + imType.toUpperCase(), userId)
                        for (let k = 0; k < JDS_PIN.length; k++) {
                            if (ckxa.indexOf(JDS_PIN[k]) > -1) {
                                for (let P = 0; P < ckx.length; P++) {
                                    if (ckx[P].name == "JD_COOKIE") {
                                        let pina = decodeURIComponent(ckx[P].value.match(/(?<=pt_pin=)[^;]+/g))
                                        if (pina == decodeURIComponent(JDS_PIN[k])) {
                                            if (jdd_ck(ckx[P].value)) {
                                                var shouquan = get("who_sq")//代理开关功能
                                                if (shouquan == "true" || shouquan == true) {
                                                    let who_time = user_vip_jc(JDS_PIN[k])
                                                    if (who_time == true) {
                                                        // Debug(decodeURIComponent(pin) + ",还没到期")
                                                        msgs = []
                                                        icons = []
                                                        asset(ckx[P].value)
                                                    } else {
                                                        sendText("账号：" + decodeURIComponent(pin) + "\n已经到期，如需继续代挂\请联系管理员")
                                                    }
                                                } else {
                                                    msgs = []
                                                    icons = []
                                                    asset(ckx[P].value)
                                                    sleep(500)
                                                }

                                            } else {
                                                sendText(`账号：${pina},账号失效\n` + ql_sx)
                                            }
                                        }
                                    }

                                }
                            } else {
                                sendText("查不到该账号:" + decodeURIComponent(JDS_PIN[i - 1]) + ",\n")
                            }


                        }
                    } else {
                        nessage = jds[i - 1]
                    }
                }

                if (ckxa.indexOf(nessage) > -1) {
                    for (let j = 0; j < ckx.length; j++) {
                        let pina = decodeURIComponent(ckx[j].value.match(/(?<=pt_pin=)[^;]+/g))
                        if (pina == decodeURIComponent(nessage)) {
                            if (ckx[j].name == "JD_COOKIE") {
                                if (jdd_ck(ckx[j].value)) {
                                    msgs = []
                                    icons = []
                                    asset(ckx[j].value)
                                    sleep(500)
                                } else {
                                    sendText(`账号：${pina},账号失效\n` + ql_sx)
                                }
                            }
                        }
                    }
                } else {
                    sendText("查不到该账号:" + decodeURIComponent(jds[i - 1]) + ",\n")
                }
            } else {
                //不使用单号查询
                for (let i = 0; i < jds.length; i++) {
                    if (ckxa.indexOf(jds[i]) > -1) {
                        for (let j = 0; j < ckx.length; j++) {
                            let pina = decodeURIComponent(ckx[j].value.match(/(?<=pt_pin=)[^;]+/g))
                            if (pina == decodeURIComponent(jds[i])) {
                                if (jdd_ck(ckx[j].value)) {
                                    if (ckx[j].name == "JD_COOKIE") {
                                        msgs = []
                                        icons = []
                                        asset(ckx[j].value)
                                        sleep(500)
                                    }
                                } else {
                                    sendText(`账号：${pina},账号失效\n` + ql_sx)
                                }
                            }
                        }
                    } else {
                        sendText("查不到该账号:" + decodeURIComponent(jds[i - 1]) + "\n" + ql_hyy)
                    }

                }
            }
        }
    } catch (err) {
        Debug(err)
    }
}
function ql_tokex(wz, token_type, tokend) {
    let data1 = request({
        url: wz + "/open/envs",
        method: "get",
        headers: {
            accept: "application/json",
            Authorization: token_type + " " + tokend
        },
        "timeOut": 90000,
        dataType: "json",
    })
    msg1 = JSON.stringify(data1)
    return msg1
}
function ql_token(wz, token_type, tokend) {
    let data1 = request({
        url: wz + "/open/envs",
        method: "get",
        headers: {
            accept: "application/json",
            Authorization: token_type + " " + tokend
        },
        "timeOut": 90000,
        dataType: "json",
    })
    msg1 = JSON.stringify(data1.data)
    msg1 = JSON.stringify(msg1)
    msg1 = JSON.parse(msg1)
    msg1 = JSON.parse(msg1)
    return msg1
}
function ql_dl(ql_host, ql_client_id, ql_client_secret) {
    token = request({
        url: ql_host + "/open/auth/token?client_id=" + ql_client_id + "&client_secret=" + ql_client_secret,
        method: "get",
        headers: {
            accept: "application/json"
        },
        "timeOut": 90000,
        dataType: "json",
    })
    console.log(token.data.token)
    return token.data
}
function add_user() {//新增账号

    var phone = ShuRu("请输入--青龙地址")
    if (phone == false) {
        sendText("手机号-输入超时,取消任务")
        return false
    } else {
        var loginPassword = ShuRu("请输入青龙--Client ID")
        if (loginPassword == false) {
            sendText("Client ID-输入超时,取消任务")
            return false
        } else {
            var userId = ShuRu("请输入青龙--Client Secret")
            if (userId == false) {
                sendText("Client Secret-输入超时,取消任务")
                return false
            } else {
                sendText("全部输入完成！")
                var data = {
                    host: phone,
                    client_id: loginPassword,
                    client_secret: userId
                }
                bucketSet("otto", "who_ck", JSON.stringify(data))
                return true
            }
        }
    }
}
function ShuRu(name) {
    sendText(name)
    var msg = input(60000, 6000)
    if (msg == "q" || msg == "Q") {
        sendText("已退出会话");
        return
    } else {
        return msg;
    }

}
main()