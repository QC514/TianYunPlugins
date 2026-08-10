#[create_at: 2026-03-21 15:49:56]
#[title:消息面分析]
#[version:1.0.1]
#[author:hdbjlizhe]
#[service:282617666]
#[price:0]
#[rule:^(精读|总结|分析)$]
#[param: {"required":true,"key":"otto.deepseek_apikey","bool":false,"type":"text","placeholder":"","name":"DeepSeek Key","desc":"DeepSeek Key"}]
#[param: {"required":true,"key":"otto.analysis_result_template","bool":false,"type":"textarea","placeholder":"","name":"文字模板","desc":"回复结果的文字模板"}]
#[description:仅支持autMan3.9.5及以上版本，安装python依赖selenium，指令：分析、总结、精读]
#[previews:https://bbs.autman.cn/assets/files/2025-11-20/1763629703-308811-9331a57c-184b-48ce-ae67-36af1c313652.png,https://bbs.autman.cn/assets/files/2025-11-20/1763630292-33582-fb48dc9a-f521-4dc3-9ec1-ebc176bb8a66.png,https://bbs.autman.cn/assets/files/2025-11-21/1763689168-530923-1b7c3ed6-3889-4cbd-9b4f-737b22ffb307.png]

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import middleware
import requests

template=middleware.get("analysis_result_template")
if template=="" or template==None:
	template="""
你是一个专业的文章分析助手。请分析用户提供的文章，并按以下格式返回分析结果：

📖 概述
[文章概述，50字内]
----------------------------
🔑 关键要点
1. [要点1]
2. [要点2]
3. [要点3]
4. [要点4]
----------------------------
📈 对股市的影响
[分析对股市有什么影响，字数控制在100字内]
----------------------------
🏷️ 标签
#标签1 #标签2 #标签3

请严格按照上述格式返回，不要添加其他内容。
"""

def get_webpage_info_selenium(url):
    """
    使用Selenium操作Chromium浏览器获取网页信息
    """
    # 配置浏览器选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')
    
    try:
        # 启动浏览器
        # 注意：需要下载对应版本的ChromeDriver并配置路径
        driver = webdriver.Chrome(options=chrome_options)
        
        # 访问网页
        print(f"正在访问: {url}")
        driver.get(url)
        
        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 获取网页信息
        page_info = {
            'title': driver.title,
            'url': driver.current_url,
            'page_source': driver.page_source,
            'text_content': driver.find_element(By.TAG_NAME, "body").text,
            'headers': []  # 可以通过driver.get_log('performance')获取网络请求信息
        }
        
        # 获取所有链接
        links = driver.find_elements(By.TAG_NAME, "a")
        page_info['links'] = [link.get_attribute('href') for link in links if link.get_attribute('href')]
        
        # 获取所有图片
        images = driver.find_elements(By.TAG_NAME, "img")
        page_info['images'] = [img.get_attribute('src') for img in images if img.get_attribute('src')]
        
        return page_info
        
    except Exception as e:
        print(f"访问网页时出错: {e}")
        return None
        
    finally:
        # 关闭浏览器
        if 'driver' in locals():
            driver.quit()


