// [author: kevin]
// [create_at: 2024-08-1 10:36:11]
// [public: true]
// [title: 小视频]
// [version: 1.2]
// [description: 指令：小视频，根据用户输入选择不同系列的视频。]
// [class: 生活类]
// [price: 0]
// [rule: 小视频]
// [disable: false]

// =======================
// 脚本及其中涉及的任何解锁和解密分析脚本，仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断。您必须在下载后的24小时内从计算机或手机中完全删除此脚本。

function main() {
    var command = param(1); // 获取传入的命令

    // 提示用户选择系列
    sendText(
        "请选择视频系列:\n" +
        "1. COS系列\n" +
        "2. 变装喜乐\n" +
        "3. 吊带系列\n" +
        "4. 抖音热点\n" +
        "5. 小姐姐系列\n" +
        "6. 萌娃喜乐\n" +
        "7. 古风系列\n" +
        "8. 玉足系列\n" +
        "9. 慢摇喜乐\n" +
        "10. 吊带系列\n" +
        "11. 清纯系列\n" +
        "12. 女高系列\n" +
        "13. 欲梦系列\n" +
        "14. 甜妹系列\n" +
        "15. JK洛丽塔\n" +
        "16. 帅哥系列\n" +
        "17. 热舞系列\n" +
        "请输入对应的数字："
    );

    var userInput = input(); // 获取用户输入的系列数字

    var url; // 存储请求地址

    // 根据用户选择设置不同的请求链接
    switch(userInput) {
        case "1":
            url = "http://api.yujn.cn/api/COS.php?type=video"; // COS系列
            break;
        case "2":
            url = "http://api.yujn.cn/api/ksbianzhuang.php?type=video"; // 变装喜乐
            break;
        case "3":
            url = "http://api.yujn.cn/api/diaodai.php?type=video"; // 吊带系列
            break;
        case "4":
            url = "http://api.yujn.cn/api/dy_hot.php?"; // 抖音热点
            break;
        case "5":
            url = "http://api.yujn.cn/api/zzxjj.php?type=video"; // 小姐姐系列
            break;
        case "6":
            url = "http://api.yujn.cn/api/mengwa.php?type=video"; // 萌娃喜乐
            break;
        case "7":
            url = "http://api.yujn.cn/api/hanfu.php?type=video"; // 古风系列
            break;
        case "8":
            url = "http://api.yujn.cn/api/jpmt.php?type=video"; // 玉足系列
            break;
        case "9":
            url = "http://api.yujn.cn/api/manyao.php?type=video"; // 慢摇喜乐
            break;
        case "10":
            url = "http://api.yujn.cn/api/diaodai.php?type=video"; // 吊带系列
            break;
        case "11":
            url = "http://api.yujn.cn/api/qingchun.php?type=video"; // 清纯系列
            break;
        case "12":
            url = "http://api.yujn.cn/api/nvgao.php?type=video"; // 女高系列
            break;
        case "13":
            url = "http://api.yujn.cn/api/ndym.php?type=video"; // 欲梦系列
            break;
        case "14":
            url = "http://api.yujn.cn/api/ndym.php?type=video"; // 甜妹系列
            break;
        case "15":
            url = "http://api.yujn.cn/api/jksp.php?type=video"; // JK洛丽塔
            break;
        case "16":
            url = "http://api.yujn.cn/api/xgg.php?type=video"; // 帅哥系列
            break;
        case "17":
            url = "http://api.yujn.cn/api/rewu.php?type=video"; // 热舞系列
            break;
        default:
            sendText("输入无效，请输入有效的数字啊柒头。");
            return;
    }

    // 使用 request 获取视频文件 URL
    var red = request({
        url: url,
        dataType: "location", // 我们期望获取的是重定向后的地址
    });

    // 调试输出，检查获取到的链接内容
    Debug(red);

    // 如果 red 是有效的 URL（可以是最终的重定向地址），则发送视频
    if (red && typeof red === 'string' && red.startsWith('http')) {
        sendVideo(red); // 使用 sendVideo 发送视频文件链接
    } else {
        sendText("无法获取视频链接或视频链接无效。");
    }
}

main();
