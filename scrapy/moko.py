# -*- coding: UTF-8 -*-
import requests
import random
import re
import time
import threading
import pymongo as pm

# 获取连接
client = pm.MongoClient('123.207.27.181', 27011)
# 连接目标数据库
db = client.moko

# 种子地址
urls = ["http://www.moko.cc/subscribe/chenhaoalex/1.html"]
# 索引
index = 0
# 锁
g_lock = threading.Lock()


class Config():
    def getHeaders(self):
        user_agent_list = [ \
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" \
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
        UserAgent = random.choice(user_agent_list)
        headers = {'User-Agent': UserAgent}
        return headers


class Producer(threading.Thread):
    def run(self):
        print("线程启动...")
        headers = Config().getHeaders()
        print(headers)

        global urls
        global index
        while True:
            g_lock.acquire()
            if len(urls) == 0:
                g_lock.release()
                continue
            page_url = urls.pop()
            g_lock.release()

            response = ""
            try:
                response = requests.get(page_url, headers=headers, timeout=5)
            except Exception as http:
                print("生产者异常")
                print(http)
                continue

            content = response.text
            # 获取用户名（加密的形式）
            rc = re.compile(r'<a class=\"imgBorder\" href=\"\/(.*?)\" hidefocus=\"true\">')
            follows = rc.findall(content)
            print(follows)

            fo_url = []
            threading_links_2 = []
            for u in follows:
                this_url = "http://www.moko.cc/subscribe/%s/1.html" % u
                g_lock.acquire()
                index += 1
                g_lock.release()
                fo_url.append({"index": index, "link": this_url})
                threading_links_2.append(this_url)

            g_lock.acquire()
            urls += threading_links_2
            g_lock.release()
            print(fo_url)

            try:
                db.text.insert_many(fo_url, ordered=False)
            except:
                continue


if __name__ == '__main__':
    p = Producer()
    p.start()
