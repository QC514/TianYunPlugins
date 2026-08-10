//[author: funyhook]
//[create_at: 2023-11-03 16:22:02]
//[version: 10]
//[title: 开卡监控pro]
//[description:  更新：新增支持监控库</br>支持自设置自动运行脚本！发送开卡监控配置 多容器监控！支持2.10以上所有版本青龙！！！<br/>命令：开卡监控，开卡监控配置<br/>申请Github token 教程：https://blog.csdn.net/qq_33568108/article/details/130744526<br/>]
//[platform: qq,wx,tg]
//[public: true]
//[icon: https://bbs.autman.cn/assets/files/2023-11-30/1701333388-893523-c1e62f9d-377a-4afd-950f-9295d95e921a.png]
//[service:<a href="https://ti.qq.com/open_qq/index2.html?url=mqqapi%3A%2F%2Fuserprofile%2Ffriend_profile_card%3Fsrc_type%3Dweb%26version%3D1.0%26source%3D2%26uin%3D635723451" target="_black">点击联系我</a>]
//[price: 0.5]
//[icon: https://vhook.cn/img/mini.png]
//[rule: kk]
//[rule: ^开卡监控$]
//[rule: ^kkjk$]
//[rule: 开卡监控配置]
//[priority: 9999]优先级
//[cron: */10 * * * *]每5分钟运行一次
//[disable: false]
//[admin: true ]
//==========================参数配置数据（最下面）===============================


let enum_gits = [
    "9Rebels/jdmax.git",
    "feverrun/my_scripts.git",
    "HarbourJ/HarbourToulu.git",
    "smiek2121/scripts.git",
    "shufflewzc/faker3.git",
    "walle1798/WALL.E.git",
    "6dylan6/jdpro.git",
    "/walle1798/EVE.git"
]
const run_script_prefix = ["open", "dplh", "jd_card"]
const plugin_key_pre = `kkjk_`

const plugin_name = `【${getTitle()}】`
const imType = ImType() === "cron" ? "fake" : ImType();
const timestemp = new Date().getTime();
const userId = GetUserID();
const chatId = GetChatID();
const aut_ver = call("version")()["sn"]//获取当前系统版本
const qls = get_ql_list()
function get_ql_list(){
    console.log(aut_ver)
    if (aut_ver>"2.6.5"){
        console.log("qls")
        qls_arr = []
        qls_id_arr = bucketAllKeys("qls")
        if(!qls_id_arr || qls_id_arr.length==0){
           return qls_arr
        }
        qls_id_arr.forEach(item => {
            qls_arr.push(JSON.parse(bucketGet("qls",item)))
        });
        return qls_arr;
    }else{
        return JSON.parse(bucketGet("qinglong", "QLS"));
    }

}

