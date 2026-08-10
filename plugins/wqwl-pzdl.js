//[title: wqwl-pzdl]
//[author: wqwlkj2985]
//[language: nodejs]
//[class: 工具类]
//[service: qq298582245] 售后联系方式
//[disable: false] 禁用开关，true表示禁用，false表示可用
//[admin: false] 是否为管理员指令
//[rule: ^(?i)品赞(登录|查询|管理|一键运行|签到)$] 匹配规则1
//[cron: 8 6,21 * * *] cron定时，支持5位域和6位域
//[priority: 298582245] 优先级，数字越大表示优先级越高
//[platform: qq] 适用的平台
//[open_source: false]是否开源
//[icon: 图标url]图标链接地址，请使用48像素的正方形图标，支持http和https
//[version: 1.0.0]版本号
//[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
//[price: 999] 上架价格
//[description: 五个指令： 品赞登录、品赞查询、品赞管理、品赞签到、品赞一键运行(管理员指令)] 使用方法尽量写具体
const middlleware = require('./middleware')
const axios = require('axios');
//链接https://www.ipzan.com?pid=1t1pf4ql8

var d = {
    table: ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "/"],
    UTF16ToUTF8: function (e) {
        for (var t = [], n = e.length, i = 0; i < n; i++) {
            var r, o, s = e.charCodeAt(i);
            0 < s && s <= 127 ? t.push(e.charAt(i)) : 128 <= s && s <= 2047 ? (r = 192 | s >> 6 & 31,
                o = 128 | 63 & s,
                t.push(String.fromCharCode(r), String.fromCharCode(o))) : 2048 <= s && s <= 65535 && (r = 224 | s >> 12 & 15,
                    o = 128 | s >> 6 & 63,
                    s = 128 | 63 & s,
                    t.push(String.fromCharCode(r), String.fromCharCode(o), String.fromCharCode(s)))
        }
        return t.join("")
    },
    UTF8ToUTF16: function (e) {
        for (var t = [], n = e.length, i = 0, i = 0; i < n; i++) {
            var r, o, s = e.charCodeAt(i);
            0 == (s >> 7 & 255) ? t.push(e.charAt(i)) : 6 == (s >> 5 & 255) ? (o = (31 & s) << 6 | 63 & (r = e.charCodeAt(++i)),
                t.push(Sting.fromCharCode(o))) : 14 == (s >> 4 & 255) && (o = (255 & (s << 4 | (r = e.charCodeAt(++i)) >> 2 & 15)) << 8 | ((3 & r) << 6 | 63 & e.charCodeAt(++i)),
                    t.push(String.fromCharCode(o)))
        }
        return t.join("")
    },
    encode: function (e) {
        if (!e)
            return "";
        for (var t = this.UTF16ToUTF8(e), n = 0, i = t.length, r = []; n < i;) {
            var o = 255 & t.charCodeAt(n++);
            if (r.push(this.table[o >> 2]),
                n == i) {
                r.push(this.table[(3 & o) << 4]),
                    r.push("==");
                break
            }
            var s = t.charCodeAt(n++);
            if (n == i) {
                r.push(this.table[(3 & o) << 4 | s >> 4 & 15]),
                    r.push(this.table[(15 & s) << 2]),
                    r.push("=");
                break
            }
            var a = t.charCodeAt(n++);
            r.push(this.table[(3 & o) << 4 | s >> 4 & 15]),
                r.push(this.table[(15 & s) << 2 | (192 & a) >> 6]),
                r.push(this.table[63 & a])
        }
        return r.join("")
    },
    decode: function (e) {
        if (!e)
            return "";
        for (var t = e.length, n = 0, i = []; n < t;)
            code1 = this.table.indexOf(e.charAt(n++)),
                code2 = this.table.indexOf(e.charAt(n++)),
                code3 = this.table.indexOf(e.charAt(n++)),
                code4 = this.table.indexOf(e.charAt(n++)),
                c1 = code1 << 2 | code2 >> 4,
                i.push(String.fromCharCode(c1)),
                -1 != code3 && (c2 = (15 & code2) << 4 | code3 >> 2,
                    i.push(String.fromCharCode(c2))),
                -1 != code4 && (c3 = (3 & code3) << 6 | code4,
                    i.push(String.fromCharCode(c3)));
        return this.UTF8ToUTF16(i.join(""))
    }
};
function account(phone, password) {
    for (var e = d.encode("".concat(phone, "QWERIPZAN1290QWER").concat(password)), t = "", o = 0; o < 80; o++)
        t += Math.random().toString(16).slice(2);
    e = "".concat(t.slice(0, 100)).concat(e.slice(0, 8)).concat(t.slice(100, 200)).concat(e.slice(8, 20)).concat(t.slice(200, 300)).concat(e.slice(20)).concat(t.slice(300, 400));
    return {
        account: e,
        source: 'ipzan-home-one'
    }
}

