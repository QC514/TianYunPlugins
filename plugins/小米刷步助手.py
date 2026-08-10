# [language: python]
# [wb: true]
# [service:	<img src="https://pic.fglt.net/common/a8/common_4_verify_icon.gif">QQ：1934103887]
# [disable: false] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [priority: 0] 优先级，数字越大表示优先级越高
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
# [open_source: false]是否开源
# [public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，方便开发者测试
# [pin: false]
# [rule: ^刷步$|^刷步登录$|^定时刷步$|^一键刷步$|^刷步定时$|^取消定时$|^登录刷步$|^登陆刷步$|^刷步登陆$|^刷步解绑$]
# [version: 5.0]
# [price: 1.88]
# [author: 1934103887]
# [title: 小米刷步助手]
# [cron: ]
# [icon: https://s1.aigei.com/src/img/gif/6a/6a49e68067f449838e0cd4c842d06b51.gif?e=2051020800&token=P7S2Xpzfz11vAkASLTkfHN7Fw-oOZBecqeJaxypL:JHEdLSp6Xg9UwKY4BFQrRKRIIA0= ]
# [description: ✨功能介绍✨<br>❶：发送“刷步登录”进行绑定，发送“刷步”输入需要的步数即可<br>❷：支持单人登录or解绑操作多个账号，解绑命令为“刷步解绑”<br>❸：定时刷步or取消定时(发送“定时刷步”提交账号，管理员计划任务定时“一键刷步”) <br>🌸6.25更新：自定义代理防止使用人数过多导致刷步失败<br>🌸10.20更新：修复接口<br><img src="https://surl.fan/FvLFgs">]
# [param: {"required":true,"key":"Joh_Shuabu_config.choice","bool":false,"placeholder":"不填不走代理","name":"代理选择","desc":"填1代理池，填2API代理。不填不走代理。注：不用代理多人使用容易登录失败或刷步失败"}]
# [param: {"required":true,"key":"Joh_Shuabu_config.proxy","bool":false,"placeholder":"例：http://192.168.10.7:8081","name":"代理池","desc":"本地代理池链接"}]
# [param: {"required":true,"key":"Joh_Shuabu_config.proxy_api","bool":false,"placeholder":"例：http://api2.xkdaili.com/","name":"API代理","desc":"API代理链接"}]

import re
import time
from datetime import datetime
import requests
import json
from middleware import Sender, getSenderID, bucketGet, bucketSet, bucketAllKeys, notifyMasters

def get_timestamp():
    # 仍使用本地毫秒时间戳
    return str(int(time.time() * 1000))

def get_code(location):
    code_pattern = re.compile("(?<=access=).*?(?=&)")
    return code_pattern.findall(location)[0]

def get_app_token(login_token, proxy=None):
    url = (
        "https://account.zepp.com/v1/client/app_tokens"
        "?app_name=com.xiaomi.hm.health"
        "&dn=account.zepp.com,api-user.zepp.com,api-mifit.zepp.com,api-watch.zepp.com,"
        "app-analytics.zepp.com,api-analytics.huami.com,auth.zepp.com"
        f"&login_token={login_token}"
    )
    headers = {
        'User-Agent': 'MiFit/6.12.0 (Android; 16; Density/1.5)'
    }
    try:
        res = requests.get(url, headers=headers, proxies=proxy, timeout=15)
        if res.status_code == 200:
            j = res.json()
            return j.get('token_info', {}).get('app_token')
        return None
    except Exception as e:
        print(f"获取app_token时出错: {e}")
        return None

