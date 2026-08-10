#[title: autman数据导出]
#[language: python]
#[class: 工具类]
#[service: 2993959969]
#[author: rujingxianghai]
#[disable: false]
#[admin: true]
#[rule: ^数据导出$|^代码导出$|^插件迁移$]
#[cron: 0 0 0 0 0]
#[priority: 0]
#[platform: qq,qb,wx,tb,tg,web,wxmp]
#[open_source: false]
#[icon: https://cdn-icons-png.flaticon.com/512/136/136525.png]
#[version: 1.1.0]
#[public: true]
#[price: 0]
#[description: 将autman数据桶/插件代码导出到远程服务器<br>指令：数据导出|代码导出|插件迁移<br>支持多数据桶、通配符匹配及插件批量迁移]

# [param: {"required":true,"key":"s_export.autman_url","bool":false,"placeholder":"http://192.168.1.1:1234","name":"autman接口地址","desc":"autman的接口地址"}]
# [param: {"required":true,"key":"s_export.autman_user","bool":false,"placeholder":"用户名","name":"autman用户名","desc":"autman登录用户名"}]
# [param: {"required":true,"key":"s_export.autman_pwd","bool":false,"placeholder":"密码","name":"autman密码","desc":"autman登录密码"}]
# [param: {"required":true,"key":"s_export.api_url","bool":false,"placeholder":"http://192.168.1.1:5678","name":"目标API地址","desc":"远程服务器API地址"}]
# [param: {"required":true,"key":"s_export.api_user","bool":false,"placeholder":"邮箱/账号","name":"目标账号","desc":"目标服务器登录账号(邮箱)"}]
# [param: {"required":true,"key":"s_export.api_pwd","bool":false,"placeholder":"密码","name":"目标密码","desc":"目标服务器登录密码"}]

import json
import requests
import middleware
from datetime import datetime
import re

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

def get_config():
    """获取配置"""
    autman_url = middleware.bucketGet('s_export', 'autman_url') or ''
    autman_user = middleware.bucketGet('s_export', 'autman_user') or ''
    autman_pwd = middleware.bucketGet('s_export', 'autman_pwd') or ''
    api_url = middleware.bucketGet('s_export', 'api_url') or ''
    api_user = middleware.bucketGet('s_export', 'api_user') or ''
    api_pwd = middleware.bucketGet('s_export', 'api_pwd') or ''
    
    if autman_url and autman_url.endswith('/'):
        autman_url = autman_url[:-1]
    if api_url and api_url.endswith('/'):
        api_url = api_url[:-1]
    
    return autman_url, autman_user, autman_pwd, api_url, api_user, api_pwd

def login_autman(autman_url, username, password):
    """登录autman获取Cookie"""
    try:
        url = autman_url + "/login"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        
        data = "username=" + username + "&password=" + password
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        result = response.json()
        
        if result.get('code') == 200:
            # 从响应头获取Set-Cookie
            cookies = response.headers.get('Set-Cookie', '')
            if cookies:
                # 提取autMan cookie
                cookie_parts = cookies.split(';')
                for part in cookie_parts:
                    part = part.strip()
                    if part.startswith('autMan='):
                        return part, None
                # 如果没找到autMan，返回整个cookie
                return cookies.split(';')[0], None
            return None, "未获取到Cookie"
        else:
            return None, result.get('message', '登录失败')
            
    except Exception as e:
        return None, str(e)

