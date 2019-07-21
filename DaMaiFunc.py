from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import json

import  os
from tkinter import *

class DaMaiFunc(object):
    # 构造请求头等
    def __init__(self):
        pass

    def OpenBrowser(self, port):
        cmd1 = r"cd C:\Program Files (x86)\Google\Chrome\Application"
        cmd2 = r"chrome.exe --remote-debugging-port=" + str(port) + " --user-data-dir=\"C:\selenum\AutomationProfile_" + str(port) + "\""
        try:
            os.popen(cmd1)
            os.popen(cmd2)
        except:
            pass

        # txt = {}
        # txt["port"] = port
        # with open(r'C:\selenum\'' + port + '.txt', 'w') as f:  # /会被转义，加r
        #     jsonTxt = json.dumps(txt)
        #     f.write(jsonTxt)

    def OpenTicketPage(self, port, url=None):
        browser = self.GetBrowser(port)
        browser.get(url)

    def GetBrowser(self, port):
        options = ChromeOptions()
        # options.add_experimental_option("debuggerAddress", "127.0.0.1:21635")
        options.add_argument('--log-level=3')
        options.add_experimental_option("debuggerAddress", "127.0.0.1:"+ str(port))
        browser = webdriver.Chrome(chrome_options=options)

        return browser

    # 先买价高的，价高的没了，就买价格次高的。以此类推
    def BuyFromHighToLow(self, ticketList):
        priceIndex = None  # 价格的索引
        dateIndex = None  # 场次的索引
        for i in range(len(ticketList["performBases"]), 0, -1):
            tmp = ticketList["performBases"][i]["performs"][0]["skuList"]
            for j in range(0, len(tmp)):
                if tmp[j]['skuEnable'] is True:
                    priceIndex = j
                    dateIndex = i
                    break

            if priceIndex is not None and dateIndex is not None:
                info = {
                    "priceIndex": priceIndex,
                    "dateIndex": dateIndex
                }
                return info

    # 先买价低的
    def BuyFromLowToHigh(self, ticketList):
        priceIndex = None   #价格的索引
        dateIndex = None # 场次的索引
        for i in range(0, len(ticketList["performBases"])):
            tmp = ticketList["performBases"][i]["performs"][0]["skuList"]
            for j in range(0, len(tmp)):
                if tmp[j]['skuEnable'] is True:
                    priceIndex = j
                    dateIndex = i
                    break

            if priceIndex is not None and dateIndex is not None:
                info = {
                    "priceIndex": priceIndex,
                    "dateIndex": dateIndex
                }
                return info

    def FindEnableTicketByPrice(self, performBases, price=None):
        rtDic = None
        if price:
            priceIndex = None  # 价格的索引
            dateIndex = None  # 场次的索引
            for i in range(0, len(performBases)):
                tmp = performBases[i]["performs"][0]["skuList"]
                for j in range(0, len(tmp)):
                    if price == tmp[j]['price'] and tmp[j]['skuEnable'] is True:
                        print("OK")
                        priceIndex = j
                        dateIndex = i
                        break

                if priceIndex is not None and dateIndex is not None:
                    rtDic = {
                        "priceIndex": priceIndex,
                        "dateIndex": dateIndex
                    }
                    return rtDic
        else:
            return rtDic


    def Buy(self, count, func, browser, ticketUrl, price=None):
        while True:
            code = self.Choose(browser, count, func, ticketUrl, price)
            if code == 0:
                print("返回码0.进入确认页面")
                break
            elif code == 1:
                print("返回码1.需要刷新页面！继续抢票……")
                # 刷新页面
                browser.refresh()
                continue
            elif code == 2:
                print("返回码2.所选价位已经无票。重新按照选择策略开始抢票……")
                price = None  # 价格置为空
                browser.refresh()
                continue

        # 确认订单，快递人等
        code = self.ConfirmOrder(browser, count)
        if code == 0:
            print("抢票成功！")
            return 0
        elif code == 1:
            print("下单失败！")
            self.Buy(count, func, browser, ticketUrl, price)


    def Choose(self, browser, count, func, ticketUrl, price):
        # 3种返回码
        # 0、已经下单到确认订单页面   1、选择的票没有了或者没开售，要刷新页面   2、全部都没有票了
        # func 抢票策略
        if browser.current_url is not ticketUrl:
            browser.get(ticketUrl)

        try:
            wait = WebDriverWait(browser, 1)
            dataDiv = wait.until(EC.presence_of_element_located((By.ID, "dataDefault")))  # 这里要2层括号，不然报错
        except:
            print("等待加载第一个页面超时！")
            return 1

        # 如果购买的btn的内容不对，说明还没开售。刷新页面
        allTicket = self.GetAllTicketInfo(browser)  # json数据
        if allTicket["buyBtnText"] == "还没开始":
            print("还没开始")
            return 1
        elif allTicket["buyBtnText"] == "选座购买":
            print("需要手动选座")
        elif allTicket["buyBtnText"] == "缺货登记":
            print("缺货登记")
            return 1
        elif allTicket["buyBtnText"] == "即将开售":
            print("即将开售！刷新页面！")
            return 1
        elif allTicket["buyBtnText"] == "立即预订":
            print("开始抢票！")
        else:
            print("未知情况")
            return 1
        # 有指定的价位，先购买指定的价位。如果指定的价位无票，则按照默认策略购买。
        # 如果还是无票，则重新刷新页面，将价格置为空，下次选票直接按照默认策略买
        if price:
            info = self.FindEnableTicketByPrice(allTicket['performBases'], int(price))
            if info is None:
                print('所选价位无票。尝试按照选择购票策略自动购买！')
                info = func(allTicket)

            if info is None:
                return 2
        else:
            info = func(allTicket)

        #如果场次和价格索引还是为空，那么就是没有票了，抢票失败，只有捡漏了。
        if info is None:
            return 1

        actions = ActionChains(browser)
        #选择场次
        dates = browser.find_elements_by_xpath("//div[@class='perform__order__select perform__order__select__performs']\
                                    /div[@class='select_right']/div[@class='select_right_list']\
                                    /div[contains(@class,'select_right_list_item')]")
        actions.click(dates[info['dateIndex']])

        # 选择价格
        tickets = browser.find_elements_by_class_name('skuname')  # 页面元素
        actions.click(tickets[info['priceIndex']])

        # 选择数量
        input = browser.find_element_by_xpath("//a[@class='cafe-c-input-number-handler cafe-c-input-number-handler-up']")
        for i in range(0, int(count) - 1):
            actions.click(input)

        #点击购买
        buybtn = browser.find_element_by_class_name('buybtn')
        actions.click(buybtn).perform()
        try:
            wait = WebDriverWait(browser, 1.2)
            isSuccess = wait.until(EC.title_is("确认订单"))
            if isSuccess:
                return 0
            else:
                return 1
        except:
            return 1


    #确认订单
    def ConfirmOrder(self, browser, count):
        try:
            wait = WebDriverWait(browser, 2)
            #等到确认订单的按钮加载出来后
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='submit-wrapper']/button")))  #这里要2层括号，不然报错
        except:
            #等待超时
            return 1

        # 选择观影人
        js1 = '''var list = document.getElementsByClassName("next-checkbox-label");
                if(list.length > 0){
                    for (var i=0;i<''' + str(count) + ''';i++)
                        { 
                            list[i].click();
                        }
                    document.getElementsByTagName("button")[2].click();
                }
                else{
                    document.getElementsByTagName("button")[1].click();
                }

                        '''
        # 点击确认
        browser.execute_script(js1)

        try:
            wait = WebDriverWait(browser, 2)
            isSuccess = wait.until(EC.title_contains("支付宝"))
            if isSuccess:
                return 0
            else:
                return 1
        except:
            return 1


    def GetAllTicketInfo(self, browser):
        allTicketInfo = browser.find_element_by_id('dataDefault')
        # 直接获取不到text,因为被隐藏了。需要使用下面的方法
        txt = allTicketInfo.get_attribute('textContent')
        allTicket = json.loads(txt)
        return allTicket

    def test(self):
        performBases = self.OpenJsonTxt()
        dic = self.FindEnableTicketByPrice(performBases['performBases'], 1980)
        print(dic)
        print(dic['dateIndex'])
        print(dic['priceIndex'])

    def OpenJsonTxt(self):
        configFile = './json.txt'
        with open(configFile, 'r', encoding='utf-8') as f:
            config = f.read()
            performBases = json.loads(config)
            print(performBases)
            return performBases


if __name__ == '__main__':
    DaMaiFunc = DaMaiFunc()
    # DaMaiFunc.OpenBrowser()
    # DaMaiFunc.OpenTicketPage()
    # DaMaiFunc.Choose(1280)
    DaMaiFunc.test()
