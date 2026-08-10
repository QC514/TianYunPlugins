//[public:true]
//[disable:false]
// [author: 960342874]
// [create_at: 2023-06-14 14:00:00]
// [version: v1.0.0]
// [title: 摸鱼日报]
// [description: 指令：摸鱼日报 <br>推送群请设置配参 <br> <img src="https://yanxuan.nosdn.127.net/66122d003684488747964189fe15ed20.jpg"/>]
// [platform: qq,vx,tg,频道]
// [price: 0.5]
//[icon:https://tse2-mm.cn.bing.net/th/id/OIP-C.yCOyRiV02wnPNcKJiNKgUQHaHa?rs=1&pid=ImgDetMain]
//================================================================
// [rule:摸鱼日报|摸鱼]
// [service: 交流群758982908]
// [cron: 0 55 12 * * ? ]
// [param: {"required":false,"key":"otto.myrb_groups","bool":false,"placeholder":"qqgroup:123,wxgroup:456","name":"推送群","desc":"推送目的地"}]


//importJs("auth.js")
function main() {
  
          
  
  var plugin_key = "myrb";
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
  
  var date1= new Date();
  if(date1.getDay() == 0 || date1.getDay() == 6){
    sendText("今天不上班，不用摸鱼哦！");
    return;

  }
  
  
  sendVideo("https://dayu.qqsuu.cn/moyuribaoshipin/apis.php");

  
  let bg = `[CQ:video,file=https://dayu.qqsuu.cn/moyuribaoshipin/apis.php]`;
  
      if (GetImType() == "fake") {
         var pushGroups = get("myrb_groups")
			var pgs = pushGroups.split(",")
			for (i = 0; i < pgs.length; i++) {
				let gps = pgs[i].split("group:")            
				push({
					imType: gps[0],
					groupCode: gps[1],
					content: bg,
				})
			}
    
    }
}
main()

