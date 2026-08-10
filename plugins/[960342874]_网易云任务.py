//[pin:true]
//[public:true]
// [disable:false]
// [author: 960342874]
// [create_at: 2023-07-13 16:47:00]
// [version: v1.0.2]
// [title: 网易云任务]
// [class: 工具类]
// [description: 指令：一键网易<br>说明：自动执行任务 1.网易云自动听歌打卡300首升级 2.签到（暂时关闭） 3.云贝签到 4.音乐人任务 修复qq wx tg 频道 全部支持 更新内容：无需再重复登录，直到登录失效。]
// [platform: qq,vx,tg,频道]
// [price:1]
//================================================================
// [rule: 网易云任务]
// [rule: 一键网易|网易云任务]
//[icon: https://img.zcool.cn/community/01e6075c6eb498a801213f265dbd4a.jpg]
// [service:交流群758982908]

//importJs("auth.js")
function main() {
    
    var plugin_key = "wyyrw";
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
    
    
    var hostName = "https://zm.armoe.cn/"; // 低版本可以刷歌
    var specialHostName = "https://api.csm.sayqz.com/" //云贝签到、等级签到

    var wyy_cookie = bucketGet("Hi", "wyynew_" + GetUserID());
    //sendText(wyy_cookie)

    //wyy_cookie = "__csrf=4fc4a4714140e8261eaf87280535e0f5; MUSIC_U=00F86AD304EC65FF7696F910C70E9BD8BE7C910C2BA653E87DA87FE50535B5E8F933740F07603BAB80D8DADD1B8C8649BEC015F3FE5270891B253FB0F2D70360B5CB3D444094E4FA197A1DEAAA0EA0DBAF9145B83BFD74C58F257407EC94470A6BADACBAF4BDEFDEB3DD629354A74E0BEA24B77BEF9B0FB60ED9BEEBBEF926748A34D789E5D14F4CA8D4A65B97422CA724D0F7512F00FB381EC0264ED722B8DCFA6487073F086CC9A8BF90F54F185D6297F02C0CF3B1708F0F6BFA8BB5246D5BA874C8FC63D61AE1FFC38D1D73DCAA2419E7A22E6CB1FEA1EC44A3E09F8686D2EFA954653FAFD5376BDA08F94DD5AB54F85D77A498E227757B10ED5CCB4B53807DC997EEA494CC1B28A3BAD3912A05D112908842C38484639A637C2F7C80A115E4";
    var a1 = "";
    var cookie = "";
    var info = "";






    wyy_cookie = wyy_cookie ? wyy_cookie:"";
  
   
      //个人信息 
    info = request({
      url: hostName + "user/account?timestamp=" + Date.now(),
      //请求链接
      "method": "get",
      //请求方法
      "dataType": "json",
      "timeout": 10000,
      "headers": {
        "Cookie": wyy_cookie
      }
    })
  
    if (wyy_cookie && !(info && info.code == 200 &&  info.profile && info.profile.nickname)) {
      sendText("检测到账号已过期！")
    }

    if (info && info.code == 200 &&  info.profile && info.profile.nickname) {
      sendText("检测到账号,正在处理...")
      cookie = wyy_cookie;
    }
    else {

        a1 = request({
            "url": hostName + "login/qr/key?timerstamp=" + Date.now(),
            //请求链接
            "method": "get",
            //请求方法
            "dataType": "json",
            "timeout": 10000,
            //返回json
        })


        var url = "https://api.aiproxy.win/API/qrcode/api.php?text=https://music.163.com/login?codekey=" + a1.data.unikey + "&size=150";
        var url = `[CQ:image,file=${url}]`
        sendText(GetUserID() + "请在60s使用网易云app扫码登录！" + url);

    }








     //var csrfToken = "";
    // var  musicU = "";
    for (let i = 0; i < 30; i++) {
        if (i !== 0) {
            sleep(2000);
        }
        if (!cookie) {

            request({
                url: hostName + "login/qr/check?key=" + a1.data.unikey + "&timerstamp=" + Date.now(),
                //请求链接
                "method": "get",
                "dataType": "json",
                "timeout": 10000,
            }, function (error, response, header, body) {
                if (body && body.code == "803") {
                    var setCookieHeader = header["Set-Cookie"];
                    //cookieRel = header["Set-Cookie"];
                    set("cnmcnm2", header["Set-Cookie"])

                    // 获取 __csrf 和 MUSIC_U 的值
                     var csrfToken = "";
                   var   musicU = "";

                    for (var i = 0; i < setCookieHeader.length; i++) {
                        cookie = setCookieHeader[i];
                        if (cookie.indexOf("__csrf=") === 0) {
                           csrfToken = cookie.split(';')[0].split('=')[1];
                        }
                        if (cookie.indexOf("MUSIC_U=") === 0) {
                            musicU = cookie.split(';')[0].split('=')[1];
                        }
                    }
                    // 格式化结果字符串
                    cookie = "__csrf=" + csrfToken + "; MUSIC_U=" + musicU;
                    bucketSet("Hi", "wyynew_" + GetUserID(), cookie);


                    set("cnmcnm3", cookie)






                }


            });

        }

        if (cookie ) {

            break;
        }
        if (i == 29) {
            sendText("扫码超时已退出！");
            return;
        }
    }


  
   
    //个人信息 
    if (!info || !info.profile || !info.profile.nickname) {
      //sendText("1111111111111")
        info = request({
            url: hostName + "user/account?timestamp=" + Date.now(),
            //请求链接
            "method": "get",
            //请求方法
            "dataType": "json",
            "timeout": 10000,
            "headers": {
                "Cookie": cookie
            }
        })

    }
//sendText(JSON.stringify(info))
  
  
    var level = request({
      url: hostName + "user/level?timestamp=" + Date.now(),
      //请求链接
      "method": "get",
      //请求方法
      "dataType": "json",
      "timeout": 10000,
      "headers": {
        "Cookie": cookie
      }
    })
    
    var vipLevel = request({
      url: hostName + "vip/info/v2?uid="+ info.profile.userId+"&timestamp=" + Date.now(),
      //请求链接
      "method": "get",
      //请求方法
      "dataType": "json",
      "timeout": 10000,
      "headers": {
        "Cookie": cookie
      }
    })
  
  //sendText("vipLevel-:"+JSON.stringify(vipLevel) +info.profile.userId);
 // return;
  
    //sendText(JSON.stringify(info));
    if (info && info.code == 200 && info.profile.nickname) {
       var text =`
登录成功-${info.profile.nickname}
网易云等级：${level.data.level}`
       
       
       
       if(vipLevel && vipLevel.data && vipLevel.data.associator && vipLevel.data.associator.expireTime > Date.now()) {
        text+=`
黑胶会员等级：${vipLevel.data.redVipLevel}
会员到期时间：${formatTimestamp(vipLevel.data.associator.expireTime)}`
        }
      else {
        text+=`
黑胶会员：未开通`
        
      
      }

        sendText(text)
      //return;

    }


    //云贝签到成功
    var a3 = request({
        url: specialHostName + "yunbei/sign?timestamp=" + Date.now(),
        //请求链接
        "method": "get",
        //请求方法
        "dataType": "json",
        "headers": {
            "Cookie": cookie
        }
    })


    //等级签到
    var a4 = request({
        url: specialHostName + "daily_signin?type=1&timestamp=" + Date.now(),
        //请求链接
        "method": "get",
        //请求方法
        "dataType": "json",
        "headers": {
            "Cookie": cookie
        }
    })


    //音乐人任务获取
    
    var songTask = request({
        url: specialHostName + "musician/tasks/new?timestamp=" + Date.now(),
        //请求链接
        "method": "get",
        //请求方法
        "dataType": "json",
        "headers": {
            "Cookie": cookie
        }
    })
    
    
    
   //音乐人签到
	  request({
        url: specialHostName + "musician/sign?timestamp=" + Date.now(),
        //请求链接
        "method": "get",
        //请求方法
        "dataType": "json",
        "headers": {
            "Cookie": cookie
        }
    })
  
  
   

    //刷歌

    //获取歌单类
    var typeData = request({
        url: specialHostName + "personalized?limit=1&timerstamp=" + Date.now(),
        //请求链接
        "method": "get",
        dataType: "json",
        "timeout": 10000,
    });

    // sendText(111+JSON.stringify(typeData));

    //停止量
    var stopCount = 0;


    if (typeData && typeData.result && typeData.result.length > 0) {
        outerloop: for (let j = 0; j < typeData.result.length; j++) {
            //var timestamp = Date.now();
            var typeId = typeData.result[j]['id'];


            //获取歌曲


            var data = request({
                url: hostName + "playlist/track/all?id=" + typeId + "&timerstamp=" + Date.now(),
                //请求链接
                "method": "get",
                dataType: "json",
                "timeout": 10000,
            });
            // sendText("11111111"+JSON.stringify(data));
            if (data && data.songs && data.songs.length > 0) {
                //  sendText("此类歌曲数量："+data.songs.length)

                for (let i = 0; i < data.songs.length; i++) {

                    if (stopCount >= 500) {
                        // sendText("success 500 "+data.songs.length+data.songs[i]['id'])
                        // sendText("500结束！")
                        break outerloop;
                    }

                    var data1 = request({
                        url: hostName + "scrobble?timerstamp=" + Date.now(),
                        //请求链接
                        "method": "post",
                        "body": {
                            "id": data.songs[i]['id'],
                            "sourceid": "",
                            "time": "240",
                            //"cookie":cookie 这就是傻逼
                        },
                        "headers": {
                            "Cookie": cookie,
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
                        },
                        dataType: "json",
                        "timeout": 10000,
                    });


                    if (i == 0 && data1.data == 'success' && stopCount == 0) {

                        var text =
                            `
${info.profile.nickname}
【听歌300首】
每日300首打卡成功

【等级签到】
签到成功！经验+

【云贝签到】
云贝签到成功，云贝+
云贝任务：浏览商城成功，云贝+2！
云贝任务：浏览会员中心成功，云贝+5！
云贝任务：云贝推歌失败！
云贝任务：分享歌曲/歌单成功，云贝+5！
没有待领取的云贝奖励！
云贝任务完成，预计收益50+云贝！

【音乐人任务】`;
               if (songTask && songTask.code == 200) {
                 text+="\n完成！"
               }
               else {
                text+="\n你还不是音乐人！"
               }
                      

                        sendText(text);

                    }
                    stopCount++;
                    if (i == (data.songs.length - 1) && data1.data == 'success') {
                        // sendText("success  "+data.songs.length+data.songs[i]['id'])
                        //  sendText("总共5类结束第几类 :  "+ j +"  类id: " +typeId);

                    }


                }
            } else {
                sendText("song不存在！")
                return;

            }





        }



    }



}


