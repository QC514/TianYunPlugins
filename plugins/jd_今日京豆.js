//[author: funyhook]
//[create_at: 2024-05-29 13:05:41]
//[version: 11]
//[title: jd_今日京豆]
//[class: 查询类]
//[description: 今日京豆明细查询 依赖“hook.js”，请先在云应用市场安装【hook】插件]
//[public: true]
//[service: 601440343]
//[class: 工具类]
//[price: 1]
//[rule: 豆豆查询]
//[rule: 豆豆明细]
//[rule: 豆豆]
//[priority: 999]优先级
//[disable: false]
//[icon: https://bbs.autman.cn/assets/files/2024-01-09/1704801305-15693-y.png]
// [param: {"required":false,"key":"otto.jd_red","bool":true,"placeholder":"false","name":"红包","desc":"关闭则不查"}]
// [param: {"required":false,"key":"otto.jd_plus","bool":true,"placeholder":"false","name":"plus","desc":"关闭则不查"}]
// [param: {"required":false,"key":"otto.jd_card","bool":true,"placeholder":"false","name":"E卡","desc":"关闭则不查"}]

const aut_ver = call("version")()["sn"]//获取当前系统版本
//媒介
imType = ImType()
//用户id
userId = GetUserID()
var H5ST = "http://o17094o427.iok.la:39003"
let h5st_arr =[
    "http://1.14.208.178:3002/api/h5st",
    "http://141.144.225.250:3002/api/h5st",
    "http://1.94.8.244:3002/api/h5st"
]


function check_denpcy(plugin) {

    try {
        if (aut_ver > "2.6.5" && get("env") !== "dev") {
            plugin = `funyhook:${plugin}`
        }
        importJs(plugin)
        Base64.decode(plugin)
    } catch (e) {
        let content = `${getTitle()}请检查是否安装以下依赖插件：`
        content += `\n【${plugin}】`
        content += `\n请前往autman面板-市场管理-应用市场-【funyhook】-安装缺失插件`
        console.log(content)
        throw new Error(content)
    }
}

function search_red(user_data){
    var red = get("jd_red")//代理开关功能
    if (red == "true" || red == true) {
        redInfo(user_data)
        content = `--------------------\n`
        content += `红包总额：${user_data.redBalance}元\n`
        content += `红包个数：${user_data.avaiCount}个\n`
        content += `今日过期：${user_data.expiredBalance}元\n`
        return content
    }
    return ""
}

function search_card(user_data){
    var value = get("jd_card")//代理开关功能
    if (value == "true" || value == true) {
        redInfo(user_data)
        content += `礼卡余额${user_data.redBalance}元\n`
    }
}


function search_plus(user_data){
    var jd_plus = get("jd_plus")//代理开关功能
    if (jd_plus == "true" || jd_plus == true) {
        if(user_data.plus){
            getPlusScore(user_data)
            if(user_data.plus_score){
                content = `plus分：${user_data.plus_score}\n`
                return content
            }
            
        }
    }
    return ""
}