def login(user, passwd, proxy=None):
    is_email = bool(re.search(r'@', user))
    third_name = "huami" if is_email else "huami_phone"
    user_for_api = user if is_email else ('+86' + user)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "MiFit/6.12.0 (Android; 16; Density/1.5)",
        "app_name": "com.xiaomi.hm.health",
    }

    try:
        # 步骤1：拿 access code
        data1 = (
            f"client_id=HuaMi&country_code=CN&json_response=true&name={user_for_api}"
            f"&password={passwd}&redirect_uri=https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html"
            f"&state=REDIRECTION&token=access"
        )
        r1 = requests.post(
            f"https://api-user.zepp.com/registrations/{user_for_api}/tokens",
            data=data1, headers=headers, allow_redirects=False, proxies=proxy, timeout=15
        )
        if r1.status_code == 429:
            print("登录过于频繁，请更换IP或稍后再试")
            return None, None
        code = r1.json().get("access")
        if not code:
            return None, None

        # 步骤2：兑换 token
        data2 = (
            f"app_name=com.xiaomi.hm.health&country_code=CN&code={code}"
            "&device_id=fuck1069-2002-7869-0129-757geoi6sam1"
            "&device_model=android_phone&app_version=6.12.0"
            "&grant_type=access_token&allow_registration=false"
            "&dn=account.zepp.com,api-user.zepp.com,api-mifit.zepp.com,api-watch.zepp.com,"
            "app-analytics.zepp.com,api-analytics.huami.com,auth.zepp.com"
            "&source=com.xiaomi.hm.health"
            f"&third_name={third_name}"
        )
        r2 = requests.post(
            "https://account.zepp.com/v2/client/login",
            data=data2, headers=headers, proxies=proxy, timeout=15
        )
        if r2.status_code == 200:
            tj = r2.json()
            token_info = tj.get("token_info", {})
            login_token = token_info.get("login_token")
            user_id = token_info.get("user_id")
            if login_token and user_id:
                return login_token, user_id
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"登录过程中出错: {e}")
        return None, None
    except Exception as e:
        print(f"登录过程中出错: {e}")
        return None, None