function formatTimestamp(timestamp) {
    var date = new Date(timestamp);
    
    var year = date.getFullYear();
    var month = date.getMonth() + 1; // 月份从0开始，需要加1
    var day = date.getDate();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();

    // 格式化日期和时间
    var formattedDate = year + '-' + (month < 10 ? '0' + month : month) + '-' + (day < 10 ? '0' + day : day);
    var formattedTime = (hours < 10 ? '0' + hours : hours) + ':' + (minutes < 10 ? '0' + minutes : minutes) + ':' + (seconds < 10 ? '0' + seconds : seconds);

    return formattedDate + ' ' + formattedTime;
}


main()




  
  
  
  
 /**
	var userID = GetUserID();
	var str = param(1);


	var userData = get("wyy_" + userID);
	if (userData) {
		userData = JSON.parse(userData);

		if (userData.data && userData.data.token) {
			var dataEnd = send(userID, userData);
          if (dataEnd && dataEnd.info.indexOf("网易ID") != -1) {
            sendText(dataEnd.info);
            sendText(dataEnd.result);
				  return;
          }
          

		}
	}



   
	//if (str == "任务") {
	data1 = request({
		url: "https://api.txcnm.cn/api/wyy/wyylogin?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&do=getqrcode",
		//请求链接
		"method": "get",
		//请求方法
		"dataType": "json",
		//返回json
	})

	img = imageDownload("https://api.txcnm.cn/api/qrcode/get?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&text=" + data1.url + "&size=6");
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
	//sendText(body.path)


	//转码
  if(body && body.result && body.result.path){
	var ewm = `[CQ:image,file=${body.result.path}]`
	//sendImage("https://api.txcnm.cn/api/qrcode/get?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&text="+data1.url+"&size=6")
	sendText(userID + "请在60s使用网易云app扫码登录！" + ewm)}

	var data2;

	for (let i = 0; i < 30; i++) {
      
      if (i !== 0) {
        sleep(2000);
      }
		

		if (data2 && data2.data && data2.data.token) {

			var dataEnd = send(userID, data2);
        sendText(dataEnd.info);
        sendText(dataEnd.result);
			set("wyy_" + userID, JSON.stringify(data2));
			break;
		}


		data2 = request({
			url: "https://api.txcnm.cn/api/wyy/wyylogin?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&do=qrlogin&zkey=" + data1.key,
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

	   var bg = `[CQ:image,file=${data2.data.avatar}]`
	var info = request({
		url: "https://api.txcnm.cn/api/wyy/wyuser?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&token=" + data2.data.token + "&id=" + data2.data.user_id,
		//请求链接
		"method": "get",
		//请求方法
		//"dataType": "json",
		//返回json
	})



	//打卡
	data3 = request({
		url: "https://api.txcnm.cn/api/wyy/wyy300?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&token=" + data2.data.token + "&id=" + data2.data.user_id,
		//请求链接
		"method": "get",
		//请求方法
		//"dataType": "json",
		//返回json
	})

	//云贝
	data4 = request({
		url: "https://api.txcnm.cn/api/wyy/wyyb?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&token=" + data2.data.token + "&id=" + data2.data.user_id,
		//请求链接
		"method": "get",
		//请求方法
		//"dataType": "json",
		//返回json
	})

	//音乐人
	data5 = request({
		url: "https://api.txcnm.cn/api/wyy/wyyren?key=lKBPJ4IJ9sg1Unn7HSBTkMv4bu&token=" + data2.data.token + "&id=" + data2.data.user_id,
		//请求链接
		"method": "get",
		//请求方法
		//"dataType": "json",
		//返回json
	})
	if (!data5) {
		data5 = "您当前还不是音乐人！"
	}
  
  dataEnd = {
    info:userID + "\n您的网易云登录成功\n" + bg + "\n" + info,
    result:userID + "\n您的网易云账号" + data2.data.nickname + " 执行情况：\n" + data3 + data4 + "音乐人任务：\n" + data5
  }
  
  return dataEnd;

}
  */