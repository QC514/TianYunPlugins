#[title: 小米钱包]
#[language: python]
#[class: 工具类]
#[service: 2993959969]
#[author: rujingxianghai]
#[disable:true]
#[admin: false]
#[rule: ^米包登录$|^登录米包$|^米包查询$|^米包管理$|^米包清理$|^米包一键更新$|^米包授权$|^米包兑换$|^米包抢兑$|^米包删除抢兑$]
#[cron: 0 0 0 0 0]
#[priority: 0]
#[platform: qq,qb,wx,tb,tg,web,wxmp]
#[open_source: false]
#[icon: https://img-cf.885666.xyz/fc6f139aa63c28af6e25ece264481322.png]
#[version: 1.1]
#[public: true]
#[price: 88.88]
#[description: 小米钱包独立版本，与小米社区插件功能相同，方便单独管理<br>指令：米包登录|登录米包|米包查询|米包管理|米包清理|米包一键更新|米包授权|米包兑换|米包抢兑|米包删除抢兑<br>小米钱包插件，未内置脚本，脚本进群获取]
# [param: {"required":true,"key":"s_mibao.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"s_mibao.ql_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"青龙配置,用丨分割"}]
# [param: {"required":true,"key":"s_mibao.var_name","bool":false,"placeholder":"必填项,例:S_XMQB","name":"青龙变量名","desc":"提交到青龙的变量名"}]
# [param: {"required":true,"key":"s_mibao.price","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"s_mibao.coin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"s_mibao.autuser","bool":false,"placeholder":"autman账号","name":"autman账号","desc":"部分微信框架无法发送二维码请填入autman账号"}]
# [param: {"required":false,"key":"s_mibao.autpwd","bool":false,"placeholder":"autman密码","name":"autman密码","desc":"部分微信框架无法发送二维码请填入autman密码"}]
# [param: {"required":false,"key":"s_mibao.ma_pay_switch","bool":true,"placeholder":"true/false","name":"码支付功能","desc":"开启后使用码支付，关闭则使用扫码支付。"}]
# [param: {"required":false,"key":"s_mibao.rush_concurrent","bool":false,"placeholder":"默认5","name":"抢兑并发数","desc":"同时进行抢兑的任务数量,建议3-10"}]
# [param: {"required":false,"key":"s_mibao.rush_retry","bool":false,"placeholder":"默认3","name":"抢兑重试次数","desc":"单个任务失败后的重试次数,建议1-5"}]
# [param: {"required":false,"key":"s_mibao.rush_time","bool":false,"placeholder":"例:10:00:00","name":"抢兑时间","desc":"定时抢兑的时间点,格式HH:MM:SS,不填则立即执行"}]
import time,json,requests,hashlib
from datetime import datetime,timedelta
import middleware
from decimal import Decimal
import random,string
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor,as_completed
PAY_TYPE_NAMES={'alipay':'支付宝','wxpay':'微信支付','qqpay':'QQ钱包'}
senderID=middleware.getSenderID()
sender=middleware.Sender(senderID)
userid=sender.getUserID()
uservalue=middleware.bucketGet(bucket='s_mibao_user',key=userid)
PAYMENT_CONFIG={}
def get_mapay_config():config={};config['ma_pay_switch']=middleware.bucketGet('s_mibao','ma_pay_switch')or'false';config['ma_pay_gateway']=middleware.bucketGet('dd_sign_config','ma_pay_gateway')or'';config['ma_pay_pid']=middleware.bucketGet('dd_sign_config','ma_pay_pid')or'';config['ma_pay_key']=middleware.bucketGet('dd_sign_config','ma_pay_key')or'';config['ma_pay_type']=middleware.bucketGet('dd_sign_config','ma_pay_type')or'alipay,wxpay';config['ma_pay_notify_url']=middleware.bucketGet('dd_sign_config','ma_pay_notify_url')or'http://localhost/notify';config['ma_pay_return_url']=middleware.bucketGet('dd_sign_config','ma_pay_return_url')or'http://localhost/return';config['pid']=config['ma_pay_pid'];config['key']=config['ma_pay_key'];config['gateway']=config['ma_pay_gateway'];config['notify_url']=config['ma_pay_notify_url'];config['return_url']=config['ma_pay_return_url'];return config
def is_valid_phone(phone):return True
def format_phone(phone):
	try:
		phone=str(phone);phone=''.join(filter(str.isdigit,phone))
		if len(phone)!=11:return phone
		return phone[:3]+'****'+phone[7:]
	except:return str(phone)
def parse_cookie_string(cookie_str):
	cookies={}
	if not cookie_str:return cookies
	for item in cookie_str.split(';'):
		if'='in item:key,value=item.split('=',1);cookies[key.strip()]=value.strip()
	return cookies
def cookie_to_string(cookies):return';'.join([f"{k}={v}"for(k,v)in cookies.items()])
def sort_dict_by_key(data):return dict(sorted(data.items()))
def generate_sign(params,key):sign_params={k:v for(k,v)in params.items()if v and k!='sign'and k!='sign_type'};sorted_params=dict(sorted(sign_params.items()));url_string='&'.join(f"{k}={v}"for(k,v)in sorted_params.items());sign_string=url_string+key;md5=hashlib.md5(sign_string.encode('utf-8')).hexdigest().lower();return md5
def get_config():
	var_name=middleware.bucketGet('s_mibao','var_name')or'xiaomick';ql_config=middleware.bucketGet('s_mibao','ql_config')or'';price=Decimal(middleware.bucketGet('s_mibao','price')or'1');coin_config=middleware.bucketGet('s_mibao','coin')
	try:
		if coin_config and coin_config.strip():
			coin_price=int(coin_config.strip())
			if coin_price<=0:coin_price=0
		else:coin_price=0
	except(ValueError,TypeError):coin_price=0
	return var_name,ql_config,price,coin_price
def get_user_points(user_id):
	try:
		points_str=middleware.bucketGet('dd_sign_points',user_id)
		if points_str is None:return 0,'积分系统未初始化或用户未参与积分活动'
		try:points=int(points_str or'0');return points,None
		except ValueError:return 0,f"积分数据格式错误: {points_str}"
	except Exception as e:return 0,f"积分查询异常: {str(e)}"
def init_qinglong():
	try:
		if not ql_config:sender.reply('❌ 未配置青龙信息');exit(0)
		ql_params=ql_config.split('丨')
		if len(ql_params)!=3:sender.reply('❌ 青龙配置格式错误');exit(0)
		ql_url=ql_params[0].strip();client_id=ql_params[1].strip();client_secret=ql_params[2].strip()
		if not all([ql_url,client_id,client_secret]):sender.reply('❌ 青龙配置参数不完整');exit(0)
		token=get_ql_token(ql_url,client_id,client_secret);return ql_url,token
	except Exception as e:sender.reply(f"❌ 连接青龙失败: {str(e)}");exit(0)
def get_ql_token(url,client_id,client_secret):
	try:
		r=requests.get(f"{url}/open/auth/token?client_id={client_id}&client_secret={client_secret}")
		if r.status_code!=200:raise Exception(f"请求失败: {r.status_code}")
		data=r.json()
		if'token'not in data.get('data',{}):raise Exception('获取token失败')
		return data['data']['token']
	except Exception as e:raise Exception(f"获取token失败: {str(e)}")
def add_to_qinglong(token,account,phone):
	try:
		url=f"{ql_url}/open/envs";headers={'Authorization':f"Bearer {ql_token}",'Content-Type':'application/json'};response=requests.get(url,headers=headers)
		if response.status_code!=200:raise Exception('获取变量失败')
		exists_id=None
		for env in response.json()['data']:
			if env['name']==var_name and account in env.get('remarks',''):exists_id=env['id'];break
		cookie_str=middleware.bucketGet('s_mibao_token',account)
		if not cookie_str:raise Exception('获取Cookie失败')
		parts=cookie_str.split('#')
		if len(parts)!=3:raise Exception('Cookie格式错误')
		uid,password,token=parts
		if not uid or uid=='None'or not token or token=='None':raise Exception('无效的Cookie值')
		data={'name':var_name,'value':cookie_str,'remarks':f"账号:{phone}丨用户:{userid}丨UID:{uid}"}
		if exists_id:data['id']=exists_id;response=requests.put(f"{url}",headers=headers,json=data)
		else:response=requests.post(url,headers=headers,json=[data])
		if response.status_code!=200:raise Exception('提交变量失败')
		return True
	except Exception as e:sender.reply(f"❌ 青龙操作失败: {str(e)}");return False
def login():
	accounts=eval(uservalue or'[]')
	if accounts:
		account_list='=====已绑定账号=====\n[0] 扫码登录新账号\n'
		for(i,account)in enumerate(accounts,1):auth_time=middleware.bucketGet('s_mibao_auth',account)or'未授权';account_list+=f"[{i}] {format_phone(account)} ({auth_time})\n"
		account_list+='------------------\n请选择序号进行操作\n或直接输入手机号进行登录\n回复"q"退出';sender.reply(account_list);choice=sender.listen(60000)
		if not choice or choice=='q':sender.reply('✅ 已退出登录流程');return
		if choice=='0':temp_id=''.join(random.choices(string.ascii_letters+string.digits,k=10));qr_login(temp_id);return
		try:
			index=int(choice)-1
			if 0<=index<len(accounts):
				selected_account=accounts[index];password=middleware.bucketGet('s_mibao_pwd',selected_account)
				if not password:
					sender.reply('⚠️ 未找到该账号的密码记录，请重新输入密码:');password=sender.listen(60000)
					if not password or password=='q':sender.reply('✅ 已退出登录流程');return
				try:login_with_account(selected_account,password)
				except Exception as e:sender.reply(f"❌ 登录失败: {str(e)}")
				return
			elif is_valid_phone(choice):
				phone=choice;sender.reply('请输入密码:\n回复"q"退出');password=sender.listen(60000)
				if not password or password=='q':sender.reply('✅ 已退出登录流程');return
				try:login_with_account(phone,password)
				except Exception as e:sender.reply(f"❌ 登录失败: {str(e)}")
				return
			else:sender.reply('❌ 无效的账号序号');return
		except ValueError:
			if is_valid_phone(choice):
				phone=choice;sender.reply('请输入密码:\n回复"q"退出');password=sender.listen(60000)
				if not password or password=='q':sender.reply('✅ 已退出登录流程');return
				try:login_with_account(phone,password)
				except Exception as e:sender.reply(f"❌ 登录失败: {str(e)}")
				return
			else:sender.reply('❌ 无效的输入，请输入账号序号或11位手机号');return
	else:
		sender.reply('\n=====登录方式=====\n[1] 账号密码登录\n[2] 扫码登录\n------------------\n请选择登录方式\n回复"q"退出');login_type=sender.listen(60000)
		if not login_type or login_type=='q':sender.reply('✅ 已退出登录流程');return
		if login_type=='1':
			sender.reply('请输入手机号:\n回复"q"退出');phone=sender.listen(60000)
			if not phone or phone=='q':sender.reply('✅ 已退出登录流程');return
			sender.reply('请输入密码:\n回复"q"退出');password=sender.listen(60000)
			if not password or password=='q':sender.reply('✅ 已退出登录流程');return
			try:login_with_account(phone,password)
			except Exception as e:sender.reply(f"❌ 登录失败: {str(e)}")
			return
		elif login_type=='2':temp_id=''.join(random.choices(string.ascii_letters+string.digits,k=10));qr_login(temp_id);return
		else:sender.reply('❌ 无效的选择');return
class LoginResultHandler:
	def __init__(self,data):self.data=data;self.status=data.get('code',-1);self.message=data.get('desc','未知错误');self.pass_token=data.get('passToken');self.user_id=str(data.get('userId',''))
	@property
	def success(self):return self.status==0 and self.pass_token and self.user_id
	@property
	def need_captcha(self):return self.status==87001 or'验证码'in self.message or self.data.get('securityStatus')==16 or'安全验证'in self.message
	@property
	def pwd_wrong(self):return self.status==70016 or'用户名或密码不正确'in self.message or'密码错误'in self.message
