#[title: 综合娱乐插件]
#[language: python]
#[class: 工具类]
#[service: 2993959969] 售后联系方式
#[author: rujingxianghai] 作者
#[disable: false] 禁用开关，true表示禁用，false表示可用
#[admin: false] 是否为管理员指令
#[rule: ^油价.+$|^视频解析$|^天气.+$]
#[cron: 0 0 0 0 0] cron定时，支持5位域和6位域
#[priority: 0] 优先级，数字越大表示优先级越高
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[open_source: false] 是否开源
#[icon: https://img-cf.885666.xyz/default.png] 图标链接地址，请使用48像素的正方形图标，支持http和https
#[version: 1.2.0] 版本号
#[public: true] 是否发布
#[price: 6.66] 上架价格
#[description: 综合娱乐插件，提供多种实用功能<br>功能1：油价查询 - 指令：油价XX（XX代表省份）<br>功能2：视频解析 - 指令：视频解析（支持唞音、小红薯、筷手、微博）<br>功能3：详细天气 - 指令：天气XX（XX为城市）]

import json
import requests
import middleware

# [param: {"required":true,"key":"s_general_ent_config.weather_key","bool":false,"placeholder":"请输入天气API密钥","name":"天气API密钥","desc":"前往 https://xxapi.cn 注册获取key"}]

# 获取用户信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)