def change_steps(user, userid, app_token, step=None, proxy=None):
    today = time.strftime("%F")

    # ================== 重要 ==================
    # 请把下面这个占位字符串替换成你自己的 data_json（URL 编码后的字符串）
    data_json = "%5B%7B%22data_hr%22%3A%22%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F9L%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2FVv%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F0v%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F9e%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F0n%5C%2Fa%5C%2F%5C%2F%5C%2FS%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F0b%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F1FK%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2FR%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F9PTFFpaf9L%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2FR%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F0j%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F9K%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2FOv%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2Fzf%5C%2F%5C%2F%5C%2F86%5C%2Fzr%5C%2FOv88%5C%2Fzf%5C%2FPf%5C%2F%5C%2F%5C%2F0v%5C%2FS%5C%2F8%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2FSf%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2Fz3%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F0r%5C%2FOv%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2FS%5C%2F9L%5C%2Fzb%5C%2FSf9K%5C%2F0v%5C%2FRf9H%5C%2Fzj%5C%2FSf9K%5C%2F0%5C%2F%5C%2FN%5C%2F%5C%2F%5C%2F%5C%2F0D%5C%2FSf83%5C%2Fzr%5C%2FPf9M%5C%2F0v%5C%2FOv9e%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2FS%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2Fzv%5C%2F%5C%2Fz7%5C%2FO%5C%2F83%5C%2Fzv%5C%2FN%5C%2F83%5C%2Fzr%5C%2FN%5C%2F86%5C%2Fz%5C%2F%5C%2FNv83%5C%2Fzn%5C%2FXv84%5C%2Fzr%5C%2FPP84%5C%2Fzj%5C%2FN%5C%2F9e%5C%2Fzr%5C%2FN%5C%2F89%5C%2F03%5C%2FP%5C%2F89%5C%2Fz3%5C%2FQ%5C%2F9N%5C%2F0v%5C%2FTv9C%5C%2F0H%5C%2FOf9D%5C%2Fzz%5C%2FOf88%5C%2Fz%5C%2F%5C%2FPP9A%5C%2Fzr%5C%2FN%5C%2F86%5C%2Fzz%5C%2FNv87%5C%2F0D%5C%2FOv84%5C%2F0v%5C%2FO%5C%2F84%5C%2Fzf%5C%2FMP83%5C%2FzH%5C%2FNv83%5C%2Fzf%5C%2FN%5C%2F84%5C%2Fzf%5C%2FOf82%5C%2Fzf%5C%2FOP83%5C%2Fzb%5C%2FMv81%5C%2FzX%5C%2FR%5C%2F9L%5C%2F0v%5C%2FO%5C%2F9I%5C%2F0T%5C%2FS%5C%2F9A%5C%2Fzn%5C%2FPf89%5C%2Fzn%5C%2FNf9K%5C%2F07%5C%2FN%5C%2F83%5C%2Fzn%5C%2FNv83%5C%2Fzv%5C%2FO%5C%2F9A%5C%2F0H%5C%2FOf8%5C%2F%5C%2Fzj%5C%2FPP83%5C%2Fzj%5C%2FS%5C%2F87%5C%2Fzj%5C%2FNv84%5C%2Fzf%5C%2FOf83%5C%2Fzf%5C%2FOf83%5C%2Fzb%5C%2FNv9L%5C%2Fzj%5C%2FNv82%5C%2Fzb%5C%2FN%5C%2F85%5C%2Fzf%5C%2FN%5C%2F9J%5C%2Fzf%5C%2FNv83%5C%2Fzj%5C%2FNv84%5C%2F0r%5C%2FSv83%5C%2Fzf%5C%2FMP%5C%2F%5C%2F%5C%2Fzb%5C%2FMv82%5C%2Fzb%5C%2FOf85%5C%2Fz7%5C%2FNv8%5C%2F%5C%2F0r%5C%2FS%5C%2F85%5C%2F0H%5C%2FQP9B%5C%2F0D%5C%2FNf89%5C%2Fzj%5C%2FOv83%5C%2Fzv%5C%2FNv8%5C%2F%5C%2F0f%5C%2FSv9O%5C%2F0ZeXv%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F1X%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F9B%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2FTP%5C%2F%5C%2F%5C%2F1b%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F0%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F9N%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2F%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%5C%2Fv7%2B%22%2C%22date%22%3A%222025-08-17%22%2C%22data%22%3A%5B%7B%22start%22%3A0%2C%22stop%22%3A1439%2C%22value%22%3A%22UA8AUBQAUAwAUBoAUAEAYCcAUBkAUB4AUBgAUCAAUAEAUBkAUAwAYAsAYB8AYB0AYBgAYCoAYBgAYB4AUCcAUBsAUB8AUBwAUBIAYBkAYB8AUBoAUBMAUCEAUCIAYBYAUBwAUCAAUBgAUCAAUBcAYBsAYCUAATIPYD0KECQAYDMAYB0AYAsAYCAAYDwAYCIAYB0AYBcAYCQAYB0AYBAAYCMAYAoAYCIAYCEAYCYAYBsAYBUAYAYAYCIAYCMAUB0AUCAAUBYAUCoAUBEAUC8AUB0AUBYAUDMAUDoAUBkAUC0AUBQAUBwAUA0AUBsAUAoAUCEAUBYAUAwAUB4AUAwAUCcAUCYAUCwKYDUAAUUlEC8IYEMAYEgAYDoAYBAAUAMAUBkAWgAAWgAAWgAAWgAAWgAAUAgAWgAAUBAAUAQAUA4AUA8AUAkAUAIAUAYAUAcAUAIAWgAAUAQAUAkAUAEAUBkAUCUAWgAAUAYAUBEAWgAAUBYAWgAAUAYAWgAAWgAAWgAAWgAAUBcAUAcAWgAAUBUAUAoAUAIAWgAAUAQAUAYAUCgAWgAAUAgAWgAAWgAAUAwAWwAAXCMAUBQAWwAAUAIAWgAAWgAAWgAAWgAAWgAAWgAAWgAAWgAAWREAWQIAUAMAWSEAUDoAUDIAUB8AUCEAUC4AXB4AUA4AWgAAUBIAUA8AUBAAUCUAUCIAUAMAUAEAUAsAUAMAUCwAUBYAWgAAWgAAWgAAWgAAWgAAWgAAUAYAWgAAWgAAWgAAUAYAWwAAWgAAUAYAXAQAUAMAUBsAUBcAUCAAWwAAWgAAWgAAWgAAWgAAUBgAUB4AWgAAUAcAUAwAWQIAWQkAUAEAUAIAWgAAUAoAWgAAUAYAUB0AWgAAWgAAUAkAWgAAWSwAUBIAWgAAUC4AWSYAWgAAUAYAUAoAUAkAUAIAUAcAWgAAUAEAUBEAUBgAUBcAWRYAUA0AWSgAUB4AUDQAUBoAXA4AUA8AUBwAUA8AUA4AUA4AWgAAUAIAUCMAWgAAUCwAUBgAUAYAUAAAUAAAUAAAUAAAUAAAUAAAUAAAUAAAUAAAWwAAUAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAeSEAeQ8AcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcBcAcAAAcAAAcCYOcBUAUAAAUAAAUAAAUAAAUAUAUAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcCgAeQAAcAAAcAAAcAAAcAAAcAAAcAYAcAAAcBgAeQAAcAAAcAAAegAAegAAcAAAcAcAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcCkAeQAAcAcAcAAAcAAAcAwAcAAAcAAAcAIAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcCIAeQAAcAAAcAAAcAAAcAAAcAAAeRwAeQAAWgAAUAAAUAAAUAAAUAAAUAAAcAAAcAAAcBoAeScAeQAAegAAcBkAeQAAUAAAUAAAUAAAUAAAUAAAUAAAcAAAcAAAcAAAcAAAcAAAcAAAegAAegAAcAAAcAAAcBgAeQAAcAAAcAAAcAAAcAAAcAAAcAkAegAAegAAcAcAcAAAcAcAcAAAcAAAcAAAcAAAcA8AeQAAcAAAcAAAeRQAcAwAUAAAUAAAUAAAUAAAUAAAUAAAcAAAcBEAcA0AcAAAWQsAUAAAUAAAUAAAUAAAUAAAcAAAcAoAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAYAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcBYAegAAcAAAcAAAegAAcAcAcAAAcAAAcAAAcAAAcAAAeRkAegAAegAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAEAcAAAcAAAcAAAcAUAcAQAcAAAcBIAeQAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcBsAcAAAcAAAcBcAeQAAUAAAUAAAUAAAUAAAUAAAUBQAcBYAUAAAUAAAUAoAWRYAWTQAWQAAUAAAUAAAUAAAcAAAcAAAcAAAcAAAcAAAcAMAcAAAcAQAcAAAcAAAcAAAcDMAeSIAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcAAAcBQAeQwAcAAAcAAAcAAAcAMAcAAAeSoAcA8AcDMAcAYAeQoAcAwAcFQAcEMAeVIAaTYAbBcNYAsAYBIAYAIAYAIAYBUAYCwAYBMAYDYAYCkAYDcAUCoAUCcAUAUAUBAAWgAAYBoAYBcAYCgAUAMAUAYAUBYAUA4AUBgAUAgAUAgAUAsAUAsAUA4AUAMAUAYAUAQAUBIAASsSUDAAUDAAUBAAYAYAUBAAUAUAUCAAUBoAUCAAUBAAUAoAYAIAUAQAUAgAUCcAUAsAUCIAUCUAUAoAUA4AUB8AUBkAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAAfgAA%22%2C%22tz%22%3A32%2C%22did%22%3A%22DA932FFFFE8816E7%22%2C%22src%22%3A24%7D%5D%2C%22summary%22%3A%22%7B%5C%22v%5C%22%3A6%2C%5C%22slp%5C%22%3A%7B%5C%22st%5C%22%3A1755407692%2C%5C%22ed%5C%22%3A1755407692%2C%5C%22dp%5C%22%3A0%2C%5C%22lt%5C%22%3A0%2C%5C%22wk%5C%22%3A0%2C%5C%22usrSt%5C%22%3A-1440%2C%5C%22usrEd%5C%22%3A-1440%2C%5C%22wc%5C%22%3A0%2C%5C%22is%5C%22%3A0%2C%5C%22lb%5C%22%3A0%2C%5C%22to%5C%22%3A0%2C%5C%22dt%5C%22%3A0%2C%5C%22rhr%5C%22%3A0%2C%5C%22ss%5C%22%3A0%7D%2C%5C%22stp%5C%22%3A%7B%5C%22ttl%5C%22%3A17760%2C%5C%22dis%5C%22%3A10627%2C%5C%22cal%5C%22%3A510%2C%5C%22wk%5C%22%3A41%2C%5C%22rn%5C%22%3A50%2C%5C%22runDist%5C%22%3A7654%2C%5C%22runCal%5C%22%3A397%2C%5C%22stage%5C%22%3A%5B%7B%5C%22start%5C%22%3A327%2C%5C%22stop%5C%22%3A341%2C%5C%22mode%5C%22%3A1%2C%5C%22dis%5C%22%3A481%2C%5C%22cal%5C%22%3A13%2C%5C%22step%5C%22%3A680%7D%2C%7B%5C%22start%5C%22%3A342%2C%5C%22stop%5C%22%3A367%2C%5C%22mode%5C%22%3A3%2C%5C%22dis%5C%22%3A2295%2C%5C%22cal%5C%22%3A95%2C%5C%22step%5C%22%3A2874%7D%2C%7B%5C%22start%5C%22%3A368%2C%5C%22stop%5C%22%3A377%2C%5C%22mode%5C%22%3A4%2C%5C%22dis%5C%22%3A1592%2C%5C%22cal%5C%22%3A88%2C%5C%22step%5C%22%3A1664%7D%2C%7B%5C%22start%5C%22%3A378%2C%5C%22stop%5C%22%3A386%2C%5C%22mode%5C%22%3A3%2C%5C%22dis%5C%22%3A1072%2C%5C%22cal%5C%22%3A51%2C%5C%22step%5C%22%3A1245%7D%2C%7B%5C%22start%5C%22%3A387%2C%5C%22stop%5C%22%3A393%2C%5C%22mode%5C%22%3A4%2C%5C%22dis%5C%22%3A1036%2C%5C%22cal%5C%22%3A57%2C%5C%22step%5C%22%3A1124%7D%2C%7B%5C%22start%5C%22%3A394%2C%5C%22stop%5C%22%3A398%2C%5C%22mode%5C%22%3A3%2C%5C%22dis%5C%22%3A488%2C%5C%22cal%5C%22%3A19%2C%5C%22step%5C%22%3A607%7D%2C%7B%5C%22start%5C%22%3A399%2C%5C%22stop%5C%22%3A414%2C%5C%22mode%5C%22%3A4%2C%5C%22dis%5C%22%3A2220%2C%5C%22cal%5C%22%3A120%2C%5C%22step%5C%22%3A2371%7D%2C%7B%5C%22start%5C%22%3A415%2C%5C%22stop%5C%22%3A427%2C%5C%22mode%5C%22%3A3%2C%5C%22dis%5C%22%3A1268%2C%5C%22cal%5C%22%3A59%2C%5C%22step%5C%22%3A1489%7D%2C%7B%5C%22start%5C%22%3A428%2C%5C%22stop%5C%22%3A433%2C%5C%22mode%5C%22%3A1%2C%5C%22dis%5C%22%3A152%2C%5C%22cal%5C%22%3A4%2C%5C%22step%5C%22%3A238%7D%2C%7B%5C%22start%5C%22%3A434%2C%5C%22stop%5C%22%3A444%2C%5C%22mode%5C%22%3A3%2C%5C%22dis%5C%22%3A2295%2C%5C%22cal%5C%22%3A95%2C%5C%22step%5C%22%3A2874%7D%2C%7B%5C%22start%5C%22%3A445%2C%5C%22stop%5C%22%3A455%2C%5C%22mode%5C%22%3A4%2C%5C%22dis%5C%22%3A1592%2C%5C%22cal%5C%22%3A88%2C%5C%22step%5C%22%3A1664%7D%2C%7B%5C%22start%5C%22%3A456%2C%5C%22stop%5C%22%3A466%2C%5C%22mode%5C%22%3A3%2C%5C%22dis%5C%22%3A1072%2C%5C%22cal%5C%22%3A51%2C%5C%22step%5C%22%3A1245%7D%2C%7B%5C%22start%5C%22%3A467%2C%5C%22stop%5C%22%3A477%2C%5C%22mode%5C%22%3A4%2C%5C%22dis%5C%22%3A1036%2C%5C%22cal%5C%22%3A57%2C%5C%22step%5C%22%3A1124%7D%2C%7B%5C%22start%5C%22%3A478%2C%5C%22stop%5C%22%3A488%2C%5C%22mode%5C%22%3A3%2C%5C%22dis%5C%22%3A488%2C%5C%22cal%5C%22%3A19%2C%5C%22step%5C%22%3A607%7D%2C%7B%5C%22start%5C%22%3A489%2C%5C%22stop%5C%22%3A499%2C%5C%22mode%5C%22%3A4%2C%5C%22dis%5C%22%3A2220%2C%5C%22cal%5C%22%3A120%2C%5C%22step%5C%22%3A2371%7D%2C%7B%5C%22start%5C%22%3A500%2C%5C%22stop%5C%22%3A511%2C%5C%22mode%5C%22%3A3%2C%5C%22dis%5C%22%3A1268%2C%5C%22cal%5C%22%3A59%2C%5C%22step%5C%22%3A1489%7D%2C%7B%5C%22start%5C%22%3A512%2C%5C%22stop%5C%22%3A522%2C%5C%22mode%5C%22%3A1%2C%5C%22dis%5C%22%3A152%2C%5C%22cal%5C%22%3A4%2C%5C%22step%5C%22%3A238%7D%5D%7D%2C%5C%22goal%5C%22%3A8000%2C%5C%22tz%5C%22%3A%5C%2228800%5C%22%7D%22%2C%22source%22%3A24%2C%22type%22%3A0%7D%5D"
    # =========================================

    # 保持原有替换逻辑（当你的 data_json 模板含有 date / ttl 字段时生效）
    try:
        finddate = re.compile(r'.*?date%22%3A%22(.*?)%22%2C%22data.*?')
        findstep = re.compile(r'.*?ttl%5C%22%3A(.*?)%2C%5C%22dis.*?')
        if finddate.findall(data_json):
            data_json = re.sub(finddate.findall(data_json)[0], today, str(data_json))
        if step is not None and findstep.findall(data_json):
            data_json = re.sub(findstep.findall(data_json)[0], step, str(data_json))
    except Exception as _:
        # 如果用户粘贴的是不同结构，直接按原样提交
        pass

    url = f"https://api-mifit-cn.huami.com/v1/data/band_data.json?t={get_timestamp()}"
    head = {"apptoken": app_token, "Content-Type": "application/x-www-form-urlencoded"}
    data = f"userid={userid}&last_sync_data_time=1597306380&device_type=0&last_deviceid=DA932FFFFE8816E7&data_json={data_json}"
    try:
        response = requests.post(url, data=data, headers=head, proxies=proxy, timeout=15)
        return True if response.status_code == 200 else False
    except Exception as e:
        print(f"修改步数时出错: {e}")
        return False

