# [title: 临时邮箱]
# [author: yss]
# [icon: https://p0.meituan.net/csc/83ea3bbe1fa311e4bda05eeb3ebf6d3c7230.jpg]
# [class: 老秦最帅]
# [version: 1.0.0]版本号
# [rule: ^临时邮箱$]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [price: 2] 上架价格
# [service: 卫星：107 108 20 30]
# [description: 需要填写邮箱时候，不想使用您的真实邮箱？那就使用我吧，指令：临时邮箱 ] 
# [admin: false] 
# [priority: 999] 
import middleware
import requests
import time
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userID = sender.getUserID()

def get_mail():
    json_data = {
        "min_name_length": 10,
        "max_name_length": 10
    }
    url = 'https://api.internal.temp-mail.io/api/v3/email/new'
    response = requests.post(url, json=json_data)
    response_data = response.json()
    mail = response_data['email']
    sender.reply(f'获取邮箱:{mail}')
    sender.reply('获取邮箱内容，请稍后...')
    return mail

def get_email_content(mail, max_retries=10, delay=6):
    retries = 0
    while retries < max_retries:
        url = f'https://api.internal.temp-mail.io/api/v3/email/{mail}/messages'
        response = requests.get(url)
        emails = response.json()
        if emails:
            for email in emails:
                sender.reply(f'邮件内容：{email["body_text"]}')
            return  
        retries += 1
        time.sleep(delay)
    sender.reply('获取邮箱内容失败')

if __name__ == "__main__":
    email = get_mail()
    get_email_content(email)