class OilPriceQuery:
    """油价查询功能类"""
    
    # 省份代码映射
    PROVINCE_MAP = {
        "北京": "11", "天津": "12", "河北": "13", "山西": "14",
        "河南": "41", "山东": "37", "上海": "31", "江苏": "32",
        "浙江": "33", "安徽": "34", "福建": "35", "江西": "36",
        "湖北": "42", "湖南": "43", "广东": "44", "广西": "45",
        "云南": "53", "贵州": "52", "海南": "46", "重庆": "50",
        "四川": "51", "新疆": "65", "内蒙古": "15", "辽宁": "21",
        "吉林": "22", "宁夏": "64", "陕西": "61", "黑龙江": "23",
        "西藏": "54", "青海": "63", "甘肃": "62"
    }
    
    def __init__(self):
        self.api_url = "https://cx.sinopecsales.com/yjkqiantai/data/switchProvince"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36 Edg/142.0.0.0",
            "Content-Type": "application/json"
        }
    
    def query(self, province_name):
        """
        查询指定省份的油价
        
        Args:
            province_name: 省份名称
            
        Returns:
            str: 格式化的油价信息
        """
        # 查找省份代码
        province_id = self.PROVINCE_MAP.get(province_name)
        
        if not province_id:
            return self._format_error("未找到省份", f"❌ 不支持的省份: {province_name}", self._get_supported_provinces())
        
        try:
            # 构建请求体
            payload = {"provinceId": province_id}
            
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            # 检查响应状态
            if response.status_code != 200:
                return self._format_error("查询失败", f"❌ 请求失败，状态码: {response.status_code}")
            
            # 解析响应
            result = response.json()
            
            # 检查数据
            if not result.get("data"):
                return self._format_error("查询失败", "❌ 未获取到油价数据")
            
            data = result["data"]
            province_data = data.get("provinceData")
            
            if not province_data:
                return self._format_error("查询失败", "❌ 该省份暂无油价数据")
            
            # 格式化并返回结果
            return self._format_result(province_name, province_data)
            
        except requests.exceptions.Timeout:
            return self._format_error("查询超时", "❌ 请求超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            return self._format_error("网络错误", f"❌ 网络请求失败: {str(e)}")
        except json.JSONDecodeError:
            return self._format_error("数据错误", "❌ 响应数据解析失败")
        except Exception as e:
            return self._format_error("查询异常", f"❌ 发生异常: {str(e)}")
    
    def _format_result(self, province_name, data):
        """
        格式化油价查询结果
        
        Args:
            province_name: 省份名称
            data: 油价数据
            
        Returns:
            str: 格式化的消息
        """
        lines = [
            f"📍 省份: {province_name}",
            "=" * 17
        ]
        
        # 获取各油价数据
        gas_92 = data.get("GAS_92")
        gas_92_status = data.get("GAS_92_STATUS")
        gas_95 = data.get("GAS_95")
        gas_95_status = data.get("GAS_95_STATUS")
        gas_98 = data.get("GAS_98")
        gas_98_status = data.get("GAS_98_STATUS")
        diesel_0 = data.get("CHECHAI_0")
        diesel_0_status = data.get("CHECHAI_0_STATUS")
        diesel_10 = data.get("CHECHAI_10")
        diesel_10_status = data.get("CHECHAI_10_STATUS")
        
        # 92号汽油
        if gas_92:
            lines.append(f"🔹 92号汽油：{gas_92}元/升")
            status_text = self._get_status_text(gas_92_status)
            if status_text:
                lines.append(f"   {status_text}")
        
        # 95号汽油
        if gas_95:
            lines.append(f"🔸 95号汽油：{gas_95}元/升")
            status_text = self._get_status_text(gas_95_status)
            if status_text:
                lines.append(f"   {status_text}")
        
        # 98号汽油
        if gas_98:
            lines.append(f"🔺 98号汽油：{gas_98}元/升")
            status_text = self._get_status_text(gas_98_status)
            if status_text:
                lines.append(f"   {status_text}")
        
        # 0号柴油
        if diesel_0:
            lines.append(f"▫️ 0号柴油：{diesel_0}元/升")
            status_text = self._get_status_text(diesel_0_status)
            if status_text:
                lines.append(f"   {status_text}")
        
        # 10号柴油
        if diesel_10:
            lines.append(f"▪️ 10号柴油：{diesel_10}元/升")
            status_text = self._get_status_text(diesel_10_status)
            if status_text:
                lines.append(f"   {status_text}")
        
        # 添加更新时间
        start_date = data.get("START_DATE")
        if start_date:
            lines.append("=" * 17)
            lines.append(f"⏰ 更新时间: \n{start_date}")
        
        return self._format_message("油价查询", lines)
    
    def _get_status_text(self, status_value):
        """
        获取涨跌状态文本
        
        Args:
            status_value: 涨跌值
            
        Returns:
            str: 状态文本
        """
        if status_value is None or status_value == 0:
            return ""
        
        try:
            value = float(status_value)
            if value > 0:
                return f" 📈 较昨日：+{value}元"
            elif value < 0:
                return f" 📉 较昨日：-{abs(value)}元"
            else:
                return ""
        except (ValueError, TypeError):
            return ""
    
    def _format_message(self, title, lines):
        """
        格式化消息
        
        Args:
            title: 标题
            lines: 内容行列表
            
        Returns:
            str: 格式化的消息
        """
        message = f"{'='*5}{title}{'='*5}\n"
        message += "\n".join(lines)
        message += f"\n{'='*18}"
        return message
    
    def _format_error(self, title, error_msg, extra_info=""):
        """
        格式化错误消息
        
        Args:
            title: 错误标题
            error_msg: 错误信息
            extra_info: 额外信息
            
        Returns:
            str: 格式化的错误消息
        """
        lines = [error_msg]
        if extra_info:
            lines.append("─" * 25)
            lines.append(extra_info)
        return self._format_message(title, lines)
    
    def _get_supported_provinces(self):
        """
        获取支持的省份列表
        
        Returns:
            str: 省份列表文本
        """
        provinces = list(self.PROVINCE_MAP.keys())
        # 分行显示，每行显示6个省份
        lines = []
        for i in range(0, len(provinces), 6):
            line = "、".join(provinces[i:i+6])
            lines.append(line)
        return "💡 支持的省份:\n" + "\n".join(lines)


class VideoParser:
    """视频解析功能类"""
    
    # 支持的平台
    SUPPORTED_PLATFORMS = ["唞音", "小红薯", "筷手", "微博"]
    
    def __init__(self):
        self.api_url = "https://mihoyonb.com/api/video-analyze"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36 Edg/142.0.0.0",
            "Content-Type": "application/json"
        }
    
    def parse(self, video_url):
        """
        解析视频链接
        
        Args:
            video_url: 视频链接
            
        Returns:
            dict: 解析结果 {"success": bool, "data": dict/str}
        """
        try:
            # 构建请求体
            payload = {
                "url": video_url,
                "format": "json"
            }
            
            # 发送请求（视频解析可能需要较长时间）
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30  # 设置30秒超时
            )
            
            # 检查响应状态
            if response.status_code != 200:
                return {
                    "success": False,
                    "data": f"请求失败，状态码: {response.status_code}"
                }
            
            # 解析响应
            result = response.json()
            
            # 检查响应码
            if result.get("code") != 200:
                return {
                    "success": False,
                    "data": result.get("message", "解析失败")
                }
            
            # 获取数据
            data = result.get("data")
            if not data:
                return {
                    "success": False,
                    "data": "未获取到视频数据"
                }
            
            return {
                "success": True,
                "data": data
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "data": "请求超时，视频解析时间过长，请稍后重试"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "data": f"网络请求失败: {str(e)}"
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "data": "响应数据解析失败"
            }
        except Exception as e:
            return {
                "success": False,
                "data": f"发生异常: {str(e)}"
            }
    
    def format_result(self, data):
        """
        格式化解析结果
        
        Args:
            data: 解析数据
            
        Returns:
            str: 格式化的消息
        """
        title = data.get("title", "未知标题")
        description = data.get("description", "")
        app_type = data.get("app_type", "")
        
        # 平台名称映射
        platform_names = {
            "douyin": "唞音",
            "xiaohongshu": "小红薯",
            "kuaishou": "筷手",
            "weibo": "微博"
        }
        platform_name = platform_names.get(app_type, app_type)
        
        lines = []
        
        if platform_name:
            lines.append(f"📱 平台: {platform_name}")
        
        #if title:
            #lines.append(f"📝 标题: {title}")
        
        if description and description != title:
            # 如果描述太长，截取前100个字符
            if len(description) > 100:
                description = description[:100] + "..."
            lines.append(f"💬 描述: {description}")
        
        return self._format_message("视频解析", lines)
    
    def _format_message(self, title, lines):
        """
        格式化消息
        
        Args:
            title: 标题
            lines: 内容行列表
            
        Returns:
            str: 格式化的消息
        """
        message = f"{'='*5}{title}{'='*5}\n"
        message += "\n".join(lines)
        message += f"\n{'='*18}"
        message += f"\n🔄 视频正在发送，请稍等..."
        return message
    
    def get_supported_platforms_text(self):
        """
        获取支持平台的文本
        
        Returns:
            str: 支持平台文本
        """
        return "、".join(self.SUPPORTED_PLATFORMS)


