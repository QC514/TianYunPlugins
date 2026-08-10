//[title: 文字或链接转二维码]
//[create_at: 2023-02-05 19:30:30]
// [rule: 转二维码]
//=========================================
// [admin: false] 
// [show: 将URL或文字生成二维码。指令：转二维码。] 
// [author: 偷CK的六舅哥]
// [version: 1.1.0] 
// [price: 0.0]
// [platform: qq,wx,tg]


function main() {
sendText("请选择您要使用的项目"+"\n"+"1.文字转换为二维码"+"\n"+"2.链接转换为二维码"+ " \n(注：q.退出)")
num1 = input();
	if(num1 == "q" || num1 == "Q"){
		sendText("已退出")
		return;
	}
	if(num1 == "1"){
		sendText("请输入你要转换为二维码的文字"+ " \n(注：q.退出)")
    // 获取内容
    num = input();
	if(num == "q" || num == "Q"){
		sendText("已退出")
		return;
	}else{
        sendText("六舅哥正在为您生成二维码，请稍后...");
    sendImage("https://api.linhun.vip/api/QRcode?apiKey=e2ad109fbb9e70654e39a674a817ac16&url="+num)
	}

		return;
	}

if(num1 == "2"){
		sendText("请输入你要转换为二维码的链接"+ " \n(注：不要加http前缀"+"\t"+"q.退出)")
    // 获取内容
    num = input();
	if(num == "q" || num == "Q"){
		sendText("已退出")
		return;
	}else{
        sendText("六舅哥正在为您生成二维码，请稍后...");
    sendImage("https://api.linhun.vip/api/QRcode?apiKey=e2ad109fbb9e70654e39a674a817ac16&url=http://"+num)
	}

		return;
	}



}



main() 