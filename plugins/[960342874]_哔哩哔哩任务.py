//[pin:true]
//[public:true]
// [disable:false]
// [author: 960342874]
// [create_at: 2023-07-18 16:47:00]
// [version: v1.0.2]
// [title: 哔哩哔哩任务]
// [class: 工具类]
// [description: 指令：一键哔哩 <br>说明：自动执行任务 |每日登录经验 |每日观看视频任务|视频投币任务 |直播签到任务|辣条收取|漫画签到|应援团签到|硬币兑换| 修复qq wx tg 频道 全部支持 更新内容：无需再重复登录，直到登录失效，新增用户信息模块。]
// [platform: qq,vx,tg,频道]
// [price:1]
//================================================================
// [rule: 一键哔哩]
// [icon: https://z1.ax1x.com/2023/12/02/pisWK2V.png]
// [service: 交流群758982908]

//importJs("auth.js")
function main() {
   // 授权判断
  //var authData = auth();
  // if (authData && !authData.code) {
  //   sendText(authData.data)
  //   return;
  // }
  
  
  
  

	

  var plugin_key = "yjbl";
  var userID = GetUserID()
   yunhei = request({ 
    url: "https://ztt-1251929976.cos.ap-beijing.myqcloud.com/aut_plugin.txt", 
    //请求链接
    "method": "get",
    //请求方法
    "dataType": "json",
    //返回json
    })
  if(!yunhei || !yunhei[plugin_key] ) {
      //未请求成功
      sendText("警告,未经过验证！")
      return;
    }
    else if (yunhei[plugin_key]['state'] == "invalid") {
      // 插件无效禁用
      sendText(yunhei[plugin_key]['invalid_info']);
      return;
    }
    else if(GetImType()!="fake" && yunhei.master_yunhei.data.indexOf(userID) > -1) {
      // 总云黑
      sendText(yunhei['master_yunhei']['msg']+ "----ALL");
      return;
    }
    else if(GetImType()!="fake" && yunhei[plugin_key]['branch_yunhei']['data'].indexOf(userID) > -1) {
      // 分支云黑
      sendText(yunhei['master_yunhei']['msg']  + "----"+ yunhei[plugin_key]['name'] );
      return;
    }
  
  sendText("正在执行,请稍后...")
   var userData = get("bili_" + userID);
	if (userData) {
		userData = JSON.parse(userData);

		if (userData && userData.data && userData.data.token && userData.data.csrf) {
			    var dataEnd = send(userID, userData);
            if (dataEnd['info'].indexOf('哔哩') > -1   &&  dataEnd['result'].indexOf('每日') > -1)  {
              sendText(dataEnd['info']);
              sendText(dataEnd['result']);
              return;
            }
            else {
             sendText("您的账号已失效！");
            }

		}
	}




	data1 = request({
		url: "https://api.txcnm.cn/api/bilibili/bililogin?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&do=getqrcode",
		//请求链接
		"method": "get",
		//请求方法
		"dataType": "json",
		//返回json
	})
  
  if (data1) {
    
    img = imageDownload("https://api.aiproxy.win/API/qrcode/api.php?text="+encodeURIComponent(data1.url)+"&size=216");

      username = bucketGet("cloud", "username")
      password = bucketGet("cloud", "password")
      body = request({
          url: "http://aut.zhelee.cn/imgUpload",
          method: "post",
          dataType: "json",
          formData: {
              username: username,
              password: password,
          },
          fileData: {
              imgfile: img.local
          }
      })
     // sendText("1111"+JSON.stringify(body.path))


      //转码
    if(body && body.result && body.result.path){
      var ewm = `[CQ:image,file=${body.result.path}]`
      sendText(userID + "请在60s使用哔哩哔哩app扫码登录！" +ewm )
    }
  }
	
	var data2;

	for (let i = 0; i < 30; i++) {
      
      if (i !== 0) {
        sleep(2000);
      }
		

		if (data2 && data2.data && data2.data.token && data2.data.csrf) {

			var dataEnd = send(userID, data2);
        sendText(dataEnd.info);
        sendText(dataEnd.result);
			set("bili_" + userID, JSON.stringify(data2));
			break;
		}


		data2 = request({
			url: "https://api.txcnm.cn/api/bilibili/bililogin?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&do=qrlogin&zkey=" + data1.key,
			//请求链接
			"method": "get",
			//请求方法
			"dataType": "json",
			//返回json
		})

		if (i >= 29) {
			sendText(userID + "\n取消扫码或已超时！")
			return;

		}



	}
  
 

}

function send(userID, data2) {

    
    var url2 = "https://api.txcnm.cn/api/bilibili/biliuser?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&mid="+data2.data.mid+"&mid_md5="+data2.data.mid_md5+"&token="+data2.data.token+"&csrf="+data2.data.csrf;
  
  var info_true;
  var count = 0;
  while (count < 3) {
    count++;
    if (info_true && info_true != null && info_true != 'null') {
    	break;
    }
    info_true = request({
		url: url2,
		//请求链接
		"method": "get",
      timeout:10000
	})
  
  }
  
  

	//做任务
  
  url = "https://api.txcnm.cn/api/bilibili/bilibili?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&mid="+data2.data.mid+"&mid_md5="+data2.data.mid_md5+"&token="+data2.data.token+"&csrf="+data2.data.csrf;
  
  var info;
  var count = 0;
  while (count < 3) {
    count++;
    if (info && info.indexOf("每日") > -1) {
      break;
    }
    info = request({
      url: url,
      //请求链接
      "method": "get",
      timeout:10000
    })
  
  }

  dataEnd = {
     "info":  "您的信息如下：\n"+info_true,
     "result":  "任务执行如下：\n" + info
  }
  
  return dataEnd;

}

main()