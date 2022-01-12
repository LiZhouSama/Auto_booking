import requests
import re
import random
import time
import datetime

#用来无视访问https链接时出现的SSL证书认证
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#加密函数所用库 cryptography是个第三方库 可能需手动安装  Crypto是标准库 可能也需手动安装
#可能需要安装的库cryptography    pycrypto
#如若pycrypto安装失败可以试试pip install pycryptodome -i https://pypi.tuna.tsinghua.edu.cn/simple
import base64
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms
from Crypto.Cipher import AES

# 用于验证码处理库
from PIL import Image #PIL库安装pip install pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
from io import BytesIO
#文字识别库 需要安装tesseract  并添加环境变量 以下是环境变量配置的教程链接
#https://segmentfault.com/a/1190000014086067
import pytesseract 

# 加密函数 用来把密码加密进行登录 网上找的代码 正常使用 好评
class PrpCrypt(object):
    def __init__(self, key):
        self.key = key.encode('utf-8')
        self.iv = 'aaaabbbbaaaabbbb'.encode('utf-8')
        self.mode = AES.MODE_CBC
    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16当时不是16的倍数，那就补足为16的倍数。
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.iv)
        text = text.encode('utf-8')
        # 这里密钥key 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用
        text=self.pkcs7_padding(text)
        self.ciphertext = cryptor.encrypt(text)
        encodestrs = base64.b64encode(self.ciphertext)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return encodestrs.decode('utf8')
    @staticmethod
    def pkcs7_padding(data):
        if not isinstance(data, bytes):
            data = data.encode()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

def getsession(username,password,k=0):
    #用来获得一个成功登陆的会话 之后将用这个会话获取预约信息 并登录
    #登录接口
    url2 = 'https://newids.seu.edu.cn/authserver/login?service=http%3A%2F%2Fyuyue.seu.edu.cn%2Feduplus%2Forder%2FinitOrderIndex.do%3FsclId%3D1'
    session = requests.session()
    r2 = session.get(url2)
    #生成64位随机字符串，加到密码前面一起加密，即使用64个A代替也没啥问题（其实没啥用
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    str3 = ''
    for i in range(64):
        str3 +=  random.choice(alphabet)
    key = re.findall('pwdDefaultEncryptSalt = "(.*)"',r2.text)[0]
    pc = PrpCrypt(key)  # 初始化密钥  这个是加密用的密钥  同时也可用于解密
    #exe和It对应发送post请求包里带的信息，没懂具体啥意思，应该是每次验证的标识符了。
    exe = re.findall('name="execution" value="(.*)"',r2.text)[0]
    lt = re.findall('name="lt" value="(.*)"',r2.text)[0]
    password = pc.encrypt(str3+password)  # 将密码加到随机字符串后面 并对合并后的字符加密   （这是登录页设定的加密方式 只能照着使用
    Data = {
        'username': username,
        'password': password,
        'lt': lt,
        'dllt': 'userNamePasswordLogin',
        'execution': exe,
        '_eventId': 'submit',
        'rmShown': '1'
    }
    #print(Data)
    #这里用页面存在'团体预约'四字判断是否登录成功，
    if '团体预约' in session.post(url2,data=Data).text:
        print('成功登录')
        return session
    elif k>9:#没成功我就继续再来几次套娃
        print('登录失败，重试ing')
        k+=1
        session = getsession(username,password,k)
        return session
    else:
        print('登录失败，放弃了')
        return 0 

def recognize_captcha(img_path):
    #验证码识别
    im = Image.open(img_path)
    im = im.convert("L")
    # 1. threshold the image 色块两极化  就是去噪  判断的准
    threshold = 140
    table = [0]*threshold + [1]*(256-threshold)
    out = im.point(table, '1')
    #out.show() #显示处理后的验证码图片
    # 2. recognize with tesseract
    num = pytesseract.image_to_string(out)
    return num.replace("\n", "")#处理结果带了换行符，很奇怪，这里加了个小处理

def yuyue(session,start_time,day,changguanID,ids,phoneNum):
    #发起预约
    start_time = start_time+':00-'+str(int(start_time)+1)+':00'
    useTime = day+" "+start_time
    url2 = 'http://yuyue.seu.edu.cn:80/eduplus/control/validateimage'#获取验证码
    r2 = session.get(url2)
    tempIm = BytesIO(r2.content)
    validcode = recognize_captcha(tempIm)#验证码识别
    Data2 = {
        'ids': ids,
        'useTime': useTime,
        'itemId': changguanID,
        'allowHalf': 2,
        'validateCode': validcode
    }
    #print(Data2)
    #预约需要通过两步，第一步判断预约请求是否合法，第二个链接用来发送添加预约记录的请求
    #也许可以不管第一步直接发送第二步的请求，但我没试过，且不建议删去第一步，
    url3 = 'http://yuyue.seu.edu.cn/eduplus/order/order/order/judgeUseUser.do?sclId=1'
    r3 = session.post(url3,data=Data2)
    print(r3.text)#错误会返回不同的信息，这里不统一写了，只看正确的判断
    if '{}' in r3.text:
        #print('审核预约请求成功')
        Data3 = {
            'orderVO.useTime': useTime,
            'orderVO.itemId': changguanID,
            'orderVO.useMode': 2,
            'useUserIds': ids,
            'orderVO.phone': phoneNum,
            'orderVO.remark': '',
            'validateCode': validcode
        }
        url4 = 'http://yuyue.seu.edu.cn/eduplus/order/order/order/insertOredr.do?sclId=1'
        r4 = session.post(url4,data=Data3)
        if 'success' in r4.text:
            print('成功预约')
            return 1
        else:
            print('预约失败1')
    else:
        print('预约失败2')
    return 0 


