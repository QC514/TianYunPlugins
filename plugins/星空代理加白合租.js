#[pin:false]
#[title: 星空代理加白合租]
#[language: python]
#[class: 工具类]
#[author: qingge]
#[service: 97393412]
#[disable:false]
#[admin: true]
#[rule: 星空代理加白]
#[priority: 999999]
#[cron: */15 0-23 * * *]
#[open_source: false]
#[version: 8.6]
#[public: true]
#[price: 999]
#[description: 指令：星空代理加白,（可自行修改定时，如果IP有变动才会执行加白）。]
#[param: {"required":false,"key":"xkpc.xkdailiIP_URL","bool":false,"placeholder":"http://myip.ipip.net","name":"获取本机IP接口","desc":"可选http://42.194.132.65:5010,http://myip.ipip.net,http://cip.cc 任选其一，不填默认http://myip.ipip.net"}]
#[param: {"required":false,"key":"xkpc.xkdailiwhiteIP","bool":false,"placeholder":"无需填写","name":"当前白名单IP","desc":"无需填写，用于记录白名单IP，手动填写任意IP，再执行加白，可马上覆盖IP。"}]
#[param: {"required":false,"key":"xkpc.xkdailiwhiteIPCaches","bool":false,"placeholder":"无需填写","name":"近期白名单IP缓存","desc":"无需填写，用于记录白名单IP"}]
#[param: {"required":false,"key":"xkpc.xkdailiLastSuccessTime","bool":false,"placeholder":"无需填写","name":"上次加白成功时间","desc":"无需填写，用于记录上次成功加白的时间戳"}]

import requests
import logging
import middleware
import re
import json
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置参数
#APIKEY = middleware.bucketGet(bucket="xkpc", key="xkdaili_apikey")
#SIGN = middleware.bucketGet(bucket="xkpc", key="xkdaili_sign")

APIKEY = "XK8480FB3B4F593C4029"
SIGN = "ac04f16fd2a4a1c82de09ba0215b8252"
LAST_IP = middleware.bucketGet(bucket="xkpc", key="xkdailiwhiteIP") or ""
CACHE_IPS = middleware.bucketGet(bucket="xkpc", key="xkdailiwhiteIPCaches") or ""
HISTORY_IPS = [ip.strip() for ip in CACHE_IPS.split(",") if ip.strip()] if CACHE_IPS else []
LAST_SUCCESS_TIME = middleware.bucketGet(bucket="xkpc", key="xkdailiLastSuccessTime") or ""

# API配置
BASE_URL = "http://api2.xkdaili.com/tools/XApi.ashx"
GET_IP_URL = middleware.bucketGet(bucket="xkpc", key="xkdailiIP_URL") or "http://myip.ipip.net"
#GET_IP_URL = "http://myip.ipip.net"

# 日志配置
LOGS = []  # 统一存储所有日志
STATUS_ICONS = {
    "success": "✅",
    "info": "ℹ️",
    "warning": "⚠️",
    "error": "❌",
    "debug": "🐞"
}

def init_logger():
    """初始化日志处理器"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 清除已有处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

def log(message, icon="info"):
    """统一日志记录函数"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"{STATUS_ICONS.get(icon, '')} [{timestamp}] {message}"
    LOGS.append(formatted_msg)
    logging.info(formatted_msg)

def is_valid_ip(ip):
    """验证IP地址格式是否合法"""
    pattern = r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$"
    if not re.match(pattern, ip):
        return False
    
    # 检查每个数字是否在0-255范围内
    return all(0 <= int(octet) <= 255 for octet in ip.split("."))

def get_current_ip():
    """获取公网IP（从特定格式文本中解析）"""
    try:
        response = requests.get(GET_IP_URL, timeout=10)
        response.raise_for_status()
        raw_text = response.text.strip()
        
        # 方案1：直接解析已知格式
        if "当前 IP：" in raw_text:
            ip_start = raw_text.find("：") + 1
            ip_end = raw_text.find(" ", ip_start)
            if ip_end == -1:  # 没有找到空格
                ip_end = None
            ip = raw_text[ip_start:ip_end].strip()
            if is_valid_ip(ip):
                return ip
        
        # 方案2：正则匹配作为回退
        ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', raw_text)
        if ip_match:
            ip = ip_match.group(0)
            if is_valid_ip(ip):
                return ip
            
        log(f"IP解析失败: {raw_text[:50]}...", "error")
        return None
    except Exception as e:
        log(f"IP获取失败: {str(e)}", "error")
        return None