def login_target(api_url, identifier, password):
    """登录目标服务器获取Cookie"""
    try:
        url = api_url + "/api/login"
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*'
        }
        
        payload = {
            'identifier': identifier,
            'password': password,
            'remember': True
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()
        
        if result.get('message') == '登录成功' or 'user_info' in result:
            # 从响应头获取Set-Cookie
            cookies = response.headers.get('Set-Cookie', '')
            if cookies:
                # 提取session cookie
                cookie_parts = cookies.split(';')
                for part in cookie_parts:
                    part = part.strip()
                    if part.startswith('session='):
                        return part, None
                # 如果没找到session，返回第一个cookie
                return cookies.split(';')[0], None
            return None, "未获取到Cookie"
        else:
            return None, result.get('message', '登录失败')
            
    except Exception as e:
        return None, str(e)

def get_all_buckets(autman_url, autman_cookie):
    """从autman获取所有数据桶列表"""
    try:
        url = autman_url + "/buckets"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': autman_cookie
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        result = response.json()
        
        if result.get('code') == 200:
            data = result.get('data', [])
            bucket_names = [item.get('name') for item in data if item.get('name')]
            return bucket_names
        else:
            sender.reply("获取数据桶列表失败: " + str(result))
            return []
            
    except Exception as e:
        sender.reply("获取数据桶列表异常: " + str(e))
        return []

def match_buckets(pattern, all_buckets):
    """根据通配符模式匹配数据桶"""
    matched = []
    
    # 将通配符转换为正则表达式
    regex_pattern = pattern.replace('*', '.*')
    regex_pattern = '^' + regex_pattern + '$'
    
    try:
        regex = re.compile(regex_pattern, re.IGNORECASE)
        
        for bucket in all_buckets:
            if regex.match(bucket):
                matched.append(bucket)
                
    except Exception as e:
        sender.reply("匹配模式错误: " + str(e))
    
    return matched

def collect_bucket_data(bucket_name):
    """收集指定数据桶的所有数据"""
    try:
        all_keys = middleware.bucketAllKeys(bucket_name)
        if not all_keys:
            return {}
        
        data = {}
        for key in all_keys:
            value = middleware.bucketGet(bucket_name, key)
            if value is not None:
                try:
                    parsed_value = json.loads(value)
                    data[key] = parsed_value
                except:
                    try:
                        data[key] = int(value)
                    except:
                        try:
                            data[key] = float(value)
                        except:
                            data[key] = value
        return data
    except Exception as e:
        sender.reply("收集 " + bucket_name + " 数据失败: " + str(e))
        return {}

def upload_data(api_url, api_cookie, bucket_name, data):
    """上传数据到远程服务器"""
    url = api_url + "/api/databucket/" + bucket_name + "/data"
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Cookie': api_cookie
    }
    
    success_count = 0
    fail_count = 0
    
    for key, value in data.items():
        try:
            payload = {
                'key': key,
                'value': value
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            result = response.json()
            
            if result.get('success'):
                success_count += 1
            else:
                fail_count += 1
                
        except Exception as e:
            fail_count += 1
    
    return success_count, fail_count

def export_bucket(api_url, api_cookie, bucket_name):
    """导出单个数据桶"""
    # 收集数据
    data = collect_bucket_data(bucket_name)
    
    if not data:
        return 0, 0, True  # 返回跳过标志
    
    # 上传数据
    success, fail = upload_data(api_url, api_cookie, bucket_name, data)
    
    return success, fail, False

# ==================== 代码导出功能 ====================

def get_plugin_list(autman_url, autman_cookie, language='python'):
    """获取autman插件列表"""
    try:
        url = autman_url + "/js/menu?language=" + language
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': autman_cookie
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        result = response.json()
        
        if result.get('code') == 200:
            return result.get('data', []), None
        else:
            return None, result.get('message', '获取插件列表失败')
            
    except Exception as e:
        return None, str(e)

def get_plugin_code(autman_url, autman_cookie, plugin_name, language='python'):
    """获取插件代码"""
    try:
        import urllib.parse
        encoded_name = urllib.parse.quote(plugin_name)
        url = autman_url + "/js/content?language=" + language + "&name=" + encoded_name
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': autman_cookie
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('code') == 200:
            return result.get('data', ''), None
        else:
            return None, result.get('message', '获取插件代码失败')
            
    except Exception as e:
        return None, str(e)

def upload_plugin_code(api_url, api_cookie, plugin_name, code, language='python'):
    """上传插件代码到目标服务器"""
    try:
        import urllib.parse
        # 构造文件路径 python/插件名.py
        file_path = language + "/" + plugin_name + ".py"
        encoded_path = urllib.parse.quote(file_path, safe='')
        url = api_url + "/api/plugins/" + encoded_path + "/code"
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Cookie': api_cookie
        }
        
        payload = {
            'code': code
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if result.get('success'):
            return True, result.get('filename', '')
        else:
            return False, result.get('message', '上传失败')
            
    except Exception as e:
        return False, str(e)

def export_code():
    """代码导出主流程"""
    try:
        # 获取配置
        autman_url, autman_user, autman_pwd, api_url, api_user, api_pwd = get_config()
        
        if not autman_url or not autman_user or not autman_pwd:
            sender.reply("请先配置autman接口地址、用户名和密码")
            return
        
        if not api_url or not api_user or not api_pwd:
            sender.reply("请先配置目标API地址、账号和密码")
            return
        
        # 登录autman
        sender.reply("🔐 正在登录autman...")
        autman_cookie, autman_err = login_autman(autman_url, autman_user, autman_pwd)
        
        if not autman_cookie:
            sender.reply("❌ autman登录失败: " + str(autman_err))
            return
        
        sender.reply("✅ autman登录成功")
        
        # 登录目标服务器
        sender.reply("🔐 正在登录目标服务器...")
        api_cookie, api_err = login_target(api_url, api_user, api_pwd)
        
        if not api_cookie:
            sender.reply("❌ 目标服务器登录失败: " + str(api_err))
            return
        
        sender.reply("✅ 目标服务器登录成功")
        
        # 获取插件列表
        sender.reply("📋 正在获取插件列表...")
        plugins, plugin_err = get_plugin_list(autman_url, autman_cookie)
        
        if not plugins:
            sender.reply("❌ 获取插件列表失败: " + str(plugin_err))
            return
        
        # 构建插件列表显示
        plugin_list_msg = "=====插件列表=====\n"
        plugin_list_msg += "共 " + str(len(plugins)) + " 个插件\n"
        plugin_list_msg += "------------------\n"
        plugin_list_msg += "0. 全部迁移\n"
        
        for idx, plugin in enumerate(plugins, 1):
            name = plugin.get('name', '')
            disable = plugin.get('disable', False)
            status = "🔴" if disable else "🟢"
            plugin_list_msg += str(idx) + ". " + status + " " + name + "\n"
        
        plugin_list_msg += "------------------\n"
        plugin_list_msg += "请输入序号(多选用英文逗号分隔)\n"
        plugin_list_msg += "例如: 1,3,5 或 0(全选)\n"
        plugin_list_msg += "回复 q 退出"
        
        sender.reply(plugin_list_msg)
        
        # 获取用户输入
        input_text = sender.input(120000, 20, False)
        
        if not input_text or input_text.strip().lower() == 'q':
            sender.reply("已退出代码导出流程")
            return
        
        # 解析用户选择
        selected_plugins = []
        input_text = input_text.strip()
        
        if input_text == '0':
            # 全选
            selected_plugins = [p.get('name') for p in plugins]
            sender.reply("已选择全部 " + str(len(selected_plugins)) + " 个插件")
        else:
            # 解析选择的序号
            try:
                indices = [int(x.strip()) for x in input_text.split(',') if x.strip()]
                for idx in indices:
                    if 1 <= idx <= len(plugins):
                        selected_plugins.append(plugins[idx - 1].get('name'))
                    else:
                        sender.reply("⚠️ 序号 " + str(idx) + " 超出范围，已跳过")
            except ValueError:
                sender.reply("❌ 输入格式错误，请输入数字序号")
                return
        
        if not selected_plugins:
            sender.reply("❌ 未选择任何插件")
            return
        
        # 去重
        selected_plugins = list(dict.fromkeys(selected_plugins))
        
        sender.reply("📦 即将迁移 " + str(len(selected_plugins)) + " 个插件:\n" + "\n".join(selected_plugins))
        
        # 开始迁移
        success_count = 0
        fail_count = 0
        success_list = []
        fail_list = []
        
        for plugin_name in selected_plugins:
            # 获取代码
            code, code_err = get_plugin_code(autman_url, autman_cookie, plugin_name)
            
            if not code:
                fail_count += 1
                fail_list.append(plugin_name + ": 获取代码失败-" + str(code_err))
                continue
            
            # 上传代码
            upload_success, upload_result = upload_plugin_code(api_url, api_cookie, plugin_name, code)
            
            if upload_success:
                success_count += 1
                success_list.append(plugin_name)
            else:
                fail_count += 1
                fail_list.append(plugin_name + ": " + str(upload_result))
        
        # 输出结果
        result_msg = "\n=====迁移完成=====\n"
        result_msg += "✅ 成功: " + str(success_count) + " 个\n"
        result_msg += "❌ 失败: " + str(fail_count) + " 个\n"
        result_msg += "⏱️ 时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        
        if success_list:
            result_msg += "------------------\n"
            result_msg += "成功列表:\n"
            result_msg += "\n".join(success_list) + "\n"
        
        if fail_list:
            result_msg += "------------------\n"
            result_msg += "失败列表:\n"
            result_msg += "\n".join(fail_list) + "\n"
        
        result_msg += "=================="
        
        sender.reply(result_msg)
        
    except Exception as e:
        sender.reply("❌ 运行出错: " + str(e))

def export_data():
    """数据导出主流程"""
    try:
        # 获取配置
        autman_url, autman_user, autman_pwd, api_url, api_user, api_pwd = get_config()
        
        if not autman_url or not autman_user or not autman_pwd:
            sender.reply("请先配置autman接口地址、用户名和密码")
            return
        
        if not api_url or not api_user or not api_pwd:
            sender.reply("请先配置目标API地址、账号和密码")
            return
        
        # 登录autman
        sender.reply("正在登录autman...")
        autman_cookie, autman_err = login_autman(autman_url, autman_user, autman_pwd)
        
        if not autman_cookie:
            sender.reply("autman登录失败: " + str(autman_err))
            return
        
        sender.reply("autman登录成功")
        
        # 登录目标服务器
        sender.reply("正在登录目标服务器...")
        api_cookie, api_err = login_target(api_url, api_user, api_pwd)
        
        if not api_cookie:
            sender.reply("目标服务器登录失败: " + str(api_err))
            return
        
        sender.reply("目标服务器登录成功")
        
        # 获取所有数据桶列表
        sender.reply("正在获取数据桶列表...")
        all_buckets = get_all_buckets(autman_url, autman_cookie)
        
        if not all_buckets:
            sender.reply("未获取到数据桶列表，请检查autman配置")
            return
        
        sender.reply("共获取到 " + str(len(all_buckets)) + " 个数据桶")
        
        # 提示输入数据桶名称
        sender.reply("=====数据导出=====\n请输入要导出的数据桶名称\n多个数据桶请换行输入\n支持通配符，如: s_yongpai_*\n------------------\n回复q退出")
        
        input_text = sender.input(120000, 20, False)
        
        if not input_text or input_text.strip().lower() == 'q':
            sender.reply("已退出导出流程")
            return
        
        # 解析输入的数据桶名称（按换行分割）
        lines = input_text.strip().split('\n')
        bucket_names = []
        
        for line in lines:
            line = line.strip()
            if line:
                # 检查是否是通配符
                if '*' in line:
                    matched = match_buckets(line, all_buckets)
                    if matched:
                        sender.reply("通配符 " + line + " 匹配到 " + str(len(matched)) + " 个数据桶")
                        bucket_names.extend(matched)
                    else:
                        sender.reply("通配符 " + line + " 未匹配到任何数据桶")
                else:
                    # 检查数据桶是否存在
                    if line in all_buckets:
                        bucket_names.append(line)
                    else:
                        sender.reply("数据桶 " + line + " 不存在，跳过")
        
        if not bucket_names:
            sender.reply("没有有效的数据桶")
            return
        
        # 去重
        bucket_names = list(set(bucket_names))
        
        sender.reply("即将导出 " + str(len(bucket_names)) + " 个数据桶:\n" + "\n".join(bucket_names))
        
        # 开始导出
        total_success = 0
        total_fail = 0
        processed_buckets = []
        skipped_count = 0
        
        for bucket_name in bucket_names:
            success, fail, skipped = export_bucket(api_url, api_cookie, bucket_name)
            if skipped:
                skipped_count += 1
            else:
                total_success += success
                total_fail += fail
                processed_buckets.append(bucket_name + ": " + str(success) + "成功/" + str(fail) + "失败")
        
        # 输出结果
        result_msg = "\n=====导出完成=====\n"
        result_msg += "处理数据桶: " + str(len(bucket_names)) + " 个\n"
        result_msg += "跳过(无数据): " + str(skipped_count) + " 个\n"
        result_msg += "成功上传: " + str(total_success) + " 条\n"
        result_msg += "上传失败: " + str(total_fail) + " 条\n"
        result_msg += "导出时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        if processed_buckets:
            result_msg += "------------------\n"
            result_msg += "\n".join(processed_buckets)
        result_msg += "\n=================="
        
        sender.reply(result_msg)
        
    except Exception as e:
        sender.reply("运行出错: " + str(e))

def main():
    """主入口函数"""
    try:
        # 获取触发消息
        content = sender.getMessage() or ''
        content = content.strip()
        
        # 根据触发指令分流
        if content in ['代码导出', '插件迁移']:
            export_code()
        else:
            # 默认为数据导出
            export_data()
        
    except Exception as e:
        sender.reply("❌ 运行出错: " + str(e))

if __name__ == "__main__":
    main()