class WeatherQuery:
    """详细天气查询功能类"""
    
    def __init__(self):
        self.api_url = "https://v2.xxapi.cn/api/weatherDetails"
        # 从配置获取key
        self.api_key = middleware.bucketGet('s_general_ent_config', 'weather_key') or ''
        
    def query(self, city_name):
        """
        查询指定城市的天气
        """
        if not self.api_key:
            return self._format_error("配置错误", "❌ 未配置天气API密钥", "💡 请在插件配置中填写key\n获取地址: https://xxapi.cn")
            
        try:
            params = {
                "city": city_name,
                "key": self.api_key
            }
            
            response = requests.get(
                self.api_url, 
                params=params, 
                timeout=10
            )
            
            if response.status_code != 200:
                return self._format_error("查询失败", f"❌ HTTP状态码: {response.status_code}")
            
            try:
                result = response.json()
            except json.JSONDecodeError:
                return self._format_error("数据错误", "❌ 响应数据解析失败")
                
            if result.get("code") != 200:
                return self._format_error("查询失败", f"❌ {result.get('msg', '未知错误')}")
                
            data = result.get("data")
            if not data:
                return self._format_error("数据错误", "❌ 未获取到天气数据")
                
            return self._format_result(data)
            
        except requests.exceptions.Timeout:
            return self._format_error("查询超时", "❌ 请求超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            return self._format_error("网络错误", f"❌ 网络请求失败: {str(e)}")
        except Exception as e:
            return self._format_error("系统异常", f"❌ 发生异常: {str(e)}")
    
    def _format_result(self, data):
        """
        格式化天气查询结果
        """
        city = data.get("city", "未知城市")
        weather_data = data.get("data", [])
        
        if not weather_data:
            return self._format_error("数据为空", "❌ 天气数据列表为空")
            
        lines = [f"📍 城市: {city}", "=" * 17]
        
        # 今日天气 (取列表第一个)
        today = weather_data[0]
        date = today.get("date", "")
        day = today.get("day", "")
        weather_from = today.get("weather_from", "")
        weather_to = today.get("weather_to", "")
        high = today.get("high_temp", "")
        low = today.get("low_temp", "")
        wind_dir = today.get("wind_from", "") # 接口返回wind_from
        wind_level = today.get("wind_level_from", "")
        
        weather_str = weather_from
        if weather_from != weather_to:
            weather_str += f"转{weather_to}"
            
        lines.append(f"📅 {date} {day}")
        lines.append(f"🌤️ 天气: {weather_str}")
        lines.append(f"🌡️ 温度: {low}℃ ~ {high}℃")
        lines.append(f"🌬️ 风向: {wind_dir} {wind_level}")
        
        # 实时详情 (展示部分)
        real_time = today.get("real_time_weather", [])
        if real_time:
            lines.append("-" * 27)
            lines.append("🕒 今日详情:")
            # 挑选几个时间点展示，避免太长 (08:00, 11:00, 14:00, 17:00, 20:00)
            target_times = ["02:00", "08:00", "14:00", "17:00", "20:00", "23:00"]
            for item in real_time:
                time = item.get("time")
                if time in target_times:
                    weather = item.get("weather")
                    temp = item.get("temperature")
                    lines.append(f"{time} | {weather} | {temp}℃")
        
        # 未来预报 (展示未来3天)
        if len(weather_data) > 1:
            lines.append("=" * 17)
            lines.append("🔮 未来预报:")
            count = 0
            for i in range(1, len(weather_data)):
                if count >= 3:
                    break
                future = weather_data[i]
                f_date = future.get("date")
                f_day = future.get("day")
                f_weather = future.get("weather_from")
                if future.get("weather_to") != f_weather:
                    f_weather += f"转{future.get('weather_to')}"
                f_high = future.get("high_temp")
                f_low = future.get("low_temp")
                
                lines.append(f"{f_date} {f_day}: {f_weather} {f_low}~{f_high}℃")
                count += 1
                
        return self._format_message("详细天气", lines)

    def _format_message(self, title, lines):
        """格式化消息"""
        message = f"{'='*5}{title}{'='*5}\n"
        message += "\n".join(lines)
        message += f"\n{'='*18}"
        return message

    def _format_error(self, title, error_msg, extra_info=""):
        """格式化错误消息"""
        lines = [error_msg]
        if extra_info:
            lines.append("─" * 25)
            lines.append(extra_info)
        return self._format_message(title, lines)


def main():
    """主入口函数"""
    try:
        # 获取用户消息
        user_message = sender.getMessage()
        
        # 油价查询功能
        if user_message.startswith("油价"):
            province = user_message[2:].strip()  # 提取省份名称
            
            if not province:
                sender.reply("""
=====使用说明=====
💡 请输入省份名称
例如：油价上海
─────────────────
支持全国31个省市自治区
发送 油价帮助 查看支持的省份列表
==================""")
                return
            
            # 如果是查询帮助
            if province in ["帮助", "列表", "支持", "help"]:
                oil_query = OilPriceQuery()
                help_text = oil_query._get_supported_provinces()
                sender.reply(f"""
=====支持省份=====
{help_text}
─────────────────
💡 使用方法：油价XX
例如：油价上海
==================""")
                return
            
            # 执行查询
            oil_query = OilPriceQuery()
            result = oil_query.query(province)
            sender.reply(result)
        
        # 视频解析功能
        elif user_message == "视频解析":
            video_parser = VideoParser()
            
            # 显示使用说明
            platforms = video_parser.get_supported_platforms_text()
            guide_text = f"""
=====视频解析=====
💡 请发送视频链接
=================
📱 支持平台:
{platforms}
=================
回复 q 取消操作
=================="""
            sender.reply(guide_text)
            
            # 等待用户输入链接，120秒超时
            video_url = sender.input(120000, 1, False)
            
            if not video_url or video_url.lower() == 'q':
                sender.reply("✅ 已取消视频解析")
                return
            
            # 提示用户正在解析
            sender.reply("🔄 正在解析视频，请稍候...\n⏰ 解析时间根据视频时长而定")
            
            # 执行解析
            result = video_parser.parse(video_url)
            
            if result["success"]:
                # 解析成功
                data = result["data"]
                video_url_parsed = data.get("video", "")
                
                if video_url_parsed:
                    # 先发送视频信息
                    formatted_result = video_parser.format_result(data)
                    sender.reply(formatted_result)
                    
                    # 再发送视频
                    try:
                        sender.replyVideo(video_url_parsed)
                    except Exception as e:
                        sender.reply(f"❌ 视频发送失败: {str(e)}\n\n🔗 视频链接:\n{video_url_parsed}")
                else:
                    sender.reply("""
=====解析失败=====
❌ 未获取到视频链接
=================
💡 该视频可能:
1. 已被删除
2. 设置了隐私权限
3. 平台不支持解析
==================""")
            else:
                # 解析失败，发送错误信息
                error_msg = f"""
=====解析失败=====
❌ {result['data']}
=================
💡 请检查:
1. 链接是否正确
2. 平台是否支持
3. 视频是否存在
=================="""
                sender.reply(error_msg)
        
        # 详细天气功能
        elif user_message.startswith("天气"):
            city = user_message[2:].strip()
            
            if not city:
                sender.reply("""
=====使用说明=====
💡 请输入城市名称
例如：天气上海
     天气山东烟台
==================""")
                return
                
            weather_query = WeatherQuery()
            result = weather_query.query(city)
            sender.reply(result)
        
        else:
            # 如果消息不匹配，继续传递给其他插件处理
            sender.setContinue()
            
    except Exception as e:
        sender.reply(f"❌ 插件执行异常: {str(e)}")


if __name__ == "__main__":
    main()
