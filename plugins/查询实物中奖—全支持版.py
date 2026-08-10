# [title: 查询实物中奖—全支持版]
# [language: python]
# [author: ahhhahh]
# [class: 工具类]
# [service: 2565720211] 售后联系方式
# [disable:true] 禁用开关，true表示禁用，false表示可用
# [admin: true] 是否为管理员指令
# [rule: ^实物查询$] 匹配规则，多个规则时向下依次写多个
# [rule: ^实物汇总( \d+)?$] 匹配规则，多个规则时向下依次写多个
# [priority: 99999] 优先级，数字越大表示优先级越高
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
# [open_source: false]是否开源
# [version: 1.3.0]版本号
# [public:true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [price: 3.66] 上架价格
# [description: 指令：实物查询，实物汇总。支持faker3，9R，M库。只支持autman目前，如果你是青龙请勿购买。可以自定义汇总天数，默认汇总5天。每次运行都会备份数据并删除源数据，备份数据文件夹在autman/task/scripts下。更新了源数据备份，可溯源数据] 使用方法尽量写具体

import csv
import os
import shutil

import middleware
from collections import defaultdict
from datetime import datetime, timedelta

# 定义数据源配置
DATA_SOURCES = {
    "faker3": {
        "source_path": "/autMan/task/scripts/shufflewzc_faker3/utils/prize/addr_record.csv",
        "has_header": True,
        "field_mapping": {
            "具体时间": "具体时间",
            "奖品": "奖品",
            "收货人": "收货人",
            "手机": "手机"
        },
        "display_name": "faker3"
    },
    "9R": {
        "source_path": "/autMan/task/scripts/9Rebels_jdmax/utils/prize/addr_record.csv",
        "has_header": True,
        "field_mapping": {
            "具体时间": "具体时间",
            "奖品": "奖品",
            "收货人": "收货人",
            "手机": "手机"
        },
        "display_name": "9R"
    },
    "M": {
        "source_path": "/autMan/task/scripts/utopia/auto/gifts.csv",
        "has_header": False,
        "field_mapping": {
            "具体时间": 0,
            "奖品": 1,
            "收货人": 4,
            "手机": 3
        },
        "display_name": "M"
    }
}

def backup_source_file(source_path):
    """备份源文件到指定目录，文件名包含当前日期"""
    try:
        # 备份目录
        backup_dir = '/autMan/task/scripts/实物(备份)'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        # 获取当前日期
        current_date = datetime.now().strftime("%Y%m%d")
        # 生成备份文件名
        backup_file_name = f"{os.path.basename(source_path).split('.')[0]}_{current_date}.csv"
        backup_file_path = os.path.join(backup_dir, backup_file_name)
        # 复制源文件到备份目录
        shutil.copy2(source_path, backup_file_path)
        print(f"源文件 {source_path} 备份成功，备份文件: {backup_file_path}")
    except Exception as e:
        print(f"备份源文件失败: {str(e)}")

