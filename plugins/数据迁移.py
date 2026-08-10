#[pin:false]
#[public:true]
#[disable:false]
# [cron: 0 0 0 * * *]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [author: sky2022]
# [title: 数据迁移]
# [class: 工具类]
# [version: 1.0.6]
# [price: 0]
# [icon: https://i.miji.bid/2025/06/27/ff2b2c997f5bf6e1ec52e97548c159c1.png]
# [description: 指令：迁移转换<br>注意：仅限个人市场插件！！<br>用途：用户可以在多个平台进行数据的无缝衔接，例如QQ转WX数据，同时支持保存两个平台的数据！]
# [rule: ^数据迁移$]
import middleware
from datetime import datetime, timedelta
import json
import random
import requests
import string
import time

class Jfxt:
    def __init__(self, user, sender, bucket):
        self.user = user
        self.sender = sender
        self.bucket = bucket

    def update_id(self, old_id, new_id):
        try:
            # 检查新ID是否已有数据
            existing_data = middleware.bucketGet(self.bucket, new_id)
            if existing_data:
                # 提示用户选择是否覆盖
                self.sender.reply(f"""=====数据已存在=====
⚠️ 新UID({new_id})已存在数据
------------------
是否覆盖现有数据？
1. 是，覆盖现有数据
2. 否，取消迁移
------------------
回复对应数字选择
==================""")
                
                choice = self.sender.input(120000, 1000, False).strip().replace("\n", "").replace("\r", "")
                
                if choice == "1":
                    # 用户选择覆盖现有数据
                    self.sender.reply("已选择覆盖现有数据，继续迁移...")
                else:
                    # 用户选择不覆盖，取消迁移
                    self.sender.reply("已取消迁移")
                    return False
                
            points = middleware.bucketGet(self.bucket, old_id)
            if points:
                # 验证数据格式
                try:
                    old_data = json.loads(points.replace("'", "\""))
                except:
                    self.sender.reply("错误：原始数据格式无效")
                    return False
                
                # 直接写入新数据（覆盖现有数据）
                set_result = middleware.bucketSet(self.bucket, new_id, points)
                
                if set_result:
                    # 确保原ID的数据删除成功
                    del_result = middleware.bucketDel(self.bucket, old_id)
                    if del_result:
                        self.sender.reply(f"""=====迁移成功=====
✅ 数据已成功迁移！
------------------
📤 原UID: {old_id}
📥 新UID: {new_id}
==================""")
                        return True
                    else:
                        self.sender.reply("""=====迁移警告=====
⚠️ 新数据已写入，但删除原数据失败
==================""")
                else:
                    self.sender.reply("""=====迁移失败=====
❌ 写入新数据失败
==================""")
            else:
                self.sender.reply(f"""=====查询结果=====
❌ 原UID({old_id})不存在或无数据记录
==================""")
        except Exception as e:
            self.sender.reply(f"""=====系统错误=====
❌ 更新UID失败
错误信息: {str(e)}
==================""")
        return False

    def print_all_keys(self):
        try:
            all_keys = middleware.bucketAllKeys(self.bucket)
            all_values = {}
            for key in all_keys:
                value = middleware.bucketGet(self.bucket, key)
                all_values[key] = value
            #self.sender.reply(f"桶 {self.bucket} 中的所有参数：\n" + json.dumps(all_values, indent=4, ensure_ascii=False))
        except Exception as e:
            self.sender.reply(f"获取所有参数失败: {e}")

    def update_dates(self, days):
        try:
            all_keys = middleware.bucketAllKeys(self.bucket)
            for key in all_keys:
                value = middleware.bucketGet(self.bucket, key)
                data = json.loads(value.replace("'", "\""))  # 解析字符串为JSON格式
                for sub_key, sub_value in data.items():
                    if 'sqsj' in sub_value:
                        old_date = datetime.strptime(sub_value['sqsj'], '%Y-%m-%d')
                        new_date = old_date + timedelta(days=days)
                        sub_value['sqsj'] = new_date.strftime('%Y-%m-%d')
                new_value = json.dumps(data, ensure_ascii=False).replace("\"", "'")
                middleware.bucketSet(self.bucket, key, new_value)
            self.sender.reply("所有日期已更新。")
        except Exception as e:
            self.sender.reply(f"更新日期失败: {e}")

if __name__ == '__main__':
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    user = sender.getUserID()

    buckets = {
        "2": "dd_fukuda_user",     # 福田
        "4": "dd_pp_user",         # 朴朴超市
        "5": "dd_sf_user",         # 顺丰
        "6": "bd_fxcks",         # 粉象生活
        "1": "dd_sign_points",           # 积分
        "9": "dd_Kuwo_bind",     # 酷我
        "11": "dd_kg_user"   ,   # 酷狗
    }

    menu = """=====数据迁移=====
请选择要迁移的数据：
------------------
1. 用户积分
2. 福田e家
3. 朴朴超市
4. 顺丰速运
5. 粉象生活
6. 酷我音乐
7. 酷狗
------------------
回复对应数字选择
=================="""
    sender.reply(menu)

    # 获取用户选择
    list_choice = sender.input(120000, 1000, False).strip().replace("\n", "").replace("\r", "")
    
    if list_choice not in buckets:
        sender.reply("已退出!")
    else:
        selected_bucket = buckets[list_choice]
        jfxt = Jfxt(user, sender, selected_bucket)
        
        # 获取原ID
        sender.reply("请输入原ID：")
        old_id = sender.input(120000, 1000, False).strip().replace("\n", "").replace("\r", "")
        
        # 使用当前用户ID作为新ID
        new_id = user
        
        # 更新ID
        jfxt.update_id(old_id, new_id)
