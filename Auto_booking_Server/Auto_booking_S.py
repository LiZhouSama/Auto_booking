import threading
import requests
import re
import time
import datetime
import inspect
import ctypes
from flask import Flask, request,redirect,url_for
import ddddocr
# import settings
#用来无视访问https链接时出现的SSL证书认证
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#execjs  安装方式 pip install PyExecJS
import execjs
# 用于验证码处理库
import re
# path = r"C:/Users/magic book/Desktop/code/SEU/Auto_booking_S"
path = r"/root/code/Auto_Booking_S"
ocr = ddddocr.DdddOcr()
class S_yuyue:
    user = ""  #统一身份
    password = ""
    ids = ""  #受邀人id号
    phoneNum = ""  #手机号
    target_time = ""  #目标预约时间
    target_day_flag = ""  #目标预约日期 为空自动预约下三天
    post_time = ""  #有所需要的时间则发送预约提示
    token = ""  #pushplus
    topic = ""  #pushplus
    changguanID = ""  #场馆号
    flag = 0
    th = ""
    def __init__(self,user,password,ids,phoneNum,target_time,target_day_flag,post_time,token,topic,changguanID,flag=0):
        self.user = user
        self.password = password
        self.phoneNum = phoneNum
        self.target_time = target_time 
        self.target_day_flag = target_day_flag
        self.post_time = post_time
        self.token = token
        self.topic = topic
        self.changguanID = changguanID
        self.flag = flag
        if len(ids)==9:
            s = getsession(self.user,self.password)
            self.ids = re.findall(r'"userId":(.*?),',s.post('http://yuyue.seu.edu.cn/eduplus/order/order/searchUser.do?sclId=1',{'cardNo':ids}).text)[0]
            # print(self.ids)
        else:
            self.ids = ids
        if int(flag) == 1:
            print(self.user,"开始预约")
            self.th=threading.Thread(target=start_booking,args=(self,self.user,self.password,self.ids,self.phoneNum,self.changguanID,self.target_day_flag,self.target_time,self.token,self.topic,self.post_time))
            self.th.start()
    def fun(self):
        if self.flag == 1:
            print(self.th,"停止")
            self.stop()
            self.flag = 0
            return f"{self.user}当前已停止"
        else:
            self.stop()
            self.th=threading.Thread(target=start_booking,args=(self,self.user,self.password,self.ids,self.phoneNum,self.changguanID,self.target_day_flag,self.target_time,self.token,self.topic,self.post_time))
            self.th.start()
            self.flag = 1
            return f"{self.user}当前已启动"
    def fun2(self):
        def tmp_reply():
            tmpstr = ''
            tmpsess = getsession(self.user,self.password,k=0)
            tmpstr += reply(tmpsess,self.user)
            print('读取'+self.user+'预约信息完成\n')
            requests.get('http://pushplus.hxtrip.com/send?token='+self.token+'&title=总预约信息'+'&content='+tmpstr+'&template=html&topic='+self.opic)
            print(tmpstr.replace('<br>','\n'))
            print('发送'+self.user+'预约信息完成\n')
        self.th=threading.Thread(target=tmp_reply)
        self.th.start()
    def show(self):
        return str(("user:",self.user,"password:",self.password,
        "ids:",self.ids,"phoneNum:",self.phoneNum,"target_time:",self.target_time,
        "target_day_flag:",self.target_day_flag,"post_time:",self.post_time,
        "token:",self.token,"topic:",self.topic,"changguanID:",self.changguanID,"flag:",self.flag)).replace(" ","")
    def show2(self):
        return str((self.user,self.password,
        self.ids,self.phoneNum,self.target_time,
        self.target_day_flag,self.post_time,
        self.token,self.topic,self.changguanID,int(self.flag))).replace(" ","")
    def show3(self):
        return str(("user:",self.user,
        "ids:",self.ids,"phoneNum:",self.phoneNum,"target_time:",self.target_time,
        "target_day_flag:",self.target_day_flag,"post_time:",self.post_time,
        "token:",self.token,"topic:",self.topic,"changguanID:",self.changguanID,"flag:",self.flag)).replace(" ","")
    def stop(self):
        try:
            if not type(self.th)==str:
                if self.th.isAlive():
                    stop_thread(self.th)
        finally:
            pass

