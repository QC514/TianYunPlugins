//[title: wqwl-粉象生活]
//[author: wqwlkj2985]
//[language: nodejs]
//[class: 工具类]
//[service: qq298582245] 售后联系方式
//[disable: false] 禁用开关，true表示禁用，false表示可用
//[admin: false] 是否为管理员指令
//[rule: ^(粉象)(登录|管理|查询|一键运行|全部提现|提现|授权|签到)$] 匹配规则1
//[cron: 38 0,22 * * *] cron定时，支持5位域和6位域
//[priority: 298582245] 优先级，数字越大表示优先级越高
//[platform: qq] 适用的平台
//[open_source: false]是否开源
//[icon: http://175.24.81.131:8044/admin/images/gallery/1771682713032996077.jpg]图标链接地址，请使用48像素的正方形图标，支持http和https
//[version: 1.0.3]版本号
//[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
//[price: 12.88] 上架价格
//[param: {"required":true,"key":"wqwl_points.fxsh","bool":false,"placeholder":"授权所需积分，默认为0","name":"授权所需积分","desc":"授权所需积分，默认为0，单位积分/月，仅适配了linzixuan的卡密系统"}]
//[param: {"required":false,"key":"wqwl_config.fxsh_isRandomUser","bool":true,"placeholder":"是否账号乱序，默认false","name":"是否账号乱序","desc":"是否账号乱序，默认false，据我观察每个账号固定时间点中奖概率高，但是中奖账号一般也是那一批账号,随机的话别的账号会高一点，但是其实也差不多，都是看脸中奖"}]
//[param: {"required":false,"key":"wqwl_config.fxsh_signDate","placeholder":"临时签到期数","name":"临时签到期数","desc":"临时签到期数，不知道以后出是否接口不变，现在先预留"}]
//[param: {"required":false,"key":"wqwl_config.fxsh_signEndDate","placeholder":"临时签到结束时间","name":"临时签到结束时间","desc":"临时签到结束时间，按照20260504的格式填，不然可能报错"}]

//[description: v1.0.3，新增临时签到，这一期只有七天，用户指令：粉象签到，管理员的已经放在粉象一键运行里面了<br>几个指令：粉象登录、粉象管理、粉象查询、粉象(全部)提现、粉象一键运行（管理员）、粉象授权（管理员）<br>每天需要运行指令粉象一键运行两次，一次开奖前（21:35），一次开奖后，可以使用autman计划任务自处理定时] 使用方法尽量写具体
const crypto = require("crypto")
const https = require('https');
const axios = require("axios")
const middlleware = require('./middleware')
const { push } = require('./middleware')
const $ = new Env("粉象生活App");

https.globalAgent.options.rejectUnauthorized = false;
let userIdx = 0;
let strSplitor = "#"; //多变量分隔符

class Task {
    constructor(str) {
        this.index = ++userIdx;
        this.did = str.split(strSplitor)[0];
        this.finger = str.split(strSplitor)[1]; //单账号多变量分隔符
        this.token = str.split(strSplitor)[2]; //单账号多变量分隔符
        this.oaid = str.split(strSplitor)[3]; //单账号多变量分隔符
        this.name = str.split(strSplitor)[4];
        this.ckStatus = true;
        this.taskList = []

    }
    async main() {
        await this.user_info();
        if (!this.ckStatus) {
            return;
        }
        await this.sign_reward()
        //await this.sign()
        //await this.coin_receive()
        await this.play_video()
        //await this.open_box()
        /*
        let fruiterId = await this.query_fruiter();
        if (!fruiterId) {
            let fruiter_list = await this.query_fruiter_list();
            if (fruiter_list?.length) {
                $.log(`✅账号[${this.index}]  自动选择第一个水果，水果名为 ${fruiter_list[0]?.description}`);
                fruiterId = await this.plat_fruiter(fruiter_list[0]?.id);
                if (!fruiterId) {
                    return;
                }

            } else {
                console.log(`❌账号[${this.index}]  未获取到可种植水果列表！`);
            }
        }
        await this.stealWater();
        const fruiter_login_info = await this.fruiter_sign_detail();
        const todaySign = fruiter_login_info?.find(item => item?.status == 1);
        if (todaySign?.id) {
            await this.loginAwardReceive(todaySign?.id);
        }
        await $.wait(Math.random() * 2000 + 1000);
        let fruite_tasks = await this.query_fruite_tasks();
        for (let index = 0; index < fruite_tasks?.length; index++) {
            const fruite_task = fruite_tasks[index];
            await this.finish_fruiter_task(fruite_task?.type, fruite_task?.taskInfoId);
            await $.wait(Math.random() * 2000 + 1000);
        }
        while (true) {
            const waterRes = await this.water_fruiter(fruiterId);
            if (waterRes?.canAcquireWaterId) {
                await this.acquireWater_fruiter(fruiterId, waterRes?.canAcquireWaterId);
            }
            if (!waterRes) {
                break;
            }
            await $.wait(Math.random() * 2000 + 1000);
        }*/
        await this.activity_withdraw_check()
        await this.special_finish()
        await this.task_list()
        //console.log(this.taskList)
        for (let i of this.taskList) {
            await $.wait(3000)
            await this.task_finish(i.id, i.title)
        }
        /*
        const gameTasks = await this.game_task();
        for (let gameTask of gameTasks) {
            await $.wait(Number(gameTask?.item?.taskDuration) * 1000 + Math.random() * 1000);
            await this.game_finish(gameTask)
        }*/
    }

    async user_info() {
        let result = await this.taskRequest("get", `https://api.fenxianglife.com/njia/users/info`)
        //console.log(result);
        if (result.code == 200) {
            $.log(`✅账号[${this.index}]  欢迎用户，Id ${result.data.userInfo.id} 昵称 ${result.data.userInfo.nickname} 手机号 ${result.data.userInfo.mobile}🎉`)
            this.ckStatus = true;
        } else {
            console.log(`❌账号[${this.index}]  用户查询: 失败`);
            this.ckStatus = false;
            //console.log(result);
        }
    }
    async task_finish(id, title) {
        let result = await this.taskRequest("post", `https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/lotteryCode/task/finish`, JSON.stringify({
            "taskId": id
        }))
        console.log(result);
        if (result.code == 200) {
            $.log(`✅账号[${this.index}]  任务[${id}][${title}]完成🎉`)
        } else {
            console.log(`❌账号[${this.index}]  任务[${id}][${title}]失败`);
            //console.log(result);
        }
    }

    async activity_withdraw_check() {
        let result = await this.taskRequest("get", `https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/withdraw/index`, '')
        // console.log(result);
        if (result.code == 200) {
            $.log(`✅账号[${this.index}]  今天开奖金额 ${result.data?.totalRewardAmount / 100}元 ${result.data?.amountReceiveStatus == 1 ? '未领取' : '已领取'}🎉`)

            await this.activity_receive_all();

        } else {
            console.log(`❌账号[${this.index}]  查询今日开奖金额: 失败`);
            //console.log(result);
        }
    }

    async activity_receive_all() {
        let result = await this.taskRequest("post", `https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/periodical/open/result/receiveAll`, JSON.stringify({}))
        console.log(result);
        if (result.code == 200) {
            $.log(`✅账号[${this.index}]  提现开奖金额成功🎉`)
        } else {
            console.log(`❌账号[${this.index}]  提现开奖金额: 失败`);
            //console.log(result);
        }
    }

    async special_finish() {
        let result = await this.taskRequest("post", `https://api.fenxianglife.com/njia/game/task/special/finish`, JSON.stringify({
        }))
        console.log(result);
        if (result.errcode == 0) {
            $.log(`✅账号[${this.index}]  欢迎用户: ${result.errcode}🎉`)
            this.ckStatus = true;
        } else {
            console.log(`❌账号[${this.index}]  用户查询: 失败`);
            this.ckStatus = false;
            //console.log(result);
        }
    }

