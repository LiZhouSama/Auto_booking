# Auto_booking
东南大学 体育场馆自动预约脚本

**本项目仅供学习使用**

东南大学统一身份认证自动登录，采用requests库进行统一认证登录建立session会话，基于tesseract自动填写验证码，发起场馆预约请求。

python版本3.7

注释大部分都写了，安装好库应该就能使用

## 未修复且不打算修复的不足

本项目仅对发起时间为整点如（18:00-19:00）的可预约场馆进行预约，未对类似12:30-13:30的场馆进行处理，主要是因为我懒得改正则表达式了

最开始用的tesseract做的验证码识别，后来发现ddddocr这个库更方便，但懒得改了XDDDD

# 信息填写
## username和password
(很明显)是账号密码
```
username #一卡通号
password #统一身份密码
```

## ids
指常用联系人，你邀请一起打球的人 填写其代号

代号获取方法：

1.登录并打开以下链接
```
http://yuyue.seu.edu.cn/eduplus/order/order/order/getContacts.do?sclId=1&flag=order
```

2.对着邀请人的那个方框右键点击“检查”或“审查元素”，总之就是按F12，找到那个框对应的代码信息（应该是一个以input开头的）

3.这一行代码中，应该具有value项，value='xxxxxx'其中的xxxxxx就是这里的代号


## phoneNum
你的手机号码，必填项

## changguanID
场馆代号 #九龙湖 羽毛球10  兵乓球7  篮球8

获得方法：

1.打开预约链接

```
http://yuyue.seu.edu.cn/eduplus/order/initOrderIndex.do?sclId=1#
```

2.对着准备预约的场馆的选项右键点击“检查”或“审查元素”，总之就是按F12，找到那个框对应的代码信息（应该也是一个以input开头的）

3.里面有一个changeInfo的信息

例changeInfo(null, '10', '羽毛球（九龙湖）')就是10

方法二

1.打开方法一网页后按F12，切换到网络（network），清除所有信息。

2.单击切换想要选的场馆，此时会多出一个getOrderInfo.do?sclId=1的东西（没跳出来的话可能是没点击显示全部（All））

3.移到最下面有个“表单数据”data，其中会有一个itemId，对应的数字即为场馆号

例itemId: 10 即为10

## target_day_flag和target_time

1.分别表示选择的日期和时间，

2.target_day_flag为空则表示不挑日期（自动预约包含今天在内的下三天内）

target_day_flag格式'2021-04-16'  为空自动预约包含今天在内的下三天内

target_time如18:00-19:00 则填'18'即可 列表模式

填写实例如下

```
target_day_flag = ['2021-04-16'] 
target_time = ['18','19','20'] 
```

## token和topic
基于pushplus公众号发送通知的，不填不影响自动预约的结果，但建议填上。

```
#pushplus的token 即令牌  用于将信息通过pushplus公众号发送到微信  没有不影响自动预约功能，但影响通知功能
#pushplus的topic 即群组号  一对多推送才需要使用
#pushplus注册链接   注：pushplus有两个公众号，同一家公司，但两个推送是不一致的，这里用的是以下的链接
#http://pushplus.hxtrip.com/ 
token = ''
topic = ''
```


# 写在最后

本脚本主要是写给真心想去场馆打球但始终难以抢到球馆的人的

故我在这希望各位同学**不要滥用此脚本**

所以虽然场馆预约后失约的惩罚并不大，但如若各位同学不需要使用已经成功预约到的场馆，请及时取消预约，**给其他有需要的同学留个地方运动**，谢谢配合！！

--made by **guoguoly**