def getsession(username,password,k=0):
    #用来获得一个成功登陆的会话 之后将用这个会话获取预约信息 并登录
    #登录接口
    url2 = 'https://newids.seu.edu.cn/authserver/login?service=http%3A%2F%2Fyuyue.seu.edu.cn%2Feduplus%2Forder%2FinitOrderIndex.do%3FsclId%3D1'
    session = requests.session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Mobile Safari/537.36',
        'referer': 'http://yuyue.seu.edu.cn/eduplus/order/initOrderIndex.do;',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br'
    }
    session.headers.update(headers)
    r2 = session.get(url2)
    key = re.findall('pwdDefaultEncryptSalt = "(.*)"',r2.text)[0]
    #exe和It对应发送post请求包里带的信息，没懂具体啥意思，应该是每次验证的标识符了。
    exe = re.findall('name="execution" value="(.*)"',r2.text)[0]
    lt = re.findall('name="lt" value="(.*)"',r2.text)[0]
    f = open(path+"/encrypt.js", 'r', encoding='UTF-8')
    line = f.readline()
    js = ''
    while line:
        js += line
        line = f.readline()
    ctx = execjs.compile(js)  #通过执行js文件获得加密后的密码
    password = ctx.call('_ep', password, key)
    #print(password)
    Data = {
        'username': username,
        'password': password,
        'lt': lt,
        'dllt': 'userNamePasswordLogin',
        'execution': exe,
        '_eventId': 'submit',
        'rmShown': '1'
    }
    # print('='*100,'\n',Data,'\n',"="*100)
    #这里用页面存在'团体预约'四字判断是否登录成功，
    rr2 = session.post(url2,data=Data).text
    # print(rr2)
    if '团体预约' in rr2:
        print('成功登录')
        return session
    elif k<9:#没成功我就继续再来几次套x娃
        print('登录失败，重试ing')
        k+=1
        session = getsession(username,password,k)
        return session
    else:
        print('登录失败，放弃了')
        return 0 

def yuyue(session,start_time,day,changguanID,ids,phoneNum):
    #发起预约
    start_time = start_time+':00-'+str(int(start_time)+1)+':00'
    useTime = day+" "+start_time
    url2 = 'http://yuyue.seu.edu.cn:80/eduplus/control/validateimage'#获取验证码
    r2 = session.get(url2)
    validcode = ocr.classification(r2.content)
    # validcode = recognize_captcha(tempIm)#验证码识别
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

def reply(session,username):
    r2 = session.get('http://yuyue.seu.edu.cn/eduplus/order/fetchMyOrders.do?sclId=1')
    print(r2.text)
    str11 = re.findall(u'([\u2E80-\u9FFF]{1,2}球).*?"item-usetime">(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} 到 \d{2}:\d{2}:\d{2})</td>.*?<td class="item-state"><span class="appo-state-(\d)',r2.text,re.S)
    str1 = username+'<br>'
    flag = 0
    if str11:
        for i in str11:
            if i[2]=='2':
                str1 += i[0]
                str1 += i[1]
                str1 += '<br>'
                flag = 1
    if flag:
        return(str1)
    else:
        return str1+'无预约<br>'

