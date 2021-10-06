import threading
from queue import Queue
import requests
from bs4 import BeautifulSoup
import re
import time

CRAW_EXIT = False # 采集队列标识，如果为True, 表示队列为空，页码全部被采集

# 数据采集的线程类
class ThreadCrawl(threading.Thread):
    def __init__(self, threadName, pageQueue, dataQueue):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.pageQueue = pageQueue
        self.dataQueue = dataQueue
        
        # 请求头
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}

    def run(self):
        print('启动' + self.threadName)
        while not CRAW_EXIT:
            try:
                page = self.pageQueue.get(False)
                url = 'http://www.bookschina.com/kinder/30000000/'.format(page)
                content = requests.get(url, headers=self.headers).content
                self.dataQueue.put(content)
            except Exception:
                print('采集线程错误')
        print('结束：' + self.threadName)

PARSE_EXIT = False  # 解析队列标识，如果为True, 表示数据队列为空，全部数据被解析

# 线程解析类
class ThreadParse(threading.Thread):
    def __init__(self, threadName, dataQueue, books, lock):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.dataQueue = dataQueue
        self.books = books
        self.lock = lock


    def run(self):
        print('启动：' + self.threadName)
        while not PARSE_EXIT:
            try:
                content = self.dataQueue.get(False)
                self.parse(content)
            except Exception as e:
                print('线程解析失败', e)
        print('结束:' + self.threadName)

    def parse(self, content):
        soup = BeautifulSoup(content, 'html5lib')
        bookList= soup.find('div', class_='bookList')

        for item in bookList:
            book={}
            book['img']=bookList.find('div',class_='cover').find('img')['src']
            book['name']=bookList.find('div',class_='cover').find('a').text
            book['janjie']=bookList.find('div',class_='infor').find('p',class_='recoLagu')

            with self.lock:
                self.books.append(book)

def main(pages):
    
    # 页码队列
    pageQueue = Queue(pages)
    for i in range(1, pages + 1):
        pageQueue.put(i)

    # 存放最终数据的列表
    books = []

    # 数据队列，每项内容是content, 即采集类对象获取到的网页源码
    dataQueue = Queue()

    # 线程互斥锁
    lock = threading.Lock()

    # 采集线程的名字列表
    crawNames = ['采集1#', '采集2#', '采集3#', '采集4#']

    # 线程采集对象列表
    threadCrawls = []
    for threadName in crawNames:
        crawl = ThreadCrawl(threadName, pageQueue, dataQueue)  # 初始化采集线程对象
        crawl.start()  # 采集线程对象启动
        threadCrawls.append(crawl)

    # 解析线程的名字列表
    parseNames = ['解析1#', '解析2#','解析3#','解析4#']

    # 线程解析对象列表
    threadParses = []
    for parseName in parseNames:
        parse = ThreadParse(parseName, dataQueue, books, lock)
        parse.start()
        threadParses.append(parse)

    while not pageQueue.empty():
        pass
    
    global CRAW_EXIT
    CRAW_EXIT = True
    print("页码队列为空")
    for thread in threadCrawls:
        thread.join()  # 子线程阴塞主线程，主线程等待子线程结束

    while not dataQueue.empty():
        pass

    global PARSE_EXIT
    PARSE_EXIT = True
    print('数据队列dataQueue为空')
    for thread in threadParses:
        thread.join()

    print(len(books), books[-1])

if __name__ == "__main__":
    t1=time.time()
    try:
        pages = int(input('请输入要爬取多少页'))
    except Exception:
        print('请输入一个大于0的整数')
    t2=time.time()
    main(pages)
    print(t2-t1)