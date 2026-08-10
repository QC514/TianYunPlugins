//[create_at: 2025-10-15 10:57:41]
//[author: XiaoBo_]
// [title: 实时天气]
// [language: es5]
// [icon: https://img.icons8.com/fluency/96/sun.png]
// [version: 2.0.0]
// [class: 生活类]
// [platform: qq,qb,wx,tb,tg,web]
// [price: 0.2]
// [service: 使用问题请联系邮箱：aboutnanbo@163.com  QQ群：753669173]
// [description: 天气查询插件，基于 60s API 的天气查询插件，支持实时天气查询、空气质量、日出日落时间、生活指数等详细功能。数据来自官方/权威源头，确保稳定与实时。QQ平台自动显示emoji图标。使用命令：天气 / 今天天气 - 查询默认城市详细天气，上海天气 / 北京天气 - 查询指定城市详细天气。配置说明：可在参数中设置"默认城市"，如设置为"上海"，则"天气"指令会查询上海天气，指令中的城市名会覆盖默认城市设置。数据来源：60s API，官方权威数据，稳定实时。]

// [rule: ^(天气|今天天气)$]
// [rule: ^(.+)(天气)$]
// [admin: false]
// [disable: false]
// [priority: 10]

// [param: {"required":false,"key":"weather.apiUrl","bool":false,"placeholder":"https://60s.192.168.5.11/v2/weather","name":"API地址","desc":"天气API接口地址，默认使用官方接口"}]
// [param: {"required":false,"key":"weather.timeout","bool":false,"placeholder":"10000","name":"请求超时(毫秒)","desc":"API请求超时时间，单位毫秒，默认10000"}]
// [param: {"required":false,"key":"weather.default_city","bool":false,"placeholder":"北京","name":"默认城市","desc":"设置默认查询的城市名称，如：北京、上海、广州等。留空则使用API默认城市"}]

// ===== 配置区域 =====
const USE_EMOJI = ImType() != "wx"; 
const API_URL = bucketGet("weather", "apiUrl") || "https://60s.aboutnb.com/v2/weather"; // 天气 API 地址
const TIMEOUT = parseInt(bucketGet("weather", "timeout") || "10000"); // 请求超时时间（毫秒）
const DEFAULT_CITY = bucketGet("weather", "default_city") || ""; // 默认城市，留空则使用API默认

// ===== 主函数 =====
function main() {
    const content = GetContent(); // 获取用户消息
    const userInput = content.trim();

    // 匹配命令：天气 / 今天天气（查询详细天气）
    if (userInput === "天气" || userInput === "今天天气") {
        queryWeather(DEFAULT_CITY || null); // 查询详细天气，使用默认城市
        return;
    }

    // 匹配命令：城市名+天气（如：上海天气、北京天气）
    const cityWeatherMatch = userInput.match(/^(.+)天气$/);
    if (cityWeatherMatch) {
        const cityName = cityWeatherMatch[1].trim();
        if (cityName && cityName !== "今天") {
            queryWeather(cityName); // 查询指定城市的详细天气
            return;
        }
    }
}

// ===== 查询天气函数 =====
function queryWeather(cityName) {
    // 构建请求URL
    let requestUrl = API_URL;
    if (cityName) {
        // 如果指定了城市名称，添加query参数
        requestUrl += "?query=" + encodeURIComponent(cityName);
    }

    // 发送请求提示
    if (USE_EMOJI) {
        if (cityName) {
            sendText("🔍 正在查询 " + cityName + " 的天气信息...");
        } else {
            sendText("🔍 正在查询天气信息...");
        }
    } else {
        if (cityName) {
            sendText("正在查询 " + cityName + " 的天气信息...");
        } else {
            sendText("正在查询天气信息...");
        }
    }

    // 发起网络请求
    request({
        url: requestUrl,
        method: "get",
        headers: {
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "autMan-Weather-Plugin/2.0"
        },
        timeOut: TIMEOUT
    }, function(error, response, header, body) {
        if (error) {
            if (USE_EMOJI) {
                sendText("❌ 网络请求失败：" + error);
            } else {
                sendText("网络请求失败：" + error);
            }
            return;
        }

        try {
            const data = JSON.parse(body);
            
            if (data.code === 200) {
                Debug(JSON.stringify(data));
                // 成功获取天气数据，默认显示详细信息
                formatDetailedWeather(data.data);
            } else {
                Debug(JSON.stringify(data));
                // API返回错误
                if (USE_EMOJI) {
                    sendText("❌ 查询失败：" + data.message + "\n错误码：" + data.code);
                } else {
                    sendText("查询失败：" + data.message + "\n错误码：" + data.code);
                }
            }
        } catch (e) {
            if (USE_EMOJI) {
                sendText("❌ 数据解析失败：" + e);
            } else {
                sendText("数据解析失败：" + e);
            }
        }
    });
}