def batch_delete_ips(ip_list):
    """批量删除IP列表（星空代理API支持逗号分隔）"""
    if not ip_list:
        log("无有效IP需要删除", "info")
        return True, "空列表跳过"

    # 过滤无效IP并去重
    valid_ips = [ip for ip in set(ip_list) if is_valid_ip(ip)]
    if not valid_ips:
        log("无有效IP需要删除", "warning")
        return False, "无有效IP"

    ip_param = ",".join(valid_ips)
    log(f"批量删除 {len(valid_ips)}个IP: {ip_param}", "info")
    
    try:
        params = {
            "apikey": APIKEY,
            "sign": SIGN,
            "type": "delwhiteip",
            "flag": 8,
            "ip": ip_param
        }
        response = requests.get(BASE_URL, params=params, verify=False, timeout=20)
        response.raise_for_status()
        
        # 解析响应
        try:
            res_data = response.json()
            status_code = res_data.get("status")
            info_msg = res_data.get("info", "无返回信息")
        except json.JSONDecodeError:
            res_data = None
            status_code = response.status_code
            info_msg = response.text[:150] + "..." if len(response.text) > 150 else response.text
        
        # 关键：仅当明确返回删除成功时才视为成功
        if status_code == 100:  # 100=成功
            log(f"批量删除成功: {info_msg}", "success")
            return True, "success"
        else:
            log(f"删除失败: {info_msg}", "error")
            return False, info_msg
    except Exception as e:
        #log(f"API请求异常: {str(e)}", "error")
        return False, str(e)

def handle_white_ip(ip, operation):
    """执行加白操作"""
    try:
        params = {
            "apikey": APIKEY,
            "sign": SIGN,
            "type": f"{operation}whiteip",
            "flag": 8,
            "ip": ip
        }
        
        response = requests.get(BASE_URL, params=params, verify=False, timeout=15)
        response.raise_for_status()
        
        # 尝试解析JSON响应
        try:
            res_data = response.json()
            status_code = res_data.get("status")
            info_msg = res_data.get("info", "无返回信息")
        except json.JSONDecodeError:
            res_data = None
            status_code = response.status_code
            info_msg = response.text[:150] + "..." if len(response.text) > 150 else response.text
        
        success = False
        if operation == "add":
            # 关键：仅当明确返回成功时才视为成功
            success = status_code == 100  # 100=成功
            log_type = "success" if success else "error"
            log(f"添加操作: {info_msg}", log_type)
        
        return success, info_msg
    except requests.exceptions.RequestException as e:
        #log(f"API请求失败: {str(e)}", "error")
        return False, str(e)
    except Exception as e:
        #log(f"未知错误: {str(e)}", "error")
        return False, str(e)

def update_ip_record(ip):
    """更新当前IP存储记录"""
    try:
        middleware.bucketSet(bucket="xkpc", key="xkdailiwhiteIP", value=ip)
        log("当前IP配参已更新", "success")
        return True
    except Exception as e:
        log(f"存储更新失败: {str(e)}", "error")
        return False

def update_ip_cache(ip):
    """更新IP缓存记录（保留最近5个）"""
    global HISTORY_IPS
    
    try:
        if not is_valid_ip(ip):
            log(f"无效IP格式，不更新缓存: {ip}", "warning")
            return False
        
        # 移除现有相同IP
        HISTORY_IPS = [existing_ip for existing_ip in HISTORY_IPS if existing_ip != ip]
        
        # 在列表开头添加新IP
        HISTORY_IPS.insert(0, ip)
        
        # 限制只保留最近3个
        HISTORY_IPS = HISTORY_IPS[:5]
        
        # 保存到配参
        cache_value = ",".join(HISTORY_IPS)
        middleware.bucketSet(bucket="xkpc", key="xkdailiwhiteIPCaches", value=cache_value)
        log(f"IP缓存已更新: {cache_value}", "success")
        return True
    except Exception as e:
        log(f"缓存更新失败: {str(e)}", "error")
        return False

def clear_ip_cache():
    """清空IP缓存记录"""
    global HISTORY_IPS
    
    try:
        HISTORY_IPS = []
        middleware.bucketSet(bucket="xkpc", key="xkdailiwhiteIPCaches", value="")
        log("IP缓存已清空", "success")
        return True
    except Exception as e:
        log(f"缓存清空失败: {str(e)}", "error")
        return False

