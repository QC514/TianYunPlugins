// [author:960342874]
// [create_at: 2023-06-13 15:00:00]
// [version: v1.0.1]
// [title: 舔狗日记]
// [class: 娱乐类]
// [description: 指令：舔狗日记 说明：下载即用  ]
// [platform: all]
// [public:true]
// [price: 0.1]
//[icon:https://nimg.ws.126.net/?url=http%3A%2F%2Fdingyue.ws.126.net%2F2024%2F0521%2Fed365d3ej00sduauc000sd000hs00b4g.jpg&thumbnail=660x2147483647&quality=80&type=jpg]
//================================================================
// [rule: raw 舔狗日记]
// [priority: 9999999]
// [service: <img src="https://pic.fglt.net/common/a8/common_4_verify_icon.gif" border="0" /> <b>官方权威认证</b>  交流群758982908 ]
//importJs("auth.js")
function main() {
  
   var userID = GetUserID()
  if (userID.indexOf("80000000") !== -1) {
		return;
	}
  
  // 授权判断
  //var authData = auth();
  // if (authData && !authData.code) {
  //   sendText(authData.data)
  //   return;
  // }
  
  
  
  
  
 
  
   var plugin_key = "tgrj";
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
  else if(yunhei.master_yunhei.data.indexOf(userID) > -1) {
    // 总云黑
     sendText(yunhei['master_yunhei']['msg']+ "----ALL");
     return;
   }
  else if(yunhei[plugin_key]['branch_yunhei']['data'].indexOf(userID) > -1) {
    // 分支云黑
     sendText(yunhei['master_yunhei']['msg']  + "----"+ yunhei[plugin_key]['name'] );
     return;
   }
  else if (yunhei[plugin_key]['state'] == "invalid") {
    // 插件无效禁用
     sendText(yunhei[plugin_key]['invalid_info']);
     return;
  }
  
  
  
  
  var userID = GetUserID()
  let data;
  /**data = request({ 
    url: "https://api.aiproxy.win/API/tgrj/api.php", 
    //请求链接
    "method": "get"
    //返回json
    })
    sendText(data);
    **/
  
  
   sendImage("https://api.suyanw.cn/api/tgbj.php?a="+Math.random())
  
  
  
   

}
main()

