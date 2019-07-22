# import tkinter as tk
from tkinter import ttk
from tkinter import *
import random
import json
import os
import sys
from DaMaiFunc import DaMaiFunc
import threading

class tkFunc(object):
    def __init__(self):
        # 第1步，实例化object，建立窗口window
        self.window = Tk()

        # 第2步，给窗口的可视化起名字
        self.window.title('Wellcome to Hongwei Website')

        # 第3步，设定窗口的大小(长 * 宽)
        self.window.geometry('800x600')  # 这里的乘是小x

        # 实例化damai
        self.DaMai = DaMaiFunc()

        self.top = None

        self.browser = None

    def EditConfig(self):
        def ConfirmConfig():
            #将配置写入文件
            # 浏览器端口号，起点：startPort（20000以上）  终点：startPort+threadCount
            username = usernameTxT.get()
            startPort = startPortTxT.get()
            threadCount = threadTxT.get()
            config = {
                "username": username,
                "startPort": int(startPort),
                "threadCount": int(threadCount)
            }

            #删除之前有的配置文件
            CUR_PATH = os.path.abspath('.')
            for x in os.listdir(CUR_PATH):
                path_now = os.path.join(CUR_PATH, x)
                if os.path.isfile(path_now) and "config" in os.path.splitext(x)[0]:
                    # 删除查找到的文件
                    os.remove(path_now)

            #写入新的配置文件
            with open(r'config.txt', 'w') as f:
                jsonTxt = json.dumps(config)
                f.write(jsonTxt)

            # 账号、端口提示
            userTips = StringVar()
            portTips = StringVar()
            threadTips = StringVar()

            userTips.set(username)
            portTips.set(startPort)
            threadTips.set(threadCount)

            Label(self.window, text='账号:', bg='green').place(x=30, y=30)
            Entry(self.window, state="readonly", textvariable=userTips).place(x=100, y=30)
            Label(self.window, text='起始端口:', bg='green').place(x=30, y=60)
            Entry(self.window, state="readonly", textvariable=portTips).place(x=100, y=60)
            Label(self.window, text='线程数:', bg='green').place(x=300, y=30)
            Entry(self.window, state="readonly", textvariable=threadTips).place(x=350, y=30)

            # 然后销毁窗口。
            self.top.destroy()

        self.top = Toplevel()
        self.top.geometry('300x300')
        self.top.title('config window')

        usernameTxT = StringVar()  # 将输入的注册名赋值给变量
        l1 = Label(self.top, text='账号', bg='green')
        e1 = Entry(self.top, show=None, font=('Arial', 14), textvariable=usernameTxT)
        l1.place(x=30, y=30)
        e1.place(x=80, y=30)

        # 给定端口起点
        startPortTxT = StringVar()
        startPortTxT.set('20000起，每个客户端增加1000（删除这句话）')
        l2 = Label(self.top, text='起始端口', bg='green')
        e2 = Entry(self.top, show=None, textvariable=startPortTxT)
        l2.place(x=30, y=80)
        e2.place(x=80, y=80)

        # 线程数
        threadTxT = StringVar()
        l3 = Label(self.top, text='线程数', bg='green')
        e3 = Entry(self.top, show=None, font=('Arial', 14), textvariable=threadTxT)
        l3.place(x=30, y=130)
        e3.place(x=80, y=130)

        #确认的button
        btn_comfirm_sign_up = Button(self.top, text='确定', command=ConfirmConfig)
        btn_comfirm_sign_up.place(x=180, y=200)

    def CreateMenuBar(self):
        # 菜单栏
        menubar = Menu(self.window)
        filemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='菜单', menu=filemenu)
        filemenu.add_command(label='配置', command=self.EditConfig)
        self.window.config(menu=menubar)

    def ShowGuide(self):
        # 操作指引
        guideTxt = r'''
        1.点击【打开浏览器】  
        2.手动登录   
        3.输入抢票URL，点击【进入抢票页面】
        4.选择场次、价格、数量、价格策略   
        5.点击【抢票】
        '''
        guideTips = Text(self.window, height=7)
        guideTips.insert(END, guideTxt)
        guideTips.place(x=30, y=90, width=400)

    def GetConfigFile(self):
        configFile = None
        for root, dirs, files in os.walk("."):
            for file in files:
                if file == 'config.txt':
                    configFile = os.path.join(root, file)
                    break

            if configFile:
                break
        return configFile

    def ReadConfig(self):
        # 读取配置文件
        configFile = self.GetConfigFile()

        with open(configFile, 'r') as f:
            config = f.read()
            jsonTxt = json.loads(config)
        return jsonTxt

    def WriteConfig(self, key, value):
        # 写配置文件
        configFile = self.GetConfigFile()
        with open(configFile, 'r+') as f:
            config = f.read()
            jsonTxt = json.loads(config)
            jsonTxt[key] = value
            f.seek(0)
            f.truncate()
            f.write(json.dumps(jsonTxt))
            f.flush()

    def ShowBtns(self):
        # 按钮组
        def OpenBrowser():
            jsonTxt = self.ReadConfig()
            startPort = jsonTxt["startPort"]
            threadCount = jsonTxt["threadCount"]
            # 打开多个浏览器
            for i in range(0, threadCount):
                port = startPort + i
                self.DaMai.OpenBrowser(port)
                # t = threading.Thread(target=test, args=(port,))
                # t = threading.Thread(target=test)
                # t.start()
                # threads.append(t)

        def OpenTicketPage():
            jsonTxt = self.ReadConfig()
            startPort = jsonTxt["startPort"]
            threadCount = jsonTxt["threadCount"]

            # 打开抢票网页
            for i in range(0, threadCount):
                port = startPort + i
                browser = self.DaMai.GetBrowser(port)
                url = urlTxT.get()
                # 将抢票页面的URL写入配置文件
                self.WriteConfig("ticketUrl", url)

                browser.get(url)

        Button(self.window, text="打开浏览器", command=OpenBrowser).place(x=30, y=200)
        urlTxT = StringVar()
        Entry(self.window, show=None, font=('Arial', 10), textvariable=urlTxT, width=30).\
            place(x=150, y=200)
        Button(self.window, text="进入抢票页面", command=OpenTicketPage).place(x=400, y=200)

    def ChooseTicketInfo(self):
        threadList = []
        def Start():
            dic = {
                1: self.DaMai.BuyFromLowToHigh,
                2: self.DaMai.BuyFromHighToLow
            }

            jsonTxt = self.ReadConfig()
            startPort = jsonTxt["startPort"]
            threadCount = jsonTxt["threadCount"]
            ticketUrl = jsonTxt["ticketUrl"]

            countInfo = countTxT.get()
            priceInfo = priceTxT.get()
            if priceInfo == "":
                priceInfo = None
            strategyInfo = dic[var.get()]
            # 打开多个浏览器
            for i in range(0, threadCount):
                port = startPort + i
                browser = self.DaMai.GetBrowser(port)
                t = threading.Thread(target=self.DaMai.Buy, args=(countInfo, strategyInfo, browser, ticketUrl, priceInfo))
                t.start()

        # 数量
        Label(self.window, text='数量', bg='green').place(x=30, y=250)
        countTxT = StringVar()
        Entry(self.window, textvariable=countTxT, width=5).place(x=80, y=250)

        # 价格策略
        Label(self.window, text='抢票策略', bg='green').place(x=150, y=250)
        var = IntVar()
        Radiobutton(self.window, text='从低到高', variable=var, value=1).place(x=200, y=250)
        Radiobutton(self.window, text='从高到低', variable=var, value=2).place(x=200, y=270)

        # 票价
        Label(self.window, text='票价', bg='green').place(x=300, y=250)
        priceTxT = StringVar()
        Entry(self.window, textvariable=priceTxT, width=5).place(x=350, y=250)

        # 抢票按钮
        Button(self.window, text="开始抢票", command=Start, height=10, width=10).place(x=550, y=300)

if __name__ == '__main__':
    tk = tkFunc()
    tk.CreateMenuBar()
    # tk.ShowUsernameAndPort()
    tk.ShowGuide()
    tk.ShowBtns()

    tk.ChooseTicketInfo()

    tk.window.mainloop()