def login_with_account(phone,password,skip_auth=False):
	try:
		data={'qs':'%3F_json%3Dtrue%26sid%3Dmiui_vip_a%26_locale%3Dzh_CN','callback':'https://api-alpha.vip.miui.com/sts','_json':'true','_sign':'eQzFP7RKdHfN0VKBbp86ZVzlgq0=','user':phone,'hash':hashlib.md5(password.encode()).hexdigest().upper(),'sid':'miui_vip_a','_locale':'zh_CN'};headers={'Content-Type':'application/x-www-form-urlencoded','User-Agent':'Dalvik/2.1.0 (Linux; U; Android 14; 2210132C Build/UKQ1.230705.002) APP/xiaomi.vipaccount APPV/20231107 MK/WGlhb21p IDEz IFBybw== SDKV/5.1.0.release.13 PassportSDK/5.1.0.release.15 passport-ui/5.1.0.release.15','Host':'account.xiaomi.com','Connection':'Keep-Alive'};response=requests.post('https://account.xiaomi.com/pass/serviceLoginAuth2',data=data,headers=headers,cookies={'deviceId':'S13aukyf5y2jecCG'})
		if response.status_code!=200:raise Exception('登录请求失败')
		response_text=response.text
		if not response_text:raise Exception('服务器返回空响应')
		try:result=response_text.lstrip('&').lstrip('START').lstrip('&');data=json.loads(result)
		except json.JSONDecodeError as e:raise Exception(f"解析响应失败: {response_text[:100]}")
		api_data=LoginResultHandler(data)
		if api_data.success:
			sender.reply(f"✅ 账号 {format_phone(phone)} 登录成功，正在获取Cookie...");middleware.bucketSet('s_mibao_pwd',phone,password);cookies=get_cookies_by_passtk(api_data.user_id,api_data.pass_token,headers['User-Agent'])
			if not cookies:raise Exception('获取Cookie失败，可能是User-Agent异常')
			cookies.update({'passToken':api_data.pass_token,'userId':api_data.user_id});return process_login(cookies,phone,api_data.user_id,skip_auth,skip_auth)
		elif api_data.need_captcha:
			if not skip_auth:sender.reply(f"\n=====需要验证=====\n⚠️ 账号 {format_phone(phone)} 需要安全验证\n系统将自动切换到扫码登录模式\n==================");return qr_login(phone,password)
			return False
		elif api_data.pwd_wrong:
			if not skip_auth:
				sender.reply(f"""
❌ 账号 {format_phone(phone)} 登录失败: 密码错误

请选择：
1. 重新输入账号和密码
2. 回复 0 使用扫码登录
3. 回复 q 退出登录
==================""")
				while True:
					choice=sender.listen(60000)
					if not choice:sender.reply('❌ 超时，登录已取消');return False
					choice=choice.strip().lower()
					if choice=='q':sender.reply('✅ 已退出登录');return False
					elif choice=='0':sender.reply('🔄 切换到扫码登录模式...');return qr_login(new_phone,new_password)
					else:
						sender.reply('请输入手机号:');new_phone=sender.listen(60000)
						if not new_phone or new_phone.lower()=='q':sender.reply('✅ 已取消登录');return False
						if not is_valid_phone(new_phone):sender.reply('❌ 手机号格式不正确，请重新选择');continue
						sender.reply('请输入密码:');new_password=sender.listen(60000)
						if not new_password or new_password.lower()=='q':sender.reply('✅ 已取消登录');return False
						return login_with_account(new_phone,new_password,skip_auth)
			else:return False
		else:raise Exception(f"登录失败: {api_data.message}")
	except Exception as e:sender.reply(f"❌ 登录失败: {str(e)}");return False
def qr_login(phone,password=None):
	try:
		global uservalue;headers={'Accept':'application/json, text/plain, */*','Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6','Cache-Control':'no-cache','Connection':'keep-alive','Pragma':'no-cache','Referer':'https://account.xiaomi.com/','Sec-Fetch-Dest':'empty','Sec-Fetch-Mode':'cors','Sec-Fetch-Site':'same-origin','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0','X-Requested-With':'XMLHttpRequest','sec-ch-ua':'"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"','sec-ch-ua-mobile':'?0','sec-ch-ua-platform':'"Windows"'};qr_url_request='https://account.xiaomi.com/longPolling/loginUrl?_group=DEFAULT&_qrsize=240&qs=%253Fcallback%253Dhttps%25253A%25252F%25252Faccount.xiaomi.com%25252Fsts%25253Fsign%25253DZvAtJIzsDsFe60LdaPa76nNNP58%2525253D%252526followup%25253Dhttps%25253A%2525252F%2525252Faccount.xiaomi.com%2525252Fpass%2525252Fauth%2525252Fsecurity%2525252Fhome%252526sid%25253Dpassport%26sid%3Dpassport&bizDeviceType=&callback=https:%2F%2Faccount.xiaomi.com%2Fsts%3Fsign%3DZvAtJIzsDsFe60LdaPa76nNNP58%253D%26followup%3Dhttps%253A%252F%252Faccount.xiaomi.com%252Fpass%252Fauth%252Fsecurity%252Fhome%26sid%3Dpassport&theme=&sid=passport&needTheme=false&showActiveX=false&serviceParam=%7B%22checkSafePhone%22:false,%22checkSafeAddress%22:false,%22lsrp_score%22:0.0%7D&_locale=zh_CN&_sign=2%26V1_passport%26BUcblfwZ4tX84axhVUaw8t6yi2E%3D&_dc=1702105962382';response=requests.get(qr_url_request,headers=headers)
		if response.status_code!=200:return False
		result=response.text.replace('&&&START&&&','')
		try:data=json.loads(result)
		except json.JSONDecodeError as e:return False
		qr_url=data.get('qr');login_url=data.get('loginUrl');check_url=data.get('lp')
		if not all([qr_url,login_url,check_url]):return False
		sender.reply(f"\n======扫码登录======\n请扫描二维码登录，有效时长2分钟\n==================")
		if middleware.bucketGet('s_mibao','autuser')and middleware.bucketGet('s_mibao','autpwd'):
			try:
				qr_response=requests.get(qr_url,timeout=10)
				if qr_response.status_code==200:
					qr_filename='xiaomi_qr.jpg'
					with open(qr_filename,'wb')as f:f.write(qr_response.content)
					try:
						with open(qr_filename,'rb')as f:files={'imgfile':f};data={'username':str(middleware.bucketGet('s_mibao','autuser')),'password':str(middleware.bucketGet('s_mibao','autpwd'))};upload_response=requests.post('http://aut.zhelee.cn/imgUpload',data=data,files=files,timeout=10)
						if upload_response.status_code==200:body=upload_response.json()
						else:sender.reply('❌ 上传图片失败');return False
					except Exception as e:sender.reply(f"❌ 上传图片失败: {str(e)}");return False
					qr_url=body['result']['path'];sender.replyImage(qr_url)
				else:sender.reply('❌ 下载二维码失败，请重试');return False
			except Exception as e:sender.reply(f"❌ 下载二维码失败: {str(e)}");return False
		else:sender.replyImage(qr_url)
		max_attempts=10;attempts=0;login_data=None
		while attempts<max_attempts:
			attempts+=1
			try:
				check_headers={'Accept':'application/json, text/plain, */*','Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6','Cache-Control':'no-cache','Connection':'keep-alive','Pragma':'no-cache','Referer':'https://account.xiaomi.com/','Sec-Fetch-Dest':'empty','Sec-Fetch-Mode':'cors','Sec-Fetch-Site':'same-origin','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0','X-Requested-With':'XMLHttpRequest','sec-ch-ua':'"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"','sec-ch-ua-mobile':'?0','sec-ch-ua-platform':'"Windows"'};response=requests.get(check_url,headers=check_headers,timeout=30)
				if response.status_code==200 and response.text:
					result=response.text.replace('&&&START&&&','')
					try:data=json.loads(result)
					except json.JSONDecodeError as e:continue
					if data.get('code')==0:
						pass_token=data.get('passToken');user_id=str(data.get('userId'))
						if not pass_token or not user_id:continue
						cookies=get_cookies_by_passtk(user_id,pass_token,headers['User-Agent'])
						if not cookies:continue
						cookies.update({'passToken':pass_token,'userId':user_id});sender.reply(f"✅ 账号: 【{user_id}】扫码登录成功！");login_data={'cookies':cookies,'user_id':user_id};break
			except Exception as e:print(f"检查登录状态异常 (第{attempts}次): {str(e)}");pass
			if attempts<max_attempts:time.sleep(3)
		if not login_data:sender.reply('❌ 扫码登录超时，请重新发送「小米登录」尝试');return False
		if password and phone:input_phone=phone;sender.reply(f"使用之前输入的账号: {format_phone(phone)}")
		else:
			sender.reply('请输入手机号:');input_phone=sender.listen(60000)
			if not input_phone:sender.reply('❌ 未输入手机号，登录流程已取消');return False
			if not is_valid_phone(input_phone):sender.reply('❌ 手机号格式不正确，登录流程已取消');return False
			sender.reply('请输入密码:');password=sender.listen(60000)
			if not password:sender.reply('❌ 未输入密码，登录流程已取消');return False
		middleware.bucketSet('s_mibao_pwd',input_phone,password);accounts=eval(uservalue or'[]')
		if input_phone not in accounts:accounts.append(input_phone);middleware.bucketSet('s_mibao_user',userid,str(accounts));uservalue=str(accounts)
		cookie_str=cookie_to_string(login_data['cookies']);new_cookie_str=f"{login_data['user_id']}#{password}#{cookie_str}";middleware.bucketSet('s_mibao_token',input_phone,new_cookie_str);result=process_login(login_data['cookies'],input_phone,login_data['user_id'])
		if result:sender.reply('✅ 账号绑定成功');return True
		else:sender.reply('❌ 账号绑定失败');return False
	except Exception as e:import traceback;sender.reply(f"❌ 扫码登录过程出错: {str(e)}");return False
