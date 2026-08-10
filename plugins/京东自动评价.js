//==========================市场元数据=========================================
//[title: 京东自动评价]
//[author: hunyan]
//[open_source: false]是否开源
//[icon: https://bbs.autman.cn/assets/files/2024-02-02/1706859269-348059-bfy.png]图标链接地址，支持http和https
//[version: 1.0.3]版本号
//[class: 工具类]从工具类、查询类、娱乐类、餐饮类、影音类、生活类、图片类、游戏类等中选择，也可自定义
//[platform: qq,qb,wx,tb,tg,web,wxmp]适用的平台 qq/qb/wx/tb/tg/wxmp/web之间选择，中间用英文逗号隔开
//[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
//[price: 5] 上架价格
//[service: 2946148573]写上售后联系方式，方便用户联系咨询
//[description: 1.0.3适配autMan2.5.5<br />1.0.2更新未获取到待评价订单时提示<br />1.0.1更新退款比例错误的问题。<br />适配盖亚2.0的一个评价插件，默认触发指令《京东自动评价》，使用前请先去网页配参。请确保你的盖亚_核心版本大于等于2.0.0，否则可能无法正常使用] 使用方法尽量写具体
//==========================功能元数据======================================
//[rule: ^京东自动评价$] 匹配规则，多个规则时向下依次写多个
//[admin: false] 是否为管理员指令
//[disable:false] 禁用开关，true表示禁用，false表示可用
//[priority: 100] 优先级，数字越大表示优先级越高
//==========================配参数据（最下面）===============================
//[param: {"required":false,"key":"Y_comment.quantityPay","bool":true,"placeholder":"","name":"按量付费","desc":"开启时，按照用户选择的评价订单数量扣费，关闭则不管用户选择多少个订单进行评价只按照设置的扣一次费"}]
//[param: {"spliter":true}]
//[param: {"required":true,"key":"Y_comment.money","bool":false,"placeholder":"","name":"单价","desc":"设置评价所需的积分(按量付费时为一个评价订单所需积分，非按量付费时为用户使用评价功能所扣除的积分)"}]
//[param: {"required":true,"key":"Y_comment.noCookie","bool":false,"placeholder":"","name":"未找到Cookie提示","desc":"当未找到用户相关的Cookie时展示的提示"}]
//[param: {"required":true,"key":"Y_comment.invalid","bool":false,"placeholder":"","name":"Cookie失效提示","desc":"用户Cookie失效时的提示"}]
// [param: {"required":false,"key":"Y_comment.qlQuery","placeholder":"","bool":true,"name":"自定义评价容器","desc":"开启后不使用缓存桶的Cookie，将从青龙容器中获取Cookie，autMan版本大于2.5.5只能使用此项，开启后下方的配参必须填写"}]
// [param: {"required":false,"key":"Y_comment.qlConfigs","placeholder":"","name":"青龙面板配置","desc":"多青龙面板配置示例:\u005b\u007b\u0022\u0068\u006f\u0073\u0074\u0022\u003a\u0020\u0022\u0068\u0074\u0074\u0070\u003a\u002f\u002f\u0031\u0032\u0037\u002e\u0030\u002e\u0030\u002e\u0031\u003a\u0035\u0037\u0030\u0030\u0022\u002c\u0020\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0069\u0064\u0022\u003a\u0020\u0022\u0061\u0062\u0063\u0064\u0065\u0066\u0067\u0022\u002c\u0020\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0073\u0065\u0063\u0072\u0065\u0074\u0022\u003a\u0020\u0022\u0061\u0062\u0063\u0064\u0065\u0066\u0067\u0022\u007d\u002c\u007b\u0022\u0068\u006f\u0073\u0074\u0022\u003a\u0020\u0022\u0068\u0074\u0074\u0070\u003a\u002f\u002f\u0031\u0032\u0037\u002e\u0030\u002e\u0030\u002e\u0031\u003a\u0035\u0037\u0030\u0031\u0022\u002c\u0020\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0069\u0064\u0022\u003a\u0020\u0022\u0067\u0066\u0065\u0064\u0063\u0062\u0061\u0022\u002c\u0020\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0073\u0065\u0063\u0072\u0065\u0074\u0022\u003a\u0020\u0022\u0067\u0066\u0065\u0064\u0063\u0062\u0061\u0022\u007d\u005d </br>单青龙面板配置示例：\u005b\u007b\u0022\u0068\u006f\u0073\u0074\u0022\u003a\u0020\u0022\u0068\u0074\u0074\u0070\u003a\u002f\u002f\u0031\u0032\u0037\u002e\u0030\u002e\u0030\u002e\u0031\u003a\u0035\u0037\u0030\u0030\u0022\u002c\u0020\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0069\u0064\u0022\u003a\u0020\u0022\u0061\u0062\u0063\u0064\u0065\u0066\u0067\u0022\u002c\u0020\u0022\u0063\u006c\u0069\u0065\u006e\u0074\u005f\u0073\u0065\u0063\u0072\u0065\u0074\u0022\u003a\u0020\u0022\u0061\u0062\u0063\u0064\u0065\u0066\u0067\u0022\u007d\u005d"}]

let UA = "";
let Cookie = "";
main();

