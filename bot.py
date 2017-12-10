#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import configparser
import json
from tkinter import *
import threading
from PIL import Image
from PIL import ImageTk

qrw=300
qrh=300
lsw=300
lsh=100

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        #self.iconbitmap('spider_128px_1169260_easyicon.net.ico')
    
    def createWidgets(self):
        #self.helloLabel = Label(self, text='Hello, world!')
        #self.helloLabel.pack()
        #self.quitButton = Button(self, text='Quit', command=self.quit)
        #self.quitButton.pack()
        self.loglist = Listbox(self.master,selectmode = BROWSE, bg='#000000', fg='#00ff00')
        self.loglist.place(x=0,y=qrh, width=lsw, height=lsh ) 
        #self.scrolly=Scrollbar(self.master)
        #self.scrolly.place(x=lsw, y=qrh, width=(qrw-lsw), height=lsh)
        #self.scrolly.config(command=self.loglist.yview)
        #self.scrolly.set(0,0.5)
        #relwidth=1

class TulingWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = ""
        self.robot_switch = True

        try:
            cf = configparser.ConfigParser()
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

            self.outputlog('    ROBOT:'+ result)
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
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 0:  # text message from contact
            self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])
            self.app.master.title(msg['user']['id'])
            #随机回复妹子图片
            if random.randint(1, 2) == 1:
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
            self.send_msg_by_uid('哇啦哇啦~你说了啥我听不懂~告诉我嘛', msg['user']['id'])
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 6:  # 表情
            self.send_msg_by_uid('嗯~？', msg['user']['id'])
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 7:  # 链接
            self.send_msg_by_uid('嗯~一个链接。好好阅读一下', msg['user']['id'])
    
    def gen_qr_code(self, qr_file_path):
        string = 'https://login.weixin.qq.com/l/' + self.uuid
        qr = pyqrcode.create(string)
        qr.png(qr_file_path, scale=8)
        self.loadqrcode(qr_file_path)
        
    def loadqrcode(self,url):
        load = Image.open(url)
        w, h = load.size
        load_resized = self.resize(w, h, qrw, qrh, load)
        render= ImageTk.PhotoImage(load_resized)    
        self.img = Label(self.app.master,image=render, width=qrw, height=qrh)  
        self.img.image = render  
        self.img.place(x=0,y=0) 
        
    def resize(self, w, h, w_box, h_box, pil_image):  
        f1 = 1.0*w_box/w # 1.0 forces float division in Python2  
        f2 = 1.0*h_box/h  
        factor = min([f1, f2])  
        #self.outputlog(f1, f2, factor) # test  
        # use best down-sizing filter  
        width = int(w*factor)  
        height = int(h*factor)  
        return pil_image.resize((width, height), Image.ANTIALIAS) 
    
    def guiwindow(self):
        self.app = Application()
        self.app.master.title('Xdx3000`s Weixin Bot')
        self.app.master.geometry(str(qrw)+'x'+str(qrh+lsh))#+500+200')        
        self.app.mainloop()
        os._exit(0)
    
    def run(self):
        windowProcess = threading.Thread(target=self.guiwindow)
        windowProcess.start()
        WXBot.run(self)

    def outputlog(self,str):
        self.app.loglist.insert(END,str)
        self.app.loglist.see(END)

    def proc_msg(self):
        self.img.place_forget()
        self.app.loglist.place(y=0, height=qrh+lsh)
        #self.app.scrolly.place(y=0, height=qrh+lsh)
        WXBot.proc_msg(self)

def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'
    
    bot.run()

if __name__ == '__main__':
    main()

