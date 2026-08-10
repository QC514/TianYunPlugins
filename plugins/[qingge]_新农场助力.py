
//[disable:false]
//[title: 新农场助力]
//[rule:新农场助力]
//[rule:火爆推送]
//[rule:新农场助力2]
//[rule:新农场管理]
//[rule:新农场开通]
//[rule:新农场开关重置]
//[rule:单助力]
//[rule:^新助力码助力+([\s\S]+)$]
//[rule:新农场火爆]
//[author: qingge] 作者，要与aut插件云账号保持一致，否则收费插件无法到账
//[class: 工具类]
//[public: true] 
//[price: 8.8] 
//[version: 0.3.2] 
//[admin: false] 
//[platform: qq,wx,tg,wb,qb]
//[priority: 9999999999]
//[service: 97393412]
//[description: 【新农场助力】多个助力码，【单农场助力】指定助力码<br/>增加指令：新农场助力,新农场管理,新农场开通,增加不使用代理<br/>过滤助力满的通知<br/>增加指令(火爆推送)把收集到火爆的PIN。进行推送给用户<br/>4.12 支持过滤用户助力]
// [param: {"required":true,"key":"otto.ql_name","placeholder":"填写你需要调用的容器名字","name":"容器名称","desc":"填写你需要调用的容器名字"}]
// [param: {"required":true,"key":"who_tong.h5st_api","placeholder":"http://110.40.165.213:39000","name":"自建H5接口","desc":"填写你搭建好的地址：http://110.40.165.213:39000"}]
// [param: {"required":false,"key":"who_tong.xnc_yhpc","placeholder":"","name":"用户排除","desc":"过滤PIN参与助力,多个用,号分开"}]
//[param: {"spliter":true}]
// [param: {"required":true,"key":"who.xnczl","placeholder":"","name":"自用助力码","desc":"格式："}]
// [param: {"required":true,"key":"who_tong.xnc_dbts","placeholder":"","name":"火爆推送底部提示","desc":"温馨提示：疑似您的账号出现滑块了,请你去过一下滑块哦"}]
// [param: {"required":true,"key":"who_tong.xnc_tsyc","placeholder":"","name":"推送延迟(秒)","desc":"每次推送的延迟,例如:5"}]
// [param: {"required":true,"key":"who_tong.xnc_tsqd","placeholder":"","name":"通知渠道","desc":"wb,qq"}]
// [param: {"required":false,"key":"who_tong.xnczl_zlyc","placeholder":"","name":"助力延迟","desc":"不填写默认0延迟,需要自定义延迟,填写数字,例如：5，秒为单位"}]

//[param: {"spliter":true}]
// [param: {"required":false,"key":"who_tong.xnczl_kg","bool":true,"placeholder":"false","name":"积分开关","desc":"是否需要开启扣取积分,默认不开启"}]
// [param: {"required":false,"key":"who_tong.xnczl_moment","placeholder":"180","name":"扣除积分","desc":"每次助力满扣除多少积分,例如：180"}]
// [param: {"required":false,"key":"who_tong.xnczl_jfts","placeholder":"","name":"积分不足尾部提示","desc":"请你先充值积分！指令:充值积分"}]

//[param: {"spliter":true}]
// [param: {"required":true,"key":"who_tong.wyw_poxy","placeholder":"API地址或者代理池地址","name":"代理地址","desc":"巨量是text，,星空/品赞/携趣，都是JSON,代理池需要带http://"}]
// [param: {"required":true,"key":"who_tong.zd_pt","placeholder":"1","name":"代理平台","desc":"巨量=1,星空=2,品赞=3,代理池=4,携取/51代理=5,不使用代理=7,填写你使用平台的数字"}]