    async game_finish(gameTask) {
        let result = await this.taskRequest("post", `https://api.fenxianglife.com/njia/game/task/finish`,
            JSON.stringify({ "taskId": gameTask?.item?.id, "gameType": gameTask?.activityType }))
        // console.log(result);
        if (result.code == 200) {
            $.log(`✅账号[${this.index}]  完成领现金兑商品活动 任务[${gameTask?.name}][${gameTask?.item?.id}][${gameTask?.item?.taskChanceUse}/${gameTask?.item?.taskChance}]: ${result.data?.toastText || `获得${result.data?.awardCount || 0}金币`}🎉`)
            this.ckStatus = true;
            if (result.data?.awardCount) {
                if (gameTask?.item?.taskChanceUse < gameTask?.item?.taskChance) {
                    $.log(`✅账号[${this.index}]  延迟${gameTask?.item?.taskDuration}秒执行下一个任务`);
                    await $.wait(Number(gameTask?.item?.taskDuration) * 1000 + Math.random() * 1000);
                    return this.game_finish(gameTask);
                }
            }
        } else {
            console.log(`❌账号[${this.index}]  完成领现金兑商品活动 任务[${gameTask?.name}][${gameTask?.item?.id}] 失败`);
            this.ckStatus = false;
            console.log(result);
        }
    }