class Task {
    constructor(user, password, token) {
        this.user = user
        this.hideUser = `${this.user.slice(0, 3)}****${this.user.slice(-4)}`
        this.password = password
        this.token = token
        this.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "authorization": "Bearer ",
            "content-type": "application/json;charset=UTF-8",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\"",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "Referer": "https://www.ipzan.com/"
        }
    }
    static async create(user, password, token = null) {
        // 如果有 token，先尝试使用 token 验证
        if (token) {
            const tempInstance = new Task(user, password, token);
            const isValid = await tempInstance.validateToken();

            if (isValid) {
                console.log(`✅ 账号 ${tempInstance.hideUser} Token 登录成功`);
                return tempInstance;
            } else {
                console.log(`⚠️ 账号 ${tempInstance.hideUser} Token 已失效，尝试密码登录`);
            }
        }

        // 如果没有 token 或 token 失效，使用密码登录
        const tempInstance = new Task(user, password);
        const newToken = await tempInstance.loginWithPassword();

        if (newToken && !newToken.includes('❌')) {
            console.log(`✅ 账号 ${tempInstance.hideUser} 密码登录成功`);
            return new Task(user, password, newToken);
        } else {
            throw new Error(`❌ 账号 ${tempInstance.hideUser} 登录失败: ${newToken}`);
        }
    }

    // 验证 token 是否有效
    async validateToken() {
        try {
            this.headers.authorization = 'Bearer ' + this.token;
            const config = {
                url: 'https://service.ipzan.com/home/userWallet-find',
                timeout: 5e4,
                headers: this.headers,
                method: 'get'
            };

            const response = await axios(config);
            //console.log(JSON.stringify(response.data))
            return response.data.code == 0;
        } catch (e) {
            return false;
        }
    }

    // 使用密码登录
    async loginWithPassword() {
        try {
            const config = {
                url: 'https://service.ipzan.com/users-login',
                timeout: 5e4,
                headers: this.headers,
                method: 'post',
                data: account(this.user, this.password)
            };

            const response = await axios(config);
            const data = response.data;

            if (data.status === 200 && data.data.token) {
                return data.data.token;
            } else {
                return `❌ 获取token失败: ${data.message}`;
            }
        } catch (e) {
            return `❌ 登录失败: ${e.message}`;
        }
    }

    async query() {
        try {
            if (this.token.includes('❌'))
                return this.token
            this.headers.authorization = 'Bearer ' + this.token
            const config = {
                url: 'https://service.ipzan.com/home/userWallet-find',
                timeout: 5e4,
                headers: this.headers,
                method: 'get'
            }
            const response = await axios(config);
            // console.log(response.data)
            const data = response.data;
            const logs = await this.extractLog()
            if (data.status == 200)
                return `=====账号信息=====\n🤪用户账号：${this.hideUser}\n💧剩余余额：${data.data.balance}\n🛜今日消费：${logs.total}IP\n💰️今日消费：${logs.price}\n================\n`
            else
                return `❌ 账号 ${this.hideUser}查询失败，${data.message}\n`
        }
        catch (e) {
            return `❌ 账号 ${this.hideUser}查询失败，${e.message}\n`
        }
    }

    async extractLog() {
        try {
            if (this.token.includes('❌')) {
                return this.token;
            }
            this.headers.authorization = 'Bearer ' + this.token;
            const config = {
                url: 'https://service.ipzan.com/home/extractLog-get-total-logs',
                timeout: 5e4,
                headers: this.headers,
                method: 'get'
            };
            const response = await axios(config);
            const data = response.data;

            const today = new Date();
            const todayString = today.toISOString().split('T')[0];

            // 注意：这里用 data.data.find，因为数据在 data.data 数组里
            const todayItem = data.data.find(item => item.label === todayString);
            console.log("匹配结果：", todayItem); // 正确打印对象

            // 返回匹配的对象，或默认值（label 用 todayString 保持格式一致）
            return todayItem || { total: "0", price: "0", label: todayString };
        } catch (e) {
            return `❌ 账号 ${this.hideUser} 获取消费日志失败，${e.message}`;
        }
    }

    // 领取每周奖励
    async receive() {
        try {
            if (this.token.includes('❌'))
                return this.token
            this.headers.authorization = 'Bearer ' + this.token
            const config = {
                url: 'https://service.ipzan.com/home/userWallet-receive',
                timeout: 5e4,
                headers: this.headers,
                method: 'get'
            }
            const response = await axios(config);
            console.log(response.data)
            const data = response.data;
            if (data.status == 200 && data.data != null)
                return `✅账号 ${this.hideUser} 领取成功`
            else
                return `❌ 账号 ${this.hideUser}领取失败，${data.message}`
        } catch (e) {
            return `❌ 账号 ${this.hideUser}领取失败，${e.message}`
        }
    }
    async main() {
        return `${await this.query()}\n${await this.receive()}\n${await this.query()}`
    }
}
const PZDL = class {
    static sqlName = 'wqwl_pzdl'
    constructor(user, Sender) {
        this.user = user;
        this.Sender = Sender;
    }

    //品赞登录
    async addUser() {
        try {
            let userInput;
            this.Sender.reply('请输入用户名（未注册请发品赞介绍按要求注册）：\n回复"q"退出')
            let user = await this.Sender.listen(60000)
            if (user === 'q') {
                return this.Sender.reply('✅已退出登录！')
            }
            if (user === '' || user === null) {
                return this.Sender.reply('❌输入超时')
            }
            if (user.length != 11 || !user.match(/^1[3-9]\d{9}$/)) {
                this.Sender.reply("❌手机号格式错误")
                return;
            }
            this.Sender.reply('请输入密码：\n回复"q"退出')
            let pwd = await this.Sender.listen(60000)
            if (pwd === 'q') {
                return this.Sender.reply('✅已退出登录！')
            }
            if (pwd === "" || pwd === null) {
                return this.Sender.reply('❌输入超时')
            }
            userInput = user + '#' + pwd
            const rawData = await this.Sender.bucketGet(`${PZDL.sqlName}_users`, this.user);
            // 做安全判断后再解析
            let allData = [];
            if (rawData && typeof rawData === 'string') {
                try {
                    allData = JSON.parse(rawData);
                } catch (e) {
                    console.error("JSON 解析失败:", e);
                    allData = [];
                }
            }
            const userData = userInput.split("#");
            if (this.isUserExist(allData, userData)) {
                this.Sender.reply('用户已经存在，是否进行覆盖？(y/n)')
                const tmp = await this.Sender.listen(60000)
                if (tmp.toLowerCase() === 'y') {
                    const isSuccess = this.updateSame(allData, userData)
                    if (isSuccess) {
                        //this.Sender.reply(`覆盖成功！请回复【品赞查询】查看是否成功添加！`)
                    }
                    else {
                        this.Sender.reply(`❌覆盖失败！请重新添加！`)
                        return;
                    }
                } else {
                    this.Sender.reply(`❌已取消覆盖！请重新添加！`)
                    return
                }
            } else {
                allData.push(userInput)
            }
            const res = await this.Sender.bucketSet(`${PZDL.sqlName}_users`, this.user, JSON.stringify(allData))

            if (!res) {
                this.Sender.reply(`❌添加失败！请重新添加！`)
                return
            }
            return this.Sender.reply(`✅添加成功，请回复【品赞查询】查看是否成功添加！`)

        }
        catch (e) {
            this.Sender.reply(`❌添加失败！请重新添加！错误原因：${e.message}`)
            return
        }
    }

    // 判断用户是否存在
    isUserExist(allData, userData) {
        for (let i = 0; i < allData.length; i++) {
            const item = allData[i];
            const itemFields = item.split('#');
            // 只比较第一个字段（用户名）
            if (itemFields[0] === userData[0]) {
                return true;
            }
        }
        return false;
    }
    //覆盖数据
    updateSame(allData, userData) {
        const userToFind = userData[0]; // 只取 userData 的第一个字段，比如手机号或用户名

        for (let i = 0; i < allData.length; i++) {
            const item = allData[i];
            const itemFields = item.split('#');

            // 判断当前行中是否包含 userData[0]
            if (itemFields.includes(userToFind)) {
                // 找到匹配项，替换为新的 userData 数据
                allData[i] = userData.join('#');
                return true; // 表示已找到并替换
            }
        }

        return false; // 没有找到匹配项
    }

    //品赞管理
    async manageUser() {
        try {
            const rawData = await this.Sender.bucketGet(`${PZDL.sqlName}_users`, this.user);
            if (!rawData || rawData === '[]' || rawData === '') {
                this.Sender.reply(`=====未绑定账号=====\n❌ 未找到任何账号信息\n发送 品赞登录 绑定账号\n==================`)
                return
            }
            const allData = JSON.parse(rawData)
            const authData = await this.Sender.bucketGet(`${PZDL.sqlName}_auth`, this.user);
            //this.Sender.reply(JSON.stringify(authData))
            // 做安全判断后再解析
            let auth = [];
            if (authData && typeof authData === 'string') {
                try {
                    auth = JSON.parse(authData);
                } catch (e) {
                    console.error("JSON 解析失败:", e);
                    auth = [];
                }
            }
            let msg = '=====账号列表====='
            msg += `\n[0] 授权全部账号`
            for (let i = 0; i < allData.length; i++) {
                const tempData = allData[i].split('#')
                const userName = this.hidePhone(tempData[0])
                const authStatus = auth[i] || 0
                if (authStatus === 0)
                    msg += `\n[${i + 1}] ${userName}\n❌未授权`
                else if (authStatus < Date.now())
                    msg += `\n[${i + 1}] ${userName}\n❌已过期`
                else
                    msg += `\n[${i + 1}] ${userName}\n✅已授权`
            }
            msg += `\n------------------\n回复数字选择账号\n回复'q'退出`
            await this.Sender.reply(msg)
            let userInput = await this.Sender.listen(60000)
            if (userInput === "q") {
                this.Sender.reply("✅已退出操作！")
                return;
            }
            if (userInput === "" || userInput === null) {
                this.Sender.reply("❌输入超时")
                return;
            }
            try {
                const userId = parseInt(userInput) - 1
                if (userId === -1) {
                    this.addAllAuth(auth, allData)
                    return;
                }
                if (userId > allData.length - 1) {
                    this.Sender.reply('❌无效的选择')
                    return;
                }
                this.Sender.reply(`=====账号操作=====\n[1] 授权账号\n[2] 删除账号\n------------------\n回复数字选择操作\n回复"q"退出`)
                let userInputAuth = await this.Sender.listen(60000)
                if (userInputAuth === "q") {
                    this.Sender.reply("✅已退出操作！")
                    return;
                }
                if (userInputAuth === "" || userInputAuth === null) {
                    this.Sender.reply("❌输入超时")
                    return;
                }
                switch (userInputAuth) {
                    case "1":
                        await this.addAuth(userId, auth, allData);
                        break;
                    case "2":
                        await this.deleteAuth(userId, auth, allData);
                        break;
                    default:
                        this.Sender.reply("❌输入错误")
                }
            }
            catch (e) {
                this.Sender.reply(`❌输入错误,仅能输入数字且要在范围之间！${e}`)
                return;
            }
        }
        catch (e) {
            this.Sender.reply(`❌查询数据失败！请重新查询！错误原因：${e.message}`)
            return
        }
    }

    //添加所有授权
    async addAllAuth(authData, allData) {
        this.Sender.reply('请输入授权的月数：')
        let times = await this.Sender.listen(60000);
        let success = 0
        if (times === "q") {
            this.Sender.reply("✅已退出操作！")
            return;
        }
        if (times === "" || times === null) {
            this.Sender.reply("❌输入超时")
            return;
        }
        try {
            times = parseInt(times)
        } catch (e) {
            this.Sender.reply(`❌请输入数字！`)
            return
        }
        try {
            for (let i = 0; i < allData.length; i++) {
                if (!authData[i])
                    authData[i] = 0
                if (authData[i] - Date.now() <= 0)
                    authData[i] = Date.now() + times * 1000 * 60 * 60 * 24 * 30;
                else
                    authData[i] += times * 1000 * 60 * 60 * 24 * 30;
                success++
            }
        } catch (e) {
            this.Sender.reply(`❌${allData[4]} 添加授权失败，请联系管理员,${e.message}`)
        }
        const res = await this.Sender.bucketSet(`${PZDL.sqlName}_auth`, this.user, JSON.stringify(authData))
        if (!res) {
            this.Sender.reply(`❌${allData[4]} 添加授权失败，请联系管理员`)
            return
        }
        return this.Sender.reply(`=====授权成功=====
✅ 成功: ${success}个账号
❌ 失败: ${allData.length - success}个账号
⏰ 时长: ${times * 30}天
    ===============`)
    }
    //添加授权
    async addAuth(userId, authData, allData) {
        this.Sender.reply('请输入授权的月数：')
        let times = await this.Sender.listen(60000);

        if (times === "q") {
            this.Sender.reply("✅已退出操作！")
            return;
        }
        if (times === "" || times === null) {
            this.Sender.reply("❌输入超时")
            return;
        }
        try {
            times = parseInt(times)
        } catch (e) {
            this.Sender.reply(`❌请输入数字！`)
            return
        }
        try {
            for (let i = 0; i < allData.length; i++) {
                if (!authData[i])
                    authData[i] = 0
                if (userId === i) {
                    if (authData[userId] - Date.now() <= 0)
                        authData[userId] = Date.now() + times * 1000 * 60 * 60 * 24 * 30;
                    else
                        authData[userId] += times * 1000 * 60 * 60 * 24 * 30;
                    break;
                }
            }
        } catch (e) {
            this.Sender.reply(`❌${this.hidePhone(allData[userId].split('#')[0])} 添加授权失败，请联系管理员,${e.message}`)
        }
        const res = await this.Sender.bucketSet(`${PZDL.sqlName}_auth`, this.user, JSON.stringify(authData))
        if (!res) {
            this.Sender.reply(`❌${this.hidePhone(allData[userId].split('#')[0])} 添加授权失败，请联系管理员`)
            return
        }
        return this.Sender.reply(`=====授权成功=====
🤪 账号: ${this.hidePhone(allData[userId].split('#')[0])}
⏰ 时长: ${times * 30}天
📅 到期: ${this.formatDate(authData[userId])}
==================`)
    }

    //删除授权
    async deleteAuth(userId, authData, allData) {
        let name = allData[userId].split('#')[0]
        name = `${name.slice(0, 3)}****${name.slice(-4)}`
        this.Sender.reply(`⚠️您确定删除账号【${name}】吗？(y/n)`)
        let answer = await this.Sender.listen(60000)
        if (answer === "" || answer === null) {
            this.Sender.reply("❌输入超时")
            return;
        }
        if (answer.toLowerCase() === "y") {
            authData.splice(userId, 1)
            allData.splice(userId, 1)
            const res = await this.Sender.bucketSet(`${PZDL.sqlName}_auth`, this.user, JSON.stringify(authData))
            const res2 = await this.Sender.bucketSet(`${PZDL.sqlName}_users`, this.user, JSON.stringify(allData))
            if (res && res2) {
                this.Sender.reply("✅删除成功")
            } else {
                this.Sender.reply("❌删除失败")
            }
        } else {
            this.Sender.reply("❌删除失败,输入有误")
        }
    }

    //品赞查询
    async query() {
        let rawData = await this.Sender.bucketGet(`${PZDL.sqlName}_users`, this.user)

        this.Sender.reply('正在查询...')
        let allData = [];
        if (rawData && typeof rawData === 'string') {
            try {
                allData = JSON.parse(rawData);
            } catch (e) {
                console.error("JSON 解析失败:", e);
                allData = [];
            }
        }
        if (allData.length === 0) {
            this.Sender.reply(`=====未绑定账号=====\n❌ 未找到任何账号信息\n💡 发送 品赞登录 绑定账号\n==================`)
            return;
        }
        const authData = await this.Sender.bucketGet(`${PZDL.sqlName}_auth`, this.user);
        //this.Sender.reply(JSON.stringify(authData))
        // 做安全判断后再解析
        let auth = [];
        if (authData && typeof authData === 'string') {
            try {
                auth = JSON.parse(authData);
            } catch (e) {
                console.error("JSON 解析失败:", e);
                auth = [];
            }
        }
        const tokenData = await this.Sender.bucketGet(`${PZDL.sqlName}_token`, this.user)
        let token = [];
        if (tokenData && typeof tokenData === 'string') {
            try {
                token = JSON.parse(tokenData);
            } catch (e) {
                console.error("JSON 解析失败:", e);
                token = [];
            }
        }
        for (let i = 0; i < allData.length; i++) {
            const data = allData[i].split("#");
            const user = data[0];
            const password = data[1];
            let token1 = token?.[i] || ''
            const task = await Task.create(user, password, token1);
            // this.Sender.reply(`${JSON.stringify(allData[i])}`)
            let result = await task.query();
            token[i] = task.token
            result += `☁️剩余授权：${auth[i] ? Math.floor((auth[i] - Date.now()) / (1000 * 60 * 60 * 24)) : "0"}天`
            this.Sender.reply(`${result}`);
        }
        const res2 = await this.Sender.bucketSet(`${PZDL.sqlName}_token`, this.user, JSON.stringify(token))

    }

    //品赞手动签到
    async sign() {
        let rawData = await this.Sender.bucketGet(`${PZDL.sqlName}_users`, this.user)
        this.Sender.reply('正在签到...')
        let allData = [];
        if (rawData && typeof rawData === 'string') {
            try {
                allData = JSON.parse(rawData);
            } catch (e) {
                console.error("JSON 解析失败:", e);
                allData = [];
            }
        }
        if (allData.length === 0) {
            this.Sender.reply(`=====未绑定账号=====\n❌ 未找到任何账号信息\n💡 输入 品赞登录 绑定账号\n==================`)
            return;
        }
        const authData = (await this.Sender.bucketGet(`${PZDL.sqlName}_auth`, this.user));
        let auth = [];
        if (authData && typeof authData === 'string') {
            try {
                auth = JSON.parse(authData);
            } catch (e) {
                console.error("JSON 解析失败:", e);
                auth = [];
            }
        }
        const tokenData = await this.Sender.bucketGet(`${PZDL.sqlName}_token`, this.user)
        let token = [];
        if (tokenData && typeof tokenData === 'string') {
            try {
                token = JSON.parse(tokenData);
            } catch (e) {
                console.error("JSON 解析失败:", e);
                token = [];
            }
        }
        for (let i = 0; i < allData.length; i++) {
            const authStatus = auth[i] || 0
            if (authStatus - Date.now() <= 0)
                continue
            const data = allData[i].split("#");
            const user = data[0];
            const password = data[1];
            let token1 = token?.[i] || ''
            const task = await Task.create(user, password, token1);
            // this.Sender.reply(`${JSON.stringify(allData[i])}`)
            let result = await task.receive();
            token[i] = task.token
            this.Sender.reply(`${result}`);
        }
        const res2 = await this.Sender.bucketSet(`${PZDL.sqlName}_token`, this.user, JSON.stringify(token))
    }
    //品赞一键运行
    async run() {
        let num = 0;
        const isAdmin = await this.Sender.isAdmin()
        if (!isAdmin) {
            return;
        }
        let rawData = await this.Sender.bucketAll(`${PZDL.sqlName}_users`)
        this.Sender.reply('正在运行品赞签到...')
        const startTime = Date.now();
        let allData = {};
        if (rawData && typeof rawData === 'object') {
            allData = rawData;
        } else if (rawData && typeof rawData === 'string') {
            try {
                allData = JSON.parse(rawData);
            } catch (e) {
                console.error("JSON 解析失败:", e);
                allData = {};
            }
        }
        if (Object.keys(allData).length === 0) {
            this.Sender.reply('没有添加任何账号')
            return;
        }
        try {
            for (const userId in allData) {
                const ckAll = JSON.parse(allData[userId]);//
                const authData = (await this.Sender.bucketGet(`${PZDL.sqlName}_auth`, userId));
                let auth = [];
                if (authData && typeof authData === 'string') {
                    try {
                        auth = JSON.parse(authData);
                    } catch (e) {
                        console.error("JSON 解析失败:", e);
                        auth = [];
                    }
                }
                const tokenData = await this.Sender.bucketGet(`${PZDL.sqlName}_token`, userId)
                let token = [];
                if (tokenData && typeof tokenData === 'string') {
                    try {
                        token = JSON.parse(tokenData);
                    } catch (e) {
                        console.error("JSON 解析失败:", e);
                        token = [];
                    }
                }
                for (let i = 0; i < ckAll.length; i++) {
                    //this.Sender.reply(`authData:${authData} auth:${auth[i]} ${userId}`)
                    const authStatus = auth[i] || 0
                    if (authStatus - Date.now() <= 0)
                        continue
                    const data = ckAll[i].split("#");
                    const user = data[0];
                    const password = data[1];
                    let token1 = token?.[i] || ''
                    const task = await Task.create(user, password, token1);
                    const result = await task.main()
                    token[i] = task.token
                    const match = result.match(/领取金额：(\d+)/)
                    num++
                }
                const res2 = await this.Sender.bucketSet(`${PZDL.sqlName}_token`, userId, JSON.stringify(token))
                const s = Math.floor(Math.random() * (5 - 3 + 1)) + 3;
                console.log(`⏱️ 随机暂停：${s}s`)
                console.log(`-------------------`)
                await new Promise(resolve => setTimeout(resolve, s * 1000));
            }
            const endTime = Date.now();
            this.Sender.reply(`✅品赞签到运行完成！共运行${num}个账号，耗时${(endTime - startTime) / 1000}秒`)
        } catch (e) {
            this.Sender.reply(`❌运行失败！请检查账号信息！错误原因：${e.message}`)
        }
    }


    //时间格式化
    formatDate(timestamp = Date.now()) {
        const date = new Date(timestamp.toString().length === 10 ? timestamp * 1000 : timestamp);
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();

        return year + '-' + month + '-' + day;
    }

    hidePhone(phone) {
        return phone.slice(0, 3) + '****' + phone.slice(-4);
    }
};
!(async function () {

    const senderID = await middlleware.getSenderID()
    const sender = new middlleware.Sender(senderID)
    const user = await sender.getUserID()
    let pzdl = new PZDL(user, sender)
    let message = await sender.getMessage()
    message = message.toLowerCase()
    if (message === '品赞登录') {
        await pzdl.addUser()
    }
    if (message === '品赞管理') {
        await pzdl.manageUser()
    }
    if (message === '品赞查询') {
        await pzdl.query()
    }
    if (message === '品赞一键运行') {
        await pzdl.run()
    }
    if (message === '品赞签到') {
        await pzdl.sign()
    }
})()