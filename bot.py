#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
try:#python2
    import ConfigParser
    from fakeframe import Frame, Image, ImageTk
except ImportError:#python3
    import configparser
    from tkinter import *
    from PIL import Image
    from PIL import ImageTk
import sys
import json
import threading
from wxbot import *

#二维码
qrw=300
qrh=300

#消息列表
lsw=300
lsh=100

#发送消息控件
tlw=50
tew=50
mlw=50
mew=130
sdh=20

#按钮
btw=50

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.place()
        
    def setbot(self,bot):
        self.bot = bot
        self.master.iconbitmap('icon.ico')
        menubar = Menu(self.master)
        menu1 = Menu(menubar, tearoff=0)
        menu1.add_command(label='发送', command=self.bot.guisend)
        menu1.add_command(label='清屏', command=self.clearlist)
        menu1.add_command(label='退出', command=self.quit)
        menubar.add_cascade(label='操作',menu=menu1)
        menubar.add_command(label='关于', command=self.about)
        self.master['menu']=menubar
        self.createWidgets()
    
    def createWidgets(self):
        self.tolabel = Label(self.master, text='发送给')
        self.tolabel.place(x=0, y=qrh+sdh, width=tlw, height=sdh)
        
        self.tostr = StringVar()
        self.toentry = Entry(self.master, textvariable=self.tostr)
        self.toentry.place(x=tlw, y=qrh+sdh, width=tew, height=sdh)
        
        self.msglabel = Label(self.master, text='内容：')
        self.msglabel.place(x=tlw+tew, y=qrh+sdh, width=mlw, height=sdh)
        
        self.msgstr = StringVar()
        self.msgentry = Entry(self.master, textvariable=self.msgstr)
        self.msgentry.place(x=tlw+tew+mlw, y=qrh+sdh, width=mew, height=sdh)
        
        #发送按钮放在另一边
        self.btsend = Button(self.master, text='发送', command=self.bot.guisend)
        self.btsend.place(x=btw,y=qrh+sdh*2.5, width=btw, height=sdh*1.5 ) 
        self.btsend = Button(self.master, text='清屏', command=self.clearlist)
        self.btsend.place(x=qrw/2-btw/2,y=qrh+sdh*2.5, width=btw, height=sdh*1.5 ) 
        self.btsend = Button(self.master, text='退出', command=self.quit)
        self.btsend.place(x=(qrw/2-btw)*2,y=qrh+sdh*2.5, width=btw, height=sdh*1.5 ) 
        
        self.loglist = Listbox(self.master,selectmode = BROWSE, bg='#000000', fg='#00ff00')
        self.loglist.place(x=0,y=qrh, width=lsw, height=lsh ) 
        
        #self.scrolly=Scrollbar(self.master)
        #self.scrolly.place(x=lsw, y=qrh, width=(qrw-lsw), height=lsh)
        #self.scrolly.config(command=self.loglist.yview)
        #self.scrolly.set(0,0.5)
        
    def clearlist(self):
        self.loglist.delete(0, END)
        
    def about(self):
        self.bot.outputlog('======================================')
        self.bot.outputlog('开发者：一石流Haber')
        self.bot.outputlog('联系方式：xdx3000(微信)')
        self.bot.outputlog('未经授权，严禁商用，个人研究请随意使用')
        self.bot.outputlog('======================================')
        for i in range(1,6):
            self.loglist.itemconfig(self.loglist.size()-i,fg="#00ffff")  

class TulingWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = ""
        self.robot_switch = True

        try:
            if(sys.version_info[0]==3):
                cf = configparser.ConfigParser()
            else:
                cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        #print('tuling_key:'+ self.tuling_key)

    def tuling_auto_reply(self, uid, msg):
        if self.tuling_key:
            url = "http://www.tuling123.com/openapi/api"
            user_id = uid.replace('@', '')[:30]
            body = {'key': self.tuling_key, 'info': msg.encode('utf8'), 'userid': user_id}
            r = requests.post(url, data=body)
            respond = json.loads(r.text)
            result = ''
            if respond['code'] == 100000:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')
            elif respond['code'] == 200000:
                result = respond['url']
            elif respond['code'] == 302000:
                for k in respond['list']:
                    result = result + u"【" + k['source'] + u"】 " +\
                        k['article'] + "\t" + k['detailurl'] + "\n"
            else:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')

            self.outputlog('    [AI回复]:')
            self.outputlog(result)
            return result
        else:
            return u"知道啦"

    def auto_switch(self, msg):
        msg_data = msg['content']['data']
        stop_cmd = [u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开']
        start_cmd = [u'出来', u'启动', u'工作']
        if self.robot_switch:
            for i in stop_cmd:
                if i == msg_data:
                    self.robot_switch = False
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已关闭！', msg['to_user_id'])
        else:
            for i in start_cmd:
                if i == msg_data:
                    self.robot_switch = True
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已开启！', msg['to_user_id'])

    def handle_msg_all(self, msg):
        if not self.robot_switch and msg['msg_type_id'] != 1:
            return
        if msg['msg_type_id'] == 1 and msg['content']['type'] == 0:  # reply to self
            self.auto_switch(msg)
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 0:  # text message from contact or 地址
            self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])
            #self.app.master.title(msg['user']['id'])
            #随机回复妹子图片
            if random.randint(1, 2) == 0:
                url = 'http://cct.name/meizi/meizixcx.php'
                try:
                    r = self.session.get(url)
                    data = r.content
                    fn = 'img_' + msg['user']['id'] + '.jpg'
                    with open(os.path.join(self.temp_pwd,fn), 'wb') as f:
                        f.write(data)
                    self.send_img_msg_by_uid(os.path.join(self.temp_pwd,fn), msg['user']['id']);
                except Exception as e:
                    self.outputlog(u'图片下载错误')
        elif msg['msg_type_id'] == 3 and msg['content']['type'] == 0:  # group text message
            if 'detail' in msg['content']:
                my_names = self.get_group_member_name(msg['user']['id'], self.my_account['UserName'])
                if my_names is None:
                    my_names = {}
                if 'NickName' in self.my_account and self.my_account['NickName']:
                    my_names['nickname2'] = self.my_account['NickName']
                if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                    my_names['remark_name2'] = self.my_account['RemarkName']

                is_at_me = False
                for detail in msg['content']['detail']:
                    if detail['type'] == 'at':
                        for k in my_names:
                            if my_names[k] and my_names[k] == detail['value']:
                                is_at_me = True
                                break
                if is_at_me:
                    src_name = msg['content']['user']['name']
                    reply = 'to ' + src_name + ': '
                    if msg['content']['type'] == 0:  # text message
                        reply += self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                    else:
                        reply += u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                    self.send_msg_by_uid(reply, msg['user']['id'])
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 3:  # 图
            self.send_msg_by_uid('嗯……一张图。图里是啥，告诉我嘛，我还看不懂呢', msg['user']['id'])
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 4:  # 语音
            self.send_msg_by_uid('哎呀我听不懂语音啦，打字好不好嘛', msg['user']['id'])
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 5:  # 名片
            self.send_msg_by_uid('这个人是谁啊~我要认识ta吗？', msg['user']['id'])
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 6:  # 表情
            self.send_msg_by_uid('你这个表情包大王', msg['user']['id'])
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 7:  # 链接
            self.send_msg_by_uid('嗯~一个链接。好好阅读一下', msg['user']['id'])
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 12:  # 红包
            self.send_msg_by_uid('哇~红包！谢谢土豪~', msg['user']['id'])
        elif msg['content']['type'] == 11:  # 登录？
            pass
        elif msg['content']['type'] == 99:  # 未知？
            pass
        else:
            self.outputlog('收到未知消息，类型：' + str(msg['content']['type']))
    
    def gen_qr_code(self, qr_file_path):
        if(sys.version_info[0]==3):
            string = 'https://login.weixin.qq.com/l/' + self.uuid
            qr = pyqrcode.create(string)
            qr.png(qr_file_path, scale=8)
            self.loadqrcode(qr_file_path)
        else:
            #self.conf = {'qr': 'tty'}
            WXBot.gen_qr_code(self, qr_file_path)
        
    def loadqrcode(self,url):
        if(sys.version_info[0]==3):
            load = Image.open(url)
            w, h = load.size
            load_resized = self.resize(w, h, qrw, qrh, load)
            render= ImageTk.PhotoImage(load_resized)    
            self.img = Label(self.app.master,image=render, width=qrw, height=qrh)  
            self.img.image = render  
            self.img.place(x=0,y=0) 
        
    def resize(self, w, h, w_box, h_box, pil_image):  
        if(sys.version_info[0]==3):
            f1 = 1.0*w_box/w # 1.0 forces float division in Python2  
            f2 = 1.0*h_box/h  
            factor = min([f1, f2])  
            #self.outputlog(f1, f2, factor) # test  
            # use best down-sizing filter  
            width = int(w*factor)  
            height = int(h*factor)  
            return pil_image.resize((width, height), Image.ANTIALIAS) 
    
    def guiwindow(self):
        if(sys.version_info[0]==3):
            self.app = Application()
            self.app.setbot(self)
            self.app.master.title('微信自动回复机器人 By Xdx3000')
            self.app.master.geometry(str(qrw)+'x'+str(qrh+lsh+20))#+500+200')        
            self.app.mainloop()
            os._exit(0)

    def guisend(self):
        if(sys.version_info[0]==3):
            to = self.app.tostr.get()
            msg= self.app.msgstr.get()
            self.outputlog('向 ['+to+'] 发送消息：'+msg)
            self.send_msg(to,msg)
            self.app.msgstr.set('')
        
    def run(self):
        if(sys.version_info[0]==3):
            windowProcess = threading.Thread(target=self.guiwindow)
            windowProcess.start()
        WXBot.run(self)

    def outputlog(self,str):
        if(sys.version_info[0]==3):
            self.app.loglist.insert(END,str)
            self.app.loglist.see(END)
        else:
            print(str)

    def proc_msg(self):
        if(sys.version_info[0]==3):
            self.img.place_forget()
            self.app.loglist.place(y=0, height=qrh)#+lsh
        WXBot.proc_msg(self)

def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'
    
    bot.run()

if __name__ == '__main__':
    main()