def backup_by_date(backup_dir):
    """根据数据中的日期字段，将数据保存到对应日期的备份文件中，并删除源文件中已备份的数据"""
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)

        date_data = defaultdict(list)  # 按日期分组的数据

        for source_name, config in DATA_SOURCES.items():
            source_path = config["source_path"]
            if not os.path.exists(source_path):
                continue

            source_success = False
            processed_rows = 0
            source_rows = []

            # 备份源文件
            backup_source_file(source_path)  # 调用新的备份函数

            try:
                # 先读取源文件所有数据，以便后续筛选未备份的行
                with open(source_path, 'r', encoding='utf-8') as src:
                    if config["has_header"]:
                        reader = csv.DictReader(src)
                        source_rows = list(reader)
                    else:
                        reader = csv.reader(src)
                        source_rows = [row for row in reader]

                # 筛选出需要备份的行（解析日期并分组）
                for row in source_rows:
                    try:
                        # 提取日期并解析
                        date_str = (row[config["field_mapping"]["具体时间"]]
                                    if not config["has_header"]
                                    else row.get(config["field_mapping"]["具体时间"], ""))

                        if not date_str:
                            continue

                        date_obj = parse_date(date_str)
                        date_key = date_obj.strftime("%Y%m%d")

                        # 映射数据行
                        mapped_row = map_row(row, config)
                        date_data[date_key].append(mapped_row)
                        processed_rows += 1

                    except Exception as e:
                        print(f"解析数据失败: {str(e)}, 数据: {row}")
                        continue

                if processed_rows == 0:
                    print(f"数据源 {source_name} 无可备份数据")
                    continue

                # 写入备份文件（追加模式，表头仅首次写入）
                for date_key, rows in date_data.items():
                    backup_path = os.path.join(backup_dir, f"addr_record_{date_key}.csv")
                    file_exists = os.path.exists(backup_path)

                    with open(backup_path, 'a', encoding='utf-8', newline='') as outfile:
                        writer = csv.DictWriter(outfile, fieldnames=["具体时间", "奖品", "收货人", "手机", "数据源"])
                        if not file_exists:
                            writer.writeheader()
                        writer.writerows(rows)

                source_success = True
                print(f"数据源 {source_name} 备份成功，处理 {processed_rows} 行")

            finally:
                if source_success and processed_rows > 0:
                    # 筛选源文件中未被备份的行（日期不在date_data中的行）
                    remaining_rows = []
                    for row in source_rows:
                        try:
                            date_str = (row[config["field_mapping"]["具体时间"]]
                                        if not config["has_header"]
                                        else row.get(config["field_mapping"]["具体时间"], ""))
                            date_obj = parse_date(date_str)
                            date_key = date_obj.strftime("%Y%m%d")
                            if date_key not in date_data:
                                remaining_rows.append(row)
                        except:
                            remaining_rows.append(row)  # 保留解析失败的行

                    # 将剩余数据写回源文件
                    with open(source_path, 'w', encoding='utf-8', newline='') as src:
                        if config["has_header"]:
                            writer = csv.DictWriter(src, fieldnames=reader.fieldnames)
                            writer.writeheader()
                            writer.writerows(remaining_rows)
                        else:
                            csv.writer(src).writerows(remaining_rows)
                    print(f"已删除源文件 {source_path} 中 {processed_rows} 条已备份数据")

        return list(date_data.keys()) if date_data else None

    except Exception as e:
        print(f"备份失败: {str(e)}")
        return None


# 辅助函数：解析日期字符串
def parse_date(date_str):
    for fmt in ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    raise ValueError(f"无法解析的日期格式: {date_str}")


# 辅助函数：映射数据行
def map_row(row, config):
    if config["has_header"]:
        return {
            "具体时间": row.get(config["field_mapping"]["具体时间"], ""),
            "奖品": row.get(config["field_mapping"]["奖品"], ""),
            "收货人": row.get(config["field_mapping"]["收货人"], ""),
            "手机": row.get(config["field_mapping"]["手机"], ""),
            "数据源": config["display_name"]
        }
    else:
        return {
            "具体时间": row[config["field_mapping"]["具体时间"]] if len(row) > config["field_mapping"][
                "具体时间"] else "",
            "奖品": row[config["field_mapping"]["奖品"]] if len(row) > config["field_mapping"]["奖品"] else "",
            "收货人": row[config["field_mapping"]["收货人"]] if len(row) > config["field_mapping"]["收货人"] else "",
            "手机": row[config["field_mapping"]["手机"]] if len(row) > config["field_mapping"]["手机"] else "",
            "数据源": config["display_name"]
        }


def merge_csv_files(file_paths):
    """合并多个CSV文件的数据"""
    if not file_paths:
        return [], []

    all_rows = []
    fieldnames = None

    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                if reader.fieldnames is None:
                    print(f"文件 {file_path} 的表头为空，跳过")
                    continue

                if fieldnames is None:
                    fieldnames = reader.fieldnames
                elif reader.fieldnames != fieldnames:
                    print(f"文件 {file_path} 的表头与已有表头不一致，跳过")
                    continue

                for row in reader:
                    all_rows.append(row)
        except Exception as e:
            print(f"读取文件 {file_path} 失败: {str(e)}")
            continue

    return all_rows, fieldnames or []


