# -*- coding: UTF-8 -*-
import requests
import threading
import re
import time
import os

# 列表页地址
all_urls = []
# 图片详细页面地址
all_img_urls = []
# 图片地址
pic_links = []
# 初始化锁
g_lock = threading.Lock()


class MeiziSpider:
    # 构造函数
    def __init__(self, target_url, headers):
        self.target_url = target_url
        self.headers = headers

    def getUrls(self, start_page, page_num):
        global all_urls
        for i in range(start_page, page_num + 1):
            url = self.target_url % i
            all_urls.append(url)


# 继承 threading.Thread 类
class Producer(threading.Thread):
    def run(self):
        # 添加头部，数据字典类型
        headers = {
            "Host": "www.meizitu.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.5383.400 QQBrowser/10.0.1313.400"
        }
        global all_urls
        while len(all_urls) > 0:
            # 在访问all_urls时，使用锁机制
            g_lock.acquire()
            page_url = all_urls.pop()
            # 释放锁
            g_lock.release()

            try:
                print("analysis: " + page_url)
                response = requests.get(page_url, headers=headers, timeout=3)
                all_pic_link = re.findall('<a target=\'_blank\' href="(.*?)">', response.text, re.S)
                global all_img_urls
                g_lock.acquire()
                all_img_urls += all_pic_link
                print(all_img_urls)
                g_lock.release()
                time.sleep(0.5)
            except:
                pass


class Consumer(threading.Thread):
    def run(self):
        # 添加头部，数据字典类型
        headers = {
            "Host": "www.meizitu.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.5383.400 QQBrowser/10.0.1313.400"
        }
        global all_img_urls
        print("%s is running " % threading.current_thread)
        while len(all_img_urls) > 0:
            g_lock.acquire()
            img_url = all_img_urls.pop()
            g_lock.release()

            try:
                response = requests.get(img_url, headers=headers, timeout=3)
                # 调整编码
                response.encoding = 'gb2312'
                title = re.search('<title>(.*?) | 妹子图</title>', response.text).group(1)
                all_pic_src = re.findall('<img alt=.*?src="(.*?)" /><br />', response.text, re.S)

                pic_dict = {title: all_pic_src}
                global pic_links
                g_lock.acquire()
                pic_links.append(pic_dict)
                print(title + " 获取成功")
                g_lock.release()
            except:
                pass


class DownPic(threading.Thread):

    def run(self):
        # 添加头部，数据字典类型
        headers = {
            "Host": "pic.topmeizi.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
        }
        while True:
            global pic_links
            g_lock.acquire()
            # 如果没有图片需要下载就解锁
            if len(pic_links) == 0:
                g_lock.release()
                continue
            else:
                pic = pic_links.pop()
                g_lock.release()

                for key, values in pic.items():
                    path = key.rstrip("\\")
                    is_exists = os.path.exists(path)

                    if not is_exists:
                        # 如果不存在则创建文件夹
                        os.makedirs(path)
                        print(path + ' 目录创建成功')
                    else:
                        print(path + ' 目录已存在')

                    for pic in values:
                        filename = path + "/" + pic.split('/')[-1]
                        if os.path.exists(filename):
                            continue
                        else:
                            try:
                                response = requests.get(pic, headers=headers)
                                with open(filename, 'wb') as f:
                                    f.write(response.content)
                                    f.close
                            except Exception as e:
                                print(e)
                                pass


if __name__ == '__main__':
    # 添加头部，数据字典类型
    headers = {
        "Host": "www.meizitu.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.5383.400 QQBrowser/10.0.1313.400"
    }
    target_url = "https://www.meizitu.com/a/list_1_%d.html"
    spider = MeiziSpider(target_url, headers)
    spider.getUrls(1, 16)
    print(all_urls)

    threads = []
    # 开启两个线程进行访问
    for x in range(2):
        t = Producer()
        t.start()
        threads.append(t)

    # 等待上面的线程执行完才往下执行（线程阻塞）
    for tt in threads:
        tt.join()

    # 开启10个线程去获取链接
    for x in range(10):
        ta = Consumer()
        ta.start()

    # 开启10个线程保存图片
    for x in range(10):
        down = DownPic()
        down.start()

    print("进行到我这里了")