def get_cookies_by_passtk(user_id,pass_token,user_agent):
	try:
		headers={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6','Cache-Control':'no-cache','Connection':'keep-alive','Pragma':'no-cache','Referer':'https://web.vip.miui.com/','Sec-Fetch-Dest':'document','Sec-Fetch-Mode':'navigate','Sec-Fetch-Site':'same-site','Upgrade-Insecure-Requests':'1','User-Agent':user_agent,'sec-ch-ua':'"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"','sec-ch-ua-mobile':'?0','sec-ch-ua-platform':'"Windows"'};params={'destUrl':'https://web.vip.miui.com/page/info/mio/mio/checkIn?app_version=dev.230904','time':round(time.time()*1000)};cookies={'userId':user_id,'passToken':pass_token};response=requests.get('https://api-alpha.vip.miui.com/page/login',params=params,headers=headers,allow_redirects=False);url=response.headers.get('location')
		if not url:return{}
		response=requests.get(url,cookies=cookies,headers=headers,allow_redirects=False);url=response.headers.get('location')
		if not url:return{}
		response=requests.get(url,cookies=cookies,headers=headers,allow_redirects=False);final_cookies=dict(response.cookies);return final_cookies
	except Exception as e:sender.reply(f"❌ 获取Cookie失败: {str(e)}");return{}
def get_account_from_env(cookie_str):
	try:
		if not cookie_str:return None,None
		parts=cookie_str.split('#')
		if len(parts)>=3:return parts[0],parts[1]
		return None,None
	except:return None,None
def process_login(cookies,phone,user_id,skip_auth=False,skip_add_account=False):
	try:
		global uservalue
		if not skip_add_account:
			accounts=eval(uservalue or'[]')
			if phone not in accounts:accounts.append(phone);middleware.bucketSet('s_mibao_user',userid,str(accounts));sender.reply(f"✅ 已将账号 {phone} 添加到您的账号列表")
		cookie_str=cookie_to_string(cookies);password=middleware.bucketGet('s_mibao_pwd',phone)or'None';new_cookie_str=f"{user_id}#{password}#{cookie_str}";middleware.bucketSet('s_mibao_token',phone,new_cookie_str);auth_time=middleware.bucketGet('s_mibao_auth',phone);current_date=str(datetime.now().date());is_authorized=auth_time and auth_time>current_date
		if skip_auth:
			if is_authorized:
				if add_to_qinglong(cookie_str,phone,phone):return True
				else:sender.reply('⚠️ 青龙变量更新失败，请联系管理员处理！');return False
			return True
		elif is_authorized:
			if add_to_qinglong(cookie_str,phone,phone):sender.reply(f"""
=====登录成功=====
📱 账号: {format_phone(phone)}
📅 授权到期: {auth_time}
✅ 账号已更新
==================""");return True
			else:sender.reply('⚠️ 青龙变量更新失败，请联系管理员处理！');return False
		else:return process_auth(phone)
	except Exception as e:sender.reply(f"❌ 处理登录失败: {str(e)}");raise Exception(f"处理登录失败: {str(e)}")
def process_auth(account):
	try:
		sender.reply('\n=====设置授权时长=====\n请输入授权月数(如:1)\n--------------------------\n回复数字设置月数\n回复"q"退出操作\n==================');months=sender.listen(60000)
		if not months or months.lower()=='q':sender.reply('✅ 已取消授权');return False
		try:
			months=int(months)
			if months<=0:raise ValueError()
		except ValueError:sender.reply('❌ 无效的月数');return False
		total_price=price*months;available_payments=[];ma_pay_switch=(middleware.bucketGet('s_mibao','ma_pay_switch')or'false').lower()
		if ma_pay_switch=='true':
			ma_pay_type=middleware.bucketGet('dd_sign_config','ma_pay_type')or'';ma_pay_pid=middleware.bucketGet('dd_sign_config','ma_pay_pid')or'';ma_pay_key=middleware.bucketGet('dd_sign_config','ma_pay_key')or'';ma_pay_gateway=middleware.bucketGet('dd_sign_config','ma_pay_gateway')or''
			if ma_pay_gateway and ma_pay_pid and ma_pay_key:
				pay_types_str=ma_pay_type.strip()
				if not pay_types_str:pay_types_str='alipay,wxpay'
				pay_types=[p.strip()for p in pay_types_str.split(',')if p.strip()]
				for pay_type in pay_types:
					if pay_type=='alipay':available_payments.append(('支付宝',pay_type))
					elif pay_type=='wxpay':available_payments.append(('微信支付',pay_type))
					elif pay_type=='qqpay':available_payments.append(('QQ钱包',pay_type))
		else:
			zsm=middleware.bucketGet('s_mibao','zsm')
			if zsm:available_payments.append(('微信支付','wxpay'))
		if coin_price>0:available_payments.append(('积分兑换','coin'))
		if not available_payments:sender.reply('\n=====授权失败=====\n❌ 未配置任何支付方式\n------------------\n请联系管理员配置支付方式\n==================');return False
		if len(available_payments)==1:payment_name,payment_type=available_payments[0]
		else:
			auth_menu=f"\n=====选择支付方式=====\n⏰ 授权时长: {months}个月\n💰 金额: {total_price}元\n------------------"
			for(i,(name,_))in enumerate(available_payments,1):auth_menu+=f"\n[{i}] {name}"
			auth_menu+='\n------------------\n回复数字选择方式\n回复"q"退出操作\n==================';sender.reply(auth_menu);pay_choice=sender.listen(60000)
			if not pay_choice or pay_choice.lower()=='q':sender.reply('✅ 已取消授权');return False
			try:
				choice_index=int(pay_choice)-1
				if not 0<=choice_index<len(available_payments):sender.reply('❌ 无效的选择');return False
				payment_name,payment_type=available_payments[choice_index]
			except ValueError:sender.reply('❌ 请输入有效的数字');return False
		if payment_type=='coin':return process_coin_exchange(account,months)
		else:return process_payment_handle(account,months,payment_type)
	except Exception as e:sender.reply(f"❌ 处理授权失败: {str(e)}");return False
def process_coin_exchange(account,months):
	try:
		total_coins=coin_price*months;user_coins,error=get_user_points(userid)
		if error:sender.reply(f"❌ {error}");return False
		sender.reply(f"💰 当前积分: {user_coins}, 所需积分: {total_coins}")
		if user_coins<total_coins:sender.reply(f"❌ 积分不足\n当前积分: {user_coins}\n所需积分: {total_coins}");return False
		current_user_coins=int(middleware.bucketGet('dd_sign_points',userid)or'0')
		if current_user_coins<total_coins:sender.reply(f"❌ 积分不足 (尝试扣除时再次检查)\n当前积分: {current_user_coins}\n所需积分: {total_coins}");return False
		middleware.bucketSet('dd_sign_points',userid,str(current_user_coins-total_coins))
		if process_authorization_xiaomi(account,months):final_user_coins=int(middleware.bucketGet('dd_sign_points',userid)or'0');sender.reply(f"=====积分详情=====\n🎯 本次消耗: {total_coins} 积分\n💰 剩余积分: {final_user_coins} 积分");return True
		else:middleware.bucketSet('dd_sign_points',userid,str(current_user_coins));sender.reply('❌ 授权记录或青龙同步失败，已尝试退还积分。请检查授权状态。');return False
	except Exception as e:raise Exception(f"积分授权失败: {str(e)}")
def process_payment_handle(account,months,payment_type):
	try:
		total_price=price*months;ma_pay_switch=(middleware.bucketGet('s_mibao','ma_pay_switch')or'false').lower()
		if ma_pay_switch=='true':
			if handle_mapay_payment(f"小米社区授权-{format_phone(account)}",months,total_price,payment_type):return process_authorization_xiaomi(account,months)
			else:return False
		elif payment_type=='wxpay':
			if pay_with_zsm(f"小米社区授权-{format_phone(account)}",months,total_price):return process_authorization_xiaomi(account,months)
			else:return False
		else:sender.reply(f"❌ 未开启码支付时只支持微信支付");return False
	except Exception as e:sender.reply(f"❌ 付费授权失败: {str(e)}");return False
def pay_with_zsm(project,months,money):
	if float(money)==0:sender.reply(f"""
=====授权成功=====
🎫 商品: {project}
📅 时长: {months}月
💰 金额: 免费
==================""");return True
	zsm=middleware.bucketGet('s_mibao','zsm')
	if not zsm:sender.reply('❌ 未配置微信收款码，请联系管理员');return False
	pay_msg=f'''
=====微信扫码支付=====
🎫 商品: {project}
📅 时长: {months}月
💰 金额: {money}元
------------------
请使用微信扫码支付
回复"q"取消支付
==================''';sender.reply(pay_msg);sender.replyImage(zsm);payment_result=sender.waitPay('q',120000)
	if str(payment_result)=='q':sender.reply('✅ 已取消支付');return False
	sender.reply(f"""
=====支付成功=====
🎫 商品: {project}
📅 时长: {months}月
💰 金额: {money}元
==================""");return True
def get_mapay_config():config={};config['ma_pay_switch']=middleware.bucketGet('s_mibao','ma_pay_switch')or'false';config['ma_pay_gateway']=middleware.bucketGet('dd_sign_config','ma_pay_gateway')or'';config['ma_pay_pid']=middleware.bucketGet('dd_sign_config','ma_pay_pid')or'';config['ma_pay_key']=middleware.bucketGet('dd_sign_config','ma_pay_key')or'';config['ma_pay_type']=middleware.bucketGet('dd_sign_config','ma_pay_type')or'alipay,wxpay';config['ma_pay_notify_url']=middleware.bucketGet('dd_sign_config','ma_pay_notify_url')or'http://localhost/notify';config['ma_pay_return_url']=middleware.bucketGet('dd_sign_config','ma_pay_return_url')or'http://localhost/return';config['pid']=config['ma_pay_pid'];config['key']=config['ma_pay_key'];config['gateway']=config['ma_pay_gateway'];config['notify_url']=config['ma_pay_notify_url'];config['return_url']=config['ma_pay_return_url'];return config
def fh_url(url):
	pay_url_fh=None;headers={'sec-ch-ua-platform':'Windows','sec-ch-ua':'"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"','Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','sec-ch-ua-mobile':'?0','Origin':'https://www.mrw.so','Sec-Fetch-Site':'same-site','Sec-Fetch-Mode':'cors','Sec-Fetch-Dest':'empty','Referer':'https://www.mrw.so/','Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'};data={'urlStr':url,'domain':'mrw.so','expireType':'1','key':'5d7798c491d2c423c8c33d2d@631d0a6ffd3fbca7c2728bebc6602f98','random':str(int(time.time()*1000))}
	try:response=requests.post('https://create.mrw.so/pageHome/createBySingle.htm',headers=headers,data=data);pay_url_fh=response.json().get('data');return pay_url_fh
	except:return
def handle_mapay_payment(project,months,money,pay_type=None):
	PAYMENT_CONFIG=get_mapay_config();gateway=PAYMENT_CONFIG['gateway'];ma_pay_switch=PAYMENT_CONFIG['ma_pay_switch'].lower()
	if ma_pay_switch!='true':sender.reply('❌ 码支付功能未开启');return False
	if not(PAYMENT_CONFIG['gateway']and PAYMENT_CONFIG['pid']and PAYMENT_CONFIG['key']):sender.reply('❌ 码支付配置不完整，请联系管理员');return False
	pay_lock_key='xiaomi_recharge_lock';lock_info=middleware.bucketGet('s_mibao',pay_lock_key)
	if lock_info:
		try:
			lock_data=json.loads(lock_info)
			if time.time()-lock_data['time']<120:sender.reply('当前有其他用户正在支付中，请稍后再试!');return False
		except:pass
	lock_data={'user':userid,'time':int(time.time())};middleware.bucketSet('s_mibao',pay_lock_key,json.dumps(lock_data))
	try:
		amount=round(float(money),2);out_trade_no=f"XM{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000,99999)}"
		if pay_type:selected_type=pay_type
		else:
			pay_types_str=PAYMENT_CONFIG['ma_pay_type'].strip()
			if not pay_types_str:pay_types_str='alipay,wxpay'
			pay_types=[p.strip()for p in pay_types_str.split(',')if p.strip()]
			if len(pay_types)==1:selected_type=pay_types[0];type_name=PAY_TYPE_NAMES.get(selected_type,selected_type);sender.reply(f"""===== 支付信息 =====
🎫 商品: {project}
📅 时长: {months}月
💰 金额: {amount}元
------------------
💳 支付方式: {type_name}
------------------
正在创建支付订单...
==================""")
			else:
				pay_options_text='=====选择支付方式====='
				for(i,t)in enumerate(pay_types,1):t_name=PAY_TYPE_NAMES.get(t,t);pay_options_text+=f"\n[{i}] {t_name}"
				pay_options_text+='\n------------------\n回复数字选择支付方式\n回复"q"取消支付\n==================';sender.reply(pay_options_text);choice=sender.listen(120000)
				if choice.lower()=='q':sender.reply('✅ 已取消支付');middleware.bucketDel('s_mibao',pay_lock_key);return False
				try:
					choice_idx=int(choice)-1
					if 0<=choice_idx<len(pay_types):selected_type=pay_types[choice_idx];type_name=PAY_TYPE_NAMES.get(selected_type,selected_type);sender.reply(f"""===== 支付信息 =====
🎫 商品: {project}
📅 时长: {months}月
💰 金额: {amount}元
------------------
💳 支付方式: {type_name}
------------------
正在创建支付订单...
==================""")
					else:sender.reply('❌ 选择无效，已取消支付');middleware.bucketDel('s_mibao',pay_lock_key);return False
				except ValueError:sender.reply('❌ 输入无效，已取消支付');middleware.bucketDel('s_mibao',pay_lock_key);return False
		ma_pay_api=MaPay_Api(PAYMENT_CONFIG)
		try:success,result,msg=ma_pay_api.create_payment(amount=amount,out_trade_no=out_trade_no,name=f"{project}-{str(amount)}",user_id=userid,pay_type=selected_type)
		except Exception as e:sender.reply(f"❌ 创建订单时出错: {str(e)}");middleware.bucketDel('s_mibao',pay_lock_key);return False
		if not success:sender.reply(f"❌ 创建订单失败: {msg}");middleware.bucketDel('s_mibao',pay_lock_key);return False
		pay_url=None;qrcode=result.get('qrcode','');payurl=result.get('payurl','');code_url=result.get('code_url','');trade_no=result.get('trade_no','')
		if qrcode and'/ewm/'in qrcode and not qrcode.startswith('http'):code_url=qrcode;qrcode=None
		if payurl:pay_url=payurl
		elif qrcode:pay_url=qrcode
		elif code_url:
			if not code_url.startswith('http'):
				if gateway.endswith('/'):gateway=gateway[:-1]
				pay_url=f"{gateway}/{code_url}"
			else:pay_url=code_url
		elif trade_no:pay_url=fh_url(requests.utils.quote(f"{gateway}pay/{trade_no}"));qrcode=pay_url
		if not pay_url:sender.reply('❌ 获取支付链接失败');middleware.bucketDel('s_mibao',pay_lock_key);return False
		selected_type_name=PAY_TYPE_NAMES.get(selected_type,selected_type)
		if qrcode:
			sender.reply(f"请使用【{selected_type_name}】扫描下方二维码完成支付:");qrcode_api_url=generate_qrcode(qrcode)
			if qrcode_api_url:
				if selected_type=='qqpay':sender.reply('QQ支付打开图片若是黑屏，长按屏幕进行"识别二维码"即可！');sender.replyImage(qrcode)
				else:sender.replyImage(qrcode_api_url)
			else:sender.reply(f"二维码生成失败，请使用【{selected_type_name}】打开链接：\n{qrcode}")
		elif code_url:sender.reply(f"请使用【{selected_type_name}】扫描下方二维码完成支付:");sender.replyImage(pay_url)
		else:sender.reply(f"请使用【{selected_type_name}】打开以下链接完成支付:\n{pay_url}")
		sender.reply('支付过程中输入"q"可取消支付');is_paid,msg,data=poll_mapi_payment_status(out_trade_no);middleware.bucketDel('s_mibao',pay_lock_key)
		if is_paid:return True
		else:sender.reply(f"❌ 支付未完成: {msg}");return False
	except Exception as e:sender.reply(f"❌ 处理支付订单时出错: {str(e)}");middleware.bucketDel('s_mibao',pay_lock_key);return False
def authorize_multiple_accounts(accounts,months=None):
	global price,coin_price
	if not accounts:sender.reply('❌ 没有账号可授权');return False
	if months is None:
		sender.reply('\n=====批量授权设置=====\n请输入授权月数(如:1)\n--------------------------\n回复数字设置月数\n回复"q"退出操作\n==================');months_input=sender.listen(60000)
		if not months_input or months_input.lower()=='q':sender.reply('✅ 已取消授权');return False
		try:
			months=int(months_input)
			if months<=0:sender.reply('❌ 无效的月数');return False
		except ValueError:sender.reply('❌ 请输入有效的数字');return False
	total_price=price*months*len(accounts);available_payments=[];ma_pay_switch=(middleware.bucketGet('s_mibao','ma_pay_switch')or'false').lower()
	if ma_pay_switch=='true':
		ma_pay_type=middleware.bucketGet('dd_sign_config','ma_pay_type')or''
		if not ma_pay_type:ma_pay_type='alipay,wxpay'
		pay_types=[p.strip()for p in ma_pay_type.split(',')if p.strip()]
		for pay_type in pay_types:
			if pay_type=='alipay':available_payments.append(('支付宝',pay_type))
			elif pay_type=='wxpay':available_payments.append(('微信支付',pay_type))
			elif pay_type=='qqpay':available_payments.append(('QQ钱包',pay_type))
	else:
		zsm=middleware.bucketGet('s_mibao','zsm')
		if zsm:available_payments.append(('微信支付','wxpay'))
	if coin_price>0:available_payments.append(('积分兑换','coin'))
	if not available_payments:sender.reply('❌ 未配置任何支付方式');return False
	if len(available_payments)==1:payment_name,payment_type=available_payments[0]
	else:
		auth_menu=f"""
=====选择支付方式=====
⏰ 授权账号: {len(accounts)}个
⏰ 授权时长: {months}个月
💰 总金额: {total_price}元
------------------"""
		for(i,(name,_))in enumerate(available_payments,1):auth_menu+=f"\n[{i}] {name}"
		auth_menu+='\n------------------\n回复数字选择方式\n回复"q"退出操作\n==================';sender.reply(auth_menu);pay_choice=sender.listen(120000)
		if not pay_choice or pay_choice.lower()=='q':sender.reply('✅ 已取消授权');return False
		try:
			choice_idx=int(pay_choice)-1
			if not 0<=choice_idx<len(available_payments):sender.reply('❌ 无效的选择');return False
			payment_name,payment_type=available_payments[choice_idx]
		except ValueError:sender.reply('❌ 请输入有效的数字');return False
	if payment_type=='coin':
		total_coins=int(coin_price)*months*len(accounts);user_coins,error=get_user_points(userid)
		if error:sender.reply(f"❌ {error}");return False
		sender.reply(f"💰 当前积分: {user_coins}, 所需积分: {total_coins}")
		if user_coins<total_coins:sender.reply(f"❌ 积分不足\n当前积分: {user_coins}\n所需积分: {total_coins}");return False
		middleware.bucketSet('dd_sign_points',userid,str(user_coins-total_coins));success_count=0;fail_count=0
		for account in accounts:
			if process_authorization_xiaomi(account,months):success_count+=1
			else:fail_count+=1
		remaining_coins=int(middleware.bucketGet('dd_sign_points',userid)or'0');success_msg=f'''
=====批量积分授权成功=====
📱 授权账号: {success_count}个
❌ 失败账号: {fail_count}个
🎯 总消耗积分: {total_coins}
⏰ 授权时长: {months}月
💰 剩余积分: {remaining_coins}
------------------
发送"小米查询"查看账号详情''';sender.reply(success_msg);return True
	elif ma_pay_switch=='true':
		if handle_mapay_payment(f"小米社区批量授权-{len(accounts)}个",months,total_price,payment_type):
			success_count=0;fail_count=0
			for account in accounts:
				if process_authorization_xiaomi(account,months):success_count+=1
				else:fail_count+=1
			sender.reply(f"""
=====批量授权完成=====
📱 成功授权: {success_count}个
❌ 授权失败: {fail_count}个
💰 总支付: {total_price}元
⏰ 授权时长: {months}月
==================""");return True
		return False
	else:
		if payment_type=='wxpay':sender.reply(f"ℹ️ 微信赞赏码模式下，需要对 {len(accounts)} 个账号分别进行支付。")
		else:sender.reply(f"❌ 未开启码支付时只支持微信支付");return False
		success_count=0;fail_count=0
		for(i,account)in enumerate(accounts,1):
			sender.reply(f"\n=====正在为第 {i}/{len(accounts)} 个账号授权=====\n📱 账号: {format_phone(account)}");single_price=price*months
			if pay_with_zsm(f"小米社区授权-{format_phone(account)}",months,single_price):
				if process_authorization_xiaomi(account,months):success_count+=1
				else:fail_count+=1
			else:sender.reply(f"❌ 账号 {format_phone(account)} 支付失败或取消，跳过此账号。");fail_count+=1
		sender.reply(f"""
=====批量授权完成=====
📱 成功授权: {success_count}个
❌ 授权失败: {fail_count}个
⏰ 授权时长: {months}月
==================""");return success_count>0
def process_authorization_xiaomi(account,months):
	try:
		cookie_str=middleware.bucketGet('s_mibao_token',account)
		if not cookie_str:sender.reply(f"❌ 账号 {format_phone(account)} 不存在或Cookie已失效");return False
		auth_time=calculate_auth_time(account,months);parts=cookie_str.split('#')
		if len(parts)>=3:cookie_str=parts[2]
		else:sender.reply(f"❌ 账号 {format_phone(account)} 的Cookie格式错误");return False
		middleware.bucketSet('s_mibao_auth',account,auth_time);global ql_url,ql_token
		if not(ql_url and ql_token):ql_url,ql_token=init_qinglong()
		if add_to_qinglong(cookie_str,account,account):success_msg=f"""
=====授权成功=====
📱 账号: {format_phone(account)}
📅 授权到期: {auth_time}
✅ 账号已更新
==================""";sender.reply(success_msg);return True
		else:sender.reply(f"❌ 账号 {format_phone(account)} 提交到青龙失败，请联系管理员处理");return False
	except Exception as e:sender.reply(f"❌ 授权处理失败: {str(e)}");return False
def calculate_auth_time(account,months):
	current=datetime.now().date();auth=middleware.bucketGet('s_mibao_auth',account)
	if auth and auth>str(current):start=datetime.strptime(auth,'%Y-%m-%d').date()
	else:start=current
	end=start+timedelta(days=30*months);return str(end)
def get_user_info(cookies):
	try:
		headers={'Content-Type':'application/x-www-form-urlencoded','User-Agent':'Dalvik/2.1.0 (Linux; U; Android 14; 2210132C Build/UKQ1.230705.002) APP/xiaomi.vipaccount APPV/20231107 MK/WGlhb21p IDEz IFBybw== SDKV/5.1.0.release.13 PassportSDK/5.1.0.release.15 passport-ui/5.1.0.release.15','Request-Container-Mark':'android','Host':'api-alpha.vip.miui.com','Connection':'Keep-Alive'};response=requests.get('https://api-alpha.vip.miui.com/mtop/planet/vip/homepage/mineInfo',cookies=cookies,headers=headers);result=response.json()
		if result.get('status')==200:user_info=result.get('entity',{}).get('userInfo',{}).get('userGrowLevelInfo',{});user_uid=result.get('entity',{}).get('userInfo',{}).get('userId','未知');return{'title':user_info.get('title','未知'),'uid':user_uid,'point':user_info.get('point',0),'showLevel':user_info.get('showLevel','未知')}
		return
	except Exception as e:raise Exception(f"获取用户信息失败: {str(e)}")
def get_xiaomi_wallet_cookies(cookies):
	try:
		if isinstance(cookies,str):cookie_dict=parse_cookie_string(cookies)
		else:cookie_dict=cookies
		pass_token=cookie_dict.get('passToken');user_id=cookie_dict.get('userId')
		if not pass_token or not user_id:return
		session=requests.Session();login_url='https://account.xiaomi.com/pass/serviceLogin?callback=https%3A%2F%2Fapi.jr.airstarfinance.net%2Fsts%3Fsign%3D1dbHuyAmee0NAZ2xsRw5vhdVQQ8%253D%26followup%3Dhttps%253A%252F%252Fm.jr.airstarfinance.net%252Fmp%252Fapi%252Flogin%253Ffrom%253Dmipay_indexicon_TVcard%2526deepLinkEnable%253Dfalse%2526requestUrl%253Dhttps%25253A%25252F%25252Fm.jr.airstarfinance.net%25252Fmp%25252Factivity%25252FvideoActivity%25253Ffrom%25253Dmipay_indexicon_TVcard%252526_noDarkMode%25253Dtrue%252526_transparentNaviBar%25253Dtrue%252526cUserId%25253Dusyxgr5xjumiQLUoAKTOgvi858Q%252526_statusBarHeight%25253D137&sid=jrairstar&_group=DEFAULT&_snsNone=true&_loginType=ticket';headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0','cookie':f"passToken={pass_token}; userId={user_id};"};session.get(url=login_url,headers=headers,verify=False);wallet_cookies=session.cookies.get_dict();return f"cUserId={wallet_cookies.get('cUserId')};jrairstar_serviceToken={wallet_cookies.get('serviceToken')}"
	except Exception as e:return
def get_video_days(cookies):
	try:
		wallet_cookies_str=get_xiaomi_wallet_cookies(cookies)
		if not wallet_cookies_str:return'获取失败'
		wallet_cookies=parse_cookie_string(wallet_cookies_str);session=requests.Session();session.cookies.update(wallet_cookies);headers={'Host':'m.jr.airstarfinance.net','User-Agent':'Mozilla/5.0 (Linux; U; Android 14; zh-CN; M2012K11AC Build/UKQ1.230804.001; AppBundle/com.mipay.wallet; AppVersionName/6.89.1.5275.2323; AppVersionCode/20577595; MiuiVersion/stable-V816.0.13.0.UMNCNXM; DeviceId/alioth; NetworkType/WIFI; mix_version; WebViewVersion/118.0.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36 XiaoMi/MiuiBrowser/4.3'};response=session.get('https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserGoldRichSum?app=com.mipay.wallet&deviceType=2&system=1&visitEnvironment=2&userExtra={"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}&activityCode=2211-videoWelfare',headers=headers,verify=False)
		if response.status_code==200:
			result=response.json()
			if result.get('code')==0:total_days=f"{int(result['value'])/100:.2f}"if result.get('value')else'0';return total_days
		return'未知'
	except Exception as e:return'获取失败'
def get_today_video_days(cookies):
	try:
		wallet_cookies_str=get_xiaomi_wallet_cookies(cookies)
		if not wallet_cookies_str:return'获取失败'
		wallet_cookies=parse_cookie_string(wallet_cookies_str);session=requests.Session();session.cookies.update(wallet_cookies);headers={'Host':'m.jr.airstarfinance.net','User-Agent':'Mozilla/5.0 (Linux; U; Android 14; zh-CN; M2012K11AC Build/UKQ1.230804.001; AppBundle/com.mipay.wallet; AppVersionName/6.96.1.5454.2614; AppVersionCode/20577623; MiuiVersion/stable-V816.0.13.0.UMNCNXM; DeviceId/alioth; NetworkType/WIFI; mix_version; WebViewVersion/118.0.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36 XiaoMi/MiuiBrowser/4.3'};response=session.get('https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserJoinList?app=com.mipay.wallet&versionCode=20577623&versionName=6.96.1.5454.2614&isNfcPhone=true&channel=mipay_indexicon_TVcard&deviceType=2&system=1&visitEnvironment=2&userExtra={"platformType":1,"com.miui.player":"4.37.0.2","com.mipay.wallet":"6.96.1.5454.2614"}&activityCode=2211-videoWelfare&pageNum=1&pageSize=20',headers=headers,verify=False)
		if response.status_code==200:
			result=response.json()
			if result.get('code')==0 and result.get('success'):
				records=result.get('value',{}).get('data',[]);from datetime import datetime;current_date=datetime.now().strftime('%Y-%m-%d');today_total=0
				for record in records:
					create_time=record.get('createTime','')
					if create_time.startswith(current_date):
						value=record.get('value',0)
						try:days=int(value)/100;today_total+=days
						except(ValueError,TypeError):continue
				return f"{today_total:.2f}天"
		return'0天'
	except Exception as e:return'获取失败'
def query_single_account(account):
	try:
		success,msg=update_cookie_by_passtoken(account)
		if not success:sender.reply(f"❌ 账号 {format_phone(account)} Cookie更新失败: {msg}，跳过查询");return False
		cookie_str=middleware.bucketGet('s_mibao_token',account)
		if not cookie_str:sender.reply(f"❌ 账号 {format_phone(account)} 的Cookie已失效");return False
		parts=cookie_str.split('#')
		if len(parts)>=3:cookie_str=parts[2]
		cookies=parse_cookie_string(cookie_str);user_info=get_user_info(cookies)
		if not user_info:sender.reply(f"❌ 账号 {format_phone(account)} 获取用户信息失败");return False
		video_days=get_video_days(cookies);today_video_days=get_today_video_days(cookies);auth_time=middleware.bucketGet('s_mibao_auth',account)or'未授权';query_msg=f"""
=====账号信息=====
📱 账号: {format_phone(account)}
👤 UID: {user_info["uid"]}
📅 到期: {auth_time}
=====小米社区=====
🎖️ 等级: {user_info["title"]}({user_info["showLevel"]})
📈 成长值: {user_info["point"]}
=====小米钱包=====
📺 总视频天数: {video_days}天
🎬 今日天数: {today_video_days}
==================""";sender.reply(query_msg);return True
	except Exception as e:sender.reply(f"❌ 账号 {format_phone(account)} 查询失败: {str(e)}");return False
def query_xiaomi():
	try:
		accounts=eval(uservalue or'[]')
		if not accounts:sender.reply('❌ 您还没有绑定小米账号');return
		if len(accounts)==1:query_single_account(accounts[0]);return
		account_list='=====选择查询账号=====\n';account_list+='[0] 查询全部账号\n'
		for(i,account)in enumerate(accounts,1):
			auth_time=middleware.bucketGet('s_mibao_auth',account)
			if auth_time and auth_time.strip():status=f"(到期: {auth_time})"
			else:status='(未授权)'
			account_list+=f"[{i}] {format_phone(account)} {status}\n"
		account_list+='------------------\n请选择要查询的账号序号\n支持多选：用英文逗号分隔，如 1,3,5\n回复"q"退出查询';sender.reply(account_list);choice=sender.listen(60000)
		if not choice or choice=='q':sender.reply('✅ 已退出查询');return
		selected_accounts=[]
		try:
			if choice=='0':selected_accounts=accounts
			elif','in choice:
				choice_nums=[int(x.strip())for x in choice.split(',')]
				for choice_num in choice_nums:
					if 1<=choice_num<=len(accounts):
						if accounts[choice_num-1]not in selected_accounts:selected_accounts.append(accounts[choice_num-1])
					else:sender.reply(f"❌ 无效选择: {choice_num}");return
			else:
				index=int(choice)-1
				if 0<=index<len(accounts):selected_accounts=[accounts[index]]
				else:sender.reply('❌ 无效的账号序号');return
		except ValueError:sender.reply('❌ 请输入有效数字或用逗号分隔的数字');return
		if not selected_accounts:sender.reply('❌ 没有选择任何账号');return
		if len(selected_accounts)==1:sender.reply(f"🔍 正在查询账号 {format_phone(selected_accounts[0])}...");query_single_account(selected_accounts[0])
		else:
			sender.reply(f"🔍 正在查询 {len(selected_accounts)} 个账号信息...");success_count=0;fail_count=0
			for account in selected_accounts:
				if query_single_account(account):success_count+=1
				else:fail_count+=1
			summary_msg=f"\n=====查询汇总=====\n✅ 成功: {success_count}个账号\n❌ 失败: {fail_count}个账号\n==================";sender.reply(summary_msg)
	except Exception as e:sender.reply(f"❌ 查询失败: {str(e)}")
def delete_from_qinglong(account):
	try:
		url=f"{ql_url}/open/envs";headers={'Authorization':f"Bearer {ql_token}"};response=requests.get(url,headers=headers)
		if response.status_code!=200:raise Exception('获取变量失败')
		env_id=None
		for env in response.json()['data']:
			if env['name']==var_name and account in env.get('remarks',''):env_id=env['id'];break
		if env_id:
			response=requests.delete(url,headers=headers,json=[env_id])
			if response.status_code!=200:raise Exception('删除变量失败')
		return True
	except Exception as e:sender.reply(f"❌ 青龙操作失败: {str(e)}");return False
def clean_xiaomi():
	if not sender.isAdmin():sender.reply('❌ 需要管理员权限');return
	try:
		global ql_url,ql_token;ql_url,ql_token=init_qinglong();users=middleware.bucketAllKeys('s_mibao_user');cleaned=0;today=str(datetime.now().date())
		for user in users:
			accounts=eval(middleware.bucketGet('s_mibao_user',user)or'[]');valid=[]
			for account in accounts:
				auth=middleware.bucketGet('s_mibao_auth',account)
				if not auth or auth<=today:middleware.bucketSet('s_mibao_token',account,'');middleware.bucketSet('s_mibao_auth',account,'');middleware.bucketSet('s_mibao_pwd',account,'');delete_from_qinglong(account);cleaned+=1
				else:valid.append(account)
			if valid:middleware.bucketSet('s_mibao_user',user,str(valid))
			else:middleware.bucketDel('s_mibao_user',user)
		sender.reply(f"✅ 已清理 {cleaned} 个过期账号")
	except Exception as e:sender.reply(f"❌ 清理失败: {str(e)}")
def manage_xiaomi():
	try:
		accounts=eval(uservalue or'[]')
		if not accounts:sender.reply('❌ 您还没有绑定小米账号');return
		manage_options='\n=====管理选项=====\n[1] 账号授权\n[2] 账号删除\n------------------\n回复数字选择操作\n回复"q"退出';sender.reply(manage_options);option=sender.listen(60000)
		if not option or option=='q':sender.reply('✅ 已退出管理流程');return
		if option not in['1','2']:sender.reply('❌ 无效的选择');return
		account_list='=====账号列表=====\n';account_list+='[0] 全部账号\n'
		for(i,account)in enumerate(accounts,1):
			auth_time=middleware.bucketGet('s_mibao_auth',account)
			if auth_time and auth_time.strip():status=f"(到期: {auth_time})"
			else:status='(未授权)'
			account_list+=f"[{i}] {format_phone(account)} {status}\n"
		manage_msg=f'{account_list}\n------------------\n请选择要{option=="1"and"授权"or"删除"}的账号\n支持多选：用英文逗号分隔，如 1,3,5\n回复"q"退出';sender.reply(manage_msg);choice=sender.listen(60000)
		if not choice or choice=='q':sender.reply('✅ 已退出管理流程');return
		selected_accounts=[]
		if choice=='0':selected_accounts=accounts[:]
		else:
			try:
				indices=[int(x.strip())-1 for x in choice.split(',')]
				for index in indices:
					if 0<=index<len(accounts):selected_accounts.append(accounts[index])
			except ValueError:sender.reply('❌ 无效的选择格式');return
		if not selected_accounts:sender.reply('❌ 未选择有效账号');return
		if option=='1':
			if len(selected_accounts)==1:process_auth(selected_accounts[0])
			else:
				sender.reply('\n=====批量授权设置=====\n请输入授权月数(如:1)\n--------------------------\n回复数字设置月数\n回复"q"退出操作\n==================');months=sender.listen(60000)
				if not months or months.lower()=='q':sender.reply('✅ 已取消授权');return
				try:
					months=int(months)
					if months<=0:raise ValueError()
				except ValueError:sender.reply('❌ 无效的月数');return
				total_price=price*months*len(selected_accounts);available_payments=[];ma_pay_switch=(middleware.bucketGet('s_mibao','ma_pay_switch')or'false').lower()
				if ma_pay_switch=='true':
					ma_pay_type=middleware.bucketGet('dd_sign_config','ma_pay_type')or''
					if not ma_pay_type:ma_pay_type='alipay,wxpay'
					pay_types=[p.strip()for p in ma_pay_type.split(',')if p.strip()]
					for pay_type in pay_types:
						if pay_type=='alipay':available_payments.append(('支付宝','alipay'))
						elif pay_type=='wxpay':available_payments.append(('微信支付','wxpay'))
						elif pay_type=='qqpay':available_payments.append(('QQ钱包','qqpay'))
				else:
					zsm=middleware.bucketGet('s_mibao','zsm')
					if zsm:available_payments.append(('微信支付','wxpay'))
				if coin_price>0:available_payments.append(('积分兑换','coin'))
				if not available_payments:sender.reply('❌ 未配置任何支付方式');return
				if len(available_payments)==1:payment_name,payment_type=available_payments[0]
				else:
					auth_menu=f"""
=====选择支付方式=====
⏰ 授权账号: {len(selected_accounts)}个
⏰ 授权时长: {months}个月
💰 总金额: {total_price}元
------------------"""
					for(i,(name,_))in enumerate(available_payments,1):auth_menu+=f"\n[{i}] {name}"
					auth_menu+='\n------------------\n回复数字选择方式\n回复"q"退出操作\n==================';sender.reply(auth_menu);pay_choice=sender.listen(120000)
					if not pay_choice or pay_choice.lower()=='q':sender.reply('✅ 已取消授权');return
					try:
						choice_idx=int(pay_choice)-1
						if not 0<=choice_idx<len(available_payments):sender.reply('❌ 无效的选择');return
						payment_name,payment_type=available_payments[choice_idx]
					except ValueError:sender.reply('❌ 请输入有效的数字');return
				if payment_type=='coin':
					total_coins=int(coin_price)*months*len(selected_accounts);user_coins,error=get_user_points(userid)
					if error:sender.reply(f"❌ {error}");return
					if user_coins<total_coins:sender.reply(f"❌ 积分不足\n当前积分: {user_coins}\n所需积分: {total_coins}");return
					middleware.bucketSet('dd_sign_points',userid,str(user_coins-total_coins));success_count=0;fail_count=0
					for account_to_auth in selected_accounts:
						if process_authorization_xiaomi(account_to_auth,months):success_count+=1
						else:fail_count+=1
					remaining_coins=int(middleware.bucketGet('dd_sign_points',userid)or'0');success_msg=f'''
=====批量积分授权成功=====
📱 授权账号: {success_count}个
❌ 失败账号: {fail_count}个
🎯 总消耗积分: {total_coins}
⏰ 授权时长: {months}月
💰 剩余积分: {remaining_coins}
------------------
发送"小米查询"查看账号详情''';sender.reply(success_msg)
				else:
					ma_pay_switch_local=(middleware.bucketGet('s_mibao','ma_pay_switch')or'false').lower()
					if ma_pay_switch_local=='true':
						if payment_type in['alipay','wxpay','qqpay']:
							if handle_mapay_payment(f"小米社区批量授权-{len(selected_accounts)}个",months,total_price,pay_type=payment_type):
								success_count=0;fail_count=0
								for account_to_auth in selected_accounts:
									if process_authorization_xiaomi(account_to_auth,months):success_count+=1
									else:fail_count+=1
								sender.reply(f"=====批量码支付授权完成=====\n📱 成功授权: {success_count}个\n❌ 授权失败: {fail_count}个\n💰 总支付: {total_price}元\n⏰ 授权时长: {months}月")
						else:sender.reply(f"❌ 码支付不支持的支付类型: {payment_type}，无法批量处理。")
					elif payment_type=='wxpay':
						sender.reply(f"ℹ️ 微信赞赏码模式下，需要对 {len(selected_accounts)} 个账号分别进行支付。");success_count=0;fail_count=0;paid_successfully_for_all=True
						for(i,account_to_auth)in enumerate(selected_accounts,1):
							sender.reply(f"\n=====正在为第 {i}/{len(selected_accounts)} 个账号授权=====\n📱 账号: {account_to_auth}");single_price=price*months
							if pay_with_zsm(f"小米社区授权-{account_to_auth}",months,single_price):
								if process_authorization_xiaomi(account_to_auth,months):success_count+=1
								else:fail_count+=1
							else:sender.reply(f"❌ 账号 {account_to_auth} 支付失败或取消，跳过此账号。");fail_count+=1;paid_successfully_for_all=False
						sender.reply(f"=====批量微信支付授权完成=====\n📱 成功授权: {success_count}个\n❌ 授权失败: {fail_count}个\n⏰ 授权时长: {months}月")
					else:sender.reply(f"❌ 配置错误或未知的支付类型: {payment_type} (码支付已关闭)，无法批量处理。")
		else:
			confirm_msg='=====删除确认=====\n';confirm_msg+='即将删除以下账号:\n'
			for account in selected_accounts:auth_time=middleware.bucketGet('s_mibao_auth',account)or'未授权';confirm_msg+=f"- {format_phone(account)} ({auth_time})\n"
			confirm_msg+='------------------\n';confirm_msg+='⚠️ 数据及授权无法恢复\n';confirm_msg+='回复"y"确认删除\n';sender.reply(confirm_msg);confirm=sender.listen(60000)
			if confirm.lower()!='y':sender.reply('✅ 已取消删除');return
			success_count=0
			for account in selected_accounts:
				try:
					accounts.remove(account);middleware.bucketSet('s_mibao_token',account,'');middleware.bucketSet('s_mibao_auth',account,'');middleware.bucketSet('s_mibao_pwd',account,'')
					if delete_from_qinglong(account):success_count+=1
				except:continue
			if accounts:middleware.bucketSet('s_mibao_user',userid,str(accounts))
			else:middleware.bucketDel('s_mibao_user',userid)
			sender.reply(f"✅ 已成功删除 {success_count}/{len(selected_accounts)} 个账号")
	except Exception as e:sender.reply(f"❌ 管理失败: {str(e)}");return False
def admin_authorize():
	try:
		sender.reply('\n=====小米授权管理=====\n请选择授权方式：\n1. 单用户授权\n2. 一键授权所有账号\n回复对应数字选择\n==================');choice=sender.listen(60000)
		if not choice:sender.reply('❌ 操作超时');return
		if choice=='1':single_user_authorize()
		elif choice=='2':batch_authorize_all()
		else:sender.reply('❌ 无效选择')
	except Exception as e:sender.reply(f"❌ 授权管理出错: {str(e)}")
def single_user_authorize():
	try:
		sender.reply('请输入用户ID:');target_userid=sender.listen(60000)
		if not target_userid:sender.reply('❌ 操作超时');return
		accounts=eval(middleware.bucketGet('s_mibao_user',target_userid)or'[]')
		if not accounts:sender.reply(f"❌ 用户 {target_userid} 没有绑定任何账号");return
		menu='=====账号选择=====\n';menu+='0. 所有账号\n'
		for(i,account)in enumerate(accounts,1):
			auth_time=middleware.bucketGet('s_mibao_auth',account)
			if auth_time and auth_time.strip():status=f"(到期: {auth_time})"
			else:status='(未授权)'
			menu+=f"{i}. {format_phone(account)} {status}\n"
		menu+='回复对应数字选择\n';menu+='支持多选：用英文逗号分隔，如 1,3,5\n';menu+='==================';sender.reply(menu);choice=sender.listen(60000)
		if not choice:sender.reply('❌ 操作超时');return
		selected_accounts=[]
		try:
			if','in choice:
				choice_nums=[int(x.strip())for x in choice.split(',')]
				for choice_num in choice_nums:
					if choice_num==0:selected_accounts=accounts;sender.reply(f"已选择所有账号 ({len(accounts)}个)");break
					elif 1<=choice_num<=len(accounts):
						if accounts[choice_num-1]not in selected_accounts:selected_accounts.append(accounts[choice_num-1])
					else:sender.reply(f"❌ 无效选择: {choice_num}");return
				if selected_accounts!=accounts:account_list=[format_phone(acc)for acc in selected_accounts];sender.reply(f"已选择 {len(selected_accounts)} 个账号")
			else:
				choice_num=int(choice)
				if choice_num==0:selected_accounts=accounts;sender.reply(f"已选择所有账号 ({len(accounts)}个)")
				elif 1<=choice_num<=len(accounts):selected_accounts=[accounts[choice_num-1]];sender.reply(f"已选择账号: {format_phone(accounts[choice_num-1])}")
				else:sender.reply('❌ 无效选择');return
		except ValueError:sender.reply('❌ 请输入有效数字或用逗号分隔的数字');return
		if not selected_accounts:sender.reply('❌ 没有选择任何账号');return
		sender.reply('请输入授权月份:');months_input=sender.listen(60000)
		if not months_input:sender.reply('❌ 操作超时');return
		try:
			months=int(months_input)
			if months<=0:sender.reply('❌ 月份必须大于0');return
		except ValueError:sender.reply('❌ 请输入有效的月份数字');return
		success_count=0;fail_count=0
		for account in selected_accounts:
			if process_authorization_xiaomi(account,months):success_count+=1
			else:fail_count+=1
		result_msg=f"""
=====授权完成=====
✅ 成功: {success_count}个
❌ 失败: {fail_count}个
⏰ 授权时长: {months}月
👤 目标用户: {target_userid}
================""";sender.reply(result_msg)
	except Exception as e:sender.reply(f"❌ 单用户授权出错: {str(e)}")
def batch_authorize_all():
	try:
		sender.reply('请输入授权月份:');months_input=sender.listen(60000)
		if not months_input:sender.reply('❌ 操作超时');return
		try:
			months=int(months_input)
			if months<=0:sender.reply('❌ 月份必须大于0');return
		except ValueError:sender.reply('❌ 请输入有效的月份数字');return
		all_accounts=set();users=middleware.bucketAllKeys('s_mibao_user')
		for user in users:accounts=eval(middleware.bucketGet('s_mibao_user',user)or'[]');all_accounts.update(accounts)
		if not all_accounts:sender.reply('❌ 没有找到任何绑定的账号');return
		all_accounts=list(all_accounts);sender.reply(f"找到 {len(all_accounts)} 个账号，开始批量授权...");success_count=0;fail_count=0
		for(i,account)in enumerate(all_accounts,1):
			sender.reply(f"正在授权 {format_phone(account)} ({i}/{len(all_accounts)})")
			if process_authorization_xiaomi(account,months):success_count+=1
			else:fail_count+=1
		result_msg=f"""
=====批量授权完成=====
✅ 成功: {success_count}个
❌ 失败: {fail_count}个
⏰ 授权时长: {months}月
📱 总账号数: {len(all_accounts)}个
===================""";sender.reply(result_msg)
	except Exception as e:sender.reply(f"❌ 批量授权出错: {str(e)}")
def get_xiaomi_cookies(user_id,pass_token):
	session=requests.Session();login_url='https://account.xiaomi.com/pass/serviceLogin?callback=https%3A%2F%2Fapi.jr.airstarfinance.net%2Fsts%3Fsign%3D1dbHuyAmee0NAZ2xsRw5vhdVQQ8%253D%26followup%3Dhttps%253A%252F%252Fm.jr.airstarfinance.net%252Fmp%252Fapi%252Flogin%253Ffrom%253Dmipay_indexicon_TVcard%2526deepLinkEnable%253Dfalse%2526requestUrl%253Dhttps%25253A%25252F%25252Fm.jr.airstarfinance.net%25252Fmp%25252Factivity%25252FvideoActivity%25253Ffrom%25253Dmipay_indexicon_TVcard%252526_noDarkMode%25253Dtrue%252526_transparentNaviBar%25253Dtrue%252526cUserId%25253Dusyxgr5xjumiQLUoAKTOgvi858Q%252526_statusBarHeight%25253D137&sid=jrairstar&_group=DEFAULT&_snsNone=true&_loginType=ticket';headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0','cookie':f"passToken={pass_token}; userId={user_id};"}
	try:
		response=session.get(url=login_url,headers=headers,verify=False,timeout=30);cookies=session.cookies.get_dict()
		if cookies.get('cUserId')and cookies.get('serviceToken'):cookie_str=f"cUserId={cookies.get('cUserId')};jrairstar_serviceToken={cookies.get('serviceToken')}";return cookie_str
		else:sender.reply(f"❌ Cookie获取失败：未获取到必要的Cookie字段");return
	except Exception as e:error_msg=f"获取Cookie失败: {e}";print(f"❌ {error_msg}");return
def xiaomi_exchange():
	try:
		accounts=eval(uservalue or'[]')
		if not accounts:sender.reply('❌ 您还没有绑定小米账号，请先发送「小米登录」绑定账号');return
		if len(accounts)==1:exchange_for_account(accounts[0]);return
		account_list='=====选择兑换账号=====\n'
		for(i,account)in enumerate(accounts,1):
			auth_time=middleware.bucketGet('s_mibao_auth',account)
			if auth_time and auth_time.strip():status=f"(到期: {auth_time})"
			else:status='(未授权)'
			account_list+=f"[{i}] {format_phone(account)} {status}\n"
		account_list+='------------------\n请选择要兑换的账号序号\n回复"q"退出兑换';sender.reply(account_list);choice=sender.listen(60000)
		if not choice or choice=='q':sender.reply('✅ 已退出兑换');return
		try:
			index=int(choice)-1
			if 0<=index<len(accounts):exchange_for_account(accounts[index])
			else:sender.reply('❌ 无效的账号序号')
		except ValueError:sender.reply('❌ 请输入有效的数字序号')
	except Exception as e:sender.reply(f"❌ 兑换功能出错: {str(e)}")
def exchange_for_account(account):
	try:
		sender.reply(f"🔄 正在为账号 {format_phone(account)} 获取兑换信息...");cookie_str=middleware.bucketGet('s_mibao_token',account)
		if not cookie_str:sender.reply(f"❌ 账号 {format_phone(account)} 的Cookie信息丢失，请重新登录");return False
		parts=cookie_str.split('#')
		if len(parts)<3:sender.reply(f"❌ 账号 {format_phone(account)} 的Cookie格式错误");return False
		user_id=parts[0];old_cookie_str=parts[2];old_cookies=parse_cookie_string(old_cookie_str);pass_token=old_cookies.get('passToken')
		if not pass_token:sender.reply(f"❌ 账号 {format_phone(account)} 的passToken丢失，请重新登录");return False
		wallet_cookies=get_xiaomi_cookies(user_id,pass_token)
		if not wallet_cookies:sender.reply(f"❌ 获取账号 {format_phone(account)} 的钱包Cookie失败");return False
		prizes=get_prize_list(wallet_cookies)
		if not prizes:sender.reply('❌ 获取奖品列表失败');return False
		available_prizes=[prize for prize in prizes if prize.get('prizeType')==26]
		if not available_prizes:sender.reply('❌ 当前没有可兑换的奖品');return False
		total_days=get_video_days(old_cookie_str);prize_menu=f"已选择账号：{format_phone(account)}\n可兑换天数：{total_days}天\n=====可兑换奖品=====\n"
		for(i,prize)in enumerate(available_prizes,1):
			prize_name=prize.get('prizeName','未知奖品');need_points=prize.get('needGoldRice',0)/100;todayStockStatus=prize.get('todayStockStatus',1)
			if todayStockStatus==2:prize_menu+=f"[{i}] {prize_name}『无库存』\n"
			elif float(total_days)>=float(need_points):prize_menu+=f"[{i}] {prize_name}『需{need_points:.0f}天』\n"
			else:prize_menu+=f"[{i}] {prize_name}『天数不足』\n"
		prize_menu+='------------------\n请选择要兑换的奖品序号\n回复"q"退出兑换';sender.reply(prize_menu);choice=sender.listen(60000)
		if not choice or choice=='q':sender.reply('✅ 已退出兑换');return False
		try:
			index=int(choice)-1
			if 0<=index<len(available_prizes):
				selected_prize=available_prizes[index];prize_code=selected_prize.get('prizeCode');prize_name=selected_prize.get('prizeName');sender.reply('请输入兑换到的手机号:');target_phone=sender.listen(60000)
				if not target_phone:sender.reply('❌ 未输入手机号，兑换已取消');return False
				if not is_valid_phone(target_phone):sender.reply('❌ 手机号格式不正确，兑换已取消');return False
				sender.reply(f'''请仔细确认兑换信息
兑换奖品：「{prize_name}」
兑换手机号：「{target_phone}」
------------------
[1] 立即兑换
[2] 提交抢兑任务
回复"q"取消''');action=sender.listen(30000)
				if not action or action=='q':sender.reply('✅ 已取消兑换');return False
				if action=='1':
					result=exchange_prize(wallet_cookies,prize_code,target_phone)
					if result:sender.reply(f"✅ 兑换成功！「{prize_name}」已兑换到手机号 {format_phone(target_phone)}")
					else:sender.reply(f"❌ 兑换失败，请进入小米钱包APP完成新手任务后重试")
				elif action=='2':task_id=f"{userid}_{account}_{int(time.time()*1000)}";task_data={'user_id':userid,'account':account,'prize_code':prize_code,'prize_name':prize_name,'target_phone':target_phone,'submit_time':datetime.now().strftime('%Y-%m-%d %H:%M:%S')};middleware.bucketSet('s_mibao_dh',task_id,json.dumps(task_data));sender.reply(f"""✅ 抢兑任务已提交
账号: {format_phone(account)}
奖品: {prize_name}
手机号: {format_phone(target_phone)}
------------------
管理员可使用「米包抢兑」指令执行抢兑
使用「米包删除抢兑」可删除任务""")
				else:sender.reply('❌ 无效的选项，已取消兑换')
			else:sender.reply('❌ 无效的奖品序号')
		except ValueError:sender.reply('❌ 请输入有效的数字序号')
	except Exception as e:sender.reply(f"❌ 兑换过程出错: {str(e)}");return False
def get_prize_list(wallet_cookies):
	try:
		headers={'sec-ch-ua-platform':'"Android"','Cache-Control':'no-cache','sec-ch-ua':'"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"','sec-ch-ua-mobile':'?1','X-Requested-With':'com.mipay.wallet','Sec-Fetch-Site':'same-origin','Sec-Fetch-Mode':'cors','Sec-Fetch-Dest':'empty','Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7','Cookie':wallet_cookies};response=requests.get('https://m.jr.airstarfinance.net/mp/api/generalActivity/getPrizeStatusV2?activityCode=2211-videoWelfare&needPrizeBrand=youku,mgtv,iqiyi,tencent,bilibili,other',headers=headers)
		if response.status_code==200:
			data=response.json()
			if data.get('success'):return data.get('value',[])
		return[]
	except Exception as e:sender.reply(f"❌ 获取奖品列表失败: {str(e)}");return[]
def exchange_prize(wallet_cookies,prize_code,phone):
	try:
		headers={'sec-ch-ua-platform':'"Android"','Cache-Control':'no-cache','sec-ch-ua':'"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"','sec-ch-ua-mobile':'?1','X-Requested-With':'com.mipay.wallet','Sec-Fetch-Site':'same-origin','Sec-Fetch-Mode':'cors','Sec-Fetch-Dest':'empty','Accept-Language':'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7','Cookie':wallet_cookies};params={'prizeCode':prize_code,'activityCode':'2211-videoWelfare','phone':phone,'app':'com.mipay.wallet','oaid':'f1dd1fcbead29141','versionCode':'20577623','versionName':'6.96.1.5454.2614','isNfcPhone':'true','channel':'exchange','deviceType':'2','system':'1','visitEnvironment':'2','userExtra':'{"platformType":1,"com.miui.player":"4.37.0.2","com.mipay.wallet":"6.96.1.5454.2614"}'};response=requests.get('https://m.jr.airstarfinance.net/mp/api/generalActivity/convertGoldRich',params=params,headers=headers)
		if response.status_code==200:data=response.json();return data.get('success',False)
		return False
	except Exception as e:sender.reply(f"❌ 兑换请求失败: {str(e)}");return False
def delete_exchange_task():
	try:
		all_tasks=middleware.bucketAllKeys('s_mibao_dh')or[];user_tasks=[]
		for task_id in all_tasks:
			task_json=middleware.bucketGet('s_mibao_dh',task_id)
			if task_json:
				try:
					task_data=json.loads(task_json)
					if task_data.get('user_id')==userid:user_tasks.append((task_id,task_data))
				except:continue
		if not user_tasks:sender.reply('❌ 您没有待处理的抢兑任务');return
		task_menu='=====您的抢兑任务=====\n'
		for(i,(task_id,task_data))in enumerate(user_tasks,1):account=task_data.get('account','未知');prize_name=task_data.get('prize_name','未知奖品');target_phone=task_data.get('target_phone','未知');submit_time=task_data.get('submit_time','未知');task_menu+=f"[{i}] {format_phone(account)} - {prize_name}\n";task_menu+=f"    目标手机: {format_phone(target_phone)}\n";task_menu+=f"    提交时间: {submit_time}\n"
		task_menu+='------------------\n请选择要删除的任务序号\n回复"q"退出';sender.reply(task_menu);choice=sender.listen(60000)
		if not choice or choice=='q':sender.reply('✅ 已退出');return
		try:
			index=int(choice)-1
			if 0<=index<len(user_tasks):
				task_id,task_data=user_tasks[index];sender.reply(f'确认删除任务？\n账号: {format_phone(task_data.get("account"))}\n奖品: {task_data.get("prize_name")}\n回复"y"确认删除');confirm=sender.listen(30000)
				if confirm=='y':middleware.bucketDel('s_mibao_dh',task_id);sender.reply('✅ 任务已删除')
				else:sender.reply('✅ 已取消删除')
			else:sender.reply('❌ 无效的任务序号')
		except ValueError:sender.reply('❌ 请输入有效的数字序号')
	except Exception as e:sender.reply(f"❌ 删除任务出错: {str(e)}")
def prepare_exchange_cookies(account):
	try:
		cookie_str=middleware.bucketGet('s_mibao_token',account)
		if not cookie_str:return None,f"❌ {format_phone(account)} - Cookie丢失"
		parts=cookie_str.split('#')
		if len(parts)<3:return None,f"❌ {format_phone(account)} - Cookie格式错误"
		user_id=parts[0];old_cookie_str=parts[2];old_cookies=parse_cookie_string(old_cookie_str);pass_token=old_cookies.get('passToken')
		if not pass_token:return None,f"❌ {format_phone(account)} - passToken丢失"
		wallet_cookies=get_xiaomi_cookies(user_id,pass_token)
		if not wallet_cookies:return None,f"❌ {format_phone(account)} - 获取钱包Cookie失败"
		return wallet_cookies,f"✅ {format_phone(account)} - Cookie准备完成"
	except Exception as e:return None,f"❌ {format_phone(account)} - Cookie准备异常: {str(e)}"
def execute_single_exchange_task(task_id,task_data,retry_times,prepared_cookies=None):
	account=task_data.get('account');prize_code=task_data.get('prize_code');prize_name=task_data.get('prize_name');target_phone=task_data.get('target_phone');wallet_cookies=prepared_cookies
	if not wallet_cookies:
		wallet_cookies,msg=prepare_exchange_cookies(account)
		if not wallet_cookies:return False,msg,task_id
	for attempt in range(retry_times):
		try:
			result=exchange_prize(wallet_cookies,prize_code,target_phone)
			if result:return True,f"✅ {format_phone(account)} - {prize_name} - 兑换成功",task_id
			if attempt<retry_times-1:time.sleep(.5)
		except Exception as e:
			if attempt<retry_times-1:time.sleep(.5)
			else:return False,f"❌ {format_phone(account)} - {prize_name} - 异常: {str(e)}",task_id
	return False,f"❌ {format_phone(account)} - {prize_name} - 重试{retry_times}次后失败",task_id
def xiaomi_rush_exchange():
	try:
		if not sender.isAdmin():sender.reply('❌ 此功能需要管理员权限');return
		concurrent_num=int(middleware.bucketGet('s_mibao','rush_concurrent')or'5');retry_times=int(middleware.bucketGet('s_mibao','rush_retry')or'3');rush_time_str=middleware.bucketGet('s_mibao','rush_time')or''
		if concurrent_num<1:concurrent_num=1
		if concurrent_num>20:concurrent_num=20
		if retry_times<1:retry_times=1
		if retry_times>10:retry_times=10
		all_task_ids=middleware.bucketAllKeys('s_mibao_dh')or[]
		if not all_task_ids:sender.reply('❌ 当前没有待处理的抢兑任务');return
		tasks=[]
		for task_id in all_task_ids:
			task_json=middleware.bucketGet('s_mibao_dh',task_id)
			if task_json:
				try:task_data=json.loads(task_json);tasks.append((task_id,task_data))
				except:continue
		if not tasks:sender.reply('❌ 没有有效的抢兑任务');return
		target_time=None
		if rush_time_str:
			try:
				time_parts=rush_time_str.strip().split(':')
				if len(time_parts)==3:
					hour,minute,second=map(int,time_parts);now=datetime.now();target_time=now.replace(hour=hour,minute=minute,second=second,microsecond=0)
					if target_time<=now:target_time+=timedelta(days=1)
			except:sender.reply('❌ 抢兑时间格式错误，应为 HH:MM:SS，将立即执行');target_time=None
		sender.reply(f"🔄 开始准备抢兑任务\n📋 任务数: {len(tasks)} 个\n⚡ 并发数: {concurrent_num}\n🔁 重试次数: {retry_times}");prepared_cookies={};prepare_success=0;prepare_fail=0
		for(task_id,task_data)in tasks:
			account=task_data.get('account');prize_name=task_data.get('prize_name');wallet_cookies,msg=prepare_exchange_cookies(account)
			if wallet_cookies:prepared_cookies[task_id]=wallet_cookies;prepare_success+=1;sender.reply(f"✅ {format_phone(account)} - {prize_name} - Cookie准备完成")
			else:prepare_fail+=1;sender.reply(msg)
		sender.reply(f"📊 Cookie准备完成\n✅ 成功: {prepare_success} 个\n❌ 失败: {prepare_fail} 个")
		if prepare_success==0:sender.reply('❌ 没有任何任务准备成功，取消抢兑');return
		if target_time:
			wait_seconds=(target_time-datetime.now()).total_seconds()
			if wait_seconds>0:sender.reply(f"⏰ 定时抢兑已设置\n🕐 目标时间: {target_time.strftime('%Y-%m-%d %H:%M:%S')}\n⏳ 等待时间: {int(wait_seconds)} 秒\n💡 抢兑将在指定时间自动执行");time.sleep(wait_seconds);sender.reply(f"🚀 时间到！开始执行抢兑...")
		else:sender.reply(f"🚀 立即开始执行抢兑...")
		success_count=0;fail_count=0;results=[]
		with ThreadPoolExecutor(max_workers=concurrent_num)as executor:
			future_to_task={executor.submit(execute_single_exchange_task,task_id,task_data,retry_times,prepared_cookies.get(task_id)):(task_id,task_data)for(task_id,task_data)in tasks if task_id in prepared_cookies}
			for future in as_completed(future_to_task):
				task_id,task_data=future_to_task[future]
				try:
					success,msg,tid=future.result()
					if success:success_count+=1;middleware.bucketDel('s_mibao_dh',tid)
					else:fail_count+=1
					results.append(msg);sender.reply(msg)
				except Exception as e:fail_count+=1;results.append(f"❌ 任务执行异常: {str(e)}")
		summary=f"""
=====抢兑任务完成=====
✅ 成功: {success_count} 个
❌ 失败: {fail_count} 个
⚡ 并发数: {concurrent_num}
🔁 重试次数: {retry_times}"""
		if target_time:summary+=f"\n⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
		summary+='\n==================';sender.reply(summary)
	except Exception as e:sender.reply(f"❌ 抢兑功能出错: {str(e)}")
def update_cookie_by_passtoken(account):
	try:
		cookie_str=middleware.bucketGet('s_mibao_token',account)
		if not cookie_str:return False,'Cookie信息丢失'
		parts=cookie_str.split('#')
		if len(parts)<3:return False,'Cookie格式错误'
		user_id=parts[0];password=parts[1];old_cookie_str=parts[2];old_cookies=parse_cookie_string(old_cookie_str);pass_token=old_cookies.get('passToken')
		if not pass_token:return False,'passToken丢失'
		user_agent='Dalvik/2.1.0 (Linux; U; Android 14; 2210132C Build/UKQ1.230705.002) APP/xiaomi.vipaccount APPV/20231107 MK/WGlhb21p IDEz IFBybw== SDKV/5.1.0.release.13 PassportSDK/5.1.0.release.15 passport-ui/5.1.0.release.15';new_cookies=get_cookies_by_passtk(user_id,pass_token,user_agent)
		if not new_cookies:return False,'获取新Cookie失败'
		new_cookies.update({'passToken':pass_token,'userId':user_id});new_cookie_str=cookie_to_string(new_cookies);updated_cookie_str=f"{user_id}#{password}#{new_cookie_str}";middleware.bucketSet('s_mibao_token',account,updated_cookie_str);return True,'更新成功'
	except Exception as e:return False,f"更新异常: {str(e)}"
def update_all_cookies(accounts,show_result=True):
	success_count=0;fail_count=0;fail_accounts=[];verify_accounts=[];unauthorized_accounts=[];current_date=str(datetime.now().date());valid_accounts=[]
	for account in accounts:
		auth_time=middleware.bucketGet('s_mibao_auth',account)
		if auth_time and auth_time>current_date:valid_accounts.append(account)
		else:unauthorized_accounts.append(account)
	if not valid_accounts:sender.reply('❌ 没有找到有效授权的账号');return 0,0,[],[]
	total=len(valid_accounts);sender.reply(f"🔄 开始更新 {total} 个授权账号的Cookie...")
	for(i,account)in enumerate(valid_accounts,1):
		try:
			sender.reply(f"🔄 正在更新账号 {format_phone(account)} ({i}/{total})...");success,msg=update_cookie_by_passtoken(account)
			if success:success_count+=1;sender.reply(f"✅ 账号 {format_phone(account)} 更新成功 ({i}/{total})")
			else:
				sender.reply(f"⚠️ passtoken更新失败: {msg}，尝试账密更新...");password=middleware.bucketGet('s_mibao_pwd',account)
				if not password:fail_count+=1;fail_accounts.append(f"{format_phone(account)} (密码丢失)");sender.reply(f"❌ 账号 {format_phone(account)} 更新失败: 密码丢失 ({i}/{total})");continue
				result=login_with_account(account,password,skip_auth=True)
				if result is False:verify_accounts.append(account);sender.reply(f"⚠️ 账号 {format_phone(account)} 需要验证，跳过更新 ({i}/{total})");continue
				success_count+=1;sender.reply(f"✅ 账号 {format_phone(account)} 账密更新成功 ({i}/{total})")
		except Exception as e:fail_count+=1;fail_accounts.append(f"{format_phone(account)} ({str(e)})");sender.reply(f"❌ 账号 {format_phone(account)} 更新失败: {str(e)} ({i}/{total})")
	if show_result:
		result_msg=f"\n=====更新结果=====\n✅ 成功: {success_count}个\n❌ 失败: {fail_count}个"
		if unauthorized_accounts:
			result_msg+='\n\n未授权账号:'
			for account in unauthorized_accounts:result_msg+=f"\n- {format_phone(account)}"
		if fail_accounts:
			result_msg+='\n\n失败账号:'
			for account in fail_accounts:result_msg+=f"\n- {format_phone(account)}"
		if verify_accounts:
			result_msg+='\n\n需要验证的账号:'
			for account in verify_accounts:result_msg+=f"\n- {format_phone(account)}"
		sender.reply(result_msg)
	return success_count,fail_count,fail_accounts,verify_accounts
def sync_to_qinglong():
	try:
		if not sender.isAdmin():sender.reply('❌ 需要管理员权限');return
		global ql_url,ql_token;ql_url,ql_token=init_qinglong();current_date=str(datetime.now().date());all_accounts=[];authorized_accounts=[];users=middleware.bucketAllKeys('s_mibao_user')
		if not users:sender.reply('❌ 没有找到任何用户数据');return
		for user in users:
			try:
				accounts=eval(middleware.bucketGet('s_mibao_user',user)or'[]')
				for account in accounts:
					if account not in all_accounts:
						all_accounts.append(account);auth_time=middleware.bucketGet('s_mibao_auth',account)
						if auth_time and auth_time>current_date:authorized_accounts.append(account)
			except Exception as e:sender.reply(f"⚠️ 处理用户 {user} 数据时出错: {str(e)}");continue
		if not authorized_accounts:sender.reply(f"❌ 没有找到有效授权的账号\n总账号数: {len(all_accounts)}\n授权账号数: 0");return
		sender.reply(f"""
=====同步统计=====
📱 总账号数: {len(all_accounts)}
✅ 授权账号数: {len(authorized_accounts)}
🔄 开始同步到青龙...
==================""");success_count=0;fail_count=0;fail_accounts=[]
		for(i,account)in enumerate(authorized_accounts,1):
			try:
				cookie_str=middleware.bucketGet('s_mibao_token',account)
				if not cookie_str:fail_accounts.append(f"{format_phone(account)} (无Token)");fail_count+=1;continue
				parts=cookie_str.split('#')
				if len(parts)>=3:cookie_data=parts[2]
				else:cookie_data=cookie_str
				if add_to_qinglong(cookie_data,account,account):success_count+=1
				else:fail_accounts.append(f"{format_phone(account)} (同步失败)");fail_count+=1
			except Exception as e:fail_accounts.append(f"{format_phone(account)} ({str(e)})");fail_count+=1;sender.reply(f"❌ 账号 {format_phone(account)} 同步失败: {str(e)}")
		result_msg=f"\n=====同步完成=====\n✅ 成功同步: {success_count}个\n❌ 同步失败: {fail_count}个\n=================="
		if fail_accounts:
			result_msg+='\n\n失败账号详情:'
			for account in fail_accounts[:10]:result_msg+=f"\n- {account}"
			if len(fail_accounts)>10:result_msg+=f"\n... 还有{len(fail_accounts)-10}个失败账号"
		sender.reply(result_msg)
		if success_count>0:sender.reply('🎉 数据同步完成！现在可以在青龙面板中看到迁移后的账号数据了。')
	except Exception as e:sender.reply(f"❌ 同步青龙失败: {str(e)}")
def main():
	try:
		global var_name,ql_config,price,coin_price,ql_url,ql_token;var_name,ql_config,price,coin_price=get_config();message=str(sender.getMessage())
		if'米包查询'in message:query_xiaomi()
		elif'米包管理'in message:ql_url,ql_token=init_qinglong();manage_xiaomi()
		elif'米包一键更新'in message:
			if not sender.isAdmin():sender.reply('❌ 需要管理员权限');return
			ql_url,ql_token=init_qinglong();all_accounts=set();users=middleware.bucketAllKeys('s_mibao_user')
			for user in users:accounts=eval(middleware.bucketGet('s_mibao_user',user)or'[]');all_accounts.update(accounts)
			if not all_accounts:sender.reply('❌ 没有找到任何账号');return
			update_all_cookies(list(all_accounts))
		elif'米包登录'in message or'米包登陆'in message:ql_url,ql_token=init_qinglong();login()
		elif message=='米包清理':clean_xiaomi()
		elif message=='米包授权':
			if not sender.isAdmin():sender.reply('❌ 需要管理员权限');return
			ql_url,ql_token=init_qinglong();admin_authorize()
		elif message=='米包兑换':xiaomi_exchange()
		elif message=='米包抢兑':xiaomi_rush_exchange()
		elif message=='米包删除抢兑':delete_exchange_task()
		else:sender.setContinue()
	except Exception as e:sender.reply(f"❌ 运行出错: {str(e)}")
def poll_mapi_payment_status(out_trade_no,order_type=2,max_tries=30):
	PAYMENT_CONFIG=get_mapay_config();ma_pay_api=MaPay_Api(PAYMENT_CONFIG)
	for i in range(max_tries):
		success,data,msg=ma_pay_api.query_order(out_trade_no,order_type)
		if success:return True,msg,data
		result=sender.listen(5000)
		if result=='q':return False,'用户取消',None
	return False,'查询超时，订单可能尚未支付',None
def generate_qrcode(url):
	try:encoded_url=requests.utils.quote(url);api_url=f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M";return api_url
	except Exception as e:return
class MaPay_Api:
	def __init__(self,config):self.config=config;self.pay_type_names={'alipay':'支付宝','wxpay':'微信支付','qqpay':'QQ钱包'}
	def calculate_md5(self,text):return hashlib.md5(text.encode('utf-8')).hexdigest()
	def sort_dict_by_key(self,data):return dict(sorted(data.items(),key=lambda x:x[0]))
	def create_payment(self,amount,out_trade_no,name,user_id,pay_type=None,sitename=''):
		try:
			if pay_type is None:
				pay_types=[p.strip()for p in self.config.get('ma_pay_type','').split(',')if p.strip()]
				if not pay_types:pay_types=['alipay','wxpay']
				pay_type=pay_types[0]
			params={'pid':self.config['pid'],'type':pay_type,'out_trade_no':out_trade_no,'notify_url':self.config['notify_url'],'return_url':self.config['return_url'],'name':name,'money':str(amount),'sitename':sitename,'param':user_id};params={k:v for(k,v)in params.items()if v};sorted_params=self.sort_dict_by_key(params);sign_str='&'.join([f"{k}={v}"for(k,v)in sorted_params.items()]);sign=self.calculate_md5(sign_str+self.config['key']).lower();params['sign']=sign;params['sign_type']='MD5';mapi_url=self.config['gateway']
			if mapi_url.endswith('/'):mapi_url=mapi_url[:-1]
			mapi_url=f"{mapi_url}/mapi.php";headers={'Content-Type':'application/x-www-form-urlencoded'};response=requests.post(mapi_url,data=params,headers=headers,timeout=10)
			if response.status_code!=200:return False,None,f"创建支付订单失败，HTTP状态码: {response.status_code}"
			try:result=response.json()
			except:return False,None,'创建支付订单失败，返回数据格式错误'
			code=result.get('code',0);msg=result.get('msg','未知状态')
			if code==1:return True,result,msg
			else:return False,None,msg
		except Exception as e:return False,None,f"创建订单失败: {str(e)}"
	def query_order(self,out_trade_no,is_trade_no=False):
		try:
			api_url=self.config['gateway']
			if api_url.endswith('/'):api_url=api_url[:-1]
			query_url=f"{api_url}/xpay/epay/api.php";params={'act':'order','pid':self.config['pid'],'key':self.config['key']};params['out_trade_no']=out_trade_no;response=requests.get(query_url,params=params,timeout=10);sender.reply(f"查询订单结果: {response.text}")
			if response.status_code!=200:return False,f"查询订单失败，HTTP状态码: {response.status_code}",None
			try:result=response.json()
			except:return False,'查询订单失败，返回数据格式错误',None
			code=result.get('code',0);msg=result.get('msg','未知状态')
			if str(code)=='1':
				status=result.get('status',0)
				if str(status)=='1':return True,'支付成功',result
				else:return False,'订单未支付',result
			else:return False,msg,result
		except Exception as e:return False,f"查询订单异常: {str(e)}",None
	def verify_sign(self,params,sign):
		try:verify_params={k:v for(k,v)in params.items()if v and k!='sign'and k!='sign_type'};sorted_params=self.sort_dict_by_key(verify_params);params_str='&'.join([f"{k}={v}"for(k,v)in sorted_params.items()]);sign_str=params_str+self.config['key'];calculated_sign=self.calculate_md5(sign_str).lower();return calculated_sign==sign.lower()
		except Exception as e:return False
if __name__=='__main__':main()