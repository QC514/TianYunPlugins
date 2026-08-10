# [title: 【必装】Vorto插件依赖]
# [language: python]
# [class: 工具类]
# [service: 203066880]
# [author: rujingxianghai]
# [rule: ^(vorto|Vorto)(初始化|下载|更新|清理)$]
# [cron: ]
# [priority: 0]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://img.xxkx.de/file/eYvOjFXl.jpg]
# [version: 3.6]
# [public: true]
# [price: 0]
# [description: Vorto工具模块初始化<br>自动安装/更新 vorto_utils 公共模块（通过pip）<br>专门清理旧版 vorto_utils 文件残留<br>指令：Vorto初始化、Vorto更新、Vorto清理]

# [param: {"required":false,"key":"s_vorto.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"青龙容器配置","desc":"青龙容器参数用丨分割"}]
# [param: {"required":false,"key":"s_vorto.dpname","bool":false,"placeholder":"Host丨AppKey丨AppSecret","name":"DumbPanel容器配置","desc":"DumbPanel容器参数用丨分割"}]
# [param: {"required":false,"key":"s_vorto.ma_pay_gateway","bool":false,"placeholder":"https://pay.example.com","name":"码支付网关","desc":"码支付网关地址"}]
# [param: {"required":false,"key":"s_vorto.ma_pay_pid","bool":false,"placeholder":"1001","name":"码支付商户ID","desc":"码支付PID"}]
# [param: {"required":false,"key":"s_vorto.ma_pay_key","bool":false,"placeholder":"","name":"码支付密钥","desc":"码支付商户密钥"}]
# [param: {"required":false,"key":"s_vorto.ma_pay_notify_url","bool":false,"placeholder":"https://pay.example.com/notify","name":"码支付异步通知","desc":"码支付异步通知地址"}]
# [param: {"required":false,"key":"s_vorto.ma_pay_return_url","bool":false,"placeholder":"https://pay.example.com/return","name":"码支付同步跳转","desc":"码支付同步跳转地址"}]
# [param: {"required":false,"key":"s_vorto.ma_pay_switch","bool":true,"placeholder":"","name":"码支付功能","desc":"开启后使用码支付"}]
# [param: {"required":false,"key":"s_vorto.qr_pay_switch","bool":true,"placeholder":"","name":"扫码支付功能","desc":"开启后使用收款码扫码支付"}]
# [param: {"required":false,"key":"s_vorto.zsm","bool":false,"placeholder":"http://xxx.jpg","name":"收款码链接","desc":"扫码支付收款码图片链接"}]
# [param: {"required":false,"key":"s_vorto.pay_types","bool":false,"placeholder":"alipay:支付宝,wxpay:微信支付,qqpay:QQ钱包","name":"码支付方式","desc":"码支付可用方式，格式：类型:名称，多个用逗号分隔"}]

import os
import subprocess
import sys
import middleware

# ==================== 配置 ====================
PACKAGE_NAME = "vorto_utils"
LEGACY_FILES = [
    "/autMan/plugin/scripts/vorto_utils.py",
    "/autMan/plugin/.tmpfs/vorto_utils.py",
]  # 旧版文件残留路径

# ==================== 初始化 ====================
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)


def clean_legacy_files():
    """专门清理旧版 vorto_utils 文件残留"""
    removed_files = []
    failed_files = []

    for legacy_file in LEGACY_FILES:
        if not os.path.exists(legacy_file):
            continue

        try:
            os.remove(legacy_file)
            removed_files.append(legacy_file)
        except Exception as e:
            failed_files.append((legacy_file, str(e)))

    if removed_files:
        sender.reply(
            "=====清理完成=====\n"
            "🧹 已删除以下旧文件:\n"
            + "\n".join(removed_files)
            + "\n=================="
        )
    elif not failed_files:
        sender.reply(
            "=====无需清理=====\n"
            "未发现旧版 vorto_utils 文件残留\n"
            "=================="
        )

    if failed_files:
        sender.reply(
            "=====清理失败=====\n"
            "⚠️ 以下文件删除失败:\n"
            + "\n".join(f"{path}\n原因: {error}" for path, error in failed_files)
            + "\n请手动删除后重试\n"
            + "=================="
        )

    return not failed_files