//加载配置
function openCardConfig() {
    let i, content, names = [], title = [];
    let github_token = get("github_token");
    let openCard_ql_list = get("opencard_qls")
    if (!openCard_ql_list) {
        content = `${plugin_name}：未配置青龙容器，请发送“青龙管理”指令，配置青龙容器！`
        if (!qls) {
            return ImType() === "fake" ? notifyMasters(content) : sendText(content)
        }
        for (i = 0; i < qls.length; i++) {
            ql_json = qls[i]
            names.push(i + 1 + ". " + ql_json[i].name)
        }
        sendText(`${plugin_name}：请在【60秒】内青龙容器名称（多个容器名称，请用英文逗号分割）:\n${names.join("\\n")}`);
        const container = input(60000);
        if (!container || container === "q") {
            return sendText(`${plugin_name}：输入有误, 请重新发送“开卡监控”指令！`);
        }
        set("opencard_qls", container)
        for (i = 0; i < enum_gits.length; i++) {
            title[i] = (i + 1).toString() + " " + enum_gits[i]
        }
        sendText(`${plugin_name}：请在【60秒】内选择开卡监控仓库对应序号，（多个序号，请用英文逗号分割）：\n${title.join("\\n")}`)
        let repoNo = input(60000)
        if (!repoNo || repoNo === "q") {
            return sendText(`${plugin_name}：输入有误, 请重新发送“开卡监控”指令！`);
        }
        let opencard_gits = []
        for (i = 0; i < repoNo.split(",").length; i++) {
            opencard_gits.push(enum_gits[repoNo.split(",")[i] - 1])
        }
        set("opencard_gits", opencard_gits.join(","))
        sendText(`${plugin_name}：请在【60秒】内输入 github_token\n教程:https://blog.csdn.net/qq_33568108/article/details/130744526`);
        const token = input(30000);
        if (!token || token === "q") {
            return sendText(`${plugin_name}：输入有误，已退出！`);
        }
        set("github_token", token)
        return sendText(`${plugin_name}：设置成功，默认只监控【opencard】和【大牌联合】类开卡脚本！请重新发送“开卡监控”指令测试`)
    } else {
        
        let ql_cofig = qls
        let opencardArr = openCard_ql_list.split(",");
        ql_cofig = ql_cofig.filter(o => opencardArr.includes(o.name));
        if (ql_cofig.length === 0) {
            content = `${plugin_name}：监控容器配置不正确，请重新配置：set otto opencard_qls 青龙容器备注，多个容器请用英文逗号分隔`
            if (ImType() !== "fake") {
                return sendText(content)
            }
        }
        const repos = get("opencard_gits").split(",");
        for (i = 0; i < repos.length; i++) {
            const repo = repos[i];
            sleep(1000)
            ql_cofig.forEach(ql => {
                getGitTreeLog(repo, github_token, ql);
            })
        }
    }

}

function editConfig() {
    let opencard_qls = get("opencard_qls")
    let opencard_gits = get("opencard_gits")
    let github_token = get("github_token")
    let opencard_auto_words = get("opencard_auto_words")
    let content = `请输入数字序号编辑:`
    content += `\n1、【监控容器】：${opencard_qls}`
    content += `\n2、【监控仓库】：${opencard_gits}`
    content += `\n3、【github_token】：${github_token}`
    content += `\n4、【自动运行脚本关键字】：${opencard_auto_words}`
    sendText(content);
    const p = input(30000)
    if (!p || p === "q") {
        return sendText(`${plugin_name}：已退出`)
    }
    switch (p["0"]) {
        case "1":
            let names = []
            for (let i = 0; i < qls.length; i++) {
                ql_json = qls[i]
                names.push(i + 1 + "、 " +ql_json.name)
            }
            sendText(`${plugin_name}：请在【60秒】内青龙容器名称（多个容器名称，请用英文逗号分割）:\n${names.join("\\n")}`);
            const container = input(60000);
            if (!container || container === "q") {
                return sendText(`${plugin_name}：输入有误, 请重新发送“开卡监控”指令！`);
            }
            set("opencard_qls", container)
            editConfig()
            break;
        case "2":
            let title = []
            for (let i = 0; i < enum_gits.length; i++) {
                title[i] = (i + 1).toString() + "、 " + enum_gits[i]
            }
            sendText(`${plugin_name}：请在【60秒】内选择开卡监控仓库对应序号，（多个序号，请用英文逗号分割）：\n${title.join("\\n")}`)
            let repoNo = input(60000)
            if (!repoNo || repoNo === "q") {
                return sendText(`${plugin_name}：输入有误, 请重新发送“开卡监控”指令！`);
            }
            let gits = []
            for (let i = 0; i < repoNo.split(",").length; i++) {
                let gits_num = repoNo.split(",")[i]
                gits.push(enum_gits[gits_num - 1])
            }
            set("opencard_gits", gits.join(","))
            editConfig()
            break;
        case "3":
            sendText(`${plugin_name}：请在【60秒】内输入 github_token\n教程:https://blog.csdn.net/qq_33568108/article/details/130744526`);
            const token = input(60000);
            if (!token || token === "q") {
                return sendText(`${plugin_name}：输入有误，已退出！`);
            }
            set("github_token", token)
            editConfig()
            break;
        case "4":
            sendText(`${plugin_name}：请在【60秒】内输入自动运行脚本关键字，多个用英文都好分割；若默认全部开卡，请发送指令 delete otto opencard_auto_words`);
            const auto_words = input(60000);
            if (!auto_words || auto_words === "q") {
                return sendText(`${plugin_name}：输入有误，已退出！`);
            }
            set("opencard_auto_words", auto_words)
            editConfig()
            break;
        default:
            editConfig()
            break;
    }
}