    async open_box() {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/elephant/activity/limitedTime/complete`,
            JSON.stringify({ "doublingKey": "doubling" }))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  开宝箱成功，获得 ${result?.data?.reward || 0} 金币🎉`)
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  开宝箱失败`);
            console.log(result);
            //console.log(result);
        }
    }

    async invite(initiatorId = "515233097") {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/elephant/mammon/help`,
            JSON.stringify({
                "initiatorId": initiatorId
            }))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  助力成功🎉`)
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  助力失败`);
            console.log(result);
            //console.log(result);
        }
    }

    async sign() {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/elephant/sign`,
            JSON.stringify({}))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  签到成功🎉`)
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  签到失败`);
            console.log(result);
            //console.log(result);
        }
    }

    async coin_receive() {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/elephant/coin/receive`,
            JSON.stringify({}))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  收取金币成功🎉`)
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  收取金币失败`);
            console.log(result);
            //console.log(result);
        }
    }

    async play_video() {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/game/task/finish`,
            JSON.stringify({
                "taskId": 1,
                "gameType": 2,
            }))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  短视频观看成功🎉`)
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  短视频观看失败`);
            console.log(result);
            //console.log(result);
        }
    }

    async game_task() {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/game/task/list`,
            JSON.stringify({ "gameType": 2, "platform": "android", "version": "6.7.1" }))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  获取游戏任务列表成功🎉`)
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  获取游戏任务列表失败`);
            console.log(result);
            //console.log(result);
        }
    }

    async sign_reward() {
        let result = await this.taskRequest("post", `https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/user/sign/reward`, JSON.stringify({
        }))
        //console.log(result);
        if (result.code == 200) {
            $.log(`✅账号[${this.index}]  签到成功🎉`)
        } else {
            console.log(`❌账号[${this.index}]  签到失败`);
            console.log(result);
        }
    }
    async task_list() {
        let result = await this.taskRequest("post", 'https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/home/data/V2', JSON.stringify({
            "plateform": "android",
            "version": "6.7.1"
        }));
        //console.log(result);
        if (result.code == 200) {
            for (let i of result.data.taskModule.taskResult) {
                if (i.taskStatus == 0) {
                    this.taskList.push(i)
                }
            }

        } else {
            console.log(`❌账号[${this.index}]  获取任务失败`);
            //console.log(result);
        }
    }
    async query_fruiter() {
        let result = await this.taskRequest("get", `https://api-1.fenxianglife.com/njia/orchard/user/fruiter/detail`, '')
        if (result.code == 200) {
            $.log(`✅账号[${this.index}]  查询果园信息成功：${result?.data?.fruiterDesc || '未种植'}🎉`);
            return result?.data?.id;
        } else {
            console.log(`❌账号[${this.index}]  查询果园信息失败`);
            console.log(result);
        }
    }
    async fruiter_sign_detail() {
        let result = await this.taskRequest("get", `https://api-1.fenxianglife.com/njia/orchard/loginAward/user/detail`, '')
        if (result.code == 200) {
            $.log(`✅账号[${this.index}]  获取果园签到信息成功🎉`);
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  获取果园签到信息失败`);
            console.log(result);
        }
    }
    async query_fruite_tasks() {
        let result = await this.taskRequest("get", `https://api-1.fenxianglife.com/njia/orchard/task/list`, '')
        if (result.code == 200) {
            $.log(`✅账号[${this.index}]  查询果园任务成功：${result?.data?.length || '0'}个任务 🎉`);
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  查询果园任务失败`);
            console.log(result);
        }
    }
    async query_fruiter_list() {
        let result = await this.taskRequest("get", `https://api-1.fenxianglife.com/njia/orchard/fruiter/list`, '')
        if (result.code == 200) {
            $.log(`✅账号[${this.index}]  当前可选择的种植水果个数为 ：${result?.data?.length || '0'}🎉`);
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  查询可选择的种植水果信息失败`);
            console.log(result);
        }
    }

    async water_fruiter(userFruiterId) {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/orchard/user/fruiter/water`,
            JSON.stringify({ "userFruiterId": userFruiterId }))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  浇水[${userFruiterId}]成功  ${result?.data?.upgradeContext || ''} 🎉`)
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  浇水[${userFruiterId}]失败`);
            console.log(result);
            //console.log(result);
        }
    }

    async loginAwardReceive(day) {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/orchard/loginAward/receive`,
            JSON.stringify({ "day": day }))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  领取签到奖励成功 🎉`)
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  领取签到奖励失败`);
            console.log(result);
            //console.log(result);
        }
    }

    async finish_fruiter_task(type, taskInfoId) {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/orchard/task/finish`,
            JSON.stringify({ "type": type, "taskInfoId": taskInfoId }))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  完成任务[${taskInfoId}]成功，获得水滴 ${result?.data?.upgradeContext || ''} 🎉`)
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  完成任务[${taskInfoId}]失败`);
            console.log(result);
            //console.log(result);
        }
    }

    async finish_push() {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/orchard/task/push/finish`,
            JSON.stringify({}))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  领取开启推送通知奖励成功，获得 ${result?.data?.awardCount || 0}个水滴 🎉`)
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  领取开启推送通知奖励失败`);
            console.log(result);
            //console.log(result);
        }
    }

    async acquireWater_fruiter(userFruiterId, canAcquireWaterId) {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/orchard/user/fruiter/acquireWater`,
            JSON.stringify({ "canAcquireWaterId": canAcquireWaterId, "userFruiterId": userFruiterId }))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  领取浇水奖励成功 🎉`)
            return result?.data;
        } else {
            console.log(`❌账号[${this.index}]  领取浇水奖励失败`);
            console.log(result);
            //console.log(result);
        }
    }

    async plat_fruiter(fruiterId) {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/orchard/user/fruiter/plant`,
            JSON.stringify({ "fruiterId": fruiterId }))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  种植水果[${fruiterId}]成功，水果树ID为 ${result?.data?.userFruiterId || ''} 🎉`)
            return result?.data?.userFruiterId;
        } else {
            console.log(`❌账号[${this.index}]  种植水果[${fruiterId}]失败`);
            console.log(result);
            //console.log(result);
        }
    }
    async stealWater(friendId = -1) {
        let result = await this.taskRequest("post", `https://api-1.fenxianglife.com/njia/orchard/friend/stealWater`,
            JSON.stringify({ "friendId": friendId }))
        if (result.success == true) {
            $.log(`✅账号[${this.index}]  从朋友[${friendId}]  ${result?.data || ''} 🎉`)
            return result?.data?.userFruiterId;
        } else {
            console.log(`❌账号[${this.index}]  从朋友[${friendId}]偷取水滴失败`);
            console.log(result);
            //console.log(result);
        }
    }


    //信息查询
    async query() {
        let result = '=====账号信息=====\n';
        try {

            let raw1 = await this.taskRequest("post", `https://api.fenxianglife.com/njia/order/withdraw/v4/create`,
                JSON.stringify({ "orderType": 5 })
            )

            let raw2 = await this.taskRequest("get", `https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/withdraw/index`, '')

            let raw3 = await this.taskRequest("post", `https://fenxiang-lottery-api.fenxianglife.com/fenxiang-lottery/home/data/V2`,
                JSON.stringify({
                    "plateform": "android",
                    "version": "6.7.1"
                })
            )
            const dataStr = raw2?.data?.dateStr || ''

            const isToday = this.getDateRange().includes(dataStr) ? true : false
            //result += `🎉今日开奖：${isToday ? '是' : '否'}${this.getDate()},${raw3?.data?.openLotteryModule?.now?.rewardCodes?.[0]?.dateStr}`
            result += `🤪 用户ID(备注)：${this.name}\n`
            if (raw1.code == 200) {
                result += `🧧活动奖励余额：${raw1?.data?.maxWithdrawAmount / 100}元(最低0.1起提)\n`
            } else {
                result += `🧧活动奖励余额：查询失败，原因：${raw1?.message || '未知原因'}\n`
            }

            if (raw2.code == 200) {

                if (isToday) {
                    result += `🎰本期开奖期数：${dataStr}期\n`
                    result += `🎉本期开奖金额：${raw2?.data?.totalRewardAmount / 100}元 (${result.data?.amountReceiveStatus == 1 ? '未领取' : '已领取'})\n`
                    if (raw2?.data?.freeOrderCount > 0 && raw2?.data?.freeItem?.itemTitle) {
                        result += `🎁本期免单商品：【${raw2?.data?.freeItem?.itemTitle}】\n`
                    } else {
                        result += '🎁本期免单商品：无\n'
                    }
                }
                else {
                    result += '🎉本期开奖金额：0元(未开奖)\n'
                }
            } else {
                result += `🎉本期开奖金额：查询失败，原因：${raw2?.message || '未知原因'}\n`
            }

            if (raw3.code == 200) {
                if (raw3?.data?.openLotteryModule?.now?.rewardCodes.length <= 0 || raw3?.data?.openLotteryModule?.now?.rewardCodes[0]?.dateStr === undefined)
                    result += `🏆现有奖码个数：${raw3?.data?.openLotteryModule?.now?.rewardCodes.length}个 \n`
                else
                    result += `🏆现有奖码个数：${raw3?.data?.openLotteryModule?.now?.rewardCodes.length}个 (${raw3?.data?.openLotteryModule?.now?.rewardCodes[0]?.dateStr}期)\n`
            } else {
                result += `🏆现有奖码个数：查询失败，原因：${raw3?.message || '未知原因'}\n`
            }

            //🏆
        } catch (e) {
            console.error("请求失败:", e);
            result = `❌用户【${this.name}】信息查询失败，原因：${e.message}\n`
        }
        return result
    }

    //短信登录
    async smsCode(phone) {
        const result = await this.taskRequest('post', 'https://api.fenxianglife.com/njia/util/sms/code',
            JSON.stringify({
                "validateType": 1,
                "mobileArea": "86",
                "mobile": phone,
                "type": 1
            })
        )
        return result
    }
    //登录验证
    async login(phone, code) {
        const result = await this.taskRequest('post', 'https://api.fenxianglife.com/njia/login/mobile',
            JSON.stringify({
                "mobileArea": "86",
                "smsCode": this.MD5(code),
                "mobile": phone
            })
        )
        return result
    }

    //提现
    async withDraw(userName) {
        let result = {
            isSuccess: false,
            msg: '',
            money: 0
        }

        //https://api.fenxianglife.com/njia/order/withdraw/v4/create
        const res1 = await this.taskRequest('post', 'https://api.fenxianglife.com/njia/order/withdraw/v4/create',
            JSON.stringify({
                "orderType": 5
            })
        )

        if (res1?.code != 200 || res1?.data?.alipayAccountInfo?.userName == null || res1?.data?.alipayAccountInfo?.identityCard == null || res1?.data?.alipayAccountInfo?.alipayAccount == null) {
            result.msg = `❌${userName}提现创建失败，请确保绑定了zfb,接口返回原因：${res1?.message}`;
            result.money = 0;
            result.isSuccess = false;
            return result;
        }

        const totalWithdrawAmount = res1?.data?.totalWithdrawAmount;

        const maxWithdrawAmount = res1?.data?.maxWithdrawAmount || 0;

        if (maxWithdrawAmount < 10) {
            result.money = 0;
            result.isSuccess = false;
            result.msg = `❌${userName}提现创建失败，还不够0.1提啥呢，当前可提现余额：${maxWithdrawAmount / 100}元`;
            return result;
        }

        const res2 = await this.taskRequest('post', 'https://api.fenxianglife.com/njia/order/withdraw/submit',
            JSON.stringify({
                "orderType": 5,
                "withdrawAmount": maxWithdrawAmount
            })
        )

        if (res2?.code != 200) {
            result.money = 0;
            result.isSuccess = false;
            result.msg = `❌${userName}提现提交失败，接口返回原因：${res2?.message || '未知原因'}`;
            return result;
        }
        //将\n换成,
        const subTitle = res2?.data?.subTitle.replace(/\n/g, ",");
        result.msg = `🎉${userName}提现提交成功，估计到账${maxWithdrawAmount / 100}元,${subTitle}`;
        result.isSuccess = true;
        result.money = maxWithdrawAmount / 100;
        return result;
    }

    //临时活动签到
    async clockSign(activityId) {
        const res = await this.taskRequest('post', 'https://api.fenxianglife.com/njia/takeaway/clock/in/sign',
            JSON.stringify({
                "activityId": activityId
            })
        )
        return res
    }

    tokenStr(phone) {
        return `${this.did}#${this.finger}#${this.token}#${this.oaid}#${phone.slice(0, 3)}****${phone.slice(-4)}`
    }
    async taskRequest(method, url, body = "") {
        function convertObjectToQueryString(obj) {
            let queryString = "";
            if (obj) {
                const keys = Object.keys(obj).sort();
                keys.forEach(key => {
                    const value = obj[key];
                    if (value !== null && typeof value !== 'object') {
                        queryString += `&${key}=${value}`;
                    }
                });
            }
            return queryString.slice(1);
        }

        const g = {
            traceid: this.MD5((new Date).getTime().toString() + Math.random().toString()),
            noncestr: Math.random().toString().slice(2, 10),
            timestamp: Date.now(),
            platform: "android",
            did: this.did,
            version: "6.7.1",
            finger: this.finger,
            token: this.token,
            oaid: this.oaid,
        }
        const c = "\u7c89\u8c61\u597d\u725b\u903cnb3b16f5a02479a0e34df78d14aefe76"
        let s = method === "get" ? void 0 : JSON.parse(body)
        let e = void 0 === s ? {} : s
        g.sign = this.MD5(c + convertObjectToQueryString(e) + convertObjectToQueryString(g))
        let headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.99 Mobile Safari/537.36 AgentWeb/5.0.0  UCBrowser/11.6.4.950',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
            'origin': 'https://m.fenxianglife.com',
            'sec-fetch-dest': 'empty',
            'x-requested-with': 'com.n_add.android',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'referer': 'https://m.fenxianglife.com',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            "Content-Type": "application/json"
        }
        Object.assign(headers, g)
        //console.log(headers)
        const requestOptions = {
            url: url,
            method: method,
            headers: headers,
            data: body  // axios 中使用 data 而不是 body
        }

        try {
            const response = await axios(requestOptions);
            return response.data;
        } catch (error) {
            return { code: -1, message: "接口请求失败", error: error.message };
        }
    }
    MD5(e) {
        return crypto.createHash("md5").update(e).digest("hex")
    }

    //期号
    getDate() {
        const now = new Date();
        // 补零函数
        const padZero = (num) => String(num).padStart(2, '0');

        const year = now.getFullYear().toString().slice(2); // 取后两位：2025 → '25'
        const month = padZero(now.getMonth() + 1); // getMonth() 是从 0 开始的，所以要 +1
        const day = padZero(now.getDate());

        return `${year}${month}${day}`;
    }
    // 获取今天和昨天的期号数组 [今天, 昨天]
    getDateRange() {
        const padZero = (num) => String(num).padStart(2, '0');

        // 获取指定日期的期号
        const getDateStr = (date) => {
            const year = date.getFullYear().toString().slice(2);
            const month = padZero(date.getMonth() + 1);
            const day = padZero(date.getDate());
            return `${year}${month}${day}`;
        };

        const today = new Date();
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);

        return [getDateStr(today), getDateStr(yesterday)];
    }
}