def update_success_time():
    """更新加白成功时间记录"""
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        middleware.bucketSet(bucket="xkpc", key="xkdailiLastSuccessTime", value=current_time)
        log(f"加白成功时间已更新: {current_time}", "success")
        return current_time
    except Exception as e:
        log(f"时间记录更新失败: {str(e)}", "error")
        return None

def get_formatted_time_display(time_str):
    """格式化时间显示"""
    if not time_str:
        return "从未加白"
    
    try:
        # 计算距离当前时间的时间差
        time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        time_diff = now - time_obj
        
        # 根据时间差显示不同的格式
        if time_diff.days == 0:
            if time_diff.seconds < 60:
                return f"{time_str} (刚刚)"
            elif time_diff.seconds < 3600:
                minutes = time_diff.seconds // 60
                return f"{time_str} ({minutes}分钟前)"
            else:
                hours = time_diff.seconds // 3600
                return f"{time_str} ({hours}小时前)"
        elif time_diff.days == 1:
            return f"{time_str} (昨天)"
        elif time_diff.days < 7:
            return f"{time_str} ({time_diff.days}天前)"
        else:
            weeks = time_diff.days // 7
            return f"{time_str} ({weeks}周前)"
    except Exception:
        return time_str

def check_ip_change(current_ip):
    """检测IP是否发生变化"""
    if not LAST_IP or LAST_IP == "0.0.0.0":
        log(f"首次运行或重置状态，当前IP: {current_ip}", "info")
        return True
    
    if current_ip != LAST_IP:
        log(f"检测到IP变化: {LAST_IP} → {current_ip}", "info")
        return True
    
    log(f"IP未变化: {current_ip}", "info")
    return False

def format_final_report(current_success_time=None):
    """生成最终执行报告"""
    # 获取时间显示信息
    last_time_display = get_formatted_time_display(LAST_SUCCESS_TIME)
    current_time_display = get_formatted_time_display(current_success_time) if current_success_time else "本次未加白"
    
    report = [
        "✨ 星空代理加白执行报告 ✨",
        f"🕒 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"⏰ 上次加白成功时间: {last_time_display}",
        f"🔄 本次加白成功时间: {current_time_display}",
        f"----------------------------------- ",
        "",
        "📝 详细执行日志:"
    ]
    report.extend(LOGS[-10:])  # 显示最后10条日志
    #report.append(f"📚 近期加白IP缓存: {', '.join(HISTORY_IPS) if HISTORY_IPS else '无'}")
    return "\n".join(report)

def main():
    init_logger()  # 初始化日志配置
    log("星空代理加白服务启动", "info")
    log(f"上次记录IP: {LAST_IP if LAST_IP else '无'}", "debug")
    log(f"近期加白IP缓存: {', '.join(HISTORY_IPS) if HISTORY_IPS else '无'}", "debug")
    #log(f"上次加白成功时间: {LAST_SUCCESS_TIME if LAST_SUCCESS_TIME else '无记录'}", "debug")
    
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    
    # 获取当前IP
    current_ip = get_current_ip()
    if not current_ip:
        log("无法获取公网IP，终止流程", "error")
        sender.reply("\n".join(LOGS))
        return
    
    current_success_time = None
    
    # 仅当IP变化时才执行操作
    if check_ip_change(current_ip):
        # 合并待删除IP：历史缓存 + 最后一次记录IP
        all_del_ips = list(set(HISTORY_IPS + ([LAST_IP] if LAST_IP else [])))
        
        # 执行批量删除（仅当有需要删除的IP时）
        if all_del_ips:
            del_success, del_msg = batch_delete_ips(all_del_ips)
            
            # 关键修改：仅当批量删除成功时才继续执行加白操作
            if not del_success:
                log("批量删除失败，跳过加白操作", "error")
                # 生成报告并退出
                report = format_final_report(current_success_time)
                sender.reply(report)
                return
            
            # 删除成功后清空缓存
            #clear_ip_cache()
        
        # 添加新IP
        log(f"添加新IP: {current_ip}", "info")
        add_success, add_msg = handle_white_ip(current_ip, "add")
        
        if add_success:
            # 更新记录
            update_ip_record(current_ip)
            update_ip_cache(current_ip)
            current_success_time = update_success_time()  # 新增：记录成功时间
            log("新IP添加成功", "success")
        else:
            log(f"添加新IP失败: {add_msg}", "error")
    else:
        log("IP未变化，跳过加白操作", "info")
    
    # 生成并发送报告
    report = format_final_report(current_success_time)
    sender.reply(report)

if __name__ == "__main__":
    main()