//获取github仓库日志
function getGitTreeLog(repo, github_token, ql) {
    let new_script_name_arr = []
    let repoHost = repo.replace(".", "/");
    let branch = "main";
    switch (repo) {
        case "KingRan/KR.git":
            branch = "main";
            break;
        case "feverrun/my_scripts.git":
            branch = "main";
            break;
        case "HarbourJ/HarbourToulu.git":
            branch = "main";
            break;
        case "smiek2121/scripts.git":
            branch = "master";
            break;
        case "shufflewzc/faker3.git":
            branch = "main";
            break;
        case "walle1798/WALL.E.git":
            branch = "master";
            repoHost = "walle1798/WALL.E/git";
            break;
        case "6dylan6/jdpro.git":
            branch = "main";
            break;
        default:
            break;
    }
    // try {
        console.log(`https://api.github.com/repos/${repoHost}/trees/${branch}`)
        let response = request({
            // 内置http请求函数
            url: `https://api.github.com/repos/${repoHost}/trees/${branch}`, //请求链接
            method: "get", //请求方法
            dataType: "json", //这里接口直接返回文本，所以不需要指定json类型数据
            headers: {
                "User-Agent": " Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML: like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
                'Content-Type': `application/json`,
                'Authorization': `Bearer ${github_token}`
            },
        });
        console.log(JSON.stringify(response))
        if (response && response.tree) {
            let tree = response.tree
            if (!tree) {
                return notifyMasters(`${plugin_name}\n【tarce_ID】：${timestemp}:【容器】：${ql.name}\n【仓库】：${repo}\n,获取仓库日志失败，请确认是否配置github_token`)
            }

            for (let i = 0; i < tree.length; i++) {
                const script_name = tree[i];

                let cacheRepoKey = repo.split("/")[0]
                const path = bucketGet(cacheRepoKey, script_name.path + "_" + ql.name);
                if (path) {
                    continue;
                }
                new_script_name_arr.push(script_name.path)
            }
            if (new_script_name_arr.length > 0) {
                let content = `====${plugin_name}新脚本提醒====\n【容器】：${ql.name}\n【仓库】：${repo}\n【新脚本】：${new_script_name_arr.join("\n")}`
                push_msg(content)
                pull_low_ver(repo, ql, new_script_name_arr)
            } else {
                let content = `${plugin_name} :【tarce_ID】：${timestemp} 【容器】：${ql.name} 【仓库】：${repo} 【新脚本】:无`
                console.log(content)
                sendText(`=====${plugin_name}====\n【容器】：${ql.name}\n【仓库】：${repo}\n【新脚本】：无`)
            }
        }
    // } catch (e) {
    //     console.error(e)
    //     notifyMasters(`${plugin_name}\n【tarce_ID】：${timestemp}:\n【容器】：${ql.name}\n【仓库】：${repo}\n【异常】：${e.message}`)
    // }
}

