//[create_at: 2026-05-14 17:04:19]
//[title: 短视频图集解析]
//[author: 297129582]
//[version: 1.2.0]
//[class: 影音类]
//[open_source: false]
//[icon: https://bbs.autman.cn/assets/files/2023-12-12/1702408610-992864-favicon.ico]
//[platform: qq,qb,wx,tb,tg,web,wxmp]
//[public: true]
//[price: 1]
//[service: <img src="https://pic.fglt.net/common/a8/common_4_verify_icon.gif" border="0"><b>官方权威认证</b>QQ：297129582 群：<a target="_blank" href="http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=iFQxHXG9uoPF_Mg--CEqAaAwuiOHUxxB&authKey=UBgOgDGMPyqtUzreMqcIsRczdy7KUQas4WiKuHfY%2FE%2B%2BtWophV0XimqByZKJdSiy&noverify=0&group_code=933677015"><font color=blue>933677015</font></a>]
//[description: ❶支持bilibili,小红书,抖音,快手,西瓜,皮皮虾,皮皮搞笑<br>❷图集解析分9张一组发送<br>❸支持QQ/微信小程序分享解析<br>❹重构优化版本，提升稳定性和可维护性<br><span style="color:red">❺</span>增加管理员命令"短视频图集解析"]
//[admin: false]
//[disable:false]
//[priority: 999999999999999999]
//[rule: raw (https?://\S+douyin\.com\/\S+/?)]
//[rule: raw (https?://\S+kuaishou\.com\/\S+/?)]
//[rule: raw (https?:\/\/\S+kuaishou\.com\/\S+/?)]
//[rule: raw (https?://\S+chenzhongtech\.com\/\S+/?)]
//[rule: raw (https?://\S+kuai-fei\.com\/\S+/?)]
//[rule: raw (https?://\S+weibo\.com\/\S+/?)]
//[rule: raw (https://video\.weibo\.com/tv/show\/\S+/?)]
//[rule: raw (https?://\S+weibo\.com/tv/show\/\S+/?)]
//[rule: raw (https?://weibo\.com/tv/show\/\S+/?)]
//[rule: raw (https?://t\.cn/\S+/?)]
//[rule: raw (https?://h5\.pipix\.com/s\/\S+/?)]
//[rule: raw (https?://h5\.pipigx\.com/pp/post\/\S+/?)]
//[rule: raw (https?://\S+ixigua\.com\/\S+/?)]
//[rule: raw (https?://xhslink\.com\/\S+/?)]
//[rule: raw (https?://\S+xiaohongshu\.com\/\S+/?)]
//[rule: raw (https?://\S+bilibili\.com/video\/\S+/?)]
//[rule: raw (https?://b23\.tv\/\S+/?)]
//[rule: raw (https?://bili2233\.cn\/\S+/?)]
//[rule: raw (https?:\\/\\/b23\.tv\\/\S+/?)]
//[rule: ^短视频图集解析$]

//[param: {"required":true,"key":"otto.dsptj_dwz","bool":false,"placeholder":"填入自定义api接口","name":"短链接口","desc":"短链接口<br>1：https://api.suol.cc/v1/dwz_free.php?suol_type=s_url&url=（注意：短链接口只能使用文本输出，不支持JSON输出。）"}]

const axios = require('axios');
const middleware = require('./middleware.js');
const senderID = middleware.getSenderID();
const sender = new middleware.Sender(senderID);

// ==================== 配置常量 ====================
const CONFIG = {
    PLUGIN_NAME: '短视频图集解析',
    VERSION: '1.2.0',
    TIMEOUT: 5000,
    LISTEN_TIMEOUT: { SHORT: 30000, LONG: 120000 },
    DEFAULT_LIMITS: { TOTAL: 66, ONCE: 9, SLEEP: 1000 },
    BUCKET_PREFIX: 'otto',
    API_ENDPOINTS: [
        'http://dsp.jx.cangg.cn/caonima.php?url=',
        'http://dsp1.jx.cangg.cn/caonima.php?url=',
        'http://dsp2.jx.cangg.cn/caonima.php?url='
    ]
};

console.log(`开始解析逻辑`);