def start_booking(SS,username,password,ids,phoneNum,changguanID,target_day_flag,target_time,token,topic,post_time):
    session = getsession(username,password)#获取登录后的会话
    changguan = '羽毛球' if changguanID == '10' else '兵乓球' if changguanID =='7' else '篮球' if changguanID =='8' else '未知'
    print(username+"预约"+changguan+"时间"+"".join(target_time)+"已启动\n")
    k = 0
    tmp2 = ['用于判断是否和上次不一致']
    if session:#session会话成功登录才通过
        while(SS.flag):
            try:
                if time.strftime("%M", time.localtime()) == '10' and (time.strftime("%H", time.localtime())in['18','10']):
                    yuyue_xinxi = reply(session,username)
                    requests.get('http://pushplus.hxtrip.com/send?token='+token+'&title='+username+'预约信息'+'&content='+yuyue_xinxi+'&template=html&topic='+topic)
                    time.sleep(60)
                    continue
                if k>=5000:
                    session = getsession(username,password)
                    print('重建会话\n')
                    k = 0
                    continue
                k += 1
                today = datetime.date.today()
                day = [today,today + datetime.timedelta(days = 1),today + datetime.timedelta(days = 2)]
                if not target_day_flag:
                    target_day = [str(i) for i in day]
                else:
                    target_day = target_day_flag
                content = ''
                flag = 0
                tmp1 = []
                for i in day:
                    url = 'http://yuyue.seu.edu.cn/eduplus/order/order/getOrderInfo.do?sclId=1&itemId='+str(changguanID)+'&dayInfo='+str(i)+'&pageNumber=1'
                    # 获取该日期是否有可预约项
                    r2 = session.get(url)
                    # print(r2.text)
                    if '预约' not in r2.text:
                        # print(r2.text)
                        print('Cookie已失效,即将更新Cookie\n')
                        session = getsession(username,password)#获取登录后的会话
                        break
                    if 'state-icon icon-yes' in r2.text:
                        a =  re.findall('(?<=icon-yes"></i> <em class="time">\r\n\t\t\t\t\t)([\d]{1,2}):00-[\d]{1,2}:00 </em>\r\n\t\t\t\t\t<em class="time2">([\d]{1,2}) <span>/</span> \r\n\t\t\t\t\t([\d]{1,2})',r2.text)
                        print(a)
                        if a:
                            for j in a:
                                if j[0] in post_time or not post_time:
                                    if str(i) not in content:
                                        content += str(i)+'<br>'
                                    tmp1.extend(j[0]+':00-'+str(int(j[0])+1)+':00可预约，当前人数'+j[1]+'/'+j[2]+'<br>')
                                    content += j[0]+':00-'+str(int(j[0])+1)+':00可预约，当前人数'+j[1]+'/'+j[2]+'<br>'
                                    flag = 1
                                if j[0] in target_time and str(i) in target_day:
                                    print('预约ing\n')
                                    yuyue_flag = yuyue(session,j[0],str(i),changguanID,ids,phoneNum)
                                    if yuyue_flag:
                                        tmpContent = str(i)+'<br>'+j[0]+':00-'+str(int(j[0])+1)+':00预约成功'
                                        print(tmpContent)
                                        requests.get('http://pushplus.hxtrip.com/send?token='+token+'&title='+username+changguan+'预约成功'+'&content='+str(i)+'<br>'+j[0]+':00-'+str(int(j[0])+1)+':00预约成功'+'&template=html&topic='+topic)
                    #日期为周末 预约有第二页 懒得改了 直接复制过来了
                    # if i.weekday() in [5,6]:
                    if 1:
                        #print('第二页\n')
                        url = 'http://yuyue.seu.edu.cn/eduplus/order/order/getOrderInfo.do?sclId=1&itemId='+str(changguanID)+'&dayInfo='+str(i)+'&pageNumber=2'
                        # 获取该日期是否有可预约项
                        r2 = session.get(url)
                        if 'state-icon icon-yes' in r2.text:
                            a =  re.findall('(?<=icon-yes"></i> <em class="time">\r\n\t\t\t\t\t)([\d]{1,2}):00-[\d]{1,2}:00 </em>\r\n\t\t\t\t\t<em class="time2">([\d]{1,2}) <span>/</span> \r\n\t\t\t\t\t([\d]{1,2})',r2.text)
                            print(a)
                            if a:
                                for j in a:
                                    if j[0] in post_time or not post_time:
                                        if str(i) not in content:
                                            content += str(i)+'<br>'
                                        tmp1.extend(j[0]+':00-'+str(int(j[0])+1)+':00可预约，当前人数'+j[1]+'/'+j[2]+'<br>')
                                        content += j[0]+':00-'+str(int(j[0])+1)+':00可预约，当前人数'+j[1]+'/'+j[2]+'<br>'
                                        flag = 1
                                    if j[0] in target_time and str(i) in target_day:
                                        print('预约ing\n')
                                        yuyue_flag = yuyue(session,j[0],str(i),changguanID,ids,phoneNum)
                                        if yuyue_flag:
                                            tmpContent = str(i)+'<br>'+j[0]+':00-'+str(int(j[0])+1)+':00预约成功'
                                            print(tmpContent)
                                            requests.get('http://pushplus.hxtrip.com/send?token='+token+'&title='+username+changguan+'预约成功'+'&content='+str(i)+'<br>'+j[0]+':00-'+str(int(j[0])+1)+':00预约成功'+'&template=html&topic='+topic)
                if flag and tmp1!=tmp2:#找到有可预约项，且和上一次发送时不一致，则重新发送
                    tmp2 = tmp1[:]
                    print(content)
                    requests.get('http://pushplus.hxtrip.com/send?token='+token+'&title='+changguan+'场馆预约'+'&content='+content+'&template=html&topic='+topic)
                    print('发送成功\n')
                    time.sleep(30)
                else:
                    print(username+'第'+str(k)+'次，未找到可预约项或未发生变化\n')
                time.sleep(3)
            except:
                print(username+'停止了\n')
                continue
    else:
        print('该修修登录部分了\n')

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident,SystemExit)


try:
    with open(path+"/test.ini", "r+", ) as f:  # 打开文件
        data = f.read()  # 读取文件
    tmp = re.findall(r"\('(.*?)','(.*?)','(.*?)','(.*?)','(.*?)','(.*?)','(.*?)','(.*?)','(.*?)','(.*?)',(.*?)\)",data)
finally:
    S_yuyue_list = []
print("读取数据")
print(tmp)
# print(tmp[0][2])
if tmp:
    for i in tmp:
        tmp2 = S_yuyue(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10])
        S_yuyue_list.append(tmp2)
print('读取数据完成')
for i in S_yuyue_list:
    print(i.show())

app = Flask(__name__,template_folder=path+'/')

@app.route("/")
def index():
    with open(path+"/index.html",encoding="UTF8") as f:
        data = f.read()
    return data

