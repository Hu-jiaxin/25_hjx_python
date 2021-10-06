import requests
from queue import Queue
from bs4 import BeautifulSoup
import re 
import gevent
import time

class Spider:
    def __init__(self):
        self.headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}
        #基准网址
        self.base_url='http://www.bookschina.com/kinder/30000000/'
        #数据队列
        self.dataQueue=Queue()
        #统计数量
        #self.count=0
        #数据列表
        self.books=[]
    #获取一页数据的方法
    def get_page_books(self,url):
        content = requests.get(url, headers=self.headers).content
        #对页面数据进行解析
        soup = BeautifulSoup(content, 'html5lib')
        bookList= soup.find('div', class_='bookList')
        for item in bookList:
            book={}
            book['img']=bookList.find('div',class_='cover').find('img')['src']
            book['name']=bookList.find('div',class_='cover').find('a').text
            book['janjie']=bookList.find('div',class_='infor').find('p',class_='recoLagu')

            self.dataQueue.put(book)

    def start_work(self,pageNum):
        job_list=[]
        for page in range(1,pageNum+1):
            url=self.base_url.format(page)
            #创建协成任务
            job=gevent.spawn(self.get_page_books,url)
            #
            job_list.append(job)

        #等待所有协程执行完毕
        gevent.joinall(job_list)

        while not self.dataQueue.empty():
            book = self.dataQueue.get()
            self.books.append(book)
if __name__=="__main__":
    pages=int(input('请输入页码：'))
    t1=time.time()
    spider =Spider()
    spider.start_work(pages)
    print(len(spider.books),spider.books[-1])
    t2=time.time()
    print(t2-t1)