function main() {
    let imType = ImType();
    let userId = GetUserID();
    let success = 0;
    let errorWname = [];
    const { quantityPay, money, check, noCookie, invalid,qlConfigs,qlQuery } = checkConfig()
    console.log("1", quantityPay, money, check, noCookie, invalid);
    if (!check) {
        notifyMasters("配参不完整，请去autMan网页配参");
        return
    }
    try {
        if (bucketGet("Y_comment", "dev")!=="true") {
            importJs("盖亚_核心.js");
        }else{
            importJs("盖亚_核心2.0.js");
        }
        
    } catch (err) {
        notifyMasters("缺少盖亚_核心")
        return
    }
    const gaia = new GAIA();
    let jds = bucketKeys("pin" + imType.toUpperCase(), userId)
    if (jds.length <= 0) {
        sendText(noCookie);
        return
    } else {
        let commPin = `请在30秒内选择要进行评价的京东账号，q退出`
        for (let i = 0; i < jds.length; i++) {
            const element = jds[i];
            commPin += `\n[${(i + 1)}] ${decodeURIComponent(element)}`
        }
        sendText(commPin)
        const choosePinInput = input(30000, 100);
        if (choosePinInput === "q") {
            sendText("退出成功")
            return
        }
        if (choosePinInput === "") {
            sendText("输入超时，程序自动退出")
            return
        }
        if (isNaN(Number(choosePinInput)) || parseInt(choosePinInput) > jds.length || parseInt(choosePinInput) <= 0) {
            sendText("输入有误，程序自动退出")
            return
        }
        const userChoosePin = jds[parseInt(choosePinInput) - 1]
        if (!qlQuery){
            try{
                const bucketCookie = JSON.parse(bucketGet("jdNotify", encodeURIComponent(decodeURIComponent(userChoosePin))))
                Cookie = "pt_key=" + bucketCookie.PtKey + ";pt_pin=" + encodeURIComponent(decodeURIComponent(userChoosePin)) + ";"
            }catch(e){
                console.log(e)
                notifyMasters("从缓存桶获取Cookie失败，请检查autMan版本是否大于等于2.5.5")
            }

        }else {
            const userCookie = findUserCookie(userChoosePin,qlConfigs);
            if (userCookie){
                Cookie = userCookie
            }
        }
        if (!checkCk(Cookie)) {
            sendText(invalid)
            return
        }

        UA = user_Agents()
        const goodsRes = getGoods()
        if (!goodsRes) {
            sendText("出错了")
            return
        }
        const maxPage = goodsRes.commentWareListInfo ? goodsRes.commentWareListInfo.maxPage : 0;
        const waitCommentCount = goodsRes.commentWareListInfo ? goodsRes.commentWareListInfo.wait4CommentCount : 0;
        const commentWareList = goodsRes.commentWareListInfo ? goodsRes.commentWareListInfo.commentWareList : [];
        console.log(maxPage);
        console.log(waitCommentCount);
        console.log(JSON.stringify(commentWareList, null, 2));
        if (!maxPage) {
            sendText("待评价数据获取失败")
            return
        }
        let waitText = `获取到待评价订单如下，请在30秒内输入需要评价的订单序号(多个订单序号用逗号隔开)，q退出。\n[0] 全部订单`
        for (let i = 0; i < commentWareList.length; i++) {
            const commentWare = commentWareList[i];
            const title = commentWare.wname;
            waitText += `\n[${i + 1}] ${title}`
        }
        if (commentWareList.length===0){
            sendText("未获取到待评价订单")
            return
        }
        sendText(waitText)
        let chooseCommentInput = input(30000, 100);
        if (chooseCommentInput === "q") {
            sendText("退出成功")
            return
        }
        if (chooseCommentInput === "") {
            sendText("输入超时，程序自动退出")
            return
        }
        chooseCommentInput = chooseCommentInput.replaceAll("，", ",");
        let chooseCommentArr = chooseCommentInput.split(",");
        for (const chooseComment of chooseCommentArr) {
            if (isNaN(Number(chooseComment)) || parseInt(chooseComment) > commentWareList.length || parseInt(chooseComment) < 0) {
                sendText("输入有误，程序自动退出")
                return
            }
        }
        if (chooseCommentArr.length === 1 && parseInt(chooseCommentArr[0]) === 0) {
            chooseCommentArr = [];
            for (let i = 0; i < commentWareList.length; i++) {
                chooseCommentArr.push(i + 1)
            }
        }
        let gaiaGoods = {}
        let payResult = {}
        if (parseInt(money) !== 0) {
            gaiaGoods = {
                title: "京东商品自动评价",
                price: money,
                quantity: quantityPay ? chooseCommentArr.length : 1,
                proportion: 1
            }
            const userConfirm = confirmOrder(gaiaGoods);
            if (!userConfirm) {
                return
            }
            const gaiaOrder = gaia.createOrder(userId, gaiaGoods);
            payResult = gaia.paymentOrder(gaiaOrder.orderID);
            const pay = payCallback(payResult);
            if (!pay) {
                return
            }
        }

        // console.log(chooseCommentArr);
        let badComs = ["很垃圾", "质量差", "评价内容"],
            goodCom = ["这个商品的质量真的很好！外观精美，手感舒适，使用起来非常顺手。卖家的服务态度也很好，让我购物无忧。", "卖家的服务真是周到细致！他们不仅耐心解答我的问题，还给予了很多实用的建议。物流速度也很快，让我及时收到了商品。", "这个商品超出了我的期待！不仅质量上乘，而且功能齐全，性价比很高。卖家的服务态度也非常好，让我有了愉快的购物体验。", "卖家的服务真是一流！他们把顾客的需求放在首位，耐心解答疑问，并提供了专业的建议。物流速度也很快，让我迅速收到了商品。", "这个商品的质量非常可靠！经过使用测试，它表现出色，没有出现任何问题。卖家的服务态度也很好，给予了及时的售后支持。", "这个商品真是物超所值！质量很好，价格也合理。卖家的服务态度也很好，及时回复我的问题，并提供了详细的产品信息。", "卖家的服务真是贴心周到！他们提供了专业的建议，帮助我选择了合适的商品。物流速度也很快，让我顺利收到了商品。", "这个商品的性能真是令人惊喜！质量上乘，使用起来非常顺手。卖家的服务态度也很好，及时回复我的问题，并解决了我的疑惑。", "卖家的服务真是一级棒！他们对待顾客非常友好，给予了专业的建议。物流速度也很快，让我很快就收到了商品。"],
            filterZeng = ["赠品", "权益", "非实物", "非卖品", "增值服务", "服务"],
            zeng = ["送的没花钱哈哈", "东西还还不错", "现在的购物体验越来越好", "以前还没有这么多贴心的赠品、增值服务、权益等服务", "给赞", "算不算白嫖"],
            couStr = ["以上是我购物感受和体验，仅供参考，也不要只看好评，适合我的不一定适合你。。。。", "总的来说，还可以，我的评价供大家参考借鉴，根据自己情况。。。。", "总之还行，买不了吃亏，买的了上当，嘿嘿！！！！"];
        for (let i = 0; i < chooseCommentArr.length; i++) {
            try {
                const cnum = parseInt(chooseCommentArr[i]);
                const commentGood = commentWareList[cnum - 1]
                let pictureArr = [];
                let commentArr = [];
                let commentTextArr = [];
                let commentText = "";
                if (filterZeng.filter(value => commentGood.wname.includes(value)).length === 0) {
                    const getGoodComments = getGoodCommentAndPic(commentGood.wareId);
                    commentArr.push(...getGoodComments.commentInfoList)
                    // console.log(getGoodComments);
                    if (getGoodComments.maxPage > 1) {
                        const secGetGoodComments = getGoodCommentAndPic(commentGood.wareId, Math.floor(Math.random() * Math.min.apply(null, [getGoodComments.maxPage, 10]) + 2))
                        // console.log(secGetGoodComments);
                        commentArr.push(...secGetGoodComments.commentInfoList)
                    }
                    sleep(1000);
                    // console.log(commentArr);
                    for (const commentTexti of commentArr) {
                        if (commentTexti.commentInfo.pictureInfoList) {
                            for (const picElement of commentTexti.commentInfo.pictureInfoList || {}) {
                                if (picElement.mediaType != "2") {
                                    let picURL = "";
                                    if (picElement.picURL.includes("dpg")) {
                                        picURL = picElement.picURL.replace(/s[0-9]{3}x[0-9]{3}_(.*).dpg/g, "$1")
                                    } else if (picElement.picURL.includes("webp")) {
                                        picURL = picElement.picURL.replace(/s[0-9]{3}x[0-9]{3}_(.*).webp/g, "$1");
                                    } else if (picElement.picURL.includes("avif")) {
                                        picURL = picElement.picURL.replace(/s[0-9]{3}x[0-9]{3}_(.*).avif/g, "$1")
                                    }
                                    pictureArr.push(picURL)
                                }
                            }
                        }
                        if (commentTexti.commentInfo.commentScore === "5") {
                            const chineseCharCount = countUniqueChineseCharacters(commentTexti.commentInfo.commentData);
                            if (chineseCharCount > 5) {
                                commentTextArr.push(commentTexti.commentInfo.commentData)
                            }
                        }
                    }
                    console.log(JSON.stringify(commentTextArr));
                    for (const badComment of badComs) {
                        commentTextArr = commentTextArr.filter(value => !value.includes(badComment))
                    }

                    commentText = randomChoose(commentTextArr)
                    const randomPic = shuffleAndTake(pictureArr, 2)
                    const pic1 = {
                        picUrl: randomPic[0]
                    }
                    const pic2 = {
                        picUrl: randomPic[1]
                    }
                    pictureArr = [pic1, pic2]
                    commentText += "" + randomChoose(goodCom);
                } else {
                    console.log("赠品，只进行文字评价！");
                    commentText += randomCommentByArr(zeng);
                }
                commentText = commentText.replace(/\*/gi, "");
                if (commentGood.estJingBean > 0 && commentText.length < 60) {
                    commentText += "" + randomChoose(couStr)
                }
                console.log(commentText);
                console.log(pictureArr);
                const submitRes = submitComment(commentGood, commentText, pictureArr)
                if (submitRes && submitRes.code == 0) {
                    sendText(commentGood.wname + "评价完成");
                    success++
                } else {
                    errorWname.push(commentGood.wname);
                }
            } catch (error) {
                console.log(error);
            }
            sleep(2000)
        }

        if (success < chooseCommentArr.length) {
            if (parseInt(money) !== 0) {
                cancalOrder(gaia, success, chooseCommentArr.length, payResult)
                sendText(gaiaGoods.title + " 订单完成")
            }
            sendText(errorWname.join(',')+"可能评价失败")
        }
        if (parseInt(money) !== 0) {
            sendText(gaiaGoods.title + " 订单完成")
        }
    }
}