def mask_mobile(mobile):
    return f"{mobile[:3]}****{mobile[7:]}" if len(mobile) == 11 else mobile

def handle_input_timeout_or_cancel(sender, input_result):
    if not input_result:
        sender.reply("输入超时！")
        return True
    elif input_result.lower() == 'q':
        sender.reply("已取消操作")
        return True
    return False

def get_proxy():
    choice = bucketGet('Joh_Shuabu_config', 'choice')
    if choice == '1':
        proxy = bucketGet('Joh_Shuabu_config', 'proxy')
        if not proxy:
            return None
        if not proxy.startswith('http://') and not proxy.startswith('https://'):
            proxy = 'http://' + proxy
        return {"http": proxy, "https": proxy}
    elif choice == '2':
        proxy_api = bucketGet('Joh_Shuabu_config', 'proxy_api')
        if not proxy_api:
            return None
        try:
            response = requests.get(proxy_api, timeout=15)
            if response.status_code == 200:
                proxy = response.text.strip()
                if proxy:
                    return {"http": f'http://{proxy}', "https": f'http://{proxy}'}
        except Exception as e:
            print(f'获取API代理失败: {str(e)}')
            return None
    return None

def shuabu_login(sender):
    sender.reply("请输入您的小米账号 (手机号或邮箱)：")
    mobile = sender.input(120000, 0, False)
    if handle_input_timeout_or_cancel(sender, mobile):
        return

    sender.reply("请输入您的密码 (请勿使用#号)：")
    password = sender.input(120000, 0, False)
    if handle_input_timeout_or_cancel(sender, password):
        return

    max_retries = 6
    for retry in range(1, max_retries + 1):
        proxy = get_proxy()
        login_token, userid = login(mobile, password, proxy)
        if login_token:
            break
        time.sleep(0)
    else:
        sender.reply("账号密码错误，请检查后重新绑定\n（需使用在ZeppLife APP注册的账号，而不是小米账号）")
        return

    # 登录成功，保存账号
    user_id = sender.getUserID()
    account_info = bucketGet(bucket='Joh_Shuabu_account', key=user_id)

    updated = False
    if account_info:
        accounts = account_info.split('&')
        for i, acc in enumerate(accounts):
            exist_mobile, _ = acc.split('#')
            if exist_mobile == mobile:
                accounts[i] = f"{mobile}#{password}"
                updated = True
                break
        if not updated:
            accounts.append(f"{mobile}#{password}")
        account_info = '&'.join(accounts)
    else:
        account_info = f"{mobile}#{password}"

    bucketSet(bucket='Joh_Shuabu_account', key=user_id, value=account_info)
    sender.reply("账号密码更新成功！" if updated else "账号登录成功！")

