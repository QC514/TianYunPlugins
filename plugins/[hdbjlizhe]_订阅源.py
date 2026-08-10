//[create_at: 2025-12-19 06:38:17]
//[author: hdbjlizhe]
//[disable:false]
//[title: 订阅源]
//[icon:https://bbs.autman.cn/assets/files/2024-06-13/1718259540-66996-1c50f15eec4691f558ea05761214a6b1.png]
//[language: es5]
//[price: 0.01]
//[service: 282617666]
//[rule:^(订阅|市场)源?$]
//[priority: 0]
//[version: 1.0.2]
//[public: true]
//[description: 查询当前活跃的autMan订阅源地址，即autMan生态上的自建市场，用户在“插件管理-订阅市场源”订阅这些源后，可安装自建源市场上的插件。指令：订阅源，需要在系统管理-插件权限-订阅源-开启cloud权限] 
function main(){
  username = bucketGet("cloud", "username")
  password = bucketGet("cloud", "password")
  Debug(username)
  Debug(password)
  option = {
    "method": "get",
    "url": `http://aut.zhelee.cn/market/records?username=${username}&password=${encodeURIComponent(password)}`,
    "headers":{//请求头
          "Username": username,
      },
  }
  rlt="未获取到数据"
  request(option, function (error, response, header, body) {
    //Debug("错误："+error)
    //Debug("响应："+response)
    //Debug("响应头："+header)
    //Debug("响应体："+body)
    resp = JSON.parse(body)
    if (resp.data) {
      //获取元素个数：
      //Debug(resp.data.length)
      rlt=("获取可用订阅源"+resp.data.length+"个\n--------------\n"+resp.data.join("\n"))
    } else {
      rlt=("未获取到数据")
    }
  })
  return rlt
}
main()