// ===== 格式化详细天气（包含生活指数）=====
function formatDetailedWeather(data) {
    const location = data.location;
    const weather = data.weather;
    const airQuality = data.air_quality;
    const sunrise = data.sunrise;
    const lifeIndices = data.life_indices;
    
    if (USE_EMOJI) {
        // Emoji 版本
        let message = "📍 " + location.city + " · " + weather.updated.split(" ")[0] + "\n";
        message += "━━━━━━━━━━━━━━━━\n\n";
        
        // 基本天气信息
        message += "【天气概况】\n";
        message += "🌥 天气：" + weather.condition + "\n";
        message += "🌡 温度：" + weather.temperature + "°C\n";
        message += "💨 风向风力：" + weather.wind_direction + " " + weather.wind_power + "级\n";
        message += "💧 相对湿度：" + weather.humidity + "%\n";
        message += "🌀 气压：" + weather.pressure + "hPa\n";
        message += "☔ 降水量：" + weather.precipitation + "mm\n";
        
        // 空气质量
        if (airQuality) {
            message += "\n【空气质量】\n";
            message += "🍃 质量等级：" + airQuality.quality + " (AQI: " + airQuality.aqi + ")\n";
            message += "📊 PM2.5：" + airQuality.pm25 + " | PM10：" + airQuality.pm10 + "\n";
            message += "🏙 城市排名：" + airQuality.rank + "/" + airQuality.total_cities + "\n";
        }
        
        // 日出日落
        message += "\n【日出日落】\n";
        message += "🌅 日出：" + sunrise.sunrise_desc + "\n";
        message += "🌇 日落：" + sunrise.sunset_desc + "\n";
        
        // 预警信息
        if (data.alerts && data.alerts.length > 0) {
            message += "\n⚠ 【天气预警】\n";
            for (let i = 0; i < data.alerts.length; i++) {
                message += data.alerts[i] + "\n";
            }
        }
        
        // 生活指数（选择性显示重要的）
        if (lifeIndices && lifeIndices.length > 0) {
            message += "\n【生活指数】\n";
            
            // 重点显示的生活指数
            const importantIndices = ["clothes", "umbrella", "sports", "carwash", "cold", "ultraviolet"];
            
            for (let i = 0; i < lifeIndices.length; i++) {
                const index = lifeIndices[i];
                if (importantIndices.indexOf(index.key) !== -1) {
                    const icon = getLifeIndexIcon(index.key);
                    message += icon + " " + index.name + "：" + index.level + "\n";
                    message += "   " + index.description + "\n";
                }
            }
        }
        
        sendText(message);
    } else {
        // 纯文字版本
        let message = "【" + location.city + "】" + weather.updated.split(" ")[0] + "\n";
        message += "━━━━━━━━━━━━━━━━\n\n";
        
        // 基本天气信息
        message += "【天气概况】\n";
        message += "天气：" + weather.condition + "\n";
        message += "温度：" + weather.temperature + "°C\n";
        message += "风向风力：" + weather.wind_direction + " " + weather.wind_power + "级\n";
        message += "相对湿度：" + weather.humidity + "%\n";
        message += "气压：" + weather.pressure + "hPa\n";
        message += "降水量：" + weather.precipitation + "mm\n";
        
        // 空气质量
        if (airQuality) {
            message += "\n【空气质量】\n";
            message += "质量等级：" + airQuality.quality + " (AQI: " + airQuality.aqi + ")\n";
            message += "PM2.5：" + airQuality.pm25 + " | PM10：" + airQuality.pm10 + "\n";
            message += "城市排名：" + airQuality.rank + "/" + airQuality.total_cities + "\n";
        }
        
        // 日出日落
        message += "\n【日出日落】\n";
        message += "日出：" + sunrise.sunrise_desc + "\n";
        message += "日落：" + sunrise.sunset_desc + "\n";
        
        // 预警信息
        if (data.alerts && data.alerts.length > 0) {
            message += "\n【天气预警】\n";
            for (let i = 0; i < data.alerts.length; i++) {
                message += data.alerts[i] + "\n";
            }
        }
        
        // 生活指数（选择性显示重要的）
        if (lifeIndices && lifeIndices.length > 0) {
            message += "\n【生活指数】\n";
            
            // 重点显示的生活指数
            const importantIndices = ["clothes", "umbrella", "sports", "carwash", "cold", "ultraviolet"];
            
            for (let i = 0; i < lifeIndices.length; i++) {
                const index = lifeIndices[i];
                if (importantIndices.indexOf(index.key) !== -1) {
                    message += index.name + "：" + index.level + "\n";
                    message += "   " + index.description + "\n";
                }
            }
        }
        
        sendText(message);
    }
}

// ===== 辅助函数：获取生活指数图标 =====
function getLifeIndexIcon(key) {
    const iconMap = {
        "clothes": "👔",
        "umbrella": "☂",
        "sports": "🏃",
        "carwash": "🚗",
        "cold": "🤧",
        "ultraviolet": "☀",
        "tourism": "✈",
        "comfort": "😊",
        "makeup": "💄",
        "mood": "😄",
        "morning": "🌄",
        "fish": "🎣",
        "sunglasses": "🕶",
        "sunscreen": "🧴",
        "traffic": "🚦",
        "allergy": "🤧",
        "airconditioner": "❄",
        "drying": "👕"
    };
    return iconMap[key] || "📌";
}

// ===== 执行主函数 =====
main();