function expire_bean(user_data,content){
    data = request({
        "url": "https://api.m.jd.com/client.action?functionId=jingBeanDetail&lmt=0&clientVersion=11.4.4&build=98651&client=android&partner=vivo&eid=eidA0e4b8122bcsbmU8cxX6JSnmFF7Cl6g5doplPHkfs3QZUs0dlNmQtEHko4TLPY2XSploxRKqK/yB2Qua2TymGyKXI2yYXc9VXWPrC9hJ5ALtEHnlT&sdkVersion=29&lang=zh_CN&harmonyOs=0&networkType=wifi&uts=0f31TVRjBSsqndu4%2FjgUPz6uymy50MQJXQvVqUBgQhGnerd2wImVdyFkNKQomq7BgrTQfs76xQdZ223tbYtRLlq4KctudrEdbOY24QB8XMv4HNbaM7x9wkM%2BmQjfk5%2FAJ1QoLbkQync6BUgJi0Uu1xsZUIzaMpDVlPaobeyFcpJgDrt8TQc2gCLProedSbKLTB8TqeEbJKH7pLgSX50zfQ%3D%3D&uemps=0-0-0&ext=%7B%22prstate%22%3A%220%22%2C%22pvcStu%22%3A%221%22%7D&avifSupport=1&ef=1&ep=%7B%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%22%2C%22ts%22%3A1675559773634%2C%22ridx%22%3A-1%2C%22cipher%22%3A%7B%22area%22%3A%22CJvpCJY3D18nDtc5XzY0CNG%3D%22%2C%22d_model%22%3A%22VtO4CtHMGG%3D%3D%22%2C%22wifiBssid%22%3A%22ZNCnDzY5DtO4ENLvCtCnCtY0EJSmDNLwDQGyZJq1CWY%3D%22%2C%22osVersion%22%3A%22CJK%3D%22%2C%22d_brand%22%3A%22dwv2bm%3D%3D%22%2C%22screen%22%3A%22CtO0CIenCNqm%22%2C%22uuid%22%3A%22CwG4Y2VvCNG1ZJq5ZNZwYG%3D%3D%22%2C%22aid%22%3A%22CwG4Y2VvCNG1ZJq5ZNZwYG%3D%3D%22%2C%22openudid%22%3A%22CwG4Y2VvCNG1ZJq5ZNZwYG%3D%3D%22%7D%2C%22ciphertype%22%3A5%2C%22version%22%3A%221.2.0%22%2C%22appname%22%3A%22com.jingdong.app.mall%22%7D&st=1675559805181&sign=fdd25a51d7bcb5fe708212df5cd7297a&sv=110",
        "body": `body={"pageNo":1,"pageSize":20}`,
        method: "post",
        "headers": {
            'Host': 'api.m.jd.com',
            'User-Agent': "Mozilla/5.0 (Linux; Android 12; SM-G9880) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36 EdgA/106.0.1370.47",
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': user_data.cookie,
            'content-length': 56,
        },
        dataType: "json",
        "timeout": 30000,
    })
    console.log(`expire_bean:::${JSON.stringify(res)}`)
    if (data.code == 0) {

    }
}

function main() {
    check_denpcy("hook.js")
    //绑定的京东账号
    let jds = bucketKeys("pin" + imType.toUpperCase(), userId)
    console.log(jds)
    if (jds.length === 0) {
        return sendText("没有与你绑定的账号，请对我说：“登陆”");
    }
    let user_data_arr = []
    for (let i = 0; i < jds.length; i++) {
        let jd = jds[i]
        let user_data = {}
        user_data.name = decodeURIComponent(jd);
        user_data.jd = jd
        let jnstr = bucketGet("jdNotify", jd);
        if (!jnstr || jnstr=="") {
            continue
        }
        console.log(jnstr)
        let jn = JSON.parse(jnstr)
        user_data.cookie = "pt_key=" + jn.PtKey + ";pt_pin=" + jn.ID + ";"
        user_data_arr.push(user_data)
    }
    if (user_data_arr.length==0){
        return sendText("查询不到ck，请手动核对数据桶jdNotify是否存在");
    }
    if (user_data_arr.length == 1) {
        user_data = user_data_arr[0]
        bean_info(user_data)
        getUserInfo(user_data)
        content = `账户：${user_data.name}\n`
        content += `昵称：${user_data.nickname}\n`
        content += search_plus(user_data)
        content += search_red(user_data)
        content += `--------------------\n`
        content += `豆豆总额：${user_data.beanNum}个\n`
        content += `今日京豆：${user_data.today_bean_count}个\n`
        if(user_data.today_bean_coun!==0){
            content += `--------------------`
            content += user_data.today_bean_detail
        }
        sendText(content)
    } else {
        conetent = []
        conetent += `\n0、查询所有`
        for (i = 0; i < user_data_arr.length; i++) {
            conetent += `\n${i + 1}、${user_data_arr[i].name}`
        }
        sendText("请选择要查询的账号：\n" + conetent)
        let index = input(30000)
        if(!index || index === "q"){
            return sendText("已退出")
        }
        i = parseInt(index)
        if(i===0){
            sendText("查询中，请稍后......")
            content = `------${timeFmt('yyyy-MM-dd')}------`
            for (let index = 0; index < user_data_arr.length; index++) {
                const item = user_data_arr[index];
                bean_info(item)                
            }
            user_data_arr.sort((a,b)=>b.today_bean_count-a.today_bean_count)
            
            user_data_arr.forEach(item => {
                if(item.name.length<=15){
                    item.name = item.name+" "
                }
                content += `\n${item.name}  日收：${item.today_bean_count}个`

            });
            sendText(content)
            return
        }
        if (i> user_data_arr.length){
            sendText("输入错误，已退出！")
            return
        }
        sendText("查询中，请稍后......")
        user_data = user_data_arr[i-1]
        bean_info(user_data)
        getUserInfo(user_data)
        content = `账户：${user_data.name}\n`
        content += `昵称：${user_data.nickname}\n`
        content += search_plus(user_data)
        content += search_red(user_data)
        // expire_bean(user_data, content)
        content += `--------------------\n`
        content += `豆豆总额：${user_data.beanNum}个\n`
        content += `今日京豆：${user_data.today_bean_count}个\n`
        if(user_data.today_bean_count!==0){
            content += `--------------------`
            content += user_data.today_bean_detail
        }
        sendText(content)
    }
}