if __name__ == '__main__':
    #信息填写
    username = ''#一卡通
    password = ''#统一身份密码
    ids = 111111#常用联系人代号
    phoneNum = ''#手机号
    session = getsession(username,password)#获取登录后的会话
    changguanID = 10 #九龙湖 羽毛球10  兵乓球7  篮球8
    target_day_flag = ['2021-04-16']#格式'2021-04-16'  为空自动预约包含今天在内的下三天内
    target_time = ['18','19','20'] #如18:00-19:00 则填'18'即可 列表模式

    #pushplus的token 即令牌  用于将信息通过pushplus公众号发送到微信  没有不影响自动预约功能，但影响通知功能
    #pushplus的topic 即群组号  一对多推送才需要使用
    #pushplus注册链接   注：pushplus有两个公众号，同一家公司，但两个推送是不一致的，这里用的是以下的链接
    #http://pushplus.hxtrip.com/ 
    token = ''
    topic = ''


    changguan = '羽毛球' if changguanID == 10 else '兵乓球' if changguanID ==7 else '篮球' if changguanID ==8 else '未知'

    k = 0
    tmp2 = ['用于判断是否和上次不一致']
    if session:#session会话成功登录才通过
        while(1):
            k += 1
            today = datetime.date.today()
            day = [today,today + datetime.timedelta(days = 1),today + datetime.timedelta(days = 2)]
            if not target_day_flag:
                target_day = [str(i) for i in day]
            else:
                target_day = target_day_flag
            url = 'http://yuyue.seu.edu.cn/eduplus/order/order/getOrderInfo.do?sclId=1'
            content = ''
            flag = 0
            tmp1 = []
            for i in day:
                Data = {
                    'itemId': changguanID,
                    'dayInfo': i,
                    'pageNumber': '1'
                }
                # 获取该日期是否有可预约项
                r2 = session.post(url,data=Data)
                if '预约' not in r2.text:
                    print('Cookie已失效,即将更新Cookie')
                    session = getsession(username,password)#获取登录后的会话
                    break
                if 'state-icon icon-yes' in r2.text:
                    a =  re.findall('(?<=icon-yes"></i> <em class="time">\r\n\t\t\t\t\t)([\d]{1,2}):00-[\d]{1,2}:00 </em>\r\n\t\t\t\t\t<em class="time2">([\d]{1,2}) <span>/</span> \r\n\t\t\t\t\t([\d]{1,2})',r2.text)
                    if a:
                        content += str(i)+'<br>'
                        for j in a:
                            tmp1.extend(j[0]+':00-'+str(int(j[0])+1)+':00可预约，当前人数'+j[1]+'/'+j[2]+'<br>')
                            content += j[0]+':00-'+str(int(j[0])+1)+':00可预约，当前人数'+j[1]+'/'+j[2]+'<br>'
                            if j[0] in target_time and str(i) in target_day:
                                print('预约ing')
                                yuyue_flag = yuyue(session,j[0],str(i),changguanID,ids,phoneNum)
                                if yuyue_flag:
                                    tmpContent = str(i)+'<br>'+j[0]+':00-'+str(int(j[0])+1)+':00预约成功'
                                    print(tmpContent)
                                    requests.get('http://pushplus.hxtrip.com/send?token='+token+'&title='+changguan+'预约成功'+'&content='+str(i)+'<br>'+j[0]+':00-'+str(int(j[0])+1)+':00预约成功'+'&template=html&topic='+topic)
                        flag = 1
                #日期为周末 预约有第二页 懒得改了 直接复制过来了
                if 'all_pages" v2' in r2.text:
                    Data = {
                        'itemId': changguanID,
                        'dayInfo': i,
                        'pageNumber': '2'
                    }
                    r2 = requests.post(url,data=Data)
                    if 'state-icon icon-yes' in r2.text:
                        a =  re.findall('(?<=icon-yes"></i> <em class="time">\r\n\t\t\t\t\t)([\d]{1,2}):00-[\d]{1,2}:00 </em>\r\n\t\t\t\t\t<em class="time2">([\d]{1,2}) <span>/</span> \r\n\t\t\t\t\t([\d]{1,2})',r2.text)
                        if a:
                            if str(i) not in content:
                                content += str(i)+'<br>'
                            for j in a:
                                tmp1.extend(j[0]+':00-'+str(int(j[0])+1)+':00可预约，当前人数'+j[1]+'/'+j[2]+'<br>')
                                content += j[0]+':00-'+str(int(j[0])+1)+':00可预约，当前人数'+j[1]+'/'+j[2]+'<br>'
                                if j[0] in target_time and str(i) in target_day:
                                    print('预约ing')
                                    yuyue_flag = yuyue(session,j[0],str(i),changguanID,ids,phoneNum)
                                    if yuyue_flag:
                                        tmpContent = str(i)+'<br>'+j[0]+':00-'+str(int(j[0])+1)+':00预约成功'
                                        print(tmpContent)
                                        requests.get('http://pushplus.hxtrip.com/send?token='+token+'&title='+changguan+'预约成功'+'&content='+str(i)+'<br>'+j[0]+':00-'+str(int(j[0])+1)+':00预约成功'+'&template=html&topic='+topic)
                            flag = 1
            if flag and tmp1!=tmp2:#找到有可预约项，且和上一次发送时不一致，则重新发送
                tmp2 = tmp1[:]
                print(content)
                requests.get('http://pushplus.hxtrip.com/send?token='+token+'&title='+changguan+'场馆预约'+'&content='+content+'&template=html&topic='+topic)
                print('发送成功')
                time.sleep(60)
            else:
                print('第'+str(k)+'次，未找到可预约项或未发生变化')
            time.sleep(3)
    else:
        print('该修修登录部分了')