function pull_low_ver(repo, q, new_script_name_arr) {
    const name = q.name;
    const host = q.host;
    const client_id = q.client_id;
    const client_secret = q.client_secret;
    let api = 'crons'
    //定义青龙对象
    let ql = Qinglong(host, client_id, client_secret)
    console.log(ql.token)
    //判断青龙版本 拉库/订阅
    let verRes = ql.ApiQL("system", "?t=" + Date.now(), "get")
    console.log(`${plugin_name}:【system】: 当前容器：【` + name + "】版本查询结果 " + JSON.stringify(verRes))
    if (verRes.code === 401) {
        let verUrl = host + "/open/auth/token?client_id=" + client_id + "&client_secret=" + client_secret
        return sendText("【开卡监控pro】：【system】：当前容器：【" + name + "】版本\n发生错误：请点击地址核对是否可以查询到版本号：" + verUrl);
    }
    if (verRes.data.version >= "2.13.0") {
        api = 'subscriptions'
    }
    //查询订阅
    let subRes = ql.ApiQL(api, "?searchValue=" + repo + "&t=" + Date.now(), "get")
    console.log(`${plugin_name}:【subscriptions】: 当前容器：【` + name + "】查询是否存在仓库：" + repo + "\n 返回结果" + JSON.stringify(subRes))
    if (subRes.code !== 200 || subRes.data.length === 0) {
        return sendText(`${plugin_name}：容器：${name},拉库${repo}失败,请查看对应仓库是否存在？已自动跳过\n错误信息:${JSON.stringify(subRes)}`)
    }
    //获取拉库订阅任务id 找到想要运行的订阅
    let subCron = subRes.data[0];
    if (subCron.status === 0) {
        return sendText(`${plugin_name}：容器：${name}:仓库：${repo},拉库运行中，请稍后...`);
    }
    if (!subCron.id) {
        if (subCron._id) {
            subCron.id = subCron._id
        } else {
            return sendText(`${plugin_name}：容器：${name}:仓库：${repo},拉库失败，请查看对应仓库是否存在？已自动跳过`);
        }
    }
    sendText(`${plugin_name}：容器：${name}:仓库：${repo},开始拉取最新脚本，请稍后...`);
    //运行订阅任务
    let runSubTask = ql.ApiQL(api, "/run?t=" + Date.now(), "put", [subCron.id])
    console.log(`${plugin_name}：容器：${name}:仓库：${repo},开始运行拉库订阅${subCron.id}，运行结果->${runSubTask.code === 200 ? "成功" : JSON.stringify(runSubTask)}`);
    if (runSubTask.code !== 200) {
        sendText(`${plugin_name}：容器：${name}:仓库：${repo},开始运行拉库订阅${subCron.id}，运行失败->${JSON.stringify(runSubTask)}`);
        return
    }
    //等待订阅运行完成
    while (true) {
        const q = input(3000)
        if (q && q === "q") {
            return sendText(`${plugin_name}：已退出`)
        }
        console.log(`${plugin_name}：容器：${name}:仓库：${repo},拉取最新脚本中，请稍后...`);
        let isFree = false
        subRes = ql.ApiQL(api, "?searchValue=" + repo + "&t=" + Date.now(), "get")
        for (let j = 0; j < subRes.data.length; j++) {
            if (subRes.data[j].id === subCron.id || subRes.data[j]._id === subCron.id) {
                if (subRes.data[j].status === 1) { //空闲状态
                    isFree = true
                    break
                }
            }
        }
        if (isFree) {
            break
        }
    }
    //查询订阅运行结果
    let subcrLog = ql.ApiQL(api, "/" + subCron.id + "/log?t=" + Date.now(), "get")
    if (subcrLog.code !== 200) {
        return
    }
    let log = subcrLog.data
    console.log(`${plugin_name}：容器：${name}:仓库：${repo},拉库日志：${log}`);
    reg = /检测到有新的定时任务/g
    let err_reg = /失败，请检查网络/g
    if (log.match(err_reg)) {
        let content = `${plugin_name}：容器：${name}:仓库：${repo},拉库失败：${log}`
        return imType === "fake" ? notifyMasters(content) : sendText(content)
    }
    if (!log.match(reg)) {
        for (const newScript of new_script_name_arr) {
            bucketSet(repo.split("/")[0], newScript + "_" + name, 1);
        }
        let content = `${plugin_name}：容器：${name}:仓库：${repo},拉库后未发现新脚本，跳过！`;
        push_msg(content)
        return
    }
    for (const newScript of new_script_name_arr) {
        console.log(`${plugin_name}：容器：${name}:仓库：${repo},新脚本：${newScript}`);
        if (log.indexOf(newScript) <= 0) {
            continue;
        }
        //查询新脚本任务id
        let crons = ql.cronsGet(newScript)
        console.log(`${plugin_name}：容器：${name}:仓库：${repo},新脚本查询结果：${JSON.stringify(crons)}`)
        if (crons.code !== 200) {
            continue;
        }
        bucketSet(repo.split("/")[0], newScript + "_" + name, 1);
        let cronTasks = [];
        if (crons.data.data) {
            cronTasks = crons.data.data
        } else {
            cronTasks = crons.data
        }
        if (!cronTasks || cronTasks.length <= 0) {
            continue;
        }
        let cronTask = cronTasks[0];
        if (!cronTask.id) cronTask.id = cronTask._id
        console.log(`${plugin_name}：容器：${name}:仓库：${repo},运行禁用新脚本：${newScript}`)
        //自动禁用
        let task_disable_res = ql.cronsDisable([cronTask.id])
        console.log(`${plugin_name}：【禁用新任务】容器： ${name} "脚本：${newScript}，是否已禁用->${task_disable_res.code === 200}`)
        let auto_words = get(`opencard_auto_words`)
        if (auto_words && auto_words !== "") {
            let auto_words_arr = auto_words.split(",")
            if (auto_words_arr.length > 0) {
                if (!auto_words_arr.some(item => newScript.includes(item))) {
                    let content = `====${plugin_name}-新脚本禁用====`
                    content+=`\n【容器】： ${name} ` 
                    content+=`\n【新脚本】：${newScript}`
                    content+=`\n【提示🔔】：非制定运行脚本，自动禁用，放弃运行！`
                    console.log(content)
                    push_msg(content)
                    continue;
                }
            }
        }

        let task_run_res = ql.cronsRun([cronTask.id])
        if (task_run_res.code !== 200) {
            console.log(`${plugin_name}：【容器】：${name} 【仓库】：${repo}:运行新任务：${newScript}-${cronTask.name}失败，请手动运行！`)
            let content = `====${plugin_name}-新脚本运行====`
            content+=`\n【容器】： ${name} ` 
            content+=`\n【仓库】： ${repo} ` 
            content+=`\n【新脚本】：${cronTask.name}`
            content+=`\n【提示】：❌运行失败，请手动运行！`
            push_msg(content)
            continue;
        }
        let content = `====${plugin_name}-新脚本运行====`
        content+=`\n【容器】： ${name} ` 
        content+=`\n【仓库】： ${repo} ` 
        content+=`\n【新脚本】：${cronTask.name}`
        content+=`\n【提示】：✅运行成功！`
        push_msg(content)
    }
}