//--------------------
var xnczl_kg = bucketGet("who_tong", "xnczl_kg")//积分开关
var xnczl_jfts = bucketGet("who_tong", "xnczl_jfts")//积分不足尾部提示
var xnczl_moment = parseInt(bucketGet("who_tong", "xnczl_moment"))//扣除积分
var xnczl_zlyc = parseInt(bucketGet("who_tong", "xnczl_zlyc"))//助力延迟
var xnc_yhpc = bucketGet("who_tong", "xnc_yhpc")//过滤PIN参与助力
//-----------------
var GetContent = GetContent()
var imType = ImType()
var sign_day = "", nc_h5 = "", nc_ua = "", H5ST = ""
var userId = GetUserID()
var zlcs = 0
var monme = false
var md = 8//控制助力8次
var xnczlcs = 0;
let container, containerEnv, zlfh = ""
var H5ST = bucketGet("who_tong", "h5st_api")
var hb = 0//火爆
var sx = 0//失效
var myzl = 0//没有助力CS
var pro = "", h5st_api = "", jddToken = ""
var dl_kg = false
var daili_kg = true//代理开关
var zlm = ""//助力码
var zlkz = 0//助力控制
var juliang = bucketGet("who_tong", "wyw_poxy")
var pingtai = bucketGet("who_tong", "zd_pt")
var xnc_dbts = bucketGet("who_tong", "xnc_dbts")//提示
var xnc_tsyc = bucketGet("who_tong", "xnc_tsyc")//延迟
var stxs = bucketGet("who_tong", "xnc_tsqd")
var ql_name = bucketGet("otto", "ql_name")//青龙信息
var checkJS = false
try {
  importJs("qinglong.js");
} catch (err) {
  checkJS = true
}
function todau() {
  let today = new Date();

  // 获取当前月份（0-11，因此需要加1）
  let currentMonth = today.getMonth() + 1;
  // 获取当前日期（1-31）
  let currentDate = today.getDate();
  return parseInt(`${currentMonth}${currentDate}`)
}
let dax = "0"
function mian2() {
  var ptp = 0

  if (ql_name == "") {
    sendText("请你先到云配置中设置一下参数")
    return
  }

  let containerData = qls(ql_name)
  // 获取容器对象
  for (let j = 0; j < 5; j++) {
    try {

      container = Qinglong(containerData.host, containerData.client_id, containerData.client_secret)
      containerEnv = container.ApiQL("envs", "", "get", "").data
      j = 10
    } catch (e) {
      // notifyMasters("【新农场助力】链接容器【" + ql_name + "】失败，请检查配置是否正确或网络是否正常")
      //return
    }
  }
  notifyMasters("开始助力..")
  let zlm_code = bucketGet("who", "xnczl")
  let allpsinss = bucketKeys("xbzlm") + zlm_code
  let sd = allpsinss.split(",")
  notifyMasters(sd.length)
  for (let j = 0; j < sd.length; j++) {
    monme = false

    var wbhb_pin = bucketGet("wabao_tong", `xnczl_${todau()}`)
    if (wbhb_pin.indexOf(sd[j]) != -1) {
      sendText(`${sd[j]},助力满.`)
    } else {
      zl(containerEnv, sd[j], 40, j)
      let md = bucketKeys("Fruit_new", sd[j])
      if (md.length == 0) {
        //sendText("未查询到绑定账号，请你先直接发送新农场开通")
        if (monme) {
          Debug("助力满")

          var wabaoshuliang = bucketGet("wabao_tong", `xnczl_${todau()}`)
          if (wabaoshuliang == "") {
            bucketSet("wabao_tong", `xnczl_${todau()}`, sd[j])
          } else {
            bucketSet("wabao_tong", `xnczl_${todau()}`, wabaoshuliang + "," + sd[j])
          }
        }
      } else {
        let PINX = bucketGet("pinWX", md[0])//青龙信息
        if (monme) {
          Debug("助力满")

          var wabaoshuliang = bucketGet("wabao_tong", `xnczl_${todau()}`)
          if (wabaoshuliang == "") {
            bucketSet("wabao_tong", `xnczl_${todau()}`, sd[j])
          } else {
            bucketSet("wabao_tong", `xnczl_${todau()}`, wabaoshuliang + "," + sd[j])
          }
          tuisong(PINX, (`${md[0]}的新农场助力:${zlfh}`))
        } else {
          notifyMasters("助力未满," + sd[j] + ",可能没助力了,退出任务")
          return
        }
      }
    }
  }

  notifyMasters("新农场助力完成！！！" + sd.length)

}