def analyze_with_gemini(title, content):
    """使用Gemini分析文章"""
    try:
        print(f"🤖 开始AI分析...")

        api_key=middleware.get("deepseek_apikey")
        base_url = "https://api.deepseek.com/v1"
        model = "deepseek-chat"

        # 构建DeepSeek API URL
        base_url = base_url.rstrip('/')  # 移除末尾的斜杠
        api_url = f"{base_url}/chat/completions"

        print(f"🔧 配置信息:")
        print(f"   API URL: {api_url}")
        print(f"   模型: {model}")
        print(f"   API Key: {api_key[:6]}...{api_key[-4:] if len(api_key) > 10 else api_key}")

        # 构建DeepSeek聊天格式的消息 - 使用文本格式
        system_prompt = template

        user_prompt = f"""请分析以下文章：

标题：{title}
内容：{content[:1500]}"""

        # 优化的重试机制，减少等待时间
        for attempt in range(2):  # 减少重试次数从3次到2次
            try:
                if attempt > 0:
                    delay = 1  # 减少重试延迟从指数增长到固定1秒
                    print(f"⏳ 第{attempt + 1}次尝试，等待{delay}秒...")
                    time.sleep(delay)

                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }

                # 使用DeepSeek OpenAI兼容格式
                data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 3500,
                    "top_p": 0.9
                }

                print(f"📡 发送API请求到: {api_url}")
                response = requests.post(api_url, headers=headers, json=data, timeout=20)

                print(f"📊 API响应状态: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ API调用成功")

                    # 处理DeepSeek OpenAI兼容API响应格式
                    if 'choices' in result and result['choices']:
                        choice = result['choices'][0]

                        # 检查是否有message和content
                        if 'message' in choice and 'content' in choice['message']:
                            content = choice['message']['content']
                            if content:
                                print(f"📝 AI返回内容: {content[:200]}...")
                                return content  # 直接返回文本内容，不再解析JSON

                        # 如果没有内容，检查finish_reason
                        finish_reason = choice.get('finish_reason', '')
                        if finish_reason == 'length':
                            print(f"⚠️ 响应被截断（达到最大token限制），尝试重新生成...")
                            continue  # 重试
                        else:
                            print(f"❌ 无法获取AI响应内容，finish_reason: {finish_reason}")

                    print(f"❌ API响应格式异常: {result}")
                    return None
                elif response.status_code == 429:
                    try:
                        error_detail = response.json()
                        error_msg = error_detail.get('error', {}).get('message', '')
                        if 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
                            print(f"🚫 API配额已用完，今日请求次数已达上限")
                            print(f"💡 建议：等待明天重置或升级到付费版本")
                            return None  # 直接返回，不再重试
                        else:
                            print(f"⚠️ API速率限制，重试中...")
                            time.sleep(3)  # 等待3秒后重试
                            continue
                    except:
                        print(f"⚠️ API速率限制，重试中...")
                        time.sleep(3)
                        continue
                else:
                    print(f"❌ API调用失败: {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"❌ 错误详情: {error_detail}")

                        # 特殊处理403错误
                        if response.status_code == 403:
                            error_msg = error_detail.get('error', {}).get('message', '')
                            if 'suspended' in error_msg.lower():
                                print(f"🚫 API密钥已被暂停，请联系服务提供商")
                                return None  # 直接返回，不再重试
                            elif 'permission' in error_msg.lower():
                                print(f"🚫 API权限不足，请检查密钥权限")
                                return None

                    except:
                        print(f"❌ 响应内容: {response.text[:500]}")

                    # 对于其他错误，不再重试
                    if response.status_code in [400, 401, 403, 404]:
                        break
                    continue

            except requests.exceptions.Timeout:
                print(f"⚠️ API请求超时，重试中...")
                continue
            except requests.exceptions.ConnectionError:
                print(f"⚠️ 网络连接错误，请检查API URL是否正确")
                continue
            except Exception as e:
                print(f"⚠️ API调用异常: {type(e).__name__}: {e}")
                continue

        print(f"❌ AI分析失败 - 所有重试均失败")
        return None

    except Exception as e:
        print(f"❌ AI分析异常: {type(e).__name__}: {e}")
        return None

def parse_ai_response(content):
    """解析AI响应 - 性能优化版"""
    try:
        # 改进的JSON匹配模式，适配DeepSeek输出
        json_str = None

        # 首先尝试匹配代码块格式
        code_block_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if code_block_match:
            json_str = code_block_match.group(1)
            print(f"✅ JSON代码块格式匹配成功")
        else:
            # 然后尝试匹配包含overview的JSON对象
            json_match = re.search(r'\{.*?"overview".*?\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                print(f"✅ JSON对象格式匹配成功")
            else:
                # 最后尝试匹配任何JSON对象
                any_json_match = re.search(r'\{.*?\}', content, re.DOTALL)
                if any_json_match:
                    json_str = any_json_match.group(0)
                    print(f"✅ 通用JSON格式匹配成功")

        if not json_str:
            return None

        # 快速JSON修复和解析
        try:
            result = json.loads(json_str)
            print(f"✅ JSON解析成功")
            return result
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON解析失败: {e}")
            print(f"🔍 JSON内容: {json_str[:200]}...")
            # 快速修复常见JSON问题
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)  # 移除尾随逗号
            json_str = re.sub(r'([{,]\s*)(\w+):', r'\1"\2":', json_str)  # 添加缺失的引号
            try:
                return json.loads(json_str)
            except:
                return None

    except Exception as e:
        print(f"❌ 响应解析失败: {e}")
        return None

def format_result(analysis):
    """格式化分析结果 - 使用分隔符提供更好的阅读性"""
    try:
        parts = []

        # 概述
        if 'overview' in analysis:
            parts.append(f"📖 概述\n{analysis['overview']}")

        # 关键要点
        if 'key_points' in analysis and analysis['key_points']:
            key_points_section = ["🔑 关键要点"]
            for i, point in enumerate(analysis['key_points'], 1):
                key_points_section.append(f"{i}. {point}")
            parts.append('\n'.join(key_points_section))

        # 价值评估
        if 'value_assessment' in analysis:
            assessment = analysis['value_assessment']
            if isinstance(assessment, dict):
                score = assessment.get('score', 'N/A')
                value_section = [f"⭐ 价值评估: {score}/10"]

                readability = assessment.get('readability', '')
                if readability:
                    value_section.append(f"✅ 可读性: {readability}")

                parts.append('\n'.join(value_section))

        # 可执行建议
        if 'actionable_insights' in analysis and analysis['actionable_insights']:
            insights_section = ["💡 建议"]
            for i, insight in enumerate(analysis['actionable_insights'], 1):
                insights_section.append(f"{i}. {insight}")
            parts.append('\n'.join(insights_section))

        # 标签
        if 'tags' in analysis and analysis['tags']:
            tags = ' '.join([f"#{tag}" for tag in analysis['tags']])
            parts.append(f"🏷️ 标签\n{tags}")

        # 使用 --- 分隔符连接各部分，提供清晰的视觉分隔
        return '\n----------------------------\n'.join(parts)

    except Exception as e:
        print(f"❌ 格式化失败: {e}")
        return str(analysis)
# 使用示例
if __name__ == "__main__":
    try:
        sender = middleware.Sender(middleware.getSenderID())
        sender.reply("请输入网址：")
        user_input = sender.listen(60000)
        
        if "http" not in user_input:
            sender.reply("非网址")
        else:
            sender.reply("分析中，请稍候...")
            webpage_info = get_webpage_info_selenium(user_input)

            # AI分析
            analysis_result = analyze_with_gemini(webpage_info['title'], webpage_info['text_content'])
            if not analysis_result:
                sender.reply("❌ AI分析失败，请稍后重试")
                print(f"❌ AI分析失败，请稍后重试")
                #return

            print(f"✅ AI分析成功")

            # 直接发送AI返回的文本结果
            sender.reply(analysis_result)
            print(analysis_result)

    except Exception as e:
        print(f"❌ 插件异常: {e}")
        sender.reply("❌ 插件执行异常，请稍后重试")
    
    # if webpage_info:
    #     print(f"网页标题: {webpage_info['title']}")
    #     print(f"当前URL: {webpage_info['url']}")
    #     print(f"链接数量: {len(webpage_info['links'])}")
    #     print(f"图片数量: {len(webpage_info['images'])}")
    #     print(f"文本内容前500字符: {webpage_info['text_content'][:5000]}...")