def select_accounts(sender):
    user_id = sender.getUserID()
    account_info = bucketGet(bucket='Joh_Shuabu_account', key=user_id)
    if not account_info:
        sender.reply("未查询到账号，请发‘刷步登录’")
        return None
    
    accounts = account_info.split('&')
    masked_accounts = [f"【{i+1}】{mask_mobile(acc.split('#')[0])}" for i, acc in enumerate(accounts)]
    masked_accounts.insert(0, "【0】全部")
    account_list = "\n".join(masked_accounts)
    
    sender.reply(f"请选择要刷步的账号，多选用逗号隔开：\n{account_list}")
    selection = sender.input(120000, 0, False)
    if handle_input_timeout_or_cancel(sender, selection):
        return None
    
    selected_indices = []
    try:
        if selection == '0':
            selected_indices = list(range(len(accounts)))
        else:
            indices = selection.split(',')
            for idx in indices:
                idx = int(idx.strip())
                if 1 <= idx <= len(accounts):
                    selected_indices.append(idx - 1)
    except:
        sender.reply("输入的账号选择无效，请重新输入数字序号。")
        return None
    
    selected_accounts = [accounts[i] for i in selected_indices] if selected_indices else []
    if not selected_accounts:
        sender.reply("未选择有效的账号。")
        return None
    
    return selected_accounts