function tuisong(qh, data) {
  console.log(`开始推送-用户ID：${qh}，推送内容：${data}`)
  push({
    imType: "wx",
    userID: qh,
    title: "东东农场新版助力推送结果:",
    groupCode: "",
    content: data,
  });
}
function mian1() {
  if (ql_name == "") {
    sendText("请你先到云配置中设置一下参数")
    return
  }
  let containerData = qls(ql_name)
  // 获取容器对象
  for (let j = 0; j < 5; j++) {
    try {

      container = Qinglong(containerData.host, containerData.client_id, containerData.client_secret)
      containerEnv = container.ApiQL("envs", "", "get", "").data
      j = 10
    } catch (e) {
    }
  }
  let fs = ShuRu("请输入农场助力码，例如格式：【qyllHJf6zgMz】多个助力码用@")
  if (fs == false) {
    return
  }
  var ladon = fs.split("@");//分割
  zlkz = parseInt(ladon[1])
  zlm = ladon[0]
  for (let j = 0; j < ladon.length; j++) {
    sendText("开始助力.." + ladon[j])
    zlm = ladon[j]
    zl(containerEnv, zlm, 40, 1)
    if (monme) {
      sendText("新农场[助力].." + zlfh)
      monme = false
    }
  }


}
function zl(containerEnv, zlm, code, ton) {
  xnczlcs = 0
  var zl_pin = bucketGet("newnc_tong", `xnccs_${todau()}`)
  var hb_pin = bucketGet("newnc_tong", `xnchb_${todau()}`)
  var cookieObj = containerEnv.filter(function (_data) {

    if (xnc_yhpc.indexOf(decodeURIComponent(_data.value.match(/(?<=pt_pin=)[^;]+/g)) != -1 || xnc_yhpc.indexOf(_data.value.match(/(?<=pt_pin=)[^;]+/g)) != -1)) {
      return _data.name == "JD_COOKIE" && _data.status == 0 && zl_pin.indexOf(_data.value.match(/(?<=pt_pin=)[^;]+/g)) == -1&& hb_pin.indexOf(_data.value.match(/(?<=pt_pin=)[^;]+/g)) == -1
    } else {

    }


  });
  if (GetContent == "新农场助力2") {
    var ssa = 300
  } else {
    var ssa = 0
  }
  Debug(cookieObj.length)
  notifyMasters(cookieObj.length)
  for (let sa = ssa; sa < cookieObj.length; sa++) {
    var pina = cookieObj[sa].value.match(/(?<=pt_pin=)[^;]+/g)

    xinchun(cookieObj[sa].value, zlm, code, ton)

    if (monme == true) {
      //sendText("助力满了")
      //monme = false
      return
    } else {

    }
  }





}
function TXfs_tuisong(tx, qh, data) {
  console.log(`开始推送-渠道：${tx},用户ID：${qh}，推送内容：${data}`)
  push({
    imType: tx,
    userID: qh,
    title: "",
    groupCode: "",
    content: data,
  });
}
function jToken(data) {
  for (let k = 0; k < 5; k++) {
    let body = request({
      url: `${host_api}/jddToken`,
      method: "post",
      body: { "url": data },
      headers: {
        "Content-Type": "application/json",
      },
      dataType: "json",//数据类型json(json数据类型)、location(跳转页)
      timeOut: 8000
    })
    if (body) {

      if (body.code = 200) {
        jddToken = body.data.token
        k = 10
        return true
      }

    } else {
      return false
    }
  }
}
function xinchun(cookie, zlm, cs, shuliang) {
  var pina = cookie.match(/(?<=pt_pin=)[^;]+/g)
  if (daili_kg == true) {
    daili()
    dl_kg = true
  } else {
    dl_kg = false
  }
  for (let p = 0; p < 5; p++) {
    try {
      jToken(`https://h5.m.jd.com/`)
      h42_nc(zlm, pina)
      body = request({
        useproxy: dl_kg,
        proxyAddr: pro,
        method: "get",
        url: `https://api.m.jd.com/client.action?${nc_h5}&x-api-eid-token=${jddToken}`,
        // body: nc_h5,
        headers: {
          "origin": "https://h5.m.jd.com",
          "referer": "https://h5.m.jd.com/",
          'user-agent': nc_ua,
          'Cookie': cookie,
        },
        dataType: "json",
        timeOut: 9000
      })
      //data = JSON.parse(body)
      if (body) {


        if (body.code == 0) {
          p = 6

          if (body.data.bizCode === 0) {
            xnczlcs = xnczlcs + 1
            if (xnczlcs == cs) {
              monme = true
            }
            Debug("助力成功," + zlm)
            let zl_pin = bucketGet("newnc_tong", `xnccs_${todau()}`)
            if (zl_pin == "") {
              bucketSet("newnc_tong", `xnccs_${todau()}`, pina)
            } else {
              bucketSet("newnc_tong", `xnccs_${todau()}`, zl_pin + "," + pina)
            }
            //  sendText("助力成功," + pina)
          } else if (body.data.bizCode === 5004) {
            Debug("【助力结果】: 助力失败，今天助力次数已耗尽," + pina)
            let zl_pin = bucketGet("newnc_tong", `xnccs_${todau()}`)
            if (zl_pin == "") {
              bucketSet("newnc_tong", `xnccs_${todau()}`, pina)
            } else {
              bucketSet("newnc_tong", `xnccs_${todau()}`, zl_pin + "," + pina)
            }
          } else if (body.data.bizCode === 5003) {
            Debug("【助力结果】: 已经助力过TA了" + pina)
            let zl_pin = bucketGet("newnc_tong", `xnccs_${todau()}`)
            if (zl_pin == "") {
              bucketSet("newnc_tong", `xnccs_${todau()}`, pina)
            } else {
              bucketSet("newnc_tong", `xnccs_${todau()}`, zl_pin + "," + pina)
            }

          } else if (body.data.bizCode === 5005) {
            //sendText("【助力结果】: 已满助力-" + zlm + ",当前第" + shuliang + "满")
            zlfh = `已满助力-${zlm}.${body.data.result.masterInfo.nickname}`
            notifyMasters("【助力结果】: 已满助力-" + zlm + ",当前第" + shuliang + `满\n${body.data.result.masterInfo.nickname}`)
            xnczlcs = 0
            monme = true
          } else if (body.data.bizCode === 5002) {
            Debug("【助力结果】: 不能给自己助力" + pina)
          } else if (body.data.bizCode === 5001) {
            zlfh = `${body.data.bizMsg}`
            monme = true
          } else if (body.data.bizCode === -1001) {
            Debug("【助力结果】: 活动太火爆了， 请稍后再试~" + pina)
            let zl_pin = bucketGet("newnc_tong", `xnchb_${todau()}`)
            if (zl_pin == "") {
              bucketSet("newnc_tong", `xnchb_${todau()}`, pina)
            } else {
              bucketSet("newnc_tong", `xnchb_${todau()}`, zl_pin + "," + pina)
            }
          }

        } else if (body.code == -30001) {
          let zl_pin = bucketGet("newnc_tong", `xnchb_${todau()}`)
          if (zl_pin == "") {
            bucketSet("newnc_tong", `xnchb_${todau()}`, pina)
          } else {
            bucketSet("newnc_tong", `xnchb_${todau()}`, zl_pin + "," + pina)
          }
          Debug("CK失效--" + pina)
          p = 6
        } else if (body.code == 405) {
          Debug(JSON.stringify(body))
          Debug(body.msg + "--" + pina)


          sleep(800)
        } else {
          Debug(JSON.stringify(body))
        }
      } else {
        Debug(JSON.stringify(body))
      }
    } catch (err) {

      Debug(err)
    }
  }
  if (xnczl_zlyc == "") {

  } else {
    sleep(xnczl_zlyc * 1000)
  }
}
function xin_ua() {//随机UA
  nc_h5 = ""
  nc_ua = ""
  let body = request({
    url: `${host_api}/UA`,
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
      h5_ver = ucxa[2]
    }
    return true
  } else {
    return false
  }
}
function h42_nc(code, pin) {
  xin_ua()
  //jdapp;iPhone;11.4.0;;;M/5.0;appBuild/168341;jdSupportDarkMode/0;ef/1;ep/%7B%22ciphertype%22%3A5%2C%22cipher%22%3A%7B%22ud%22%3A%22EQG4YWGnCtZuC2ZtEWYmZtruDJvuDJU2YWOyDtVuDzqyYJdrYWUzDG%3D%3D%22%2C%22sv%22%3A%22CJCkDs44%22%2C%22iad%22%3A%22%22%7D%2C%22ts%22%3A1720791361%2C%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%22%2C%22version%22%3A%221.0.3%22%2C%22appname%22%3A%22com.360buy.jdmobile%22%2C%22ridx%22%3A-1%7D;Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1;
  let body = request({
    url: `${host_api}/H5ST_V`,
    method: "post",
    body: { "appId": "28981", "fn": "farm_assist", "body": { "version": 1, "inviteCode": String(code), "shareChannel": "", "assistChannel": "" }, "apid": "signed_wh5", "clientVersion": "1.0.0", "cl": "ios", "client": "wh5", "ver": String(h5_ver), "user": String(pin), "xcr": 1, "ua": String(nc_ua) },

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
function getCaption(obj, text) {
  let index = obj.lastIndexOf(text) + text.length - 1;

  obj = obj.substring(index + 1, obj.length);
  return obj;
}
function ShuRu(name) {
  sendText(name)
  var msg = input(60000, 6000)
  if (msg == "q" || msg == "Q" || msg == "") {
    sendText("已退出会话");
    return false
  } else {
    return msg
  }

}
function qls(uid) {//获取奥特曼青龙数据
  allpins = bucketKeys("qls")
  for (let j = 0; j < allpins.length; j++) {
    var ql_a = JSON.parse(bucketGet("qls", String(allpins[j])))
    //sendText(JSON.stringify(ql_a)+"--1")
    if (ql_a.name == uid) {
      return ql_a
    }
  }

}
function todau() {
  let today = new Date();

  // 获取当前月份（0-11，因此需要加1）
  let currentMonth = today.getMonth() + 1;
  // 获取当前日期（1-31）
  let currentDate = today.getDate();
  return parseInt(`${currentMonth}${currentDate}`)
}
function mian() {
  if (checkJS) {
    if (isAdmin()) {
      notifyMasters("请到群内下载【qinglong】依赖插件放到plugin/replies")
    }
    return
  }
  if (H5ST == "") {
    host_api = "http://139.224.135.148:3006"
  } else {
    host_api = H5ST
  }
  if (ql_name == "") {
    sendText("请你先到云配置中设置一下参数")
    return
  }
  if (GetContent == "单助力") {
    if (isAdmin() || imType == "croncmd") {
    } else {
      sendText("叼毛!不要乱搞咯")
      return
    }
    mian1()

  } else if (GetContent == "新农场管理") {
    if (isAdmin() || imType == "croncmd") {
    } else {
      sendText("叼毛!不要乱搞咯")
      return
    }
    var txt = ""
    txt += "=====新农场助力通知=====\n"
    yk = bucketKeys("xbzlm")
    for (let i = 0; i < yk.length; i++) {
      let wskeyck = bucketGet("xbzlm", yk[i])
      let date = new Date(wskeyck * 1000);
      Y = date.getFullYear();
      M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1);
      D = date.getDate();
      s = date.getSeconds();

      let time_who = Date.parse(new Date()).toString();//获取到毫秒的时间戳，精确到毫秒
      time_who = parseInt(time_who / 1000);
      sendText(time_who)
      if (wskeyck > time_who) {
        txt += `${yk[i]}--未到期--${Y}-${M}-${D}\n`
      } else {
        txt += `=====新农场助力到期通知=====\n${yk[i]}--，已经到期--${Y}-${M}-${D}\n`
        //  txfs(`${yk[i]}，已经到期---${Y}-${M}-${D}, "=====新农场助力到期通知====="`)
        bucketSet("xbzlm", yk[i])
      }
    }
    notifyMasters(txt)

  } else if (GetContent == "新农场火爆") {
    if (isAdmin() || imType == "croncmd") {
    } else {
      sendText("叼毛!不要乱搞咯")
      return
    }
    bucketSet("newnc_tong", `xnchb_${todau()}`)
    sendText(`重新[新农场助力]火爆的数据完成`)
  } else if (GetContent == "新农场开关重置") {
    if (isAdmin() || imType == "croncmd") {
    } else {
      sendText("叼毛!不要乱搞咯")
      return
    }
    bucketSet("who_tong", `xnc_rw`, false)
    sendText(`重新[新农场助力]开关重置的数据完成`)
  } else if (GetContent == "火爆推送") {
    if (isAdmin() || imType == "croncmd") {
    } else {
      return
    }
    let data = bucketGet("newnc_tong", `xnchb_${todau()}`).split(",")
    for (let j = 0; j < data.length; j++) {
      var qd = stxs.split(",")
      for (let k = 0; k < qd.length; k++) {
        bind = bucketGet("pin" + qd[k].toUpperCase(), data[j])
        TXfs_tuisong(qd[k], bind, `===JD火爆通知===\n东东账号：${decodeURIComponent(data[j])}\n${xnc_dbts}`)
      }
      sleep(parseInt(xnc_tsyc) * 1000)
    }
  } else if (GetContent == "新农场开通") {
    if (isAdmin() || imType == "croncmd") {
    } else {
      sendText("叼毛!不要乱搞咯")
      return
    }
    sendText("输入新版助力时间天数")
    var inp1 = input(80000)
    if (inp1 == "" || inp1 == "q") {
      sendText("操作超时，已退出会话")
      return

    } else {
      sendText("输入新版助力版助力码")
      var inp2 = input(80000)
      if (inp2 == "" || inp2 == "q") {
        sendText("操作超时，已退出会话")
        return

      } else {
        sendText("更新成功")
        cz_data("xbzlm", inp2, inp1)
      }
    }

  } else {
    var xnc_rw = false
    if (GetContent.indexOf("新助力码助力") > -1) {
      var xnc_rw = bucketGet("who_tong", "xnc_rw")//新农场任务调用开关
      if (xnc_rw == "true") {
        sendText(`亲,抱歉哦,有其他用户正在使用..\n请您等候几分钟后在重新尝试`)
        return
      } else {
        if (xnczl_kg == "true") {
        bucketSet("who_tong", "xnc_rw", true)//新农场任务调用开关
        }
      }
      var password = getCaption(GetContent, '+');
      if (isAdmin() || imType == "croncmd") {
        sendText(`开始助力..${password}`)
      } else {
        if (xnczl_kg == "true") {
          vip_tay()
          var qd = bucketGet("who_user_qd", userId)//获取用户积分
          if (qd == "") {
            sendText("你还没有积分哦\n" + xnczl_jfts)
            bucketSet("who_user_qd", userId, JSON.stringify({ "day": 0, "creationTime": sign_day }))
            bucketSet("who_tong", "xnc_rw", false)//新农场任务调用开关
            return
          } else {
            qd = JSON.parse(qd)
            if (qd.day >= xnczl_moment) {
              sendText(`积分充足,继续下一步任务\n当前积分${qd.day}\n开始助力..${password}\n助力不满不会扣取积分`)
              if (qd.day == "0" || qd.day == 0) {
                sendText(`积分不足,停止任务\n当前积分:${qd.day}\n${xnczl_jfts}`)
                bucketSet("who_tong", "xnc_rw", false)//新农场任务调用开关
                return
              }
            } else {
              sendText(`积分不足,停止任务\n当前积分:${qd.day}\n${xnczl_jfts}`)
              bucketSet("who_tong", "xnc_rw", false)//新农场任务调用开关
              return
            }
          }
        }
      }

      let containerData = qls(ql_name)
      // 获取容器对象
      for (let j = 0; j < 8; j++) {
        try {

          container = Qinglong(containerData.host, containerData.client_id, containerData.client_secret)
          containerEnv = container.ApiQL("envs", "", "get", "").data
          j = 10
        } catch (e) {
        }
      }
      zl(containerEnv, password, 40, 1)
      if (monme) {
        sendText("新农场[助力].." + zlfh)
        if (xnczl_kg == "true") {
          var qd = bucketGet("who_user_qd", userId)//获取用户积分
          qd = JSON.parse(qd)
          bucketSet("who_user_qd", userId, JSON.stringify({ "day": parseInt(qd.day) - xnczl_moment, "creationTime": qd.creationTime }))
        }
      } else {
        sendText("助力未满," + password + ",可能没助力了,退出任务")
      }
      bucketSet("who_tong", "xnc_rw", false)//新农场任务调用开关
    } else {
      if (isAdmin() || imType == "croncmd") {
        mian2()
      }
    }
    //


  }
}
function vip_tay() {
  // 创建 Date 对象
  let date = new Date(new Date());
  // 获取年、月、日、小时、分钟、秒
  var days = parseInt(date / (1000 * 60 * 60 * 24));
  var hours = parseInt((date % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  Y = date.getFullYear();
  M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1);
  D = date.getDate() + ' ';
  s = date.getSeconds();
  // 拼接时间字符串
  let formattedTime = Y + '-' + M + '-' + D;
  sign_day = D
  return formattedTime
}
function addDays(daate, days) {
  let newDate = new Date(daate);
  // 使用 setDate() 方法增加天数
  newDate.setDate(newDate.getDate() + days);
  // 返回增加天数后的日期字符串
  return newDate.toISOString().split('T')[0];
}
function cz_data(tong, zlm, time_days) {
  let dauy = parseInt(time_days)
  let time_who = Date.parse(new Date()).toString();//获取到毫秒的时间戳，精确到毫秒
  time_who = parseInt(time_who / 1000);
  let date = new Date(time_who * 1000);
  Y = date.getFullYear();
  M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1);
  D = date.getDate();
  s = date.getSeconds();
  let time_day = `${Y}-${M}-${D}`
  let newDate = addDays(time_day, dauy);

  let date_time = new Date(newDate);
  let dateString = date_time.toISOString();
  let timestamp = Date.parse(dateString);
  let days = parseInt(timestamp / 1000);
  sendText(`开通成功:${zlm}\n天数：${time_days}`)
  bucketSet(tong, zlm, days)
}
function proxy() {//巨量
  let body = request({
    url: juliang,
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
function daili() {//选择代理模式
  //巨量=1,星空=2,品赞=3
  if (pingtai == 3 || pingtai == "3") {
    //sendText("当前使用--品赞")
    pro = `http://${pinzan()}`
    daili_kg = true
  } else if (pingtai == 2 || pingtai == "2") {
    //sendText("当前使用--星空")
    daili_kg = true
    pro = `http://${xk()}`
  } else if (pingtai == 1 || pingtai == "1") {
    //sendText("当前使用--巨量")
    daili_kg = true
    pro = `http://${proxy()}`
  } else if (pingtai == 4 || pingtai == "4") {
    //sendText("当前使用--代理池")
    daili_kg = true
    pro = juliang
  } else if (pingtai == 5 || pingtai == "5") {
    //sendText("当前使用--携取")
    pro = `http://${xiequ()}`
    daili_kg = true
  } else if (pingtai == 7 || pingtai == "7") {
    //sendText("当前使用--携取")
    //pro = `http://${xiequ()}`
    daili_kg = false
  }
  if (daili_kg) {
    Debug(`当前使用IP:${pro}`)
  } else {
    Debug(`当前不使用IP`)
  }
}
function xk() {//星空
  let body = request({
    url: juliang,
    method: "get",
    // body: water,
    headers: {
      //"Host": "h5.xss333.top:8001",
      "Content-Type": "application/json; charset=utf-8",
    },
    dataType: "json",//数据类型json(json数据类型)、location(跳转页)
    timeOut: 30000
  })
  if (body) {
    if (body.status == 100) {
      var IOP = `${body.data[0].ip}:${body.data[0].port}`
      return IOP
    }
  }
}
function pinzan() {//品赞
  let body = request({
    url: juliang,
    method: "get",
    // body: water,
    headers: {
      //"Host": "h5.xss333.top:8001",
      "Content-Type": "application/json; charset=utf-8",
    },
    dataType: "json",//数据类型json(json数据类型)、location(跳转页)
    timeOut: 30000
  })
  if (body) {
    if (body.code == 0) {
      var IOP = `${body.data.list[0].ip}:${body.data.list[0].port}`
      return IOP
    }
  }

}
function xiequ() {//携趣
  let body = request({
    url: juliang,
    method: "get",
    // body: water,
    headers: {
      //"Host": "h5.xss333.top:8001",
      "Content-Type": "application/json; charset=utf-8",
    },
    dataType: "json",//数据类型json(json数据类型)、location(跳转页)
    timeOut: 30000
  })
  if (body) {
    if (body.code == 0) {
      var IOP = `${body.data[0].IP}:${body.data[0].Port}`
      return IOP
    }
  }

}
mian()