function bean_info(user_data){
    page = 1
    today_bean_list = []
    user_data.today_bean_detail = ""
    user_data.today_bean_count=0
    while (true) {
        today_arr = getJingBeanBalanceDetail(user_data,page,today_bean_list)
        if(!today_arr || today_arr.length <= 0){
            break;
        }
        today_bean_list.push(...today_arr)
        // console.log(`第${page}页，查询到${today_arr.length}条数据,当前共${today_bean_list.length}条数据`)
        page++
    }
    if(today_bean_list.length>0){
        const groupedData = today_bean_list.reduce((acc, item) => {
            const { eventMassage, amount } = item;
            if (!acc[eventMassage]) {
                acc[eventMassage] = 0;
            }
            acc[eventMassage] += parseInt(amount);
            return acc;
        }, {});
        for (item in groupedData){
            user_data.today_bean_detail+= `\n${item}：${groupedData[item]}`
            user_data.today_bean_count+=groupedData[item]
        }
       
    }
}
function getJingBeanBalanceDetail(user_data, page) {
    body = encodeURIComponent(JSON.stringify({ "pageSize": "20", "page": page.toString() }))
    today_arr = []
    const today = timeFmt('yyyy-MM-dd')
    res = request({
        "url": "https://bean.m.jd.com/beanDetail/detail.json?page=" + page,
        "body": "body=" + body + "&appid=ld",
        "headers": {
            'User-Agent': "Mozilla/5.0 (Linux; Android 12; SM-G9880) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36 EdgA/106.0.1370.47",
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': user_data.cookie,
        },
        dataType:"json"
    })
    console.log(`${user_data.name}======查询第${page}页`)
    if(res.message==="用户未登录"){
        sendText(`账号：${user_data.name},已过期，请重新登陆`)
        return
    }
    if(res && res.success){
        data = res
        for (i = 0; i < data.jingDetailList.length; i++) {
            dateStr=data.jingDetailList[i].date
            if (dateStr.slice(0,10)==today){
                today_arr.push(data.jingDetailList[i])
            }
        }  
    }
    return today_arr
}


main()

//plus分数
function shopSign(home) {
    let body = request({
        url: `${H5ST}/shopSign`,
        method: "post",
        body: home,
        headers: {
            "Content-Type": "application/json",
        },
        dataType: "json",//数据类型json(json数据类型)、location(跳转页)
        timeOut: 10000
    })
    if (body) {
        if (body.code = 200) {
            user_data.body = body.data
            user_data.ua = body.ua
        }
        return true
    } else {
        return false
    }
}

function xin_ua() {
    nc_h5 = ""
    nc_ua = ""
    let body = request({
        url: `${H5ST}/UA`,
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
            user_data.ua = body.data
            var ucxa = nc_ua.split(";")
            user_data.h5_ver = ucxa[2]
        }
        return true
    } else {
        return false
    }
}

