//[pin:true]
//[disable:false]
//[title:充值]
//[icon:https://p1.meituan.net/csc/2cdfd231bb55d413e2736cd07dc8c20558125.png]
//[language:es5]
//[price:0]
//[class:工具类]
//[author:hicong]
//[version:1.0.4]
//[open_source:false]
//[platform:wb]
//[public:true]
//[service:728818890]
//[description:指令：充余额、查余额。必须配置微信赞赏码。反馈QQ群233349587]

//[rule: 充余额]
//[rule: 查余额]

//==========================配参数据（最下面）===============================
// [param: {"required":false,"key":"sm_gaia_config.disablePrivateChat","placeholder":"","bool":true,"name":"禁用私聊","desc":"开启则插件不开放私聊回复"}]
// [param: {"required":false,"key":"sm_gaia_config.disableGroupChat","placeholder":"","bool":true,"name":"禁用群聊","desc":"开启则插件不开放群聊回复"}]
// [param: {"required":false,"key":"sm_gaia_config.groupWhitelist","placeholder":"","name":"群聊白名单","desc":"留空不填写则表示全监听，填写则只回复设置的群组。多个id用英文逗号分割"}]
// [param: {"required":true,"key":"sm_gaia_config.WXQRURL","placeholder":"","name":"微信赞赏码url","desc":"填写你机器人微信赞赏码url"}]
// [param: {"required":true,"key":"sm_gaia_config.WXQRRechargeInstruction","placeholder":"","name":"自定义充余额命令","desc":"默认：充余额"}]
// [param: {"required":true,"key":"sm_gaia_config.queryBalanceInstruction","placeholder":"","name":"自定义查余额命令","desc":"默认：查余额"}]

//充值
function chongzhi() {
  if (atWaitPay()) {
    sendText("赞赏系统正在运行，请稍等再试")
    return
  }
  zsm=bucketGet("sm_gaia_config", "WXQRURL") || null
  sendImage(zsm)
  sendText("请在2分钟内使用【微信APP】完成打赏，期间不要发其他内容！回复'q'退出！")
  pay=waitPay(120000,'q')
  if (pay == 'timeout') {
	sendText('超时了，自动退出')
	return
  }
  if (pay == 'q') {
	sendText('退出成功')
	return
  }
  jifen=bucketGet(("sm_gaia_userData_" + GetImType().toUpperCase()), GetUserID()) || null
  if (jifen == null) {
    bucketSet("sm_gaia_userData_" + GetImType().toUpperCase(), GetUserID(), `{"balance":${(pay.money*100)},"isBlacklist":false,"registrationTime":"${timeFmt()}"}`)
  } else {
    userData=JSON.parse(bucketGet(("sm_gaia_userData_" + GetImType().toUpperCase()), GetUserID()))
    balance=userData.balance + (pay.money*100)
    bucketSet("sm_gaia_userData_" + GetImType().toUpperCase(), GetUserID(), `{"balance":${balance},"isBlacklist":false,"registrationTime":"${timeFmt()}"}`)
  }
  sendText(`充值${(pay.money)*100}`)
}
//查余额
function chayue() { userData=bucketGet(("sm_gaia_userData_" + GetImType().toUpperCase()), GetUserID()) || false
if (!userData) {
sendText("余额：0")
return
}
sendText("余额：" + JSON.parse(userData).balance)
}
//主进程
function main() {
    // 回复检测
    // 是否禁用私聊
    var disablePrivateChat = bucketGet('sm_ddb_config', 'disablePrivateChat') === "true" ? true : false
    //sendText(GetChatID())
    if (disablePrivateChat && GetChatID() == "") {
        console.log("【顿顿饿】已禁止私聊回复")
        //Continue()
        return
    }
    // 是否禁用群聊
    var disableGroupChat = bucketGet('sm_ddb_config', 'disableGroupChat') === "true" ? true : false
    if (disableGroupChat && GetChatID() != 0) {
        console.log("【顿顿饿】已禁止群聊回复")
        //Continue()
        return
    }
    // 群聊检测
    let groupWhitelist = bucketGet('sm_ddb_config', 'groupWhitelist').split(/[,，]/);
    if (GetChatID() != 0 && groupWhitelist[0] != "" && groupWhitelist.indexOf(GetChatID().toString()) == -1) {
        console.log("【顿顿饿】非白名单群聊")
        //Continue()
        return
    }
    var WXQRRechargeInstruction = bucketGet("sm_gaia_config", "WXQRRechargeInstruction") || "充余额"
    var queryBalanceInstruction = bucketGet("sm_gaia_config", "queryBalanceInstruction") || "查余额"
    if (GetContent() == WXQRRechargeInstruction) {
        chongzhi()
    } else if (GetContent() == queryBalanceInstruction) {
        chayue()
    }
}
main()