def schedule_brush_steps(sender):
    selected_accounts = select_accounts(sender)
    if not selected_accounts:
        return
    
    sender.reply("请输入定时刷步的步数：")
    step = sender.input(120000, 0, False)
    if handle_input_timeout_or_cancel(sender, step):
        return
    
    schedule_data = []
    for account in selected_accounts:
        mobile, password = account.split('#')
        schedule_data.append({
            "mobile": mobile,
            "password": password,
            "step": step
        })
    
    user_id = sender.getUserID()
    bucketSet(bucket='Joh_Shuabu', key=user_id, value=json.dumps(schedule_data))
    sender.reply(f"定时设置成功，步数：{step}\n停止任务发“取消定时”")

def cancel_schedule(sender):
    user_id = sender.getUserID()
    schedule_data_str = bucketGet(bucket='Joh_Shuabu', key=user_id)
    if not schedule_data_str:
        sender.reply("未找到定时刷步任务")
        return
    
    schedule_data = json.loads(schedule_data_str)
    
    if not schedule_data:
        sender.reply("未找到定时刷步任务")
        return
    
    # Extract mobile numbers for display
    mobiles = [f"【{i+1}】{mask_mobile(acc['mobile'].split('#')[0])}" for i, acc in enumerate(schedule_data)]
    mobiles.insert(0, "【0】全部")
    mobile_list = "\n".join(mobiles)
    
    sender.reply(f"请选择要取消定时的账号，多选用逗号隔开：\n{mobile_list}")
    selection = sender.input(120000, 0, False)
    if handle_input_timeout_or_cancel(sender, selection):
        return
    
    selected_indices = []
    try:
        if selection == '0':
            selected_indices = list(range(len(schedule_data)))
        else:
            indices = selection.split(',')
            for idx in indices:
                idx = int(idx.strip())
                if 1 <= idx <= len(schedule_data):
                    selected_indices.append(idx - 1)
    except:
        sender.reply("输入的账号选择无效，请重新输入数字序号。")
        return
    
    if not selected_indices:
        sender.reply("未选择有效的账号。")
        return
    
    # Remove selected accounts from schedule_data
    for idx in sorted(selected_indices, reverse=True):
        del schedule_data[idx]
    
    # Update the schedule_data in the bucket
    if schedule_data:
        bucketSet(bucket='Joh_Shuabu', key=user_id, value=json.dumps(schedule_data))
        sender.reply("已取消选定账号的定时任务")
    else:
        bucketSet(bucket='Joh_Shuabu', key=user_id, value='')
        sender.reply("已取消所有定时刷步任务")