// ==================== 平台配置 ====================
const PLATFORM_CONFIG = {
    douyin: {
        name: '抖音',
        patterns: [/https?:\/\/\S+douyin\.com\/\S+/],
        needsShortLink: true
    },
    kuaishou: {
        name: '快手',
        patterns: [
            /https?:\/\/\S+kuaishou\.com\/\S+/,
            /https?:\/\/\S+kuai-fei\.com\/\S+/,
            /https?:\/\/\S+chenzhongtech\.com\/([^"]+)/
        ],
        needsShortLink: true
    },
    bilibili: {
        name: '哔哩哔哩',
        patterns: [
            /https?:\/\/\S+bilibili\.com\/video\/\S+/,
            /https?:\/\/b23\.tv\/[^?]+/,
            /https?:\/\/bili2233\.cn\/\S+/
        ],
        needsShortLink: true,
        videoUrlHandler: 'encode'
    },
    xiaohongshu: {
        name: '小红书',
        patterns: [
            /https?:\/\/xhslink\.com\/\S+/,
            /https?:\/\/\S+xiaohongshu\.com\/[^\s<>"\']+/
        ],
        needsShortLink: true,
        videoUrlHandler: 'encode',
        urlDecoder: true
    },
    pipixia: {
        name: '皮皮虾',
        patterns: [/https?:\/\/\S+pipix\.com\/s\/\S+/],
        needsShortLink: true
    },
    pipigaoxiao: {
        name: '皮皮搞笑',
        patterns: [/https?:\/\/\S+pipigx\.com\/pp\/post\/\S+\?/],
        needsShortLink: true
    },
    ixigua: {
        name: '西瓜视频',
        patterns: [/https?:\/\/\S+ixigua\.com\/\S+/],
        needsShortLink: true
    },
    weibo: {
        name: '微博',
        patterns: [
            /https?:\/\/\S+weibo\.com\/tv\/show\/\d{4}:\d+/,
            /https?:\/\/weibo\.com\/tv\/show\/\d{4}:\d+/,
            /https?:\/\/\S+weibo\.com\/show\?fid=\d{4}:\d+/,
            /https?:\/\/\S+weibo\.com\/show\/\d{4}:\d+/,
            /https?:\/\/t\.cn\/\S+/
        ],
        needsShortLink: true,
        videoUrlHandler: 'encode'
    }
};

// ==================== 存储管理器 ====================
class StorageManager {
    constructor(bucketPrefix) {
        this.prefix = bucketPrefix;
    }

    getKey(type, id) {
        return `${type}${id}`;
    }

    async get(type, id) {
        const key = this.getKey(type, id);
        return await middleware.get(key);
    }

    async set(type, id, value) {
        const key = this.getKey(type, id);
        await middleware.bucketSet(this.prefix, key, value);
    }

    async getGlobal(key) {
        return await middleware.get(key);
    }

    async setGlobal(key, value) {
        await middleware.bucketSet(this.prefix, key, value);
    }

    async getLimits() {
        const [total, once, sleep] = await Promise.all([
            middleware.get("sendCosImgTotleLimit"),
            middleware.get("sendCosImgOnceLimit"),
            middleware.get("sendCosImgOnceSleep")
        ]);
        return {
            total: parseInt(total) || CONFIG.DEFAULT_LIMITS.TOTAL,
            once: parseInt(once) || CONFIG.DEFAULT_LIMITS.ONCE,
            sleep: parseInt(sleep) || CONFIG.DEFAULT_LIMITS.SLEEP
        };
    }
}

// ==================== URL处理器 ====================
class URLProcessor {
    static extractUrl(content, patterns) {
        for (const pattern of patterns) {
            const match = content.match(pattern);
            if (match) {
                return match[0]?.match(/^https?:\/\/[^"]+/)?.[0] || null;
            }
        }
        return null;
    }

    static decodeHtmlEntities(str) {
        const entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'"
        };

        return str.replace(/&#(\d+);|&#x([a-fA-F0-9]+);|&([a-zA-Z0-9]+);/g, (match, dec, hex, named) => {
            if (dec) return String.fromCharCode(parseInt(dec, 10));
            if (hex) return String.fromCharCode(parseInt(hex, 16));
            return entities[match] || match;
        });
    }

    static cleanUrl(url) {
        return url.replace(/\\/g, '');
    }
}

// ==================== 时间格式化工具 ====================
class TimeFormatter {
    static formatTimestamp(timestamp) {
        if (!timestamp) return '';
        const ts = timestamp.toString().length === 10 ? timestamp * 1000 : timestamp;
        const date = new Date(ts);
        const pad = (n) => ("0" + n).slice(-2);
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
    }
}

// ==================== API服务 ====================
class APIService {
    constructor(endpoints, timeout) {
        this.endpoints = endpoints;
        this.timeout = timeout;
    }

    async fetchWithFallback(url) {
        const cleanUrl = URLProcessor.cleanUrl(url);

        for (const endpoint of this.endpoints) {
            try {
                console.log(`尝试API: ${endpoint}`);
                const response = await axios.get(`${endpoint}${cleanUrl}`, {
                    timeout: this.timeout,
                    validateStatus: (status) => status < 500
                });

                if (response.data && response.data.code !== undefined) {
                    console.log(`API请求成功: ${endpoint}`);
                    return response.data;
                }
            } catch (error) {
                console.log(`API请求失败: ${endpoint}`, error.message);
            }
        }

        console.log(`所有API端点请求失败`);
        return null;
    }

    async generateShortLink(apiUrl, targetUrl) {
        if (!targetUrl) return '';
        if (!apiUrl) return targetUrl;

        try {
            const response = await axios.get(`${apiUrl}${targetUrl}`, { timeout: this.timeout });
            return response.data || targetUrl;
        } catch (error) {
            console.log(`短链接生成失败`, error.message);
            return targetUrl;
        }
    }
}

// ==================== 消息构建器 ====================
class MessageBuilder {
    constructor(shortLinkService) {
        this.shortLinkService = shortLinkService;
    }

    async buildInfoMessage(data) {
        const lines = [`▁▂【${data.name}${data.type}】▂▁`];

        if (data.cover) lines.push(`[CQ:image,file=${data.cover}]`);
        if (data.author) lines.push(`🗣️作者:${data.author}`);
        if (data.uid) lines.push(`🆔UID:${data.uid}`);
        if (data.title) lines.push(`📝标题:${data.title}`);

        const stats = [];
        if (data.like) stats.push(`👍点赞:${data.like}`);
        if (data.comment) stats.push(`💬评论:${data.comment}`);
        if (stats.length) lines.push(stats.join('\t'));

        const moreStats = [];
        if (data.collect) moreStats.push(`⭐收藏:${data.collect}`);
        if (data.share) moreStats.push(`🔄分享:${data.share}`);
        if (moreStats.length) lines.push(moreStats.join('\t'));

        if (data.time) lines.push(`🕐发布:${TimeFormatter.formatTimestamp(data.time)}`);

        // 异步并行生成短链接
        const shortLinks = await Promise.all([
            this.shortLinkService(data.cover),
            this.shortLinkService(data.avatar),
            this.shortLinkService(data.music),
            this.shortLinkService(data.url)
        ]);

        if (shortLinks[0]) lines.push(`🌄封面:${shortLinks[0]}`);
        if (shortLinks[1]) lines.push(`👤头像:${shortLinks[1]}`);
        if (shortLinks[2]) lines.push(`🎵音频:${shortLinks[2]}`);
        if (shortLinks[3]) lines.push(`🎬视频:${shortLinks[3]}`);

        return lines.join('\n');
    }

    async getVideoUrl(data, imType, shortLinkService) {
        const { name, type, url, url1, url2 } = data;

        if (type !== '视频') return null;

        // 注意：name 匹配要用 API 返回的实际值
        switch (name) {
            case '抖音':
                // replyVideo 用无水印链接，文案展示用短链
                return imType === 'wx' ? url2 : url1;
            case '哔哩':
            case '微博':
            case '小红书':
                // 这些平台 replyVideo 也用短链
                return await shortLinkService(encodeURIComponent(url));
            default:
                // 其他平台直接用原链接
                return url;
        }
    }
}

// ==================== 图集发送器 ====================
class PhotoSender {
    constructor(sender, storage) {
        this.sender = sender;
        this.storage = storage;
    }

    async send(photoUrls, platformName, imType, shortLinkService) {
        console.log(`开始发送图集`, { count: photoUrls.length, platform: platformName });

        const limits = await this.storage.getLimits();
        const urls = photoUrls.slice(0, limits.total);

        const batches = this.createBatches(urls, limits.once);

        for (let i = 0; i < batches.length; i++) {
            const batch = batches[i];
            const message = await this.buildBatchMessage(batch, platformName, imType, shortLinkService);
            await this.sender.reply(message);

            if (i < batches.length - 1) {
                await this.sleep(limits.sleep);
            }
        }

        console.log(`图集发送完成`);
    }

    createBatches(arr, size) {
        const batches = [];
        for (let i = 0; i < arr.length; i += size) {
            batches.push(arr.slice(i, i + size));
        }
        return batches;
    }

    async buildBatchMessage(urls, platformName, imType, shortLinkService) {
        const isWxDouyin = imType === 'wx' && platformName === '抖音';
        const isWxPipixia = imType === 'wx' && platformName === '皮皮虾';

        const imageTags = await Promise.all(
            urls.map(async (url) => {
                if (isWxDouyin || isWxPipixia) {
                    const shortUrl = await shortLinkService(encodeURIComponent(url));
                    return `[CQ:image,file=${shortUrl}]`;
                }
                return `[CQ:image,file=${url}]`;
            })
        );

        return imageTags.join('');
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// ==================== 管理员处理器 ====================
class AdminHandler {
    constructor(sender, storage) {
        this.sender = sender;
        this.storage = storage;
    }

    async handle() {
        const isAdmin = await this.sender.isAdmin();
        if (!isAdmin) return false;

        const [wenan, benqun] = await Promise.all([
            this.storage.get('dspWA', await this.sender.getChatID()),
            this.storage.get('dspBQ', await this.sender.getChatID())
        ]);

        await this.showMenu(wenan, benqun);
        await this.handleSelection(wenan, benqun);
        return true;
    }

    async showMenu(wenan, benqun) {
        const menu = [
            `◇—短视频图集解析设置—◇`,
            `1.开/关本群解析[${benqun || 'false'}]`,
            `2.开/关文案[${wenan || 'false'}]`,
            `3.设置你的短链`,
            `回复编号设置`,
            `版本(${CONFIG.VERSION})`
        ].join('\n');

        await this.sender.reply(menu);
    }

    async handleSelection(currentWenan, currentBenqun) {
        const chatId = await this.sender.getChatID();
        const number = await this.sender.listen(CONFIG.LISTEN_TIMEOUT.SHORT);

        switch (number) {
            case '1':
                const newBenqun = !currentBenqun || currentBenqun === 'false' ? 'true' : 'false';
                await this.storage.set('dspBQ', chatId, newBenqun);
                await this.sender.reply(newBenqun === 'true' ? '本群已开启' : '本群已关闭');
                break;

            case '2':
                const newWenan = !currentWenan || currentWenan === 'false' ? 'true' : 'false';
                await this.storage.set('dspWA', chatId, newWenan);
                await this.sender.reply(newWenan === 'true' ? '文案已开启' : '文案已关闭');
                break;

            case '3':
                await this.sender.reply('请在2分钟内输入你的短链接口:');
                const sourl = await this.sender.listen(CONFIG.LISTEN_TIMEOUT.LONG);
                await this.storage.setGlobal('dsptj_dwz', sourl);
                await this.sender.reply('短网址已经设置完毕');
                break;
        }
    }
}

// ==================== 内容处理器 ====================
class ContentProcessor {
    constructor(sender, storage, apiService) {
        this.sender = sender;
        this.storage = storage;
        this.apiService = apiService;
        this.messageBuilder = new MessageBuilder(this.getShortLinkService());
        this.photoSender = new PhotoSender(sender, storage);
    }

    getShortLinkService() {
        return async (url) => {
            const shortUrlApi = await this.storage.getGlobal('dsptj_dwz');
            return this.apiService.generateShortLink(shortUrlApi, url);
        };
    }

    async shouldProcess(chatId) {
        const benqun = await this.storage.get('dspBQ', chatId);
        return benqun === 'true';
    }

    async process(url, platformConfig) {
        const wenan = await this.storage.get('dspWA', await this.sender.getChatID());
        const shortUrlApi = await this.storage.getGlobal('dsptj_dwz');

        if (wenan === 'true' && !shortUrlApi) {
            await this.sender.reply('您开启了发送文案，需要用到短网址。\n请后台打开配参，配置短网址api');
            return;
        }

        const messageId = await this.sender.getMessageID();
        await this.sender.recallMessage(messageId);

        const loadingMsg = wenan === 'true' ? await this.sender.reply('马上就来,请稍等哦!') : null;

        try {
            const data = await this.apiService.fetchWithFallback(url);

            if (!data) {
                await this.handleError(loadingMsg, '网络堵塞，请稍后再试。');
                return;
            }

            if (data.code !== 200 || !data.url) {
                await this.handleError(loadingMsg, data.msg || '解析失败，视频不存在或接口失效');
                return;
            }

            if (loadingMsg) {
                await this.sender.recallMessage(loadingMsg);
            }

            await this.handleSuccess(data, wenan, platformConfig);

        } catch (error) {
            console.log(`处理内容时出错`, error);
            await this.handleError(loadingMsg, '处理过程中发生错误');
        }
    }

    async handleSuccess(data, wenan, platformConfig) {
        const imType = await this.sender.getImtype();

        if (wenan === 'true') {
            const infoMessage = await this.messageBuilder.buildInfoMessage(data);
            await this.sender.reply(infoMessage);

            const videoUrl = await this.messageBuilder.getVideoUrl(data, imType, this.getShortLinkService());

            if (data.type === '视频') {
                await this.sender.replyVideo(videoUrl);
            } else {
                await this.photoSender.send(data.url, data.name, imType, this.getShortLinkService());
            }
        } else {
            if (data.type === '视频') {
                const videoUrl = await this.messageBuilder.getVideoUrl(data, imType, this.getShortLinkService());
                await this.sender.replyVideo(videoUrl);
            } else {
                await this.photoSender.send(data.url, data.name, imType, this.getShortLinkService());
            }
        }
    }

    async handleError(loadingMsg, errorMessage) {
        if (loadingMsg) {
            await this.sender.recallMessage(loadingMsg);
        }
        const errorReply = await this.sender.reply(errorMessage);

        if (errorMessage.includes('网络堵塞')) {
            await this.sleep(5000);
            await this.sender.recallMessage(errorReply);
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// ==================== 主程序 ====================
async function main() {
    console.log(`插件启动, senderID:`, senderID);

    try {
        const storage = new StorageManager(CONFIG.BUCKET_PREFIX);
        const apiService = new APIService(CONFIG.API_ENDPOINTS, CONFIG.TIMEOUT);

        // 获取基本信息
        const [userId, chatId, messageId, content, imType] = await Promise.all([
            sender.getUserID(),
            sender.getChatID(),
            sender.getMessageID(),
            sender.getMessage(),
            sender.getImtype()
        ]);

        console.log(`收到消息`, { userId, chatId, content: content?.substring(0, 50) });

        // 处理管理员命令
        if (content === '短视频图集解析') {
            const adminHandler = new AdminHandler(sender, storage);
            const handled = await adminHandler.handle();
            if (handled) return;
        }

        // 查找匹配的平台
        const platformEntry = Object.entries(PLATFORM_CONFIG).find(([key, config]) => {
            return content.includes(key) || config.patterns.some(p => p.test(content));
        });

        if (!platformEntry) {
            console.log(`未匹配到任何平台`);
            return;
        }

        const [platformKey, platformConfig] = platformEntry;
        console.log(`匹配到平台`, { platform: platformConfig.name });

        // 检查是否应该处理
        const shouldProcess = await new ContentProcessor(sender, storage, apiService).shouldProcess(chatId);
        if (!shouldProcess) {
            console.log(`本群解析功能未开启`);
            return;
        }

        // 提取URL
        let url = URLProcessor.extractUrl(content, platformConfig.patterns);

        if (!url) {
            console.log(`URL提取失败`);
            return;
        }

        // 处理需要解码的平台
        if (platformConfig.urlDecoder) {
            url = URLProcessor.decodeHtmlEntities(url);
            url = encodeURIComponent(url);
        }

        console.log(`开始解析`, { url: url.substring(0, 100) });

        // 处理内容
        const processor = new ContentProcessor(sender, storage, apiService);
        await processor.process(url, platformConfig);

    } catch (error) {
        console.log(`主程序执行失败`, error);
        try {
            await sender.reply(`插件出错: ${error.message}`);
        } catch (e) {
            console.log(`发送错误消息失败`, e);
        }
    }
}

// 启动
main().catch(err => {
    console.log(`未捕获的错误`, err);
});