@app.route("/", methods=['POST'])
def index2():
    for i in S_yuyue_list:
        if i.user == request.form.get("user") :
            if i.password == request.form.get("password"):
                with open(path+"/index.html",encoding="UTF8") as f:
                    data = f.read()
                data = re.sub('"user" value=""',f'"user" value="{i.user}"',data) 
                data = re.sub('"password" value=""',f'"password" value="{i.password}"',data)
                data = re.sub('"ids" value=""',f'"ids" value="{i.ids}"',data)
                data = re.sub('"phoneNum" value=""',f'"phoneNum" value="{i.phoneNum}"',data)
                data = re.sub('"target_day_flag" value=""',f'"target_day_flag" value="{i.target_day_flag}"',data)
                data = re.sub('"target_time" value="19,20"',f'"target_time" value="{i.target_time}"',data)
                data = re.sub('"post_time" value="22"',f'"post_time" value="{i.post_time}"',data)
                data = re.sub('"token" value=""',f'"token" value="{i.token}"',data)
                data = re.sub('"topic" value=""',f'"topic" value="{i.topic}"',data)
                data = re.sub('"changguanID" value="10"',f'"changguanID" value="{i.changguanID}"',data)
                data = re.sub('"flag" value="0"',f'"flag" value="{i.flag}"',data)
                return data
            else:
                return "密码错误"
    with open(path+"/index.html",encoding="UTF8") as f:
        data = f.read()
    return data

@app.route('/change_S', methods=['GET', 'POST'])
def change_S():
    for i in S_yuyue_list:
        if i.user == request.form.get("user") :
            if i.password == request.form.get("password"):
                str1 = i.fun()
                with open(path+"/test.ini","w+") as f:
                    for k in S_yuyue_list:
                        f.write(k.show2())
                return str1
            else:
                return "密码错误"

@app.route('/delete_S', methods=['GET', 'POST'])
def delete_S():
    for j,i in enumerate(S_yuyue_list):
        if i.user == request.form.get("user") :
            if i.password == request.form.get("password"):
                if i.flag == 1:
                    i.fun()
                tmp = i.user
                S_yuyue_list.pop(j)
                del i 
                with open(path+"/test.ini","w+") as f:
                    for k in S_yuyue_list:
                        f.write(k.show2())
                return f"删除{tmp}设置"
            else:
                return "密码错误"
            
@app.route('/register', methods=['GET', 'POST'])
def register():
    global S_yuyue_list
    if request.method == 'POST':
        if not getsession(request.form.get("user"),request.form.get("password"))==0:
        # if 1:
            for i in S_yuyue_list:#查找是否存在相同账号
                if i.user == request.form.get("user"):
                    i.password = request.form.get("password")
                    i.phoneNum = request.form.get("phoneNum")
                    i.target_time = request.form.get("target_time")
                    i.target_day_flag = request.form.get("target_day_flag")
                    i.post_time = request.form.get("post_time")
                    i.token = request.form.get("token")
                    i.topic = request.form.get("topic")
                    i.changguanID = request.form.get("changguanID")
                    if len(request.form.get("ids"))==9:
                        s = getsession(i.user,i.password)
                        i.ids = re.findall(r'"userId":(.*?),',s.post('http://yuyue.seu.edu.cn/eduplus/order/order/searchUser.do?sclId=1',{'cardNo':request.form.get("ids")}).text)[0]
                        # print(self.ids)
                    else:
                        i.ids = request.form.get("ids")
                    if not i.flag == request.form.get("flag"):
                        i.fun()
                    with open(path+"/test.ini","w+") as f:
                        for k in S_yuyue_list:
                            f.write(k.show2())
                    return "已存在该账号信息，正在修改配置，修改后配置如下："+i.show()
            print(request.form.get("flag"))
            if request.form.get("flag")=="1":
                tmpflag = 1
            else:
                tmpflag = 0
            tmp = S_yuyue(request.form.get("user"),request.form.get("password"),request.form.get("ids"),request.form.get("phoneNum"),request.form.get("target_time"),request.form.get("target_day_flag"),request.form.get("post_time"),request.form.get("token"),request.form.get("topic"),request.form.get("changguanID"),tmpflag)
            S_yuyue_list.append(tmp)
            with open(path+"/test.ini","w+") as f:
                for k in S_yuyue_list:
                    f.write(k.show2())
                    print(k.show2())
            return "登录成功，信息如下:"+tmp.show()
        else:
            return "登录失败，检查账号密码，也有可能是SEU服务器没开"
    return redirect(url_for('index'))

@app.route('/show', methods=['GET', 'POST'])
def show3():
    str1 = ""
    for i in S_yuyue_list:
        str1 +=i.show3()
    return str1
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=9989)