function Qinglong(ql_ipport, client_id, client_secret,otoken='') {
    this.ql_ipport = ql_ipport;
    this.client_id = client_id;
    this.client_secret = client_secret
    this.token = otoken
    this.getToken = function() {
        //连接青龙获取token
        var qltoken = request({
            // 内置http请求函数
            url:
                this.ql_ipport +
                "/open/auth/token?client_id=" +
                this.client_id +
                "&client_secret=" +
                this.client_secret,
            //请求链接
            method: "get",
            //请求方法
            dataType: "json",
            //这里接口直接返回文本
            timeOut: 30000//单位为毫秒ms，也可以都小写timeout
        });
        try{
            let token = qltoken.data.token;
            return token
        }catch(e){
            return false
        }


    }

    if(!this.token){
        this.token=this.getToken()
    }

    //其他接口
    this.ApiQL=function(api, apd, method,body="") {
        if (!this.token) {
            return false
        }
        var url = this.ql_ipport + "/open/" + api + apd//"?searchValue="+searchValue+"&t=" + Date.now();
        Debug(url)
        Debug(body)
        var json = request({
            url: url,
            method: method,
            headers: {
                //"Content-Type": "application/x-www-form-urlencoded",
                "Content-Type": "application/json;charset=UTF-8",
                Authorization: "Bearer " + this.token,
            },
            body:body,
            timeOut: 30000//单位为毫秒ms，也可以都小写timeout
        });
        return JSON.parse(json)
    }
    return this
}

function findUserCookie(pin, qlConfigs) {
    for (const ql of qlConfigs) {
        const qlInstance = new Qinglong(ql.host, ql.client_id, ql.client_secret)
        const res = qlInstance.ApiQL("envs", `?searchValue=JD_COOKIE&t=${Date.now()}`, "get");
        const envs = res.data;
        for (const qlenv of envs) {
            let vpin = decodeURIComponent(qlenv.value.match(/pt_pin=(.*?);/)[1])
            if (vpin === decodeURIComponent(pin)) {
                if (checkCk(qlenv.value)) {
                    return qlenv.value
                } else {
                    hasck = qlenv.value
                }
            }
        }
    }

    if (hasck) {
        return hasck
    }
    return false
}

