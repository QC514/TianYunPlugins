//[create_at: 2024-08-17 11:11:20]
//[open_source:true]
//[public:true]
//[title:美女 ]
//[version:1.0.0]
//[author:kevin]
//[service:395202420]
//[rule:美女]
//[description: 美女，随机发送一张美女图片]


(function() {
    var lastCallTime = {}; // 用于记录每个用户的上次调用时间

    function main() {
        var userid = GetUserID(); // 获取当前会话用户ID
        var currentTime = new Date().getTime(); // 获取当前时间的时间戳（毫秒）

        // 检查用户是否在20秒内重复发送指令
        if (lastCallTime[userid] && (currentTime - lastCallTime[userid] < 20000)) {
            sendText("你调用频繁，请稍后再试。");  // 如果距离上次调用不到20秒，提示用户
            return;
        }

        lastCallTime[userid] = currentTime; // 更新用户最后调用时间

        // 执行截图请求
        sendImage("http://api.yujn.cn/api/yht.php?type=image");
    }

    var msg = input(20000, 0, "group"); // 等待群内任意用户的输入，等待时间为20秒，输入后不撤回
    main(); // 执行主函数
})();