const Fxsh = class {
    static sqlName = 'wqwl_fxsh'
    constructor(user, Sender) {
        this.user = user;
        this.Sender = Sender;
    }

    //粉象登录
    async addUser() {
        try {
            this.Sender.reply('=====登录方式=====\n[1] 短信登录\n[2] cookie登录\n------------------\n回复数字选择方式\n回复"q"退出')
            let select = await this.Sender.listen(60000)
            let userInput
            if (select === "1") {
                let ck = ''
                const fx = new Task("did#finger#token#oaid#备注")
                fx.token = ''
                fx.did = this.randomDid()
                fx.oaid = this.randomOaid(fx.did)
                fx.finger = this.randomFinger()
                this.Sender.reply("请输入手机号(输入q退出)：")
                let phone = await this.Sender.listen(60000)
                if (phone === "q") {
                    this.Sender.reply("❌已退出登录！")
                    return;
                }
                if (phone === "" || phone === null) {
                    this.Sender.reply("❌输入超时")
                    return;
                }
                if (phone.length != 11 || !phone.match(/^1[3-9]\d{9}$/)) {
                    this.Sender.reply("❌手机号格式错误")
                    return;
                }
                const sendResult = await fx.smsCode(phone)
                if (sendResult.code == 200) {
                    this.Sender.reply("✅发送成功，请回复短信验证码");
                    let code = await this.Sender.listen(60000)
                    if (code === "" || code === null) {
                        this.Sender.reply("❌输入超时")
                        return;
                    }
                    let loginResult = await fx.login(phone, code)
                    if (loginResult.code == 200) {
                        this.ckStatus = true;
                        fx.token = loginResult.data.token;
                        userInput = fx.tokenStr(phone)
                    } else {
                        this.Sender.reply("❌登录失败,请检查验证码是否正确");
                        return;
                    }
                } else {
                    this.Sender.reply(`❌发送失败，请稍后再试,返回结果：${JSON.stringify(sendResult)}`)
                    return;
                }
            } else if (select === "2") {
                this.Sender.reply("正在使用ck登录！请按照以下格式输入：\n did#finger#token#oaid#备注 \n 退出输入'q'!")
                userInput = await this.Sender.listen(60000)
                if (userInput === "q") {
                    this.Sender.reply("❌已退出登录！")
                    return;
                }
                if (userInput === "" || userInput === null) {
                    this.Sender.reply("❌输入超时")
                    return;
                }
            } else {
                this.Sender.reply("❌输入错误或q退出！")
                return;
            }
            const rawData = await this.Sender.bucketGet(`${Fxsh.sqlName}_users`, this.user);
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
            const userData = userInput.split("#")
            if (userData.length !== 5) {
                this.Sender.reply("❌输入格式错误！请按照以下格式重新添加：\n did#finger#token#oaid#备注")
                return
            }
            if (this.isUserExist(allData, userData)) {
                this.Sender.reply('用户已经存在，是否进行覆盖？(y/n)')
                const tmp = await this.Sender.listen(60000)
                if (tmp.toLowerCase() === 'y') {
                    const isSuccess = this.updateSame(allData, userData)
                    if (isSuccess) {
                        //this.Sender.reply(`覆盖成功！请回复【粉象运行】查看是否成功添加！`)
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
            const res = await this.Sender.bucketSet(`${Fxsh.sqlName}_users`, this.user, JSON.stringify(allData))

            if (!res) {
                this.Sender.reply(`❌添加失败！请重新添加！`)
                return
            }
            return this.Sender.reply(`✅添加成功，请回复【粉象查询】查看是否成功添加（不授权不运行）！`)

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
            if (itemFields[4] === userData[4]) {
                return true;
            }
        }
        return false;
    }

    //覆盖数据
    updateSame(allData, userData) {
        const fields = userData; // [did, finger, token, oaid, 备注]

        for (let i = 0; i < allData.length; i++) {
            const item = allData[i];
            const itemFields = item.split('#');

            // 检查是否有任意字段相等
            const hasMatch = itemFields.some(field => fields.includes(field));

            if (hasMatch) {
                // 找到了匹配项，替换为新的数据（或 userData 的格式）
                allData[i] = userData.join('#'); // 替换整条记录
                return true; // 表示已找到并替换
            }
        }

        return false; // 没有找到匹配项
    }

    //粉象管理
    async manageUser() {
        try {
            const rawData = await this.Sender.bucketGet(`${Fxsh.sqlName}_users`, this.user);

            const allData = JSON.parse(rawData)
            const authData = await this.Sender.bucketGet(`${Fxsh.sqlName}_auth`, this.user);
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
            if (!allData || allData.length === 0) {
                this.Sender.reply(`=====未绑定账号=====\n❌ 未找到任何账号信息\n发送 粉象登录 绑定账号\n==================`)
                return
            }
            let msg = '=====账号列表====='
            msg += `\n[0] 授权全部账号`
            for (let i = 0; i < allData.length; i++) {
                const tempData = allData[i].split('#')
                const userName = tempData[4]
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
                const num = parseInt(userInput, 10);
                const userId = (!isNaN(num) && num >= 0) ? (num - 1) : 0;
                if (userId === -1) {
                    this.addAllAuth(auth, allData)
                    return;
                }
                if (userId > allData.length - 1) {
                    this.Sender.reply('❌无效的选择')
                    return;
                }
                this.Sender.reply(`=====账号操作=====\n[1] 授权账号\n[2] 运行任务\n[3] 余额提现\n[4] 删除账号\n------------------\n回复数字选择操作\n回复"q"退出`)
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
                        await this.runAlone(userId, auth, allData);
                        break;
                    case "3":
                        await this.withDraw(userId, auth, allData, true);
                        break;
                    case "4":
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
    // 余额提现
    async withDraw(userId, authData, allData, isAlone = false) {
        try {
            //  this.Sender.reply((authData) + ',' + userId)
            const authStatus = authData[userId] || 0;
            const userCk = allData[userId];
            const task = new Task(userCk);
            const userName = userCk.split('#')[4];
            //  this.Sender.reply(`authStatus: ${authStatus},${Date.now()}`)
            if (authStatus - Date.now() <= 0) {

                this.Sender.reply(`❌${userName}未授权或已过期，无法进行操作`);
                return {
                    isSuccess: false,
                    msg: `${userName}未授权或已过期，无法进行操作`

                };
            }


            this.Sender.reply(`🚀开始提现账号: ${userName}`);


            // 查询结果
            let result = await task.withDraw(userName);

            await this.addSumWithdraw(result.money)
            if (isAlone) {
                await this.Sender.reply(result.msg)
            }
            else
                return result

        } catch (e) {
            await this.Sender.reply(`❌账号提现失败！错误原因：${e.message}`);
            return {
                isSuccess: false,
                msg: `❌账号提现失败！错误原因：${e.message}`

            };
        }
    }
    //提现全部账号
    async withDrawAll() {
        const rawData = await this.Sender.bucketGet(`${Fxsh.sqlName}_users`, this.user);
        if (!rawData) {
            this.Sender.reply(`=====未绑定账号=====\n❌ 未找到任何账号信息\n发送 粉象登录 绑定账号\n==================`)
            return
        }
        const allData = JSON.parse(rawData)
        const authData = await this.Sender.bucketGet(`${Fxsh.sqlName}_auth`, this.user);
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
        let times = 0;
        let sumMoney = 0;
        let success = 0;
        for (let i = 0; i < allData.length; i++) {
            const result = await this.withDraw(i, auth, allData)
            if (result.isSuccess) {
                sumMoney += result.money;
                success++;
            }
            await this.Sender.reply(result.msg);
            times++;
            await this.wait(3)
        }
        const msg = `
=====粉象提现统计====
✨ 总账号数: ${times}个
✅ 提现成功: ${success}个
❌ 提现失败: ${times - success}个
🧧 总提金额: ${sumMoney.toFixed(2)}元
${await this.getSumWithdraw()}
==================`
        await this.Sender.reply(msg)
    }

    //获取累计提现
    async getSumWithdraw() {
        const rawData = await this.Sender.bucketGet(`${Fxsh.sqlName}_draw`, this.user);
        let allData = {
            money: 0,
            times: 0
        }
        if (rawData && typeof rawData === 'string') {
            try {
                allData = JSON.parse(rawData);
            } catch (e) {
                console.error("JSON 解析失败:", e);
                allData = {
                    money: 0,
                    times: 0
                }
            }
        }
        if (allData.money === 0 && allData.times === 0) {
            await this.Sender.bucketSet(`${Fxsh.sqlName}_draw`, this.user, JSON.stringify(allData))
        }
        return `💰 累计提现: ${parseFloat(allData.money).toFixed(2)}元(${allData.times}次)`
    }

    //添加累计提现
    async addSumWithdraw(money) {
        const rawData = await this.Sender.bucketGet(`${Fxsh.sqlName}_draw`, this.user);
        let allData = {
            money: 0,
            times: 0
        }
        if (rawData && typeof rawData === 'string') {
            try {
                allData = JSON.parse(rawData);
            } catch (e) {
                console.error("JSON 解析失败:", e);
                allData = {
                    money: 0,
                    times: 0
                }
            }
        }
        if (money > 0) {
            allData.money += money;
            allData.times++
            await this.Sender.bucketSet(`${Fxsh.sqlName}_draw`, this.user, JSON.stringify(allData))
        }
    }
    // 单独运行指定账号
    async runAlone(userId, authData, allData) {
        try {
            const authStatus = authData[userId] || 0;
            if (authStatus - Date.now() <= 0) {
                this.Sender.reply("❌该账号未授权或已过期，无法运行");
                return;
            }

            const userCk = allData[userId];
            const task = new Task(userCk);
            const userName = userCk.split('#')[4];

            this.Sender.reply(`🚀开始运行账号: ${userName}`);
            const startTime = Date.now();

            // 执行主要任务
            await task.main();

            // 查询结果
            let result = await task.query();
            const endTime = Date.now();

            const formattedTime = this.getCurrentTime()

            result += `==================\n⏰ 运行耗时: ${(endTime - startTime) / 1000}秒\n📅 运行时间: ${formattedTime}`;

            this.Sender.reply(result)

        } catch (e) {
            this.Sender.reply(`❌运行账号失败！错误原因：${e.message}`);
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
        // 获取积分价格
        const priceRaw = await this.Sender.bucketGet('wqwl_points', 'fxsh');
        const pointsPrice = priceRaw ? parseInt(priceRaw) : 0;
        if (pointsPrice > 0) {
            const totalCost = pointsPrice * times * allData.length;
            // 获取用户积分
            const userPointsRaw = await this.Sender.bucketGet('dd_sign_points', this.user);
            const userPoints = userPointsRaw ? parseInt(userPointsRaw) : 0;
            if (userPoints < totalCost) {
                this.Sender.reply(`❌积分不足！需要${totalCost}积分（${pointsPrice}积分/月×${times}月×${allData.length}个账号），当前积分：${userPoints}`)
                return;
            }
            // 确认扣除
            this.Sender.reply(`⚠️本次授权需要扣除${totalCost}积分（${pointsPrice}积分/月×${times}月×${allData.length}个账号），当前积分：${userPoints}，确认授权吗？(y/n)`)
            let confirmInput = await this.Sender.listen(60000)
            if (confirmInput === "q") {
                this.Sender.reply("✅已退出操作！")
                return;
            }
            if (confirmInput === "" || confirmInput === null) {
                this.Sender.reply("❌输入超时")
                return;
            }
            if (confirmInput.toLowerCase() !== 'y') {
                this.Sender.reply("❌已取消授权")
                return;
            }
            // 扣除积分
            const newPoints = userPoints - totalCost;
            await this.Sender.bucketSet('dd_sign_points', this.user, newPoints.toString());
            this.Sender.reply(`✅已扣除${totalCost}积分，剩余积分：${newPoints}`)
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
        const res = await this.Sender.bucketSet(`${Fxsh.sqlName}_auth`, this.user, JSON.stringify(authData))
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
        // 获取积分价格
        const priceRaw = await this.Sender.bucketGet('wqwl_points', 'fxsh');
        const pointsPrice = priceRaw ? parseInt(priceRaw) : 0;
        if (pointsPrice > 0) {
            const totalCost = pointsPrice * times;
            // 获取用户积分
            const userPointsRaw = await this.Sender.bucketGet('dd_sign_points', this.user);
            const userPoints = userPointsRaw ? parseInt(userPointsRaw) : 0;
            if (userPoints < totalCost) {
                this.Sender.reply(`❌积分不足！需要${totalCost}积分（${pointsPrice}积分/月×${times}月），当前积分：${userPoints}`)
                return;
            }
            // 确认扣除
            this.Sender.reply(`⚠️本次授权需要扣除${totalCost}积分（${pointsPrice}积分/月×${times}月），当前积分：${userPoints}，确认授权吗？(y/n)`)
            let confirmInput = await this.Sender.listen(60000)
            if (confirmInput === "q") {
                this.Sender.reply("✅已退出操作！")
                return;
            }
            if (confirmInput === "" || confirmInput === null) {
                this.Sender.reply("❌输入超时")
                return;
            }
            if (confirmInput.toLowerCase() !== 'y') {
                this.Sender.reply("❌已取消授权")
                return;
            }
            // 扣除积分
            const newPoints = userPoints - totalCost;
            await this.Sender.bucketSet('dd_sign_points', this.user, newPoints.toString());
            this.Sender.reply(`✅已扣除${totalCost}积分，剩余积分：${newPoints}`)
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
            this.Sender.reply(`❌${allData[4]} 添加授权失败，请联系管理员,${e.message}`)
        }
        const res = await this.Sender.bucketSet(`${Fxsh.sqlName}_auth`, this.user, JSON.stringify(authData))
        if (!res) {
            this.Sender.reply(`❌${allData[4]} 添加授权失败，请联系管理员`)
            return
        }
        return this.Sender.reply(`=====授权成功=====
🤪 账号: ${allData[userId].split('#')[4]}
⏰ 时长: ${times * 30}天
📅 到期: ${this.formatDate(authData[userId])}
==================`)
    }

    //删除授权
    async deleteAuth(userId, authData, allData) {
        const name = allData[userId].split('#')[4]
        this.Sender.reply(`⚠️您确定删除账号【${name}】吗？(y/n)`)
        let answer = await this.Sender.listen(60000)
        if (answer === "" || answer === null) {
            this.Sender.reply("❌输入超时")
            return;
        }
        if (answer.toLowerCase() === "y") {
            authData.splice(userId, 1)
            allData.splice(userId, 1)
            const res = await this.Sender.bucketSet(`${Fxsh.sqlName}_auth`, this.user, JSON.stringify(authData))
            const res2 = await this.Sender.bucketSet(`${Fxsh.sqlName}_users`, this.user, JSON.stringify(allData))
            if (res && res2) {
                this.Sender.reply("✅删除成功")
            } else {
                this.Sender.reply("❌删除失败")
            }
        } else {
            this.Sender.reply("❌删除失败,输入有误")
        }
    }

    //粉象查询
    async query() {
        let rawData = await this.Sender.bucketGet(`${Fxsh.sqlName}_users`, this.user)

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
            this.Sender.reply(`=====未绑定账号=====\n❌ 未找到任何账号信息\n💡 发送 粉象登录 绑定账号\n==================`)
            return;
        }
        const authData = await this.Sender.bucketGet(`${Fxsh.sqlName}_auth`, this.user);
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
        let choiceMsg = `请输入要查询的账号：\n[0] 全部查询\n${'-'.repeat(20)}`
        for (let i = 0; i < allData.length; i++) {
            choiceMsg += `\n[${i + 1}] ${allData[i].split('#')[4]}`
        }
        this.Sender.reply(choiceMsg)
        let choice = await this.Sender.listen(60000);
        if (choice === "q") {
            this.Sender.reply("✅已退出操作！")
            return;
        }
        if (choice === "" || choice === null) {
            this.Sender.reply("❌输入超时")
            return;
        }
        this.Sender.reply('正在查询...')
        choice = parseInt(choice) - 1;
        if (choice === -1) {
            for (let i = 0; i < allData.length; i++) {
                const task = new Task(allData[i]);
                // this.Sender.reply(`${JSON.stringify(allData[i])}`)
                let result = await task.query()
                const authTimes = auth[i] ? Math.floor((auth[i] - Date.now()) / (1000 * 60 * 60 * 24)) : 0
                if (authTimes <= 0)
                    return this.Sender.reply(`【${allData[i].split('#')[4]}】⚠️未授权或授权已到期，请及时授权`)
                result += `☁️剩余授权时间：${authTimes}天\n================\n`
                this.Sender.reply(result)
                await this.wait(1)
            }
        } else {
            const task = new Task(allData[choice]);
            // this.Sender.reply(`${JSON.stringify(allData[i])}`)
            let result = await task.query()
            const authTimes = auth[choice] ? Math.floor((auth[choice] - Date.now()) / (1000 * 60 * 60 * 24)) : 0
            if (authTimes <= 0)
                return this.Sender.reply(`【${allData[choice].split('#')[4]}】⚠️未授权或授权已到期，请及时授权`)
            result += `☁️剩余授权时间：${authTimes}天\n================\n`
            this.Sender.reply(result)
        }
    }



    //粉象一键运行
    async run() {
        let num = 0;
        let priceNum = 0;
        const isAdmin = await this.Sender.isAdmin()
        if (!isAdmin) {
            return;
        }
        let rawData = await this.Sender.bucketAll(`${Fxsh.sqlName}_users`)
        let notifData = await this.Sender.bucketAll(`${Fxsh.sqlName}_notify`);
        let notifyData = {};
        if (notifData && typeof notifData === 'object') {
            notifyData = notifData;
        } else if (notifData && typeof notifData === 'string') {
            try {
                notifyData = JSON.parse(notifData);
            } catch (e) {
                console.error("JSON 解析失败:", e);
                notifyData = {};
            }
        }

        this.Sender.reply('正在运行粉象生活...')
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
            let sumAmount = 0
            // 1. 收集所有账号数据
            const allAccounts = [];

            for (const userId in allData) {
                const ckAll = JSON.parse(allData[userId]);
                const authData = await this.Sender.bucketGet(`${Fxsh.sqlName}_auth`, userId);
                let auth = [];

                if (authData && typeof authData === 'string') {
                    try {
                        auth = JSON.parse(authData);
                    } catch (e) {
                        console.error("JSON 解析失败:", e);
                        auth = [];
                    }
                }

                // 收集每个用户的账号和认证信息
                for (let i = 0; i < ckAll.length; i++) {
                    allAccounts.push({
                        userId,
                        ck: ckAll[i],
                        auth: auth[i] || 0,
                        originalIndex: i // 保留原始索引，如果需要的话
                    });
                }
            }

            const isRandomUserRaw = await this.Sender.bucketGet(`wqwl_config`, 'fxsh_isRandomUser');
            const isRandomUser = isRandomUserRaw === true || isRandomUserRaw === 'true';
            if (isRandomUser === 'true' || isRandomUser === true) {
                // 2. 全局打乱所有账号
                for (let i = allAccounts.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [allAccounts[i], allAccounts[j]] = [allAccounts[j], allAccounts[i]];
                }
            }
            // 3. 处理所有账号
            let todayPeriod = ''
            //获取临时活动是否过期
            const act = await this.Sender.bucketGet(`wqwl_config`, 'fxsh_signDate') || '20260428';
            const actEndDate = await this.Sender.bucketGet(`wqwl_config`, 'fxsh_signEndDate') || '20260504';
            const isTodayBeforeOrEqual = (dateStr) => {
                const today = new Date();
                const todayNum = parseInt(
                    `${today.getFullYear()}${String(today.getMonth() + 1).padStart(2, '0')}${String(today.getDate()).padStart(2, '0')}`
                );
                return todayNum <= parseInt(dateStr);
            };
            const actIsEnd = isTodayBeforeOrEqual(actEndDate)
            for (const account of allAccounts) {
                const { userId, ck, auth } = account;

                // 检查认证状态
                if (auth - Date.now() <= 0) {
                    continue;
                }

                const task = new Task(ck);
                await task.main();
                let result = await task.query();

                // 提取今天开奖金额
                const todayAmountMatch = result.match(/本期开奖金额：([\d\.]+)元/);

                const todayDataMat = result.match(/本期开奖期数：\s*(\d+)\s*期/);
                todayPeriod = todayDataMat ? 'qi' + todayDataMat[1] : '';
                const hasNotified = todayPeriod && Object.keys(notifyData).includes(todayPeriod);
                //  await this.Sender.reply(hasNotified + '')
                // await this.Sender.reply(`状态${hasNotified ? '已通知' : '未通知'}`)
                // await this.Sender.reply(`,todayPeriod:${todayPeriod}`)
                // await this.Sender.reply(`shuj:${JSON.stringify(notifyData)}`)
                if (!hasNotified) {
                    await this.Sender.bucketSet(`${Fxsh.sqlName}_notify`, todayPeriod, '1')
                    //await this.Sender.reply(`,todayPeriod:${todayPeriod}`)
                    const todayAmount = todayAmountMatch ? parseFloat(todayAmountMatch[1]) : 0;
                    sumAmount += todayAmount;

                    if (todayAmount > 1.0) {
                        push('qq', '', userId, '粉象中奖通知', result);
                    }

                    const formattedTime = this.getCurrentTime()
                    result += `==================\n所属用户ID：${userId}\n时间：${formattedTime}`;

                    if (todayAmount > 0) {
                        priceNum++;
                        this.Sender.reply(result);
                    }
                }
                num++;
                if (actIsEnd) {
                    await this.wait(3)
                    task.clockSign(act)
                }
                await this.wait(1)
            }
            const endTime = Date.now();
            await this.Sender.bucketSet(`${Fxsh.sqlName}_notify`, todayPeriod, '1')
            await this.Sender.reply(`✅粉象生活运行完成！共运行${num}个账号，耗时${(endTime - startTime) / 1000}秒，总中奖数：${priceNum}，总收益：${sumAmount.toFixed(2)}`)
        } catch (e) {
            this.Sender.reply(`❌运行失败！请检查账号信息！错误原因：${e.message}`)
        }
    }


    async clockSignAlone() {
        const act = await this.Sender.bucketGet(`wqwl_config`, 'fxsh_signDate') || '20260428';
        const rawData = await this.Sender.bucketGet(`${Fxsh.sqlName}_users`, this.user);
        if (!rawData || rawData.length <= 0) {
            this.Sender.reply(`=====未绑定账号=====\n❌ 未找到任何账号信息\n发送 粉象登录 绑定账号\n==================`)
            return
        }
        const allData = JSON.parse(rawData)
        const authData = await this.Sender.bucketGet(`${Fxsh.sqlName}_auth`, this.user);
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
        let times = 0;
        let sumMoney = 0;
        let success = 0;
        for (let i = 0; i < allData.length; i++) {
            const result = await this._clockSign(i, auth, allData, act)
            if (result.isSuccess) {
                sumMoney += result.money;
                success++;
            }
            await this.Sender.reply(result.msg);
            times++;
            await this.wait(3)
        }
        const msg = `
    =====粉象活动签到统计====
    ✨ 总账号数: ${times}个
    ✅ 签到成功: ${success}个
    ❌ 签到失败: ${times - success}个
    🧧 总获金额: ${sumMoney.toFixed(2)}元
    ==================`
        await this.Sender.reply(msg)
    }

    async _clockSign(userId, authData, allData, activityId) {
        try {
            //  this.Sender.reply((authData) + ',' + userId)
            const authStatus = authData[userId] || 0;
            const userCk = allData[userId];
            const task = new Task(userCk);
            const userName = userCk.split('#')[4];
            //  this.Sender.reply(`authStatus: ${authStatus},${Date.now()}`)
            if (authStatus - Date.now() <= 0) {

                this.Sender.reply(`❌${userName}未授权或已过期，无法进行操作`);
                return {
                    isSuccess: false,
                    msg: `${userName}未授权或已过期，无法进行操作`

                };
            }


            this.Sender.reply(`🚀开始签到账号: ${userName}`);


            // 查询结果
            let result = await task.clockSign(activityId);
            if (result?.code === 200) {
                const money = (result?.data?.rewardAmount / 100)
                return {
                    isSuccess: true,
                    msg: `签到成功,获得${money.toFixed(2)}元`,
                    money: money.toFixed(2)
                }
            } else {
                return {
                    isSuccess: false,
                    msg: `❌账号签到失败！错误原因：${result?.message}`

                };
            }

        } catch (e) {
            await this.Sender.reply(`❌账号签到失败！错误原因：${e.message}`);
            return {
                isSuccess: false,
                msg: `❌账号签到失败！错误原因：${e.message}`

            };
        }
    }
    //时间格式化
    formatDate(timestamp) {
        const date = new Date(timestamp.toString().length === 10 ? timestamp * 1000 : timestamp);
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();

        return year + '-' + month + '-' + day;
    }

    //获取当前详细时间
    getCurrentTime() {
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth() + 1;
        const day = now.getDate();
        const hours = now.getHours();
        const minutes = now.getMinutes();
        const seconds = now.getSeconds();

        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }


    //random did
    randomDid() {
        // 生成 UUID v4 的核心部分
        const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });

        // 替换前四位为 njia，并保留后面 UUID 的 32 位不变
        return 'njia' + uuid.slice(4);
    }
    //oaid
    randomOaid(did) {
        return crypto.createHash('md5').update(did).digest('hex').slice(8, 24);;
    }

    //finger
    randomFinger() {
        return crypto.createHash('md5').update(Date.now() + '').digest('hex');
    }

    //管理员批量授权（不需要积分）
    async adminAuth() {
        const isAdmin = await this.Sender.isAdmin()
        if (!isAdmin) {
            return;
        }
        try {
            this.Sender.reply('请输入要授权的用户ID（回复q退出）：')
            let targetUser = await this.Sender.listen(60000)
            if (targetUser === "q") {
                this.Sender.reply("✅已退出操作！")
                return;
            }
            if (targetUser === "" || targetUser === null) {
                this.Sender.reply("❌输入超时")
                return;
            }
            // 获取目标用户的账号数据
            const rawData = await this.Sender.bucketGet(`${Fxsh.sqlName}_users`, targetUser);
            if (!rawData || rawData.length === 0) {
                this.Sender.reply(`❌未找到用户【${targetUser}】的账号信息`)
                return;
            }
            const allData = JSON.parse(rawData);
            const authRaw = await this.Sender.bucketGet(`${Fxsh.sqlName}_auth`, targetUser);
            let authData = [];
            if (authRaw && typeof authRaw === 'string') {
                try {
                    authData = JSON.parse(authRaw);
                } catch (e) {
                    authData = [];
                }
            }
            // 展示账号列表
            let msg = `=====用户【${targetUser}】账号列表=====`
            msg += `\n[0] 授权全部账号`
            for (let i = 0; i < allData.length; i++) {
                const userName = allData[i].split('#')[4]
                const authStatus = authData[i] || 0
                if (authStatus === 0)
                    msg += `\n[${i + 1}] ${userName}\n❌未授权`
                else if (authStatus < Date.now())
                    msg += `\n[${i + 1}] ${userName}\n❌已过期`
                else
                    msg += `\n[${i + 1}] ${userName}\n✅已授权 到期：${this.formatDate(authStatus)}`
            }
            msg += `\n------------------\n回复数字选择账号\n回复'q'退出`
            this.Sender.reply(msg)
            let userInputAuth = await this.Sender.listen(60000)
            if (userInputAuth === "q") {
                this.Sender.reply("✅已退出操作！")
                return;
            }
            if (userInputAuth === "" || userInputAuth === null) {
                this.Sender.reply("❌输入超时")
                return;
            }
            const selectNum = parseInt(userInputAuth, 10);
            if (isNaN(selectNum) || selectNum < 0 || selectNum > allData.length) {
                this.Sender.reply('❌无效的选择')
                return;
            }
            // 输入月数（支持负数）
            this.Sender.reply('请输入授权月数（支持负数扣除授权，回复q退出）：')
            let timesInput = await this.Sender.listen(60000)
            if (timesInput === "q") {
                this.Sender.reply("✅已退出操作！")
                return;
            }
            if (timesInput === "" || timesInput === null) {
                this.Sender.reply("❌输入超时")
                return;
            }
            const times = parseInt(timesInput, 10);
            if (isNaN(times) || times === 0) {
                this.Sender.reply('❌请输入有效的数字（不能为0）')
                return;
            }
            // 执行授权
            let success = 0;
            if (selectNum === 0) {
                // 授权全部
                for (let i = 0; i < allData.length; i++) {
                    if (!authData[i]) authData[i] = 0
                    if (times > 0) {
                        if (authData[i] - Date.now() <= 0)
                            authData[i] = Date.now() + times * 1000 * 60 * 60 * 24 * 30;
                        else
                            authData[i] += times * 1000 * 60 * 60 * 24 * 30;
                    } else {
                        authData[i] += times * 1000 * 60 * 60 * 24 * 30;
                        if (authData[i] < 0) authData[i] = 0;
                    }
                    success++;
                }
            } else {
                // 授权单个
                const idx = selectNum - 1;
                if (!authData[idx]) authData[idx] = 0
                if (times > 0) {
                    if (authData[idx] - Date.now() <= 0)
                        authData[idx] = Date.now() + times * 1000 * 60 * 60 * 24 * 30;
                    else
                        authData[idx] += times * 1000 * 60 * 60 * 24 * 30;
                } else {
                    authData[idx] += times * 1000 * 60 * 60 * 24 * 30;
                    if (authData[idx] < 0) authData[idx] = 0;
                }
                success = 1;
            }
            const res = await this.Sender.bucketSet(`${Fxsh.sqlName}_auth`, targetUser, JSON.stringify(authData))
            if (!res) {
                this.Sender.reply(`❌授权保存失败，请重试`)
                return;
            }
            if (selectNum === 0) {
                this.Sender.reply(`=====管理员授权成功=====\n👤 用户：${targetUser}\n✅ 成功：${success}个账号\n⏰ 操作：${times > 0 ? '增加' : '扣除'}${Math.abs(times) * 30}天\n==================`)
            } else {
                const idx = selectNum - 1;
                this.Sender.reply(`=====管理员授权成功=====\n👤 用户：${targetUser}\n🤪 账号：${allData[idx].split('#')[4]}\n⏰ 操作：${times > 0 ? '增加' : '扣除'}${Math.abs(times) * 30}天\n📅 到期：${authData[idx] > 0 ? this.formatDate(authData[idx]) : '已清除'}\n==================`)
            }
        } catch (e) {
            this.Sender.reply(`❌管理员授权失败！错误原因：${e.message}`)
        }
    }

    async wait(s) {
        return await new Promise(resolve => setTimeout(resolve, s * 1000));
    }
};

function Env(t, s) { return new (class { constructor(t, s) { this.name = t; this.logs = []; this.logSeparator = "\n"; this.startTime = new Date().getTime(); Object.assign(this, s); this.log("", `\ud83d\udd14${this.name},\u5f00\u59cb!`) } isNode() { return "undefined" != typeof module && !!module.exports } isQuanX() { return "undefined" != typeof $task } isSurge() { return "undefined" != typeof $httpClient && "undefined" == typeof $loon } isLoon() { return "undefined" != typeof $loon } initRequestEnv(t) { try { require.resolve("got") && ((this.requset = require("got")), (this.requestModule = "got")) } catch (e) { } try { require.resolve("axios") && ((this.requset = require("axios")), (this.requestModule = "axios")) } catch (e) { } this.cktough = this.cktough ? this.cktough : require("tough-cookie"); this.ckjar = this.ckjar ? this.ckjar : new this.cktough.CookieJar(); if (t) { t.headers = t.headers ? t.headers : {}; if (typeof t.headers.Cookie === "undefined" && typeof t.cookieJar === "undefined") { t.cookieJar = this.ckjar } } } queryStr(options) { return Object.entries(options).map(([key, value]) => `${key}=${typeof value === "object" ? JSON.stringify(value) : value}`).join("&") } getURLParams(url) { const params = {}; const queryString = url.split("?")[1]; if (queryString) { const paramPairs = queryString.split("&"); paramPairs.forEach((pair) => { const [key, value] = pair.split("="); params[key] = value }) } return params } isJSONString(str) { try { return JSON.parse(str) && typeof JSON.parse(str) === "object" } catch (e) { return false } } isJson(obj) { var isjson = typeof obj == "object" && Object.prototype.toString.call(obj).toLowerCase() == "[object object]" && !obj.length; return isjson } async sendMsg(message) { if (!message) return; if (this.isNode()) { await notify.sendNotify(this.name, message) } else { this.msg(this.name, "", message) } } async httpRequest(options) { let t = { ...options }; t.headers = t.headers || {}; if (t.params) { t.url += "?" + this.queryStr(t.params) } t.method = t.method.toLowerCase(); if (t.method === "get") { delete t.headers["Content-Type"]; delete t.headers["Content-Length"]; delete t.headers["content-type"]; delete t.headers["content-length"]; delete t.body } else if (t.method === "post") { let ContentType; if (!t.body) { t.body = "" } else if (typeof t.body === "string") { ContentType = this.isJSONString(t.body) ? "application/json" : "application/x-www-form-urlencoded" } else if (this.isJson(t.body)) { t.body = JSON.stringify(t.body); ContentType = "application/json" } if (!t.headers["Content-Type"] && !t.headers["content-type"]) { t.headers["Content-Type"] = ContentType } } if (this.isNode()) { this.initRequestEnv(t); if (this.requestModule === "axios" && t.method === "post") { t.data = t.body; delete t.body } let httpResult; if (this.requestModule === "got") { httpResult = await this.requset(t); if (this.isJSONString(httpResult.body)) { httpResult.body = JSON.parse(httpResult.body) } } else if (this.requestModule === "axios") { httpResult = await this.requset(t); httpResult.body = httpResult.data } return httpResult } if (this.isQuanX()) { t.method = t.method.toUpperCase(); return new Promise((resolve, reject) => { $task.fetch(t).then((response) => { if (this.isJSONString(response.body)) { response.body = JSON.parse(response.body) } resolve(response) }) }) } } randomNumber(length) { const characters = "0123456789"; return Array.from({ length }, () => characters[Math.floor(Math.random() * characters.length)]).join("") } randomString(length) { const characters = "abcdefghijklmnopqrstuvwxyz0123456789"; return Array.from({ length }, () => characters[Math.floor(Math.random() * characters.length)]).join("") } timeStamp() { return new Date().getTime() } uuid() { return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) { var r = (Math.random() * 16) | 0, v = c == "x" ? r : (r & 0x3) | 0x8; return v.toString(16) }) } time(t) { let s = { "M+": new Date().getMonth() + 1, "d+": new Date().getDate(), "H+": new Date().getHours(), "m+": new Date().getMinutes(), "s+": new Date().getSeconds(), "q+": Math.floor((new Date().getMonth() + 3) / 3), S: new Date().getMilliseconds(), }; /(y+)/.test(t) && (t = t.replace(RegExp.$1, (new Date().getFullYear() + "").substr(4 - RegExp.$1.length))); for (let e in s) new RegExp("(" + e + ")").test(t) && (t = t.replace(RegExp.$1, 1 == RegExp.$1.length ? s[e] : ("00" + s[e]).substr(("" + s[e]).length))); return t } msg(s = t, e = "", i = "", o) { const h = (t) => !t || (!this.isLoon() && this.isSurge()) ? t : "string" == typeof t ? this.isLoon() ? t : this.isQuanX() ? { "open-url": t } : void 0 : "object" == typeof t && (t["open-url"] || t["media-url"]) ? this.isLoon() ? t["open-url"] : this.isQuanX() ? t : void 0 : void 0; this.isMute || (this.isSurge() || this.isLoon() ? $notification.post(s, e, i, h(o)) : this.isQuanX() && $notify(s, e, i, h(o))); let logs = ["", "==============📣系统通知📣=============="]; logs.push(t); e ? logs.push(e) : ""; i ? logs.push(i) : ""; console.log(logs.join("\n")); this.logs = this.logs.concat(logs) } log(...t) { t.length > 0 && (this.logs = [...this.logs, ...t]), console.log(t.join(this.logSeparator)) } logErr(t, s) { const e = !this.isSurge() && !this.isQuanX() && !this.isLoon(); e ? this.log("", `\u2757\ufe0f${this.name},\u9519\u8bef!`, t.stack) : this.log("", `\u2757\ufe0f${this.name},\u9519\u8bef!`, t) } wait(t) { return new Promise((s) => setTimeout(s, t)) } done(t = {}) { const s = new Date().getTime(), e = (s - this.startTime) / 1e3; this.log("", `\ud83d\udd14${this.name},\u7ed3\u675f!\ud83d\udd5b ${e}\u79d2`); this.log(); if (this.isNode()) { process.exit(1) } if (this.isQuanX()) { $done(t) } } })(t, s) }

!(async function () {

    const senderID = await middlleware.getSenderID()
    const sender = new middlleware.Sender(senderID)
    const user = await sender.getUserID()
    let fxsh = new Fxsh(user, sender)
    let message = await sender.getMessage()
    if (message === '粉象登录') {
        await fxsh.addUser()
    }
    if (message === '粉象管理') {
        await fxsh.manageUser()
    }
    if (message === '粉象查询') {
        await fxsh.query()
    }
    if (message === '粉象一键运行') {
        await fxsh.run()
    }
    if (message === '粉象全部提现' || message === '粉象提现') {
        await fxsh.withDrawAll()
    }
    if (message === '粉象授权') {
        await fxsh.adminAuth()
    }
    if (message === "粉象签到") {
        await fxsh.clockSignAlone()
    }
})()