function submitComment(commentWare, commentData, pictureInfoList = []) {
    const extInfo = {
        mediasExt: "[{\"VideoIsEditCover\":\"0\",\"ImagePropId\":\"0\",\"ImageTakePhotoFilterId\":\"0\",\"ImageIsCrop\":\"0\",\"VideoIsEditCrop\":\"0\",\"VideoEditFilterId\":\"0\",\"VideoMusicId\":\"0\",\"ImageEditFilterId\":\"0\",\"VideoPropId\":\"0\",\"TakeRate\":\"0\",\"VideoRecordIsMakup\":\"0\",\"ImageTakePhotoIsMakup\":\"0\",\"VideoRecordFilterId\":\"0\",\"ImageFontId\":\"0\",\"FromType\":\"1\",\"ImageStrickId\":\"0\"},{\"VideoIsEditCover\":\"0\",\"ImagePropId\":\"0\",\"ImageTakePhotoFilterId\":\"0\",\"ImageIsCrop\":\"0\",\"VideoIsEditCrop\":\"0\",\"VideoEditFilterId\":\"0\",\"VideoMusicId\":\"0\",\"ImageEditFilterId\":\"0\",\"VideoPropId\":\"0\",\"TakeRate\":\"0\",\"VideoRecordIsMakup\":\"0\",\"ImageTakePhotoIsMakup\":\"0\",\"VideoRecordFilterId\":\"0\",\"ImageFontId\":\"0\",\"FromType\":\"1\",\"ImageStrickId\":\"0\"}]"
    }
    const data = {
        productId: commentWare.wareId,
        kocSynFlag: "0",
        categoryList: commentWare.categoryList,
        voucherStatus: "0",
        extInfo: extInfo,
        officerScore: "1699",
        anonymousFlag: "1",
        commentScore: "5",
        shopType: "0",
        orderId: commentWare.orderId,
        shopId: commentWare.shopId,
        addPictureFlag: "0",
        commentData: commentData,
        pictureInfoList: pictureInfoList,
        officerLevel: "3",
        isCommentTagContent: "0"
    }
    if (pictureInfoList.length <= 0) {
        delete data.extInfo
        data.pictureInfoList = ""
    }
    const submitRes = JdCommonReq("pubComment", JSON.stringify(data))
    console.log(submitRes);
    if (submitRes) {
        return submitRes
    }
    return false
}

function getGoodCommentAndPic(sku, pageNum = 1) {
    const data = {
        sortType: "5",
        isCurrentSku: false,
        sku: "" + sku,
        pictureCommentType: "A",
        shieldCurrentComment: "1",
        shopType: "0",
        type: "4",
        shadowMainSku: "0",
        num: "10",
        offset: "" + pageNum,
        pageNum: "" + pageNum,
        pageSize: "10"
    }
    const getCommentRes = JdCommonReq("getCommentListWithCard", JSON.stringify(data));
    if (getCommentRes) {
        return getCommentRes
    }
    return false
}

function getGoods(pageIndex = "1") {
    const data = {
        status: "1",
        planType: "1",
        pageIndex: pageIndex,
        pageSize: "10"
    };
    const body = JdCommonReq("getCommentWareList", JSON.stringify(data))
    if (body) {
        return body
    }
    return false
}

function bytesToString(params, ascii) { //该方法只适用于utf-8编码和ascii编码,参数为byte数组
    var result = "";
    if (ascii) {
        for (var i = 0; i < params.length; i++) {
            result += String.fromCharCode(params[i]);
        }
        return result;
    }
    for (var i = 0; i < params.length; i++) {
        if (params[i] >= 0xf8) { //超过0xf8=11111000,属于不合法字符
            result += String.fromCharCode(params[i]);
        } else if (params[i] >= 0xf0) { //0xf0=11110000,表示该起始字节有3个后续字节
            var bits = (params[i] & 0x07) << 18 | (params[i + 1] & 0x3f) << 12 | (params[i + 2] & 0x3f) << 6 | (params[i + 3] & 0x3f);
            result += String.fromCharCode(bits);
            i += 3;
        } else if (params[i] >= 0xe0) { //0xe0=11100000,表示该起始字节有2个后续字节
            var bits = (params[i] & 0x0f) << 12 | (params[i + 1] & 0x3f) << 6 | (params[i + 2] & 0x3f);
            result += String.fromCharCode(bits);
            i += 2;
        } else if (params[i] >= 0xc0) { //0xc0=11000000,表示该起始字节有1个后续字节
            var bits = (params[i] & 0x1f) << 6 | (params[i + 1] & 0x3f);
            result += String.fromCharCode(bits);
            i++;
        } else { //[227,132,128],[194,128]的情形已经融入到上面的判断语句中
            result += String.fromCharCode(params[i]);
        }
    }
    return result;
}

function stringToBytes(param, ascii) { //该方法只适用于utf-8编码和ascii编码(适用于生成文件),参数为string
    var bytes = [];
    if (ascii) {
        for (var i = 0; i < param.length; i++) {
            bytes.push(param.charCodeAt(i));
        }
        return bytes;
    }
    for (var i = 0; i < param.length; i++) {
        var c = param.charCodeAt(i);
        if (c == 0) { //兼容ascii编码向utf8转码,一般用不到
            bytes.push(0xe3); //0xe3=227
            bytes.push(0x84); //0x84=132
            bytes.push(0x80); //0x80=128
        } else if (c < 0x80) { //c < 128,首位为0,剩余7位
            bytes.push(c);
        } else if (c < 0x100) { //c < 256,兼容ascii编码向utf8转码,一般用不到
            bytes.push(0xc2); //0xc2=194
            bytes.push(c);
        } else if (c < 0x800) { //c < 2048,首位为110,表示该起始字节有1个后续字节,剩余5位
            bytes.push(((c >> 6) & 0x1f) | 0xc0); //0xC0=11000000,&0x1f表示取低5位(高位补0)
            bytes.push((c & 0x3f) | 0x80); //0x80=10000000,&0x3f表示取低6位(对64求余)
        } else if (c < 0x10000) { //c < 65536,首位为1110,表示该起始字节有2个后续字节,剩余4位
            bytes.push(((c >> 12) & 0x0f) | 0xe0); //0xE0=11100000,&0x0f表示取低4位(对16求余,高位补0)
            bytes.push(((c >> 6) & 0x3f) | 0x80);
            bytes.push((c & 0x3f) | 0x80);
        } else if (c < 0x10ffff) { //c < 2097152,首位为11110,表示该起始字节有3个后续字节,剩余3位
            bytes.push(((c >> 18) & 0x07) | 0xf0); //0xF0=11110000,&0x07表示取低3位(高位补0)
            bytes.push(((c >> 12) & 0x3f) | 0x80);
            bytes.push(((c >> 6) & 0x3f) | 0x80);
            bytes.push((c & 0x3f) | 0x80);
        } else return null; //超过0x10ffff,属于不合法字符
    }
    return bytes;
}