function pushToGroups(content) {
    let pushGroups = get("opencard_push_groups")
    if (pushGroups) {
        Debug(pushGroups)
        let pgs = pushGroups.split(",")
        for (let i = 0; i < pgs.length; i++) {
            Debug(pgs[i].slice(0, 2))
            Debug(pgs[i].slice(8))
            push({
                imType: pgs[i].slice(0, 2),
                groupCode: pgs[i].slice(8),
                content: content,
            })
        }
    }
}

function push_msg(content){
    ImType() === "fake" ? notifyMasters(content) : sendText(content)
    pushToGroups(content)
}

function check_denpcy(plugin){
    try {
        if(aut_ver>"2.6.5" && get("env") !== "dev"){
            plugin = `funyhook:${plugin}`
        }
        importJs(plugin)
    } catch (e) {
        let content = `${getTitle()}请检查是否安装以下依赖插件：`
        content += `\n【${plugin}】`
        content += `\n请前往autman面板-市场管理-应用市场-【funyhook】-安装缺失插件`
        console.log(content)
        throw new Error(content)
    }
}

function main() {
    check_denpcy("hook.js")
   
    if (imType === "fake" || GetContent() === "kk") {
        console.log(`${plugin_name}：【tarce_ID】：${timestemp}：定时运行中...`)
        openCardConfig(); //加载开卡监控

    }
    if (GetContent() === "开卡监控配置") {
        editConfig()
    }
    if (GetContent() === "开卡监控" || GetContent() === "kkjk") {
        sendText(`${plugin_name}：手动监控开启，请稍等...`)
        openCardConfig(); //加载开卡监控
    }
}

main()
