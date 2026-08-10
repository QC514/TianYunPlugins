# [pin:true]
# ==========================市场元数据=========================================
# [opensource: false]是否开源
# [title: Epic限免]
# [author: buzhi]
# [icon: ]图标链接地址，支持http和https
# [version: 1.0.1]
# [description: Epic限免]
# [platform: qq,wx]
# [public:true]
# [price: 0]
# [service: Q群862839828]
# [class: 工具类]
# ==========================函数解析元数据======================================
# [rule: ^(epic|EPIC|Epic)限免$] 匹配规则，多个规则时向下依次写多个
# [priority: 1000 ]
# [admin: false]
# [disable:false]
# ==========================参数配置数据（最下面）===============================

#   --------------------------------一般不动区--------------------------------
#                     _ooOoo_
#                    o8888888o
#                    88" . "88
#                    (| -_- |)
#                     O\ = /O
#                 ____/`---'\____
#               .   ' \\| |// `.
#                / \\||| : |||// \
#              / _||||| -:- |||||- \
#                | | \\\ - /// | |
#              | \_| ''\---/'' | |
#               \ .-\__ `-` ___/-. /
#            ___`. .' /--.--\ `. . __
#         ."" '< `.___\_<|>_/___.' >'"".
#        | | : `- \`.;`\ _ /`;.`/ - ` : | |
#          \ \ `-. \_ __\ /__ _/ .-` / /
#  ======`-.____`-.___\_____/___.-`____.-'======
#                     `=---='
#
#  .............................................
#           佛祖保佑             永无BUG
#           佛祖镇楼             BUG辟邪

# [pin:true]
# ==========================市场元数据=========================================
# [opensource: false]是否开源
# [title: Epic限免]
# [author: buzhi]
# [icon: ]图标链接地址，支持http和https
# [version: 1.0.0]
# [description: Epic限免]
# [platform: qq,wx]
# [public:false]
# [price: 8.8]
# [service: Q群862839828]
# [class: 工具类]
# ==========================函数解析元数据======================================
# [rule: ^(epic|EPIC|Epic)限免?$] 匹配规则，多个规则时向下依次写多个
# [priority: 1000 ]
# [admin: false]
# [disable:false]
# ==========================参数配置数据（最下面）===============================

#   --------------------------------一般不动区--------------------------------
#                     _ooOoo_
#                    o8888888o
#                    88" . "88
#                    (| -_- |)
#                     O\ = /O
#                 ____/`---'\____
#               .   ' \\| |// `.
#                / \\||| : |||// \
#              / _||||| -:- |||||- \
#                | | \\\ - /// | |
#              | \_| ''\---/'' | |
#               \ .-\__ `-` ___/-. /
#            ___`. .' /--.--\ `. . __
#         ."" '< `.___\_<|>_/___.' >'"".
#        | | : `- \`.;`\ _ /`;.`/ - ` : | |
#          \ \ `-. \_ __\ /__ _/ .-` / /
#  ======`-.____`-.___\_____/___.-`____.-'======
#                     `=---='
#
#  .............................................
#           佛祖保佑             永无BUG
#           佛祖镇楼             BUG辟邪


import json
import requests
import datetime

import middleware

# 获取发送者ID
senderID = middleware.getSenderID()
# 创建发送者
sender = middleware.Sender(senderID)
# 获取发送者类型,定时的类型是fake
senderType = sender.getImtype()
# 获取触发信息
mess = sender.getMessage()


def get_free_games() -> dict:
    timestamp = datetime.datetime.timestamp(datetime.datetime.now())
    games = {"timestamp": timestamp, "free_now": [], "free_next": []}
    base_store_url = "https://store.epicgames.com"
    api_url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?country=CN"
    resp = requests.get(api_url, timeout=30)
    for element in resp.json()["data"]["Catalog"]["searchStore"]["elements"]:
        if promotions := element["promotions"]:
            game = {}
            game["title"] = element["title"]
            game["images"] = element["keyImages"]
            game["origin_price"] = element["price"]["totalPrice"]["fmtPrice"][
                "originalPrice"
            ]
            game["discount_price"] = element["price"]["totalPrice"]["fmtPrice"][
                "discountPrice"
            ]
            game["store_url"] = (
                f"{base_store_url}/p/{element['catalogNs']['mappings'][0]['pageSlug']}"
                if element["catalogNs"]["mappings"]
                else base_store_url
            )
            if offers := promotions["promotionalOffers"]:
                game["start_date"] = offers[0]["promotionalOffers"][0]["startDate"]
                game["end_date"] = offers[0]["promotionalOffers"][0]["endDate"]
                games["free_now"].append(game)
            if offers := promotions["upcomingPromotionalOffers"]:
                game["start_date"] = offers[0]["promotionalOffers"][0]["startDate"]
                game["end_date"] = offers[0]["promotionalOffers"][0]["endDate"]
                games["free_next"].append(game)
    return games


def generate_json(games: dict, filename: str):
    with open(filename, "w") as f:
        json.dump(games, f)
        # json.dump(obj=games, fp=f, ensure_ascii=False, indent=4)


def get_msg(games: dict):
    if games:
        content = """
- ## Epic 本周限免"""
        for game in games["free_now"]:
            if game["discount_price"] == "0":
                content += f"""
- 游戏名：{game['title']}
    原价：{game['origin_price']}
    折扣价：{game['discount_price']}
    时间：{datetime.datetime.strftime(datetime.datetime.strptime(game["start_date"],'%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=8),'%Y年%m月%d日')} - {datetime.datetime.strftime(datetime.datetime.strptime(game["end_date"],'%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=8),'%Y年%m月%d日')}
    购买链接：{game['store_url']}
"""
        content += """
- ## Epic 下周限免"""
        for game in games["free_next"]:
            if game["discount_price"] == "0":
                content += f"""
- 游戏名：{game['title']}
    原价：{game['origin_price']}
    折扣价：{game['discount_price']}
    时间：{datetime.datetime.strftime(datetime.datetime.strptime(game["start_date"],'%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=8),'%Y年%m月%d日')} - {datetime.datetime.strftime(datetime.datetime.strptime(game["end_date"],'%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=8),'%Y年%m月%d日')}
    购买链接：{game['store_url']}
"""
    return content


if __name__ == "__main__":
    games = get_free_games()
    # print(games)
    content = get_msg(games)
    # print(content)
    sender.reply(content)
