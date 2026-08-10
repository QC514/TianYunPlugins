#[pin:false]
#[public:true]
#[title: 视频解析]
#[service:2661320550]
#[disable:false]
#[admin: false]
#[author: sky2022]
#[rule: ^(视频解析|解析视频)$]
#[priority: 0]
#[platform: qq,qb,wx,tb,tg,web,wxmp]
#[icon: https://i.miji.bid/2025/06/27/b26bceeed8be81da129e93a6d0fd75ae.png]
#[version: 1.2.1]
#[price: 1.88]
#[description: 指令：豆音视频解析<br>更新：v1.2.1新增：支持逗音短链接自动重定向解析，提升解析成功率]

import requests
import middleware
import re
import base64
import os

class DouyinParserPlugin:
    def __init__(self):
        self.senderID = middleware.getSenderID()
        self.sender = middleware.Sender(self.senderID)
        # 设置API密钥
        self.APP_ID = os.getenv('MXNZP_APP_ID', 'glxlmvjllaeqecch')
        self.APP_SECRET = os.getenv('MXNZP_APP_SECRET', 'v0iWLN7uo1AUesOyEjN1OxQPAceQ0qoj')
    
    def resolve_redirect_url(self, url):
        """解析重定向链接，获取真实的视频链接"""
        try:
            # 检查是否是短链接
            if "v.douyin.com" in url:
                # 使用HEAD请求获取重定向后的URL，避免下载整个页面
                response = requests.head(
                    url, 
                    allow_redirects=True, 
                    timeout=10,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                )
                
                redirect_url = response.url
                
                # 从重定向的URL中提取视频ID
                # 例如: https://www.douyin.com/video/7530921197392104762?previous_page=app_code_link
                # 提取出视频ID: 7530921197392104762
                video_id_pattern = r'/video/(\d+)'
                match = re.search(video_id_pattern, redirect_url)
                
                if match:
                    video_id = match.group(1)
                    # 构建iesdouyin.com格式的链接
                    final_url = f"https://www.iesdouyin.com/share/video/{video_id}"
                    return final_url
                else:
                    return redirect_url
            
            return url
            
        except Exception as e:
            return url

    def parse_video_link(self, link):
        try:
            # 先解析重定向链接（特别是抖音短链接）
            resolved_link = self.resolve_redirect_url(link)
            
            # 使用新的统一API接口解析所有平台视频
            api_url = "https://api.qsy.ink/api/douyin"
            
            # 使用与独立脚本相同的请求头和Cookie
            headers = {
                'Host': 'api.qsy.ink',
                'Accept': '*/*',
                'Cookie': 'PHPSESSID=cj1f08h3fiev6aprehbf7n2frv',
                'User-Agent': 'Aweme/348020 CFNetwork/3826.500.131 Darwin/24.5.0',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(api_url, 
                                  params={
                                      "key": "DYYY",
                                      "url": resolved_link
                                  },
                                  headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    data = result.get('data', {})
                    
                    # 获取标题
                    title = data.get('title')
                    if title:
                        self.sender.reply(f"内容文案：{title}")
                    
                    # 处理视频列表
                    video_list = data.get('video_list', [])
                    if video_list:
                        # 过滤掉免责声明等无效选项，只保留实际的视频质量选项
                        valid_videos = []
                        for video in video_list:
                            level = video.get('level', '')
                            # 跳过免责声明和其他非质量描述的项目
                            if not any(keyword in level for keyword in ['免责声明', '未经作者授权', '当前作品播放量']):
                                valid_videos.append(video)
                        
                        if valid_videos:
                            # 显示可选的清晰度选项
                            options = []
                            for i, video in enumerate(valid_videos, 1):
                                level = video.get('level', '未知清晰度')
                                size = video.get('size', 0)
                                # 格式化文件大小显示
                                if size and size < 999999999999999:  # 排除占位符大小
                                    size_mb = size / (1024 * 1024)
                                    size_str = f" ({size_mb:.2f}MB)"
                                else:
                                    size_str = ""
                                options.append(f"{i}. {level}{size_str}")
                            
                            options_text = "\n".join(options)
                            self.sender.reply(f"请选择视频清晰度（输入数字1-{len(options)}）：\n{options_text}")
                            
                            # 等待用户选择
                            choice = self.sender.listen(30000)
                            if choice and choice.isdigit():
                                index = int(choice) - 1
                                if 0 <= index < len(valid_videos):
                                    selected_video = valid_videos[index]
                                    try:
                                        self.sender.replyVideo(selected_video['url'])
                                    except Exception as e:
                                        self.sender.reply(f"视频发送失败：{str(e)}\n视频链接：{selected_video['url']}")
                                else:
                                    self.sender.reply("无效的选择，已取消操作。")
                            else:
                                self.sender.reply("未收到有效选择，已取消操作。")
                            return
                        else:
                            # 如果没有有效的视频选项，使用默认的url字段
                            video_url = data.get('url')
                            if video_url:
                                try:
                                    self.sender.replyVideo(video_url)
                                except Exception as e:
                                    self.sender.reply(f"视频发送失败：{str(e)}\n视频链接：{video_url}")
                                return
                    
                    # 处理单个视频 URL（兼容旧格式）
                    video_url = data.get('url')
                    if video_url and not video_list:
                        try:
                            self.sender.replyVideo(video_url)
                        except Exception as e:
                            self.sender.reply(f"视频发送失败：{str(e)}\n视频链接：{video_url}")
                        return
                    
                    # 处理图集
                    pics = data.get('pics', [])
                    if pics:
                        self.sender.reply(f"解析到图集，共 {len(pics)} 张图片")
                        
                        for i, pic_url in enumerate(pics, 1):
                            try:
                                self.sender.replyImage(pic_url)
                            except Exception as e:
                                self.sender.reply(f"第 {i} 张图片发送失败：{str(e)}\n图片链接：{pic_url}")
                        return
                    
                    if not video_url and not pics and not video_list:
                        self.sender.reply("未找到视频或图片内容")
                else:
                    error_msg = result.get('msg', '未知错误')
                    self.sender.reply(f"解析失败：{error_msg}")
            else:
                self.sender.reply(f"API请求失败，状态码：{response.status_code}")
            
        except Exception as e:
            self.sender.reply(f"解析出错：{str(e)}")

    def parse_kuaishou_link(self, link):
        try:
            base64_url = base64.b64encode(link.encode()).decode()
            response = requests.get("https://www.mxnzp.com/api/ks/video",
                                params={
                                    "url": base64_url,
                                    "app_id": self.APP_ID,
                                    "app_secret": self.APP_SECRET
                                })
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1 and result.get('data', {}).get('url'):
                    self.sender.replyVideo(result['data']['url'])
                else:
                    self.sender.reply("快手视频解析失败")
        except Exception as e:
            self.sender.reply(f"快手视频解析出错：{str(e)}")

    def parse_bilibili_link(self, link):
        try:
            base64_url = base64.b64encode(link.encode()).decode()
            response = requests.get("https://www.mxnzp.com/api/bilibili/video",
                                params={
                                    "url": base64_url,
                                    "app_id": self.APP_ID,
                                    "app_secret": self.APP_SECRET
                                })
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1:
                    data = result.get('data', {})
                    
                    # 发送视频标题
                    title = data.get('title')
                    if title:
                        self.sender.reply(f"视频标题：{title}")
                    
                    # 处理视频列表
                    video_list = data.get('list', [])
                    if video_list:
                        video = video_list[0]  # 获取第一个视频片段
                        try:
                            self.sender.replyVideo(video['url'])
                        except Exception as e:
                            # 如果发送失败，提供视频信息和链接
                            duration = video.get('durationFormat', '未知')
                            quality = ', '.join(video.get('accept', ['未知']))
                            self.sender.reply(
                                f"视频发送失败：{str(e)}\n"
                                f"时长：{duration}\n"
                                f"清晰度：{quality}\n"
                                f"视频链接：{video['url']}"
                            )
                    else:
                        self.sender.reply("未找到可用的视频片段")
                else:
                    self.sender.reply(f"B站视频解析失败：{result.get('msg', '未知错误')}")
            else:
                self.sender.reply(f"B站API请求失败，状态码：{response.status_code}")
        except Exception as e:
            self.sender.reply(f"B站视频解析出错：{str(e)}")

    def extract_link(self, message):
        # 支持更多平台的链接提取
        patterns = {
            'douyin': r'https?://[^\s]*?(?:douyin|iesdouyin)\.com[^\s]*',
            'douyin_short': r'https?://v\.douyin\.com/[^\s]*',
            'kuaishou': r'https?://v\.kuaishou\.com/[^\s]+',
            'bilibili': r'https?://(www\.)?bilibili\.com/[^\s]+',
            'xiaohongshu': r'https?://www\.xiaohongshu\.com/[^\s]+',
            'weibo': r'https?://weibo\.com/[^\s]+',
            'pipix': r'https?://www\.pipix\.com/[^\s]+',
            'huoshan': r'https?://huoshan\.com/[^\s]+',
            'weishi': r'https?://weishi\.qq\.com/[^\s]+',
            'other': r'https?://[^\s]+' # 其他平台的通用匹配
        }
        
        for platform, pattern in patterns.items():
            match = re.search(pattern, message)
            if match:
                return platform, match.group(0)
        return None, None

    def listen_for_command(self):
        # 使用 middleware 中的 get_local_service_response
        usermessage = self.sender.getMessage()
        if '视频解析' in usermessage or '解析视频' in usermessage:
            self.sender.reply("请输入视频链接（仅支持逗音平台）：")
            link_message = self.sender.listen(30000)
            if link_message:
                platform, link = self.extract_link(link_message)
                if link:
                    self.parse_video_link(link)
                else:
                    self.sender.reply("未找到有效的链接。")
            else:
                self.sender.reply("超时未输入链接，结束解析！")

douyin_parser_plugin = DouyinParserPlugin()
douyin_parser_plugin.listen_for_command()