def generate_statistics(data_rows, sender):
    """生成统计信息并发送给用户"""
    if not data_rows:
        sender.reply("⚠️ 未找到有效数据")
        return

    # 使用 (日期, 数据源) 作为键
    date_source_prizes = defaultdict(lambda: defaultdict(int))
    total_all = 0

    for row in data_rows:
        if not row.get('具体时间') or not row.get('奖品'):
            continue

        try:
            date_str = datetime.strptime(row['具体时间'].split()[0], "%Y-%m-%d")
            date_str = date_str.strftime("%Y-%m-%d")
        except:
            date_str = "未知日期"

        prize = row['奖品'].strip()
        source = row.get('数据源', '')
        key = (date_str, source)

        date_source_prizes[key][prize] += 1
        total_all += 1

    response = ["🎁 实物奖品统计 🎁", ""]

    # 按日期排序（日期越新越靠后）
    sorted_dates = sorted({k[0] for k in date_source_prizes.keys()},
                          key=lambda x: datetime.strptime(x, "%Y-%m-%d") if x != "未知日期" else datetime.min,
                          reverse=False)

    # 每日统计
    for date in sorted_dates:
        # 获取该日期的所有数据源
        sources = sorted({k[1] for k in date_source_prizes.keys() if k[0] == date})

        for source in sources:
            prizes = date_source_prizes.get((date, source), {})
            if not prizes:
                continue

            date_total = sum(prizes.values())

            response.append("─" * 20)
            response.append(f"📅 {date}")
            if source:
                response.append(f"🔖 数据源: {source}")

            for idx, (prize, count) in enumerate(
                    sorted(prizes.items(), key=lambda x: (-x[1], x[0])), 1
            ):
                response.append(f"{idx}. {prize:<10} ×{count}")

            response.append(f"📊 当日合计: {date_total}件\n")

    # 全局统计
    day_count = len({k[0] for k in date_source_prizes.keys()})
    if day_count > 0:
        response.append("─" * 20)
        response.append("🌟 全局统计 🌟")
        response.append(f"• 统计天数: {day_count}天")
        response.append(f"• 奖品总数: {total_all}件")
        if day_count > 0:
            response.append(f"• 日均发放: {round(total_all / day_count, 1)}件/天")
        else:
            response.append("⚠️ 未找到有效数据")

    response.append("")
    response.append("💡 数据仅供参考，请以实际发放为准")

    sender.reply("\n".join(response))


def read_and_print_csv(sender, query_type="daily", days=5):
    """读取CSV文件并生成统计信息"""
    try:
        backup_dir = '/autMan/task/scripts/实物'

        # 先尝试备份数据
        backup_dates = backup_by_date(backup_dir)

        if query_type == "daily":
            # 获取当天日期
            today = datetime.now().strftime("%Y%m%d")
            backup_file = os.path.join(backup_dir, f"addr_record_{today}.csv")
            if not os.path.exists(backup_file):
                sender.reply("⚠️ 今日无数据")
                # 查找最近一天的中奖数据
                recent_dates = sorted(backup_dates, reverse=True)
                if recent_dates:
                    recent_date_file = os.path.join(backup_dir, f"addr_record_{recent_dates[0]}.csv")
                    data_rows, _ = merge_csv_files([recent_date_file])
                    generate_statistics(data_rows, sender)
                else:
                    sender.reply("⚠️ 无历史数据")
                return
            data_rows, _ = merge_csv_files([backup_file])
            generate_statistics(data_rows, sender)
        elif query_type == "summary":
            # 获取自定义天数内的日期
            today = datetime.now()
            recent_dates = []
            for i in range(days):
                date = today - timedelta(days=i)
                recent_dates.append(date.strftime("%Y%m%d"))

            backup_files = [os.path.join(backup_dir, f"addr_record_{date_str}.csv") for date_str in recent_dates if
                            os.path.exists(os.path.join(backup_dir, f"addr_record_{date_str}.csv"))]
            if not backup_files:
                sender.reply(f"⚠️ 未找到最近 {days} 天内的有效数据文件")
                return
            data_rows = []
            for file_path in backup_files:
                rows, _ = merge_csv_files([file_path])
                data_rows.extend(rows)

            generate_statistics(data_rows, sender)

    except Exception as e:
        sender.reply(f"❌ 处理失败: {str(e)}")


if __name__ == "__main__":
    sender = middleware.Sender(middleware.getSenderID())
    content = sender.getMessage()

    if content.startswith('实物汇总'):
        parts = content.split()
        if len(parts) > 1 and parts[1].isdigit():
            days = int(parts[1])
            read_and_print_csv(sender, query_type="summary", days=days)
        else:
            read_and_print_csv(sender, query_type="summary", days=5)
    elif content == '实物查询':
        read_and_print_csv(sender, query_type="daily")