def run_pip_command(args):
    """执行pip命令"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip"] + args,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)


def get_installed_version():
    """获取已安装的模块版本（通过pip show）"""
    try:
        success, stdout, stderr = run_pip_command(["show", PACKAGE_NAME])
        if success and stdout:
            for line in stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        return None
    except Exception:
        return None


def install_package():
    """安装模块"""
    sender.reply("🔄 正在安装 vorto_utils 模块...")
    success, stdout, stderr = run_pip_command(["install", "--no-cache-dir", PACKAGE_NAME])

    if success:
        version = get_installed_version()
        sender.reply(
            f"=====安装成功=====\n"
            f"📦 {PACKAGE_NAME}\n"
            f"📌 版本: {version}\n"
            f"✅ 可在插件中使用:\n"
            f"  import vorto_utils\n"
            f"=================="
        )
        return True
    else:
        sender.reply(
            f"=====安装失败=====\n"
            f"❌ 错误信息:\n"
            f"{stderr[:500]}\n"
            f"=================="
        )
        return False


def upgrade_package(old_version=None):
    """升级模块，对比前后版本号判断是否真正更新"""
    sender.reply("🔄 正在升级 vorto_utils 模块...")
    success, stdout, stderr = run_pip_command(["install", "--upgrade", "--no-cache-dir", PACKAGE_NAME])

    if success:
        new_version = get_installed_version()
        if old_version and new_version and old_version != new_version:
            sender.reply(
                f"=====升级成功=====\n"
                f"📦 {PACKAGE_NAME}\n"
                f"📌 {old_version} → {new_version}\n"
                f"✅ 模块已更新\n"
                f"=================="
            )
        else:
            sender.reply(
                f"=====已是最新=====\n"
                f"📦 {PACKAGE_NAME}\n"
                f"📌 当前版本: {new_version}\n"
                f"✅ 无需更新\n"
                f"=================="
            )
        return True
    else:
        sender.reply(
            f"=====升级失败=====\n"
            f"❌ 错误信息:\n"
            f"{stderr[:500]}\n"
            f"=================="
        )
        return False


def main():
    """主入口"""
    msg = sender.getMessage()

    if '清理' in msg:
        clean_legacy_files()
        return

    if '初始化' in msg or '下载' in msg or '更新' in msg:
        installed_version = get_installed_version()

        # 模块未安装
        if installed_version is None:
            sender.reply(
                "=====模块未安装=====\n"
                f"📦 {PACKAGE_NAME}\n"
                "准备从PyPI安装...\n"
                "=================="
            )
            install_package()
            return

        # 模块已安装，检查更新
        if '更新' in msg:
            sender.reply(
                "=====当前状态=====\n"
                f"📦 {PACKAGE_NAME}\n"
                f"📌 本地版本: {installed_version}\n"
                "------------------\n"
                "是否检查并升级到最新版？\n"
                "回复 y 确认\n"
                "回复 q 取消\n"
                "=================="
            )

            confirm = sender.input(60000, 1, False)
            if not confirm or confirm.lower() != 'y':
                sender.reply("✅ 已取消")
                return

            upgrade_package(old_version=installed_version)
        else:
            # 初始化/下载指令，模块已存在
            sender.reply(
                "=====模块已安装=====\n"
                f"📦 {PACKAGE_NAME}\n"
                f"📌 版本: {installed_version}\n"
                "------------------\n"
                "如需更新，发送 \"Vorto更新\"\n"
                "如需清理旧文件，发送 \"Vorto清理\"\n"
                "=================="
            )
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