def one_key_brush_steps(sender):
    if not sender.isAdmin():
        sender.reply("只有管理员可以执行此命令")
        return
    
    user_ids = bucketAllKeys(bucket='Joh_Shuabu')
    if not user_ids:
        sender.reply("未找到定时刷步任务")
        return
    
    success_count = 0
    for user_id in user_ids:
        schedule_data_str = bucketGet(bucket='Joh_Shuabu', key=user_id)
        if not schedule_data_str:
            continue
        
        try:
            schedule_data = json.loads(schedule_data_str)
            for data in schedule_data:
                mobile = data.get("mobile")
                password = data.get("password")
                step = data.get("step")
                
                proxy = get_proxy()
                login_token, userid = login(mobile, password, proxy)
                if login_token:
                    app_token = get_app_token(login_token, proxy)
                    if app_token:
                        if change_steps(mobile, userid, app_token, step, proxy):
                            success_count += 1
                        else:
                            # 刷步失败，尝试重试
                            retry_count = 0
                            max_retries = 6  # 最大重试次数
                            while retry_count < max_retries:
                                retry_count += 1
                                # 根据代理方式决定是否重新获取代理
                                choice = bucketGet('Joh_Shuabu_config', 'choice')
                                if choice == '2':  # API代理
                                    proxy = get_proxy()  # 重新获取API代理
                                
                                login_token, userid = login(mobile, password, proxy)
                                if login_token:
                                    app_token = get_app_token(login_token, proxy)
                                    if app_token:
                                        if change_steps(mobile, userid, app_token, step, proxy):
                                            success_count += 1
                                            break
                                time.sleep(0)
        except Exception as e:
            print(f"处理用户 {user_id} 的定时任务时出错: {e}")
    
    # 通知管理员
    imtypes = ["qq", "wx", "tg"]  # 指定要推送的平台列表
    notifyMasters(f"一键刷步完成，成功：{success_count}个账号", imtypes=imtypes)
    
    sender.reply(f"一键刷步完成，成功：{success_count}个账号")