function base64(params, ascii) { //将byte数组(或字符串)转换成base64
    var BASE64C = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 43, 47];
    if (params == null) return null;
    if (typeof params === "string") params = stringToBytes(params, ascii); //该方法只适用于utf-8编码和ascii编码
    var result = new Array(); //每3个字节一组,重组为4个字节一组
    var index = 0;
    for (var i = 0; i < parseInt(params.length / 3) * 3; i += 3) { //除3取整再乘3可以取到最后面的3的倍数个
        var bits = (params[i] & 0xff) << 16 | (params[i + 1] & 0xff) << 8 | (params[i + 2] & 0xff); //&0xff表示由byte转int,<<表示向左移多少位,高位会被丢弃,低位会补0
        result[index++] = BASE64C[(bits >>> 18) & 0x3f]; //&0x3f表示保留6位数(类似对64求余),>>表示向右移多少位,低位会被丢弃,高位补0(无符号)或1(有符号),>>>表示向右移多少位,高位补0(无符号)
        result[index++] = BASE64C[(bits >>> 12) & 0x3f];
        result[index++] = BASE64C[(bits >>> 6) & 0x3f];
        result[index++] = BASE64C[bits & 0x3f];
    }
    if (params.length % 3 == 1) { //多余1个加两个=号
        var bits = (params[params.length - 1] & 0xff) << 4;
        result[index++] = BASE64C[(bits >>> 6) & 0x3f];
        result[index++] = BASE64C[bits & 0x3f];
        result[index++] = 61; //stringToBytes('=')
        result[index] = 61;
    } else if (params.length % 3 == 2) { //多余2个加一个=号
        var bits = (params[params.length - 2] & 0xff) << 10 | (params[params.length - 1] & 0xff) << 2;
        result[index++] = BASE64C[(bits >>> 12) & 0x3f];
        result[index++] = BASE64C[(bits >>> 6) & 0x3f];
        result[index++] = BASE64C[bits & 0x3f];
        result[index] = 61;
    }
    return bytesToString(result);
}

function countUniqueChineseCharacters(inputString) {
    // 用于存储唯一中文字符的数组
    const uniqueChineseCharacters = [];

    // 定义匹配中文字符的正则表达式
    const chineseCharacterRegex = /[\u4e00-\u9fa5]/;

    // 遍历输入字符串的每个字符
    for (let index = 0; index < inputString.length; index++) {
        const currentCharacter = inputString[index];

        // 检查当前字符是否是中文字符，并且是否尚未在数组中
        if (chineseCharacterRegex.test(currentCharacter) &&
            !uniqueChineseCharacters.includes(currentCharacter)) {

            // 将唯一的中文字符添加到数组中
            uniqueChineseCharacters.push(currentCharacter);
        }
    }

    // 返回唯一中文字符的数量
    return uniqueChineseCharacters.length;
}

function randomCommentByArr(textArr) {
    for (let i = textArr.length - 1; i > 0; i--) {
        const randomNumber = Math.floor(Math.random() * (i + 1));
        [textArr[i], textArr[randomNumber]] = [textArr[randomNumber], textArr[i]];
    }
    return textArr.join(",");
}

function randomChoose(strArr) {
    return strArr[Math.floor(Math.random() * strArr.length)] || "";
}

function shuffleAndTake(arr, num) {
    // 复制输入数组，以不改变原始数组
    const shuffledArray = arr.slice();

    let arrayLength = arr.length,
        randomIndex,
        tempValue;

    while (arrayLength--) {
        // 生成一个随机索引
        randomIndex = Math.floor((arrayLength + 1) * Math.random());

        // 交换当前位置和随机位置的元素
        tempValue = shuffledArray[randomIndex];
        shuffledArray[randomIndex] = shuffledArray[arrayLength];
        shuffledArray[arrayLength] = tempValue;
    }

    // 返回洗牌后的数组的前 num 个元素
    return shuffledArray.slice(0, num);
}

function confirmOrder(gaiaGoods) {
    const confirmOrderText = `========订单确定========\n类型-----单价(积分)-----数量\n${gaiaGoods.title}-----${gaiaGoods.price}-----${gaiaGoods.quantity}\n\n账号：${GetUserID()}\n回复【q】退出,回复【y确定订单】`
    sendText(confirmOrderText)
    let confirmInput = input(30000, 100);
    if (confirmInput === "q") {
        sendText("退出成功")
        return false
    }
    if (confirmInput === "") {
        sendText("输入超时，程序自动退出")
        return false
    }
    if (confirmInput === "y") {
        return true
    }
    sendText("输入有误，退出程序")
    return false
}

function payCallback(payResult) {
    const payText = `==========结算==========\n【类型】${payResult.data.goods.title}\n【总价】${payResult.data.totalAmount}\n【账号】${GetUserID()}\n【订单号】${payResult.data.orderID}\n【支付结果】${payResult.msg}\n【支付时间】${call("unixTimeFormat")(parseInt(Number(payResult.data.paymentTime) / 1000), parseInt(Number(payResult.data.paymentTime) % 1000), "yyyy-MM-dd hh:mm:ss")}`
    sendText(payText)
    if (payResult.code === 200) {
        return true
    } else {
        return false
    }
}

function cancalOrder(gaia, success, all, payResult) {
    const orderid = payResult.data.orderID
    const cancelProportion = success / all;
    const cancalResult = gaia.cancelOrder(orderid, 1-cancelProportion)
    const cancalText = `==========退款==========\n【类型】${cancalResult.data.goods.title}\n【总价】${cancalResult.data.totalAmount}\n【账号】${GetUserID()}\n【订单号】${cancalResult.data.orderID}\n【退款积分】${cancalResult.data.refundSituation.refundIntegral}\n【退款余额】${cancalResult.data.refundSituation.refundBalance}\n【退款结果】${cancalResult.msg}\n【退款时间】${call("unixTimeFormat")(parseInt(Number(cancalResult.data.paymentTime) / 1000), parseInt(Number(cancalResult.data.paymentTime) % 1000), "yyyy-MM-dd hh:mm:ss")}`
    sendText(cancalText)
}

function JdCommonReq(functionId, data) {
    // UA = user_Agents(1)
    const headers = {
        Host: "api.m.jd.com",
        accept: "*/*",
        "user-agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "accept-language": "zh-Hans-JP;q=1, en-JP;q=0.9, zh-Hant-TW;q=0.8, ja-JP;q=0.7, en-US;q=0.6",
        Cookie: Cookie
    }
    console.log(UA);
    const sign = signJd(functionId, data)
    // console.log(sign);
    const options = {
        url: "https://api.m.jd.com/client.action?functionId=" + functionId,
        body: `functionId=${functionId}&${sign.body}`,
        method: "post",
        headers
    }
    const res = req(options)
    return res
}