function getPlusScore(user_data) {
    try {
        var pina = user_data.cookie.match(/(?<=pt_pin=)[^;]+/g)
        for (let k = 0; k < 3; k++) {
            xin_ua()
            let home = { "appId": "b63ff", "fn": "windControl_queryScore_v1", "body": {}, "apid": "plus_business", "ver": String(user_data.h5_ver), "cl": "ios", "code": 1, "user": String(pina), "ua": user_data.ua }
            shopSign(home)
            var h5st_h5 = user_data.body.match(/(?<=h5st=)[^;]+/g)
            body = request({
                method: "post",
                url: "https://api.m.jd.com/api?appid=plus_business&functionId=windControl_queryScore_v1&body=%7B%7D&h5st=" + h5st_h5 + "&loginType=2&loginWQBiz=",
                //body: nc_h5,
                headers: {
                    "Referer": "https://plus.m.jd.com/rights/windControl",
                    "User-Agent": user_data.ua,
                    "Cookie": user_data.cookie,
                },
                dataType: "json",
                timeOut: 10000
            })
            console.log("PLUS分数据" + JSON.stringify(body))
            if (body && body.code == "1000") {
                user_data.plus_score = body.data.rs.userSynthesizeScore.totalScore
                break;
            }
        }
    } catch (err) {
        Debug(err)
    }
}


//查询包裹
function getUserInfo(user_data) {
    request({
        method: "get",
        url: "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion?isLogin=1",
        headers: {
            'Host': 'api.m.jd.com',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-cn',
            'Referer': 'https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&',
            //'Accept-Encoding': 'gzip, deflate, br',
            "Cookie": user_data.cookie,
            'User-Agent': userAgent()
        },
        dataType: "json",
        // formData: {
        //     body: "version:4",
        //     appid: "wh5",
        //     clientVersion: '9.1.0'
        // }
    }, function (error, response, header, body) {
        // console.log(`【getUserInfo】：【req】：${user_data.cookie}【resp】：${JSON.stringify(response)}`)
        if (!error && response.statusCode === 200 && body.retcode === "0") {
            if (body.data.userInfo.isPlusVip == 1 || body.data.userInfo.plusStatus == "1") {
                user_data.plus = true
            } else {
                user_data.plus = true
            }
            console.log(user_data.plus)
            user_data.beanNum = body.data.assetInfo.beanNum
            user_data.redBalance = body.data.assetInfo.redBalance
            user_data.nickname = body.data.userInfo.baseInfo.nickname
        }
    })
}

function redInfo(user_data){
    url = "https://api.jingxi.com/api?functionId=myassets.queryHongBao&appid=jx_h5&t=1717385927923&channel=jxh5&cv=1.2.5&clientVersion=1.2.5&client=jxh5&uuid=7488516494229936189&cthr=1&loginType=2&body={%22listtype%22%3A1%2C%22orgFlag%22%3A%22JD_PinGou_New%22%2C%22page%22%3A1%2C%22cashRedType%22%3A1%2C%22redBalanceFlag%22%3A1%2C%22platform%22%3A3%2C%22sceneval%22%3A2%2C%22buid%22%3A325%2C%22appCode%22%3A%22ms2362fc9e%22%2C%22time%22%3A1717385927923%2C%22signStr%22%3A%222a17612515442c7fe8be17329111dc97%22}&callback=__jsonp1717385927895"
    request({
        method: "get",
        url: url,
        headers: {
            'Host': 'api.m.jd.com',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-cn',
            'Referer': 'https://st.jingxi.com/my/redpacket.shtml?lng=116.490377&lat=39.977559&un_area=1_2809_51226_0&sid=973b290e515dbe65baa0b4135562b39w',
            "Cookie": user_data.cookie,
            'User-Agent': userAgent()
        },
    }, function (error, response, header, body) {
        console.log(`【redInfo】：【req】：${user_data.cookie}【resp】：${body}`)
        if (!error && response.statusCode === 200 && body) {
            jsonString = body.substring(body.indexOf('(') + 1, body.lastIndexOf(')'));
            data = JSON.parse(jsonString)
            user_data.avaiCount = data.data.avaiCount
            user_data.redBalance = data.data.balance
            user_data.expiredBalance = data.data.expiredBalance
        }
    })
}