def brush_steps(sender):
    selected_accounts = select_accounts(sender)
    if not selected_accounts:
        return
    
    sender.reply("请输入需要的步数：\n(最高98800步)")
    step = sender.input(120000, 0, False)
    if handle_input_timeout_or_cancel(sender, step):
        return
    
    # 增加提示信息
    sender.reply("正在进行刷步...请稍后")
    
    success_count = 0
    for account in selected_accounts:
        mobile, password = account.split('#')
        刷步成功 = False  # 确保这一行的缩进正确
        retry_count = 0
        max_retries = 6
        
        while retry_count < max_retries and not 刷步成功:
            retry_count += 1
            # 根据代理方式获取代理
            proxy = get_proxy()
            
            # 获取 login_token（新接口）
            login_token, userid = login(mobile, password, proxy)
            if not login_token:
                if retry_count >= max_retries:
                    sender.reply(f"账号 {mask_mobile(mobile)} 刷步失败，获取login_token失败")
                continue
            
            # 获取 app_token（新接口）
            app_token = get_app_token(login_token, proxy)
            if not app_token:
                if retry_count >= max_retries:
                    sender.reply(f"账号 {mask_mobile(mobile)} 刷步失败，获取app_token失败")
                continue
            
            # 执行刷步操作
            if change_steps(mobile, userid, app_token, step, proxy):
                success_count += 1
                刷步成功 = True
            else:
                if retry_count >= max_retries:
                    sender.reply(f"账号 {mask_mobile(mobile)} 执行刷步操作失败")
    if success_count > 0:
        sender.reply(f"刷步完成，步数：{step}\n成功：{success_count}个账号\n若微信步数未同步是因为Zepp没绑定设备\n（小米手环等运动设备）")
def unbind_accounts(sender):
    user_id = sender.getUserID()
    account_info = bucketGet(bucket='Joh_Shuabu_account', key=user_id)
    if not account_info:
        sender.reply("未查询到已绑定的账号")
        return
    
    accounts = account_info.split('&')
    masked_accounts = [f"【{i+1}】{mask_mobile(acc.split('#')[0])}" for i, acc in enumerate(accounts)]
    masked_accounts.insert(0, "【0】全部")
    account_list = "\n".join(masked_accounts)
    
    sender.reply(f"请选择要解绑的账号，多选用逗号隔开：\n{account_list}")
    selection = sender.input(120000, 0, False)
    if handle_input_timeout_or_cancel(sender, selection):
        return
    
    selected_indices = []
    try:
        if selection == '0':
            selected_indices = list(range(len(accounts)))
        else:
            indices = selection.split(',')
            for idx in indices:
                idx = int(idx.strip())
                if 1 <= idx <= len(accounts):
                    selected_indices.append(idx - 1)
    except:
        sender.reply("输入的账号选择无效，请重新输入数字序号。")
        return
    
    if not selected_indices:
        sender.reply("未选择有效的账号。")
        return
    
    # Remove selected accounts from the list
    for idx in sorted(selected_indices, reverse=True):
        del accounts[idx]
    
    if accounts:
        bucketSet(bucket='Joh_Shuabu_account', key=user_id, value='&'.join(accounts))
        sender.reply("账号解绑成功")
    else:
        bucketSet(bucket='Joh_Shuabu_account', key=user_id, value='')
        sender.reply("所有账号已解绑")

def main(sender):
    usermessage = sender.getMessage().strip().lower()
    message_mapping = {
        "刷步登录": shuabu_login,
        "登录刷步": shuabu_login,
        "刷步登陆": shuabu_login,
        "登陆刷步": shuabu_login,
        "定时刷步": schedule_brush_steps,
        "刷步定时": schedule_brush_steps,
        "一键刷步": one_key_brush_steps,
        "取消定时": cancel_schedule,
        "刷步": brush_steps,
        "刷步解绑": unbind_accounts
    }
    message_mapping.get(usermessage, lambda s: sender.reply("未识别的指令"))(sender)

if __name__ == "__main__":
    senderID = getSenderID()
    sender = Sender(senderID)
    main(sender)