function user_Agents(tjb) {
    function randomStr(num) {
        let str = "0123456789abcdef",
            fstr = "";
        for (let i = 0; i < num; i++) {
            fstr += str[Math.ceil(100000000 * Math.random()) % str.length];
        }
        return fstr;
    }

    function randomA(arr, num) {
        let narr = new Array();
        for (let arrKey in arr) {
            narr.push(arr[arrKey]);
        }
        let temArr = new Array();
        for (let i = 0; i < num; i++) {
            if (narr.length > 0) {
                let randNum = Math.floor(Math.random() * narr.length);
                temArr[i] = narr[randNum];
                narr.splice(randNum, 1);
            } else {
                break;
            }
        }
        return temArr;
    }

    function UARAM(tjb = false) {
        const dictionary = {
            "A": "K",
            "B": "L",
            "C": "M",
            "D": "N",
            "E": "O",
            "F": "P",
            "G": "Q",
            "H": "R",
            "I": "S",
            "J": "T",
            "K": "A",
            "L": "B",
            "M": "C",
            "N": "D",
            "O": "E",
            "P": "F",
            "Q": "G",
            "R": "H",
            "S": "I",
            "T": "J",
            "e": "o",
            "f": "p",
            "g": "q",
            "h": "r",
            "i": "s",
            "j": "t",
            "k": "u",
            "l": "v",
            "m": "w",
            "n": "x",
            "o": "e",
            "p": "f",
            "q": "g",
            "r": "h",
            "s": "i",
            "t": "j",
            "u": "k",
            "v": "l",
            "w": "m",
            "x": "n"
        };
        const cipher = {
            "ud": "",
            "sv": "",
            "iad": ""
        };
        let sv = randomA([12, 13, 14, 15, 16], 1) + "." + randomA([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 1) + "." + randomA([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 1),
            jdb = randomA([10, 11, 12], 1) + "." + randomA([0, 1, 2, 3, 4, 5, 6, 7, 8], 1) + "." + randomA([0, 1, 2, 3, 4, 5], 1),
            liteb = randomA([4, 5, 6], 1) + "." + randomA([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 1) + "." + randomA([0, 1, 2, 3, 4, 5], 1),
            ep = {
                "ciphertype": 5,
                "cipher": cipher,
                "ts": parseInt(new Date().getTime() / 1000),
                "hdid": "",
                "version": "1.0.3",
                "appname": "",
                "ridx": -1
            };
        ep.cipher.sv = base64(stringToBytes(sv)).split("").map(_0x49219d => dictionary[_0x49219d] || _0x49219d).join("");
        ep.cipher.ud = base64(stringToBytes(randomStr(40))).split("").map(_0x2db617 => dictionary[_0x2db617] || _0x2db617).join("");
        ep.appname = "com.jingdong.app.mall";
        ep.hdid = "JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=";
        let jdUa = "jdapp;android;" + "11.2.2" + ";;;M/5.0;appBuild/98990;ef/1;ep/" + encodeURIComponent(JSON.stringify(ep)) + ";jdSupportDarkMode/0;Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046269 Mobile Safari/537.36";
        ep.appname = "com.jd.jdmobilelite";
        ep.hdid = "ViZLFbOc+bY6wW3m9/8iSFjgglIbmHPOGSM9aXIoBes=";
        ep.ridx = 1;
        let liteUa = "jdltapp;android;" + liteb + ";;;M/5.0;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;hasOCPay/0;appBuild/1338;supportBestPay/0;jdSupportDarkMode/0;ef/1;ep/" + encodeURIComponent(JSON.stringify(ep)) + ";Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 MQQBrowser/6.2 TBS/046269 Mobile Safari/537.36";
        return tjb ? liteUa : jdUa;
    }
    return UARAM(tjb)
}

function signJd(functionId, body, client = "android", clientVersion = '11.2.2') {
    function get_sign(functionId, body, client = "android", clientVersion = '11.2.2') {
        console.log(functionId, body);
        const d = JSON.parse(body)
        if (d.hasOwnProperty("eid")) {
            eid = d["eid"]
        } else {
            eid = randomeid()
        }
        const { ep, ts, jduuid, d_brand } = getep()
        const version = [[0, 2], [1, 1], [2, 0]];
        const r1r2 = version[Math.floor(Math.random() * version.length)];
        const r1 = r1r2[0];
        const r2 = r1r2[1];
        const sv = "1" + r1 + r2;
        const all_arg = `functionId=${functionId}&body=${body}&uuid=${jduuid}&client=${client}&clientVersion=${clientVersion}&st=${ts}&sv=${sv}`;
        const by = stringToBytes(all_arg)
        const back_base64 = sign_core(by)
        const sign = call("md5")(back_base64)
        const ext = encodeURIComponent('{"prstate":"0","pvcStu":"1"}');
        const partner = d_brand.toLowerCase();
        const convertUrl = `body=${encodeURIComponent(body)}&clientVersion=${clientVersion}&build=98935&client=${client}&partner=${partner}&sdkVersion=31&lang=zh_CN&harmonyOs=0&networkType=wifi&ext=${ext}&oaid=${jduuid}&eid=${eid}&ef=1&ep=${encodeURIComponent(ep)}&st=${ts}&sign=${sign}&sv=${sv}`;
        console.log(convertUrl);
        const result = {
            code: 200,
            fn: functionId,
            body: convertUrl,
            data: {
                functionId,
                body,
                clientVersion,
                client,
                partner,
                sdkVersion: '31',
                lang: 'zh_CN',
                harmonyOs: '0',
                networkType: 'wifi',
                ext,
                oaid: jduuid,
                eid,
                ef: '1',
                ep: encodeURIComponent(ep),
                st: ts,
                sign,
                sv,
                convertUrl,
            },
        };
        return result
    }

    function stringToBytes(param, ascii) { //该方法只适用于utf-8编码和ascii编码(适用于生成文件),参数为string
        var bytes = [];
        if (ascii) {
            for (var i = 0; i < param.length; i++) {
                bytes.push(param.charCodeAt(i));
            }
            return bytes;
        }
        for (var i = 0; i < param.length; i++) {
            var c = param.charCodeAt(i);
            if (c == 0) { //兼容ascii编码向utf8转码,一般用不到
                bytes.push(0xe3); //0xe3=227
                bytes.push(0x84); //0x84=132
                bytes.push(0x80); //0x80=128
            } else if (c < 0x80) { //c < 128,首位为0,剩余7位
                bytes.push(c);
            } else if (c < 0x100) { //c < 256,兼容ascii编码向utf8转码,一般用不到
                bytes.push(0xc2); //0xc2=194
                bytes.push(c);
            } else if (c < 0x800) { //c < 2048,首位为110,表示该起始字节有1个后续字节,剩余5位
                bytes.push(((c >> 6) & 0x1f) | 0xc0); //0xC0=11000000,&0x1f表示取低5位(高位补0)
                bytes.push((c & 0x3f) | 0x80); //0x80=10000000,&0x3f表示取低6位(对64求余)
            } else if (c < 0x10000) { //c < 65536,首位为1110,表示该起始字节有2个后续字节,剩余4位
                bytes.push(((c >> 12) & 0x0f) | 0xe0); //0xE0=11100000,&0x0f表示取低4位(对16求余,高位补0)
                bytes.push(((c >> 6) & 0x3f) | 0x80);
                bytes.push((c & 0x3f) | 0x80);
            } else if (c < 0x10ffff) { //c < 2097152,首位为11110,表示该起始字节有3个后续字节,剩余3位
                bytes.push(((c >> 18) & 0x07) | 0xf0); //0xF0=11110000,&0x07表示取低3位(高位补0)
                bytes.push(((c >> 12) & 0x3f) | 0x80);
                bytes.push(((c >> 6) & 0x3f) | 0x80);
                bytes.push((c & 0x3f) | 0x80);
            } else return null; //超过0x10ffff,属于不合法字符
        }
        return bytes;
    }

    function bytesToString(params, ascii) { //该方法只适用于utf-8编码和ascii编码,参数为byte数组
        var result = "";
        if (ascii) {
            for (var i = 0; i < params.length; i++) {
                result += String.fromCharCode(params[i]);
            }
            return result;
        }
        for (var i = 0; i < params.length; i++) {
            if (params[i] >= 0xf8) { //超过0xf8=11111000,属于不合法字符
                result += String.fromCharCode(params[i]);
            } else if (params[i] >= 0xf0) { //0xf0=11110000,表示该起始字节有3个后续字节
                var bits = (params[i] & 0x07) << 18 | (params[i + 1] & 0x3f) << 12 | (params[i + 2] & 0x3f) << 6 | (params[i + 3] & 0x3f);
                result += String.fromCharCode(bits);
                i += 3;
            } else if (params[i] >= 0xe0) { //0xe0=11100000,表示该起始字节有2个后续字节
                var bits = (params[i] & 0x0f) << 12 | (params[i + 1] & 0x3f) << 6 | (params[i + 2] & 0x3f);
                result += String.fromCharCode(bits);
                i += 2;
            } else if (params[i] >= 0xc0) { //0xc0=11000000,表示该起始字节有1个后续字节
                var bits = (params[i] & 0x1f) << 6 | (params[i + 1] & 0x3f);
                result += String.fromCharCode(bits);
                i++;
            } else { //[227,132,128],[194,128]的情形已经融入到上面的判断语句中
                result += String.fromCharCode(params[i]);
            }
        }
        return result;
    }

    function base64(params, ascii) { //将byte数组(或字符串)转换成base64
        var BASE64C = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 43, 47];
        if (params == null) return null;
        if (typeof params === "string") params = stringToBytes(params, ascii); //该方法只适用于utf-8编码和ascii编码
        var result = new Array(); //每3个字节一组,重组为4个字节一组
        var index = 0;
        for (var i = 0; i < parseInt(params.length / 3) * 3; i += 3) { //除3取整再乘3可以取到最后面的3的倍数个
            var bits = (params[i] & 0xff) << 16 | (params[i + 1] & 0xff) << 8 | (params[i + 2] & 0xff); //&0xff表示由byte转int,<<表示向左移多少位,高位会被丢弃,低位会补0
            result[index++] = BASE64C[(bits >>> 18) & 0x3f]; //&0x3f表示保留6位数(类似对64求余),>>表示向右移多少位,低位会被丢弃,高位补0(无符号)或1(有符号),>>>表示向右移多少位,高位补0(无符号)
            result[index++] = BASE64C[(bits >>> 12) & 0x3f];
            result[index++] = BASE64C[(bits >>> 6) & 0x3f];
            result[index++] = BASE64C[bits & 0x3f];
        }
        if (params.length % 3 == 1) { //多余1个加两个=号
            var bits = (params[params.length - 1] & 0xff) << 4;
            result[index++] = BASE64C[(bits >>> 6) & 0x3f];
            result[index++] = BASE64C[bits & 0x3f];
            result[index++] = 61; //stringToBytes('=')
            result[index] = 61;
        } else if (params.length % 3 == 2) { //多余2个加一个=号
            var bits = (params[params.length - 2] & 0xff) << 10 | (params[params.length - 1] & 0xff) << 2;
            result[index++] = BASE64C[(bits >>> 12) & 0x3f];
            result[index++] = BASE64C[(bits >>> 6) & 0x3f];
            result[index++] = BASE64C[bits & 0x3f];
            result[index] = 61;
        }
        return bytesToString(result);
    }

    function sign_core(inarg) {
        let key = stringToBytes('80306f4370b39fd5630ad0529f77adb6')
        let mask = [0x37, 0x92, 0x44, 0x68, 0xA5, 0x3D, 0xCC, 0x7F, 0xBB, 0xF, 0xD9, 0x88, 0xEE, 0x9A, 0xE9, 0x5A]
        let array = []
        for (let i = 0; i < inarg.length; i++) {
            let r0 = inarg[i]
            let r2 = mask[i & 0xf]
            let r4 = key[i & 7]
            r0 = r2 ^ r0
            r0 = r0 ^ r4
            r0 = r0 + r2
            r2 = r2 ^ r0
            let r1 = key[i & 7]
            r2 = r2 ^ r1
            array[i] = r2 & 0xff
        }
        // console.log(array)
        return base64(array)
    }

    function randomeid() {
        return "eidAaf8081218as20a2GM" + randomstr(20) + "7FnfQYOecyDYLcd0rfzm3Fy2ePY4UJJOeV0Ub840kG8C7lmIqt3DTlc11fB/s4qsAP8gtPTSoxu"
    }

    function randomstr(num) {
        let string = '';
        let str1 = "abcdefghijklmnopqrstuvwxyz0123456789"
        for (let i = 0; i < num; i++) {
            string += str1.charAt(Math.floor(Math.random() * str1.length));
        }
        return string;
    }

    function translate(str, str1, str2) {
        let str3 = ''
        for (let i = 0; i < str.length; i++) {
            for (let j = 0; j < str1.length; j++) {
                if (str[i] === str1[j]) {
                    str3 += str2[j]
                }
            }
        }
        return str3
    }

    function randomhex(num) {
        let string = '';
        let str1 = "abcdef0123456789"
        for (let i = 0; i < num; i++) {
            string += str1.charAt(Math.floor(Math.random() * str1.length));
        }
        return string;
    }

    function uuidv1() {
        return `${randomhex(8)}-${randomhex(4)}-${randomhex(4)}-${randomhex(4)}-${randomhex(12)}`
    }

    function base64Encode(str) {
        return translate(base64(str), "KLMNOPQRSTABCDEFGHIJUVWXYZabcdopqrstuvwxefghijklmnyz0123456789+/", "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/")
    }

    function randomnum(num) {
        let string = '';
        let str1 = "0123456789"
        for (let i = 0; i < num; i++) {
            string += str1.charAt(Math.floor(Math.random() * str1.length));
        }
        return string;
    }
    function getep() {
        let jduuid = uuidv1().replace(/-/g, '').slice(0, 16)
        let ts = Date.now()
        let area = randomnum(2) + '_' + randomnum(4) + '_' + randomnum(5) + '_' + randomnum(4)
        const d_brand_model = {
            "OPPO": ["PAFM00", "PDEM10", "PDRM00", "PENM00", "PGW110"],
            "Xiaomi": ["23078PND5G", "2211133C", "M1902F1A"],
            "HUAWEI": ["LIO-AL00", "OCE-AN10", "JER-AN20", "RTE-AL00"]
        }
        const d_brand = Object.keys(d_brand_model)[Math.floor(Math.random() * (Object.keys(d_brand_model).length))]
        const d_model = d_brand_model[d_brand][Math.floor(Math.random() * (d_brand_model[d_brand].length))]
        const wifiBssid = `TP_LINK_${randomstr(6)}`
        const osVersion = ["10", "11", "12"][Math.floor(Math.random() * (["10", "11", "12"].length))]
        const screen = ["640x1136", "750x1334", "1080x1920"][Math.floor(Math.random() * (["640x1136", "750x1334", "1080x1920"].length))]
        const ep = JSON.stringify({
            "hdid": "JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=",
            "ts": ts,
            "ridx": -1,
            "cipher": {
                "area": base64Encode(area),
                "d_model": base64Encode(d_model),
                "wifiBssid": base64Encode(wifiBssid),
                "osVersion": base64Encode(osVersion),
                "d_brand": base64Encode(d_brand),
                "screen": base64Encode(screen),
                "uuid": base64Encode(jduuid),
                "aid": base64Encode(jduuid),
                "openudid": base64Encode(jduuid)
            },
            "ciphertype": 5,
            "version": "1.2.0",
            "appname": "com.jingdong.app.mall",
        })
        return { ep, ts, jduuid, d_brand }
    }
    return get_sign(functionId, body, client = "android", clientVersion = '11.2.2')
}

function checkConfig() {
    let quantityPay = bucketGet("Y_comment", "quantityPay")
    const money = bucketGet("Y_comment", "money")
    const noCookie = bucketGet("Y_comment", "noCookie")
    const invalid = bucketGet("Y_comment", "invalid")
    let qlQuery = bucketGet("Y_comment", "qlQuery")
    let qlConfigs = bucketGet("Y_comment", "qlConfigs")
    let check = false;
    if (money && quantityPay.toString() && invalid && noCookie) {
        if (qlQuery.toString()&&(qlQuery == ("true" || true))) {
            try {
                const qlarr = JSON.parse(qlConfigs);
                if (qlarr) {
                    qlConfigs = qlarr
                    check = true
                }
            } catch (e) {
                check = false
            }
        } else {
            check = true
        }
        check = true
    }
    quantityPay == ("true" || true) ? quantityPay = 1 : quantityPay = 0;
    qlQuery == ("true" || true) ? qlQuery = 1 : qlQuery = 0;
    return {
        quantityPay,
        money,
        noCookie,
        invalid,
        check,
        qlQuery,
        qlConfigs
    }
}

function checkCk(cookie) {
    let check1 = totalBean(cookie)
    Debug(check1)
    if (check1) {
        return true
    } else {
        let check2 = isLoginByX1a0He(cookie)
        Debug(check2)
        if (check2) {
            return true
        } else {
            return false
        }
    }
}

function totalBean(cookie) {
    const options = {
        url: "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion",
        headers: {
            Host: "me-api.jd.com",
            Accept: "*/*",
            Connection: "keep-alive",
            Cookie: cookie,
            "User-Agent": "jdapp;iPhone;9.4.4;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            "Accept-Language": "zh-cn",
            "Referer": "https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&",
            // "Accept-Encoding": "gzip, deflate, br"
        },
        method: "get",
        dataType: "json"
    }
    let res = req(options)
    Debug(JSON.stringify(res))
    if (res) {
        try {
            let data = res
            // Debug(data)
            if (data['retcode'] === "1001") {
                Debug("失效")
                return false
            }
            if (data['retcode'] === "0" && data.data && data.data.hasOwnProperty("userInfo")) {
                return true
            } else {
                return false
            }
        } catch (e) {
            Debug(e)
            Debug("出错了")
            return false
        }

    } else {
        Debug("返回空数据")
        return false
    }
}

function isLoginByX1a0He(cookie) {
    const options = {
        url: 'https://plogin.m.jd.com/cgi-bin/ml/islogin',
        headers: {
            "Cookie": cookie,
            "referer": "https://h5.m.jd.com/",
            "User-Agent": "jdapp;iPhone;10.1.2;15.0;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        },
        method: "get",
        dataType: "json"
    }
    let res = req(options)
    // Debug(JSON.stringify(res))
    if (res) {
        let data = res
        if (data.islogin === "1") {
            return true
        } else if (data.islogin === "0") {
            return false
        } else {
            return false
        }
    } else {
        return false
    }
}

function req(options) {
    try {
        let body = request({
            url: options.url,
            headers: options.headers,
            method: options.method ? options.method : "get",
            dataType: options.dataType ? options.dataType : "json",
            body: options.body ? options.body : "",
            formData: options.formData ? options.formData : {},
            // proxyAddr: "http://8.134.162.53:18082",
            timeOut: 30000
        })
        // console.log(body);
        return body
    } catch (e) {
        Debug(e);
        Debug("发生